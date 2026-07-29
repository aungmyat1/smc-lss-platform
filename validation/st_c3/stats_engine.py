"""ST-C3 stats engine bound to a verified replay ledger hash."""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from validation.performance_metrics import compute_metrics
from validation.st_c3.replay_engine import load_ledger, verify_ledger_hash

STATS_ENGINE_VERSION = "st_c3_stats_engine.v1"


@dataclass(frozen=True)
class StatsResult:
    status: str
    ledger_sha256: str
    stats_engine_version: str
    metrics: Mapping[str, Any]
    thresholds: Mapping[str, Any]
    threshold_results: Mapping[str, bool]
    stability: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DEFAULT_KPI_THRESHOLDS = {
    "min_profit_factor": 1.40,
    "min_expectancy_r": 0.20,
    "min_sharpe_ratio": 1.20,
}


def compute_stats_from_ledger(
    ledger_path: str | Path,
    hash_path: str | Path,
    thresholds: Mapping[str, Any] | None = None,
) -> StatsResult:
    ledger_sha256 = verify_ledger_hash(ledger_path, hash_path)
    ledger = load_ledger(ledger_path)
    trades = ledger["trades"]
    metrics = compute_metrics([float(trade["r"]) for trade in trades])
    kpis = dict(DEFAULT_KPI_THRESHOLDS)
    if thresholds:
        kpis.update(thresholds)
    threshold_results = check_kpi_thresholds(metrics, kpis)
    status = "PASS" if all(threshold_results.values()) else "FAIL"
    return StatsResult(
        status=status,
        ledger_sha256=ledger_sha256,
        stats_engine_version=STATS_ENGINE_VERSION,
        metrics=metrics,
        thresholds=kpis,
        threshold_results=threshold_results,
        stability=build_stability_summary(trades),
    )


def check_kpi_thresholds(metrics: Mapping[str, Any], thresholds: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "profit_factor": _finite_at_least(metrics.get("profit_factor"), thresholds["min_profit_factor"]),
        "expectancy_r": _finite_at_least(metrics.get("expectancy_r"), thresholds["min_expectancy_r"]),
        "sharpe_ratio": _finite_at_least(metrics.get("sharpe_ratio"), thresholds["min_sharpe_ratio"]),
    }


def build_stability_summary(trades: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    trade_list = list(trades)
    return {
        "by_symbol": _group_metrics(trade_list, lambda trade: str(trade["symbol"])),
        "by_session": _group_metrics(trade_list, lambda trade: str(trade["session"])),
        "by_direction": _group_metrics(trade_list, lambda trade: str(trade["direction"])),
        "by_year": _group_metrics(trade_list, lambda trade: str(trade["timestamp_entry"])[:4]),
    }


def write_stats_report(result: StatsResult, json_path: str | Path, md_path: str | Path | None = None) -> Path:
    out_path = Path(json_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if md_path is not None:
        Path(md_path).write_text(_stats_markdown(result), encoding="utf-8")
    return out_path


def _group_metrics(trades: list[Mapping[str, Any]], label_fn) -> dict[str, Any]:
    grouped: dict[str, list[float]] = {}
    for trade in trades:
        grouped.setdefault(label_fn(trade), []).append(float(trade["r"]))
    return {label: compute_metrics(values) for label, values in sorted(grouped.items())}


def _finite_at_least(value: Any, minimum: float) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and float(value) >= minimum


def _stats_markdown(result: StatsResult) -> str:
    metrics = result.metrics
    return "\n".join(
        [
            "# ST-C3 Replay Statistics",
            "",
            f"- Status: `{result.status}`",
            f"- Ledger SHA-256: `{result.ledger_sha256}`",
            f"- Stats engine: `{result.stats_engine_version}`",
            f"- Expectancy R: `{metrics.get('expectancy_r')}`",
            f"- Profit factor: `{metrics.get('profit_factor')}`",
            f"- Win rate pct: `{metrics.get('win_rate_pct')}`",
            f"- Average R: `{metrics.get('average_r')}`",
            f"- Max drawdown R: `{metrics.get('maximum_drawdown_r')}`",
            f"- Recovery factor: `{metrics.get('recovery_factor')}`",
            f"- Sharpe: `{metrics.get('sharpe_ratio')}`",
            f"- Sortino: `{metrics.get('sortino_ratio')}`",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=Path("reports/validation/st_c3/replay/ledger.json"))
    parser.add_argument("--hash", type=Path, default=Path("reports/validation/st_c3/replay/ledger.hash"))
    parser.add_argument("--json-out", type=Path, default=Path("reports/validation/st_c3/replay/stats_summary.json"))
    parser.add_argument("--md-out", type=Path, default=Path("reports/validation/st_c3/replay/stats_summary.md"))
    args = parser.parse_args()
    result = compute_stats_from_ledger(args.ledger, args.hash)
    write_stats_report(result, args.json_out, args.md_out)
    print(json.dumps({"status": result.status, "ledger_sha256": result.ledger_sha256, "output": str(args.json_out)}, indent=2))


if __name__ == "__main__":
    main()
