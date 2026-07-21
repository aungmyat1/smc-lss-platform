"""Deterministic baseline runner for corrected ST-C1 research replay."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import yaml

from validation.batch_validation_runner import BatchValidationRunner, ValidationTarget

from .dataset_manifest import build_dataset_manifest, sha256_file, write_manifest
from .diagnostics import failure_counts
from .metrics import combined_metrics, symbol_metrics
from .report_builder import render_table, write_markdown
from .trade_recorder import candidate_rows, event_rows, trade_rows, write_csv


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from symbol_metadata import resolve_symbol
DEFAULT_COST_PROFILE = ROOT / "config" / "research_costs.yaml"
DEFAULT_CACHE_DIR = ROOT / "validation" / "cache" / "baseline"
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
TIMEFRAME_MINUTES = {"M5": 5, "H1": 60, "D1": 1440}


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


def _repo_relative(path: str | Path) -> str:
    candidate = Path(path)
    try:
        return str(candidate.resolve().relative_to(ROOT))
    except Exception:
        return str(candidate)


def _artifact_sha256(path: str | Path) -> str:
    return sha256_file(path)


def _validate_dataset_file(path: Path, *, symbol: str, source_symbol: str, timeframe: str) -> dict[str, Any]:
    if timeframe not in TIMEFRAME_MINUTES:
        raise ValueError(f"{path}: unsupported timeframe {timeframe}")
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    required = {"time", "open", "high", "low", "close"}
    if not rows:
        raise ValueError(f"{path}: empty dataset")
    if not required.issubset(rows[0].keys()):
        missing = ", ".join(sorted(required - set(rows[0].keys())))
        raise ValueError(f"{path}: missing required columns: {missing}")
    prev_time: dt.datetime | None = None
    seen: set[str] = set()
    first_timestamp = last_timestamp = None
    step_minutes = TIMEFRAME_MINUTES[timeframe]
    for row in rows:
        ts = _parse_time(row["time"])
        if row["time"] in seen:
            raise ValueError(f"{path}: duplicate timestamp {row['time']}")
        seen.add(row["time"])
        open_ = float(row["open"])
        high = float(row["high"])
        low = float(row["low"])
        close = float(row["close"])
        if high < low or high < max(open_, close) or low > min(open_, close):
            raise ValueError(f"{path}: invalid OHLC at {row['time']}")
        if prev_time is not None and ts < prev_time:
            raise ValueError(f"{path}: candles must be sorted chronologically")
        if prev_time is not None:
            delta_minutes = int((ts - prev_time).total_seconds() / 60)
            if delta_minutes < step_minutes:
                raise ValueError(f"{path}: timeframe spacing smaller than expected for {timeframe}")
        prev_time = ts
        first_timestamp = first_timestamp or ts
        last_timestamp = ts
    return {
        "symbol": symbol,
        "source_symbol": source_symbol,
        "timeframe": timeframe,
        "path": _repo_relative(path),
        "rows": len(rows),
        "first_timestamp": first_timestamp.isoformat().replace("+00:00", "Z") if first_timestamp else None,
        "last_timestamp": last_timestamp.isoformat().replace("+00:00", "Z") if last_timestamp else None,
        "timezone": "UTC",
        "bar_semantics": _bar_semantics(timeframe),
    }


def _dataset_stats(path: Path, *, symbol: str, source_symbol: str, timeframe: str) -> dict[str, Any]:
    return _validate_dataset_file(path, symbol=symbol, source_symbol=source_symbol, timeframe=timeframe)


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


def _aggregate_trade_components(results: Iterable[Any]) -> dict[str, float | int]:
    trades = [trade for result in results for trade in getattr(result, "trades", [])]
    return {
        "trade_count": len(trades),
        "gross_r": round(sum(float(trade.gross_r) for trade in trades), 6),
        "net_r": round(sum(float(trade.net_r) for trade in trades), 6),
        "spread_r": round(sum(float(trade.spread_r) for trade in trades), 6),
        "slippage_r": round(sum(float(trade.slippage_r) for trade in trades), 6),
        "commission_r": round(sum(float(trade.commission_r) for trade in trades), 6),
        "swap_r": round(sum(float(trade.swap_r) for trade in trades), 6),
        "total_cost_drag_r": round(sum(float(trade.cost_r) for trade in trades), 6),
    }


def _artifact_hashes(run_dir: Path) -> dict[str, str]:
    mapping = {
        "manifest": run_dir / "baseline_manifest.json",
        "metrics": run_dir / "baseline_metrics.json",
        "report": run_dir / "baseline_report.md",
        "trades": run_dir / "baseline_trades.csv",
        "equity": run_dir / "baseline_equity.csv",
        "management_events": run_dir / "management_events.csv",
        "rejected_candidates": run_dir / "rejected_candidates.csv",
    }
    return {name: _artifact_sha256(path) for name, path in mapping.items() if path.exists()}


def _resolve_artifact_path(root: Path, raw_value: str) -> Path:
    candidate = Path(raw_value)
    search_paths = [candidate] if candidate.is_absolute() else [(root / candidate), (ROOT / candidate), candidate]
    for path in search_paths:
        resolved = path.resolve()
        if resolved.exists():
            return resolved
    return search_paths[0].resolve()


def resolve_latest_run(output_root: str | Path) -> dict[str, Any]:
    root = Path(output_root)
    latest_path = root / "LATEST.json"
    if not latest_path.exists():
        raise FileNotFoundError(f"{latest_path} does not exist")
    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    if not isinstance(latest, dict):
        raise ValueError(f"{latest_path}: expected a mapping")
    required = {"run_id", "run_dir", "manifest_path", "metrics_path", "report_path"}
    missing = sorted(required - set(latest))
    if missing:
        raise ValueError(f"{latest_path}: missing keys: {', '.join(missing)}")
    if not latest.get("complete", False):
        raise ValueError(f"{latest_path}: incomplete run pointer")
    run_dir = _resolve_artifact_path(root, str(latest["run_dir"]))
    if not run_dir.exists():
        raise FileNotFoundError(f"{latest_path}: run directory missing: {run_dir}")
    artifact_hashes = latest.get("artifact_hashes", {})
    if not isinstance(artifact_hashes, dict):
        raise ValueError(f"{latest_path}: artifact_hashes must be a mapping")
    for rel_key in ("manifest_path", "metrics_path", "report_path", "run_dir"):
        file_path = _resolve_artifact_path(root, str(latest[rel_key]))
        if not file_path.exists():
            raise FileNotFoundError(f"{latest_path}: missing artifact {file_path}")
    for artifact_name, expected_hash in artifact_hashes.items():
        file_name = {
            "manifest": "baseline_manifest.json",
            "metrics": "baseline_metrics.json",
            "report": "baseline_report.md",
            "trades": "baseline_trades.csv",
            "equity": "baseline_equity.csv",
            "management_events": "management_events.csv",
            "rejected_candidates": "rejected_candidates.csv",
        }.get(artifact_name)
        if not file_name:
            continue
        file_path = run_dir / file_name
        if not file_path.exists():
            raise FileNotFoundError(f"{latest_path}: missing artifact {file_path}")
        if expected_hash != _artifact_sha256(file_path):
            raise ValueError(f"{latest_path}: hash mismatch for {artifact_name}")
    return latest


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def _frame_from_rows(rows: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if not df.empty and "entry_time" in df.columns:
        df = df.sort_values(by=["entry_time", "signal_time", "entry_index"], kind="stable")
    return df


def run_baseline(
    spec_path: str | Path,
    data_dir: str | Path,
    output_dir: str | Path,
    random_seed: int = 7,
    *,
    cache_dir: str | Path = DEFAULT_CACHE_DIR,
    resume: bool = False,
    symbols: Iterable[str] | None = None,
    progress_every: int = 1000,
) -> dict[str, Any]:
    spec = _load_spec(spec_path)
    _validate_spec_shape(spec, spec_path)
    strategy = spec.get("strategy", {})
    data_dir = Path(data_dir)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    cache_dir = Path(cache_dir)
    requested_symbols = _resolve_requested_symbols(spec, symbols)

    run_id = f"{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    staging_dir = Path(
        tempfile.mkdtemp(prefix=f"{output_root.name}.staging.", dir=str(output_root.parent))
    )
    run_dir = output_root / run_id
    latest_path = output_root / "LATEST.json"
    published = False

    try:
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
            start_index = len(dataset_metadata)
            for timeframe, path in paths.items():
                dataset_metadata.append(
                    _dataset_stats(path, symbol=meta.canonical_symbol, source_symbol=source_symbol, timeframe=timeframe)
                )
            date_ranges[meta.canonical_symbol] = {
                "start": dataset_metadata[start_index]["first_timestamp"],
                "end": dataset_metadata[start_index]["last_timestamp"],
            }

        if missing_datasets:
            raise ValueError("missing required baseline datasets:\n- " + "\n- ".join(missing_datasets))
        if not targets:
            raise ValueError("no datasets found for baseline run")

        runner = BatchValidationRunner(
            cache_dir=cache_dir,
            report_path=staging_dir / "stc1_validation_report.md",
            warmup_bars=20,
            progress_every=progress_every,
        )
        results = [runner.run_job(target, resume=resume) for target in targets]
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
            equity_frame = equity_frame[["entry_time", "cum_net_r"]]
        else:
            equity_frame = pd.DataFrame(columns=["entry_time", "cum_net_r"])

        symbol_metrics_map = symbol_metrics(replay_results)
        combined = combined_metrics(replay_results)
        failures = failure_counts(replay_results)
        funnel_counts = _aggregate_funnel_counts(replay_results)
        cost_breakdown = _aggregate_trade_components(replay_results)

        manifest = build_dataset_manifest(
            strategy_id=str(strategy.get("strategy_id", "ST-C1")),
            strategy_version=str(strategy.get("version", "unknown")),
            git_sha=_git_sha(),
            generated_utc=dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            random_seed=random_seed,
            spec_path=str(spec_path),
            cost_profile_path=str(DEFAULT_COST_PROFILE),
            spec_sha256=sha256_file(spec_path),
            cost_profile_sha256=sha256_file(DEFAULT_COST_PROFILE) if DEFAULT_COST_PROFILE.exists() else None,
            runner_fingerprint=runner.runner_fingerprint,
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
            dirty_worktree=None,
        )

        write_manifest(staging_dir / "baseline_manifest.json", manifest)
        (staging_dir / "baseline_metrics.json").write_text(
            json.dumps(
                {
                    "combined": combined,
                    "by_symbol": symbol_metrics_map,
                    "failure_counts": failures,
                    "funnel_counts": funnel_counts,
                    "cost_breakdown": cost_breakdown,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        trade_columns = [
            "signal_index",
            "signal_time",
            "entry_index",
            "entry_time",
            "exit_index",
            "exit_time",
            "direction",
            "entry",
            "stop",
            "target",
            "exit_price",
            "gross_r",
            "cost_r",
            "net_r",
            "outcome",
            "structure_key",
            "symbol_metadata_version",
            "spread_price",
            "spread_points",
            "spread_pips",
            "entry_slippage_price",
            "exit_slippage_price",
            "slippage_price_round_trip",
            "commission_usd_round_turn",
            "commission",
            "spread_r",
            "slippage_r",
            "commission_r",
            "swap_r",
            "price_cost_round_trip",
            "total_cost",
            "total_cost_r",
            "partial_taken",
            "break_even_activated",
            "ambiguous_bar",
            "unresolved_open_position",
            "management_events",
            "experiment_id",
            "strategy_id",
            "strategy_version",
            "symbol",
        ]
        event_columns = [
            "experiment_id",
            "event",
            "bar",
            "fraction",
            "new_stop",
            "symbol",
            "strategy_version",
            "trade_id",
            "remaining_fraction",
            "stop_before",
            "stop_after",
            "price",
            "reason",
        ]
        equity_columns = ["entry_time", "cum_net_r"]
        candidate_columns = [
            "signal_time",
            "stage",
            "direction",
            "structure_key",
            "rejection_reason",
            "symbol",
            "metadata",
            "experiment_id",
        ]
        candidate_frame = pd.DataFrame(candidate_rows_all)
        if candidate_frame.empty:
            candidate_frame = pd.DataFrame(columns=candidate_columns)
        else:
            for column in candidate_columns:
                if column not in candidate_frame.columns:
                    candidate_frame[column] = None
            candidate_frame = candidate_frame[candidate_columns]
        write_csv(staging_dir / "baseline_trades.csv", trade_rows_all, fieldnames=trade_columns)
        write_csv(staging_dir / "baseline_equity.csv", equity_frame.to_dict(orient="records"), fieldnames=equity_columns)
        write_csv(staging_dir / "management_events.csv", event_rows_all, fieldnames=event_columns)
        candidate_frame.to_csv(staging_dir / "rejected_candidates.csv", index=False, columns=candidate_columns)

        lines = [
            "# ST-C1 Corrected Baseline Report",
            "",
            f"- Strategy: `{strategy.get('strategy_id', 'ST-C1')}`",
            f"- Version: `{strategy.get('version', 'unknown')}`",
            f"- Git SHA: `{_git_sha()}`",
            f"- Runner fingerprint: `{runner.runner_fingerprint}`",
            f"- Dataset count: `{len(manifest.datasets)}`",
            f"- Funnel records: `{len(candidate_rows_all)}`",
            "",
            "## Combined Metrics",
            "",
            render_table(
                ["Metric", "Value"],
                [[key, combined.get(key)] for key in ("total_trades", "win_rate_pct", "profit_factor", "expectancy_r", "maximum_drawdown_r", "sharpe_ratio")],
            ),
            "",
            "## R Breakdown",
            "",
            render_table(
                ["Metric", "Value"],
                [[key, cost_breakdown.get(key)] for key in ("trade_count", "gross_r", "net_r", "spread_r", "slippage_r", "commission_r", "swap_r", "total_cost_drag_r")],
            ),
            "",
            "## Funnel Counts",
            "",
            render_table(["Metric", "Value"], list(funnel_counts.items())) if funnel_counts else "No funnel counts available.",
            "",
            "## By Symbol",
            "",
        ]
        for symbol, metrics in symbol_metrics_map.items():
            lines.extend(
                [
                    f"### {symbol}",
                    render_table(
                        ["Metric", "Value"],
                        [[key, metrics.get(key)] for key in ("total_trades", "win_rate_pct", "profit_factor", "expectancy_r", "maximum_drawdown_r", "sharpe_ratio")],
                    ),
                    "",
                ]
            )
        lines.extend(
            [
                "## Notes",
                "",
                "- Higher-timeframe context is gated on bar-close visibility.",
                "- Cost drag is split into spread, slippage, commission, and swap components.",
                "- Rejected candidates and management events are persisted as dedicated artifacts.",
            ]
        )
        write_markdown(staging_dir / "baseline_report.md", lines)

        if run_dir.exists():
            raise FileExistsError(f"{run_dir} already exists")
        staging_dir.replace(run_dir)
        published = True
        artifact_hashes = _artifact_hashes(run_dir)

        latest_payload = {
            "run_id": run_id,
            "run_dir": _repo_relative(run_dir),
            "report_path": _repo_relative(run_dir / "baseline_report.md"),
            "manifest_path": _repo_relative(run_dir / "baseline_manifest.json"),
            "metrics_path": _repo_relative(run_dir / "baseline_metrics.json"),
            "created_utc": manifest.generated_utc,
            "runner_fingerprint": runner.runner_fingerprint,
            "dirty_worktree": manifest.dirty_worktree,
            "spec_sha256": manifest.spec_sha256,
            "cost_profile_sha256": manifest.cost_profile_sha256,
            "complete": True,
            "artifact_hashes": artifact_hashes,
        }
        _atomic_write_json(latest_path, latest_payload)

        return {
            "run_id": run_id,
            "run_dir": str(run_dir),
            "latest_path": str(latest_path),
            "manifest": manifest.to_dict(),
            "combined": combined,
            "by_symbol": symbol_metrics_map,
            "failure_counts": failures,
            "funnel_counts": funnel_counts,
            "cost_breakdown": cost_breakdown,
            "report_path": str(run_dir / "baseline_report.md"),
            "metrics_path": str(run_dir / "baseline_metrics.json"),
        }
    finally:
        if not published and staging_dir.exists():
            shutil.rmtree(staging_dir, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run corrected ST-C1 baseline research replay.")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--symbols", default="")
    parser.add_argument("--progress-every", type=int, default=1000)
    args = parser.parse_args(argv)
    symbols = [item.strip() for item in args.symbols.split(",") if item.strip()] or None
    run_baseline(
        args.spec,
        args.data_dir,
        args.output,
        random_seed=args.seed,
        cache_dir=args.cache_dir,
        resume=not args.no_resume,
        symbols=symbols,
        progress_every=args.progress_every,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
