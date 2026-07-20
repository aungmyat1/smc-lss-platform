"""Deterministic baseline runner for corrected ST-C1 research replay."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from validation.historical_replay_engine import HistoricalReplayEngine
from symbol_metadata import resolve_symbol

from .dataset_manifest import build_dataset_manifest, write_manifest
from .diagnostics import failure_counts
from .metrics import combined_metrics, symbol_metrics
from .report_builder import render_table, write_markdown
from .trade_recorder import candidate_rows, event_rows, trade_rows, write_csv


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COST_PROFILE = ROOT / "config" / "research_costs.yaml"
DEPRECATED_TIMEFRAME_KEYS = {"version", "track", "status", "promotion_stage", "symbol", "htf", "entry_tf", "ltf_confirm", "swing_lookback", "equal_level_tol_pips", "min_fvg_pips", "risk_pct", "min_rr", "sessions"}


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
        raise ValueError(f"{spec_path}: market_universe.timeframes must contain a multi-timeframe model, not one repeated label")


def _dataset_paths(data_dir: Path, symbols: list[str]) -> list[Path]:
    paths: list[Path] = []
    for symbol in symbols:
        meta = resolve_symbol(symbol)
        prefixes = [meta.canonical_symbol, *meta.aliases]
        for timeframe in ("M5", "H1", "D1"):
            for prefix in prefixes:
                path = data_dir / f"{prefix}_{timeframe}.csv"
                if path.exists():
                    paths.append(path)
                    break
    return paths


def _frame_from_rows(rows: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if not df.empty and "entry_time" in df.columns:
        df = df.sort_values(by=["entry_time", "signal_time", "entry_index"], kind="stable")
    return df


def run_baseline(spec_path: str | Path, data_dir: str | Path, output_dir: str | Path, random_seed: int = 7) -> dict[str, Any]:
    spec = _load_spec(spec_path)
    _validate_spec_shape(spec, spec_path)
    strategy = spec.get("strategy", {})
    market = spec.get("market_universe", {})
    instruments = list(market.get("instruments", []))
    if not instruments:
        instruments = [spec.get("symbol", "EURUSD")]
    data_dir = Path(data_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    engine = HistoricalReplayEngine(
        contract_path=str(spec_path),
        point_size=None,
        cost_profile_path=str(DEFAULT_COST_PROFILE),
        warmup_bars=20,
    )
    results = []
    for symbol in instruments:
        meta = resolve_symbol(symbol)
        prefixes = [meta.canonical_symbol, *meta.aliases]
        m5_path = next((data_dir / f"{prefix}_M5.csv" for prefix in prefixes if (data_dir / f"{prefix}_M5.csv").exists()), None)
        h1_path = next((data_dir / f"{prefix}_H1.csv" for prefix in prefixes if (data_dir / f"{prefix}_H1.csv").exists()), None)
        d1_path = next((data_dir / f"{prefix}_D1.csv" for prefix in prefixes if (data_dir / f"{prefix}_D1.csv").exists()), None)
        if m5_path is None:
            continue
        m5, h1, d1 = engine.load_series(str(m5_path), h1_path=str(h1_path) if h1_path else None, d1_path=str(d1_path) if d1_path else None)
        results.append(engine.replay(m5, h1=h1, d1=d1, symbol=symbol))

    if not results:
        raise ValueError("no datasets found for baseline run")

    trade_rows_all = [row for result in results for row in trade_rows(result, experiment_id="baseline")]
    event_rows_all = [row for result in results for row in event_rows(result, experiment_id="baseline")]
    candidate_rows_all = [row for result in results for row in candidate_rows(result, experiment_id="baseline")]

    trade_frame = _frame_from_rows(trade_rows_all)
    equity_frame = trade_frame.copy()
    if not equity_frame.empty:
        equity_frame["cum_net_r"] = equity_frame["net_r"].cumsum()
    else:
        equity_frame = pd.DataFrame(columns=["entry_time", "cum_net_r"])

    symbol_metrics_map = symbol_metrics(results)
    combined = combined_metrics(results)
    failures = failure_counts(results)

    manifest = build_dataset_manifest(
        strategy_id=strategy.get("strategy_id", "ST-C1"),
        strategy_version=str(strategy.get("version", "unknown")),
        git_sha=_git_sha(),
        generated_utc=dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        random_seed=random_seed,
        spec_path=str(spec_path),
        cost_profile_path=str(DEFAULT_COST_PROFILE),
        dataset_paths=_dataset_paths(data_dir, instruments),
        symbols=instruments,
        timeframes=("M5", "H1", "D1"),
        date_ranges={symbol: {"start": None, "end": None} for symbol in instruments},
        execution_assumptions={"entry": "next-bar-open", "stop_first": True, "managed_partial": True, "breakeven": True},
    )

    write_manifest(output_dir / "baseline_manifest.json", manifest)
    trade_frame.to_csv(output_dir / "baseline_trades.csv", index=False)
    equity_frame.to_csv(output_dir / "baseline_equity.csv", index=False)
    pd.DataFrame(event_rows_all).to_csv(output_dir / "management_events.csv", index=False)
    pd.DataFrame(candidate_rows_all).to_csv(output_dir / "rejected_candidates.csv", index=False)
    (output_dir / "baseline_metrics.json").write_text(json.dumps({"combined": combined, "by_symbol": symbol_metrics_map, "failure_counts": failures}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# ST-C1 Corrected Baseline Report",
        "",
        f"- Strategy: `{strategy.get('strategy_id', 'ST-C1')}`",
        f"- Version: `{strategy.get('version', 'unknown')}`",
        f"- Git SHA: `{_git_sha()}`",
        f"- Dataset count: `{len(manifest.datasets)}`",
        "",
        "## Combined Metrics",
        "",
        render_table(
            ["Metric", "Value"],
            [[key, combined.get(key)] for key in ("total_trades", "win_rate_pct", "profit_factor", "expectancy_r", "maximum_drawdown_r", "sharpe_ratio")],
        ),
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
    write_markdown(output_dir / "baseline_report.md", lines)
    return {
        "manifest": manifest.to_dict(),
        "combined": combined,
        "by_symbol": symbol_metrics_map,
        "failure_counts": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run corrected ST-C1 baseline research replay.")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args(argv)
    run_baseline(args.spec, args.data_dir, args.output, random_seed=args.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
