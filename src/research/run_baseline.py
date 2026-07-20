"""Deterministic baseline runner for corrected ST-C1 research replay."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import yaml

from symbol_metadata import resolve_symbol
from validation.batch_validation_runner import BatchValidationRunner, ValidationTarget

from .dataset_manifest import build_dataset_manifest, write_manifest
from .diagnostics import failure_counts
from .metrics import combined_metrics, symbol_metrics
from .report_builder import render_table, write_markdown
from .trade_recorder import candidate_rows, event_rows, trade_rows, write_csv


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COST_PROFILE = ROOT / "config" / "research_costs.yaml"
DEPRECATED_TIMEFRAME_KEYS = {
    "version",
    "track",
    "status",
    "promotion_stage",
    "symbol",
    "htf",
    "entry_tf",
    "ltf_confirm",
    "swing_lookback",
    "equal_level_tol_pips",
    "min_fvg_pips",
    "risk_pct",
    "min_rr",
    "sessions",
}
REQUIRED_TIMEFRAMES = ("M5", "H1", "D1")


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "unknown"


def _load_spec(path: str | Path) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a mapping")
    return data


def _validate_spec_shape(spec: dict[str, Any], spec_path: str | Path) -> None:
    legacy_keys = sorted(key for key in spec.keys() if key in DEPRECATED_TIMEFRAME_KEYS)
    if legacy_keys:
        raise ValueError(
            f"{spec_path}: deprecated top-level timeframe/spec keys are not allowed: {', '.join(legacy_keys)}. "
            "Use market_universe.timeframes as the authoritative model."
        )
    market = spec.get("market_universe")
    if not isinstance(market, dict):
        raise ValueError(f"{spec_path}: missing market_universe mapping")
    timeframes = market.get("timeframes")
    if not isinstance(timeframes, dict):
        raise ValueError(f"{spec_path}: missing market_universe.timeframes mapping")
    required = {"bias", "setup", "confirmation", "execution"}
    missing = sorted(required - set(timeframes))
    if missing:
        raise ValueError(f"{spec_path}: market_universe.timeframes missing keys: {', '.join(missing)}")
    if len({str(timeframes[key]) for key in required}) < 2:
        raise ValueError(
            f"{spec_path}: market_universe.timeframes must contain a multi-timeframe model, not one repeated label"
        )


def _parse_time(value: str) -> dt.datetime:
    cleaned = value.replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(cleaned)
    except ValueError:
        parsed = dt.datetime.strptime(value[:16], "%Y-%m-%d %H:%M")
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt.UTC)
    return parsed.astimezone(dt.UTC)


def _bar_semantics(timeframe: str) -> str:
    return f"{timeframe.upper()} bar-open timestamp; visible only after close"


def _dataset_stats(path: Path, *, symbol: str, source_symbol: str, timeframe: str) -> dict[str, Any]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    first_timestamp = _parse_time(rows[0]["time"]).isoformat().replace("+00:00", "Z") if rows else None
    last_timestamp = _parse_time(rows[-1]["time"]).isoformat().replace("+00:00", "Z") if rows else None
    return {
        "symbol": symbol,
        "source_symbol": source_symbol,
        "timeframe": timeframe,
        "path": str(path),
        "rows": len(rows),
        "first_timestamp": first_timestamp,
        "last_timestamp": last_timestamp,
        "timezone": "UTC",
        "bar_semantics": _bar_semantics(timeframe),
    }


def _resolve_symbol_datasets(data_dir: Path, symbol: str) -> tuple[str, dict[str, Path]]:
    meta = resolve_symbol(symbol)
    checked: list[str] = []
    for prefix in (meta.canonical_symbol, *meta.aliases):
        checked.append(prefix)
        paths = {timeframe: data_dir / f"{prefix}_{timeframe}.csv" for timeframe in REQUIRED_TIMEFRAMES}
        if all(path.exists() for path in paths.values()):
            return prefix, paths
    missing = ", ".join(checked) if checked else symbol
    raise ValueError(f"{symbol}: missing required M5/H1/D1 datasets after checking prefixes: {missing}")


def _atomic_copy_tree(source: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for path in source.rglob("*"):
        if path.is_dir():
            continue
        relative = path.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def _frame_from_rows(rows: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if not df.empty and "entry_time" in df.columns:
        df = df.sort_values(by=["entry_time", "signal_time", "entry_index"], kind="stable")
    return df


def _resolve_requested_symbols(spec: dict[str, Any], requested: Iterable[str] | None) -> list[str]:
    if requested:
        return list(requested)
    market = spec.get("market_universe", {})
    instruments = list(market.get("instruments", [])) if isinstance(market, dict) else []
    if instruments:
        return instruments
    return [str(spec.get("symbol", "EURUSD"))]


def _aggregate_funnel_counts(results: list[Any]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for result in results:
        for key, value in getattr(result, "funnel_counts", {}).items():
            totals[key] = totals.get(key, 0) + int(value)
    return dict(sorted(totals.items()))


def run_baseline(
    spec_path: str | Path,
    data_dir: str | Path,
    output_dir: str | Path,
    random_seed: int = 7,
    symbols: Iterable[str] | None = None,
    progress_every: int = 1000,
) -> dict[str, Any]:
    spec = _load_spec(spec_path)
    _validate_spec_shape(spec, spec_path)
    strategy = spec.get("strategy", {})
    output_dir = Path(output_dir)
    data_dir = Path(data_dir)
    requested_symbols = _resolve_requested_symbols(spec, symbols)

    targets: list[ValidationTarget] = []
    dataset_metadata: list[dict[str, Any]] = []
    date_ranges: dict[str, Any] = {}
    missing_datasets: list[str] = []

    for requested_symbol in requested_symbols:
        meta = resolve_symbol(requested_symbol)
        try:
            source_symbol, paths = _resolve_symbol_datasets(data_dir, requested_symbol)
        except ValueError as exc:
            missing_datasets.append(str(exc))
            continue
        target = ValidationTarget(
            symbol=meta.canonical_symbol,
            timeframe="M5",
            m5_path=str(paths["M5"]),
            h1_path=str(paths["H1"]),
            d1_path=str(paths["D1"]),
            source_symbol=source_symbol,
        )
        targets.append(target)
        for timeframe, path in paths.items():
            dataset_metadata.append(_dataset_stats(path, symbol=meta.canonical_symbol, source_symbol=source_symbol, timeframe=timeframe))
        date_ranges[meta.canonical_symbol] = {
            "start": dataset_metadata[-3]["first_timestamp"],
            "end": dataset_metadata[-3]["last_timestamp"],
        }

    if missing_datasets:
        raise ValueError("missing required baseline datasets:\n- " + "\n- ".join(missing_datasets))
    if not targets:
        raise ValueError("no datasets found for baseline run")

    runner = BatchValidationRunner(
        cache_dir=ROOT / "validation" / "cache",
        report_path=output_dir / "stc1_validation_report.md",
        progress_every=progress_every,
    )
    results = [runner.run_job(target, resume=True) for target in targets]
    if not all(result.complete for result in results):
        raise ValueError("baseline run did not complete for every requested symbol")
    replay_results = [item.result for item in results]

    trade_rows_all = [row for result in replay_results for row in trade_rows(result, experiment_id="baseline")]
    event_rows_all = [row for result in replay_results for row in event_rows(result, experiment_id="baseline")]
    candidate_rows_all = [row for result in replay_results for row in candidate_rows(result, experiment_id="baseline")]

    trade_frame = _frame_from_rows(trade_rows_all)
    equity_frame = trade_frame.copy()
    if not equity_frame.empty:
        equity_frame["cum_net_r"] = equity_frame["net_r"].cumsum()
    else:
        equity_frame = pd.DataFrame(columns=["entry_time", "cum_net_r"])

    symbol_metrics_map = symbol_metrics(replay_results)
    combined = combined_metrics(replay_results)
    failures = failure_counts(replay_results)
    funnel_counts = _aggregate_funnel_counts(replay_results)

    manifest = build_dataset_manifest(
        strategy_id=str(strategy.get("strategy_id", "ST-C1")),
        strategy_version=str(strategy.get("version", "unknown")),
        git_sha=_git_sha(),
        generated_utc=dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        random_seed=random_seed,
        spec_path=str(spec_path),
        cost_profile_path=str(DEFAULT_COST_PROFILE),
        dataset_paths=[item["path"] for item in dataset_metadata],
        symbols=[item["symbol"] for item in dataset_metadata if item["timeframe"] == "M5"],
        timeframes=list(REQUIRED_TIMEFRAMES),
        date_ranges=date_ranges,
        execution_assumptions={
            "entry": "next-bar-open",
            "stop_first": True,
            "managed_partial": True,
            "breakeven": True,
            "slippage_convention": "per_side",
            "commission_unit": "usd_round_turn",
        },
        dataset_metadata=dataset_metadata,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    staging_dir = Path(tempfile.mkdtemp(prefix=f"{output_dir.name}.staging.", dir=str(output_dir.parent)))

    write_manifest(staging_dir / "baseline_manifest.json", manifest)
    (staging_dir / "baseline_metrics.json").write_text(
        json.dumps({"combined": combined, "by_symbol": symbol_metrics_map, "failure_counts": failures, "funnel_counts": funnel_counts}, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    write_csv(staging_dir / "baseline_trades.csv", trade_rows_all)
    write_csv(staging_dir / "baseline_equity.csv", equity_frame.to_dict(orient="records"))
    write_csv(staging_dir / "management_events.csv", event_rows_all)
    candidate_columns = ["signal_time", "stage", "direction", "structure_key", "rejection_reason", "symbol", "metadata", "experiment_id"]
    candidate_frame = pd.DataFrame(candidate_rows_all)
    if candidate_frame.empty:
        candidate_frame = pd.DataFrame(columns=candidate_columns)
    else:
        for column in candidate_columns:
            if column not in candidate_frame.columns:
                candidate_frame[column] = None
        candidate_frame = candidate_frame[candidate_columns]
    candidate_frame.to_csv(staging_dir / "rejected_candidates.csv", index=False)

    lines = [
        "# ST-C1 Corrected Baseline Report",
        "",
        f"- Spec: `{spec_path}`",
        f"- Git SHA: `{_git_sha()}`",
        f"- Strategy version: `{strategy.get('version', 'unknown')}`",
        f"- Symbols: `{', '.join(item['symbol'] for item in dataset_metadata if item['timeframe'] == 'M5')}`",
        f"- Dataset count: `{len(manifest.datasets)}`",
        f"- Funnel records: `{len(candidate_rows_all)}`",
        "",
        "## Combined Metrics",
        "",
        render_table(["Key", "Value"], list(combined.items())) if combined else "No metrics available.",
        "",
        "## Funnel Counts",
        "",
        render_table(["Key", "Value"], list(funnel_counts.items())) if funnel_counts else "No funnel counts available.",
        "",
        "## Symbol Metrics",
        "",
    ]
    for symbol, metrics in symbol_metrics_map.items():
        lines.append(f"### {symbol}")
        lines.append("")
        lines.append(render_table(["Key", "Value"], list(metrics.items())) if metrics else "No symbol metrics available.")
        lines.append("")
    lines.extend(
        [
            "## Notes",
            "",
            "- Higher-timeframe context is gated on bar close visibility.",
            "- Slippage is recorded as per-side price movement; USD commission is tracked separately.",
            "- Rejected candidates and stage funnel counts are persisted in dedicated CSV/JSON artifacts.",
        ]
    )
    write_markdown(staging_dir / "baseline_report.md", lines)

    _atomic_copy_tree(staging_dir, output_dir)

    return {
        "manifest": manifest.to_dict(),
        "combined": combined,
        "by_symbol": symbol_metrics_map,
        "failure_counts": failures,
        "funnel_counts": funnel_counts,
        "output_dir": str(output_dir),
        "staging_dir": str(staging_dir),
        "results": [result.assumptions for result in replay_results],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run corrected ST-C1 baseline research replay.")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--symbols", default="")
    parser.add_argument("--progress-every", type=int, default=1000)
    args = parser.parse_args(argv)
    symbols = [item.strip() for item in args.symbols.split(",") if item.strip()] or None
    run_baseline(args.spec, args.data_dir, args.output, random_seed=args.seed, symbols=symbols, progress_every=args.progress_every)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
