"""Parallel robustness matrix for immutable ST-C3 replay ledgers."""
from __future__ import annotations

import argparse
import json
import random
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from validation.performance_metrics import compute_metrics
from validation.st_c3.replay_engine import load_ledger, verify_ledger_hash

ROBUSTNESS_ENGINE_VERSION = "st_c3_robustness_engine.v1"


@dataclass(frozen=True)
class RobustnessScenarioResult:
    scenario: str
    status: str
    ledger_sha256: str
    robustness_engine_version: str
    parameters: Mapping[str, Any]
    metrics: Mapping[str, Any]
    threshold_results: Mapping[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_robustness_matrix(
    ledger_path: str | Path,
    hash_path: str | Path,
    thresholds_path: str | Path,
    *,
    max_workers: int | None = None,
) -> dict[str, Any]:
    ledger_sha256 = verify_ledger_hash(ledger_path, hash_path)
    ledger = load_ledger(ledger_path)
    config = yaml.safe_load(Path(thresholds_path).read_text(encoding="utf-8"))
    scenarios = config["scenarios"]
    base_rs = [float(trade["r"]) for trade in ledger["trades"]]
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        results = list(
            pool.map(
                lambda item: _run_scenario(item[0], item[1], base_rs, ledger["trades"], ledger_sha256),
                sorted(scenarios.items()),
            )
        )
    matrix_status = "PASS" if all(result.status == "PASS" for result in results) else "FAIL"
    return {
        "status": matrix_status,
        "ledger_sha256": ledger_sha256,
        "robustness_engine_version": ROBUSTNESS_ENGINE_VERSION,
        "scenario_results": [result.to_dict() for result in results],
    }


def write_robustness_matrix(matrix: Mapping[str, Any], path: str | Path) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path


def _run_scenario(
    name: str,
    params: Mapping[str, Any],
    base_rs: list[float],
    trades: list[Mapping[str, Any]],
    ledger_sha256: str,
) -> RobustnessScenarioResult:
    transformed = _transform_returns(name, params, base_rs, trades)
    metrics = compute_metrics(transformed)
    threshold_results = {
        "profit_factor": _metric_at_least(metrics.get("profit_factor"), params.get("min_profit_factor")),
        "expectancy_r": _metric_at_least(metrics.get("expectancy_r"), params.get("min_expectancy_r")),
    }
    status = "PASS" if all(threshold_results.values()) else "FAIL"
    return RobustnessScenarioResult(
        scenario=name,
        status=status,
        ledger_sha256=ledger_sha256,
        robustness_engine_version=ROBUSTNESS_ENGINE_VERSION,
        parameters=dict(params),
        metrics=metrics,
        threshold_results=threshold_results,
    )


def _transform_returns(
    name: str,
    params: Mapping[str, Any],
    base_rs: list[float],
    trades: list[Mapping[str, Any]],
) -> list[float]:
    penalty = float(params.get("r_penalty_per_trade", 0.0))
    values = [r - penalty for r in base_rs]
    if name == "random_trade_removal_10pct":
        rng = random.Random(int(params.get("seed", 17)))
        keep_probability = 1.0 - float(params.get("removal_fraction", 0.10))
        values = [r for r in values if rng.random() <= keep_probability]
    elif name == "monte_carlo_shuffle":
        rng = random.Random(int(params.get("seed", 17)))
        values = list(values)
        rng.shuffle(values)
    elif name == "yearly_splits":
        values = _worst_group_returns(values, trades, lambda trade: str(trade["timestamp_entry"])[:4])
    elif name == "session_slices":
        values = _worst_group_returns(values, trades, lambda trade: str(trade["session"]))
    elif name == "volatility_regimes":
        values = _worst_group_returns(values, trades, lambda trade: str(trade.get("volatility_regime", "unknown")))
    return values


def _worst_group_returns(values: list[float], trades: list[Mapping[str, Any]], label_fn) -> list[float]:
    grouped: dict[str, list[float]] = {}
    for value, trade in zip(values, trades):
        grouped.setdefault(label_fn(trade), []).append(value)
    if not grouped:
        return []
    return min(grouped.values(), key=lambda group: compute_metrics(group).get("expectancy_r") or -999999.0)


def _metric_at_least(value: Any, minimum: Any) -> bool:
    if minimum is None:
        return True
    return isinstance(value, (int, float)) and float(value) >= float(minimum)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=Path("reports/validation/st_c3/replay/ledger.json"))
    parser.add_argument("--hash", type=Path, default=Path("reports/validation/st_c3/replay/ledger.hash"))
    parser.add_argument("--thresholds", type=Path, default=Path("validation/st_c3/robustness_thresholds.yaml"))
    parser.add_argument("--out", type=Path, default=Path("reports/validation/st_c3/replay/robustness_matrix.json"))
    parser.add_argument("--max-workers", type=int)
    args = parser.parse_args()
    matrix = run_robustness_matrix(args.ledger, args.hash, args.thresholds, max_workers=args.max_workers)
    write_robustness_matrix(matrix, args.out)
    print(json.dumps({"status": matrix["status"], "ledger_sha256": matrix["ledger_sha256"], "output": str(args.out)}, indent=2))


if __name__ == "__main__":
    main()
