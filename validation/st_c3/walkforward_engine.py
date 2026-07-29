"""Fixed-year walk-forward / OOS checks for ST-C3 replay ledgers."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from validation.performance_metrics import compute_metrics
from validation.st_c3.replay_engine import load_ledger, verify_ledger_hash
from validation.st_c3.stats_engine import STATS_ENGINE_VERSION

WALKFORWARD_ENGINE_VERSION = "st_c3_walkforward_engine.v1"


def run_fixed_year_walkforward(
    ledger_path: str | Path,
    hash_path: str | Path,
    *,
    min_pf_majority: float = 1.20,
    require_non_negative_expectancy: bool = True,
) -> dict[str, Any]:
    ledger_sha256 = verify_ledger_hash(ledger_path, hash_path)
    ledger = load_ledger(ledger_path)
    windows = _year_windows(ledger["trades"])
    pf_passes = 0
    expectancy_passes = 0
    results = []
    for year, trades in windows.items():
        metrics = compute_metrics([float(trade["r"]) for trade in trades])
        pf_ok = isinstance(metrics.get("profit_factor"), (int, float)) and float(metrics["profit_factor"]) > min_pf_majority
        expectancy_ok = (
            isinstance(metrics.get("expectancy_r"), (int, float))
            and float(metrics["expectancy_r"]) >= 0.0
        )
        pf_passes += int(pf_ok)
        expectancy_passes += int(expectancy_ok)
        results.append(
            {
                "window": year,
                "metrics": metrics,
                "profit_factor_pass": pf_ok,
                "expectancy_pass": expectancy_ok,
            }
        )
    majority_needed = (len(results) // 2) + 1 if results else 1
    pass_pf = pf_passes >= majority_needed
    pass_expectancy = (expectancy_passes == len(results)) if require_non_negative_expectancy else True
    status = "PASS" if results and pass_pf and pass_expectancy else "FAIL"
    return {
        "status": status,
        "ledger_sha256": ledger_sha256,
        "walkforward_engine_version": WALKFORWARD_ENGINE_VERSION,
        "stats_engine_version": STATS_ENGINE_VERSION,
        "window_method": "fixed_year_slices",
        "criteria": {
            "min_pf_majority": min_pf_majority,
            "require_non_negative_expectancy": require_non_negative_expectancy,
        },
        "summary": {
            "windows": len(results),
            "pf_pass_windows": pf_passes,
            "expectancy_pass_windows": expectancy_passes,
            "pf_majority_needed": majority_needed,
        },
        "windows": results,
    }


def write_walkforward_results(result: Mapping[str, Any], path: str | Path) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path


def _year_windows(trades: list[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    windows: dict[str, list[Mapping[str, Any]]] = {}
    for trade in trades:
        windows.setdefault(str(trade["timestamp_entry"])[:4], []).append(trade)
    return dict(sorted(windows.items()))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=Path("reports/validation/st_c3/replay/ledger.json"))
    parser.add_argument("--hash", type=Path, default=Path("reports/validation/st_c3/replay/ledger.hash"))
    parser.add_argument("--out", type=Path, default=Path("reports/validation/st_c3/replay/walkforward_results.json"))
    parser.add_argument("--min-pf-majority", type=float, default=1.20)
    args = parser.parse_args()
    result = run_fixed_year_walkforward(args.ledger, args.hash, min_pf_majority=args.min_pf_majority)
    write_walkforward_results(result, args.out)
    print(json.dumps({"status": result["status"], "ledger_sha256": result["ledger_sha256"], "output": str(args.out)}, indent=2))


if __name__ == "__main__":
    main()
