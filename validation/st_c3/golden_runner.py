from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Any

from validation.st_c3.evidence import make_evidence
from validation.st_c3.kernel import EvidenceBundle, run_kernel


ROOT = Path(__file__).resolve().parents[2]
GOLDEN_ROOT = ROOT / "golden" / "st_c3"

EVIDENCE_FIELDS = (
    "htf_bias",
    "sweep",
    "sweep_reclaim",
    "displacement",
    "bos",
    "bos_extreme",
    "dealing_range",
    "ote",
    "fvg",
    "order_block",
    "ltf_confirmation",
    "session_window",
    "entry_window",
    "invalidation_swing",
    "target_tp1",
    "target_tp2",
    "target_tp3",
)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _build_evidence(data: dict[str, Any]):
    payload = dict(data)
    kind = payload.pop("kind")
    fields = payload.pop("fields")
    return make_evidence(kind, **payload, **fields)


def bundle_from_case(case: dict[str, Any]) -> EvidenceBundle:
    bundle_data = case["bundle"]
    evidence = bundle_data["evidence"]
    values = {field: _build_evidence(evidence[field]) for field in EVIDENCE_FIELDS}
    expiry_data = bundle_data.get("expiry")
    expiry = _build_evidence(expiry_data) if expiry_data else None
    return EvidenceBundle(
        **values,
        computed_rr=bundle_data["computed_rr"],
        min_rr=bundle_data["min_rr"],
        entry_price=bundle_data["entry_price"],
        risk_per_trade_pct=bundle_data["risk_per_trade_pct"],
        session_open=bundle_data.get("session_open", True),
        instrument_enabled=bundle_data.get("instrument_enabled", True),
        expiry=expiry,
    )


def iter_case_paths(root: Path = GOLDEN_ROOT, scenario: str | None = None) -> list[Path]:
    base = root / scenario if scenario else root
    return sorted(base.rglob("case_*.json"))


def _assert_subset(actual: Any, expected: Any, path: str = "root") -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            raise AssertionError(f"{path}: expected dict, got {type(actual).__name__}")
        for key, value in expected.items():
            if key not in actual:
                raise AssertionError(f"{path}: missing key {key!r}")
            _assert_subset(actual[key], value, f"{path}.{key}")
        return
    if isinstance(expected, list):
        if actual != expected:
            raise AssertionError(f"{path}: expected {expected!r}, got {actual!r}")
        return
    if actual != expected:
        raise AssertionError(f"{path}: expected {expected!r}, got {actual!r}")


def evaluate_case(case_path: Path) -> dict[str, Any]:
    case = _load_json(case_path)
    bundle = bundle_from_case(case)
    result = run_kernel(bundle)
    expected = case["expected"]

    actual = {
        "outcome": result.outcome,
        "states_reached": list(result.states_reached),
        "rejection": asdict(result.rejection) if result.rejection else None,
        "trade_plan": result.trade_plan.to_dict() if result.trade_plan else None,
    }
    _assert_subset(actual, expected)

    return {
        "case_id": case["case_id"],
        "scenario_type": case["scenario_type"],
        "path": str(case_path.relative_to(ROOT)).replace("\\", "/"),
        "status": "PASS",
        "outcome": result.outcome,
    }


def run_golden_suite(root: Path = GOLDEN_ROOT, scenario: str | None = None) -> dict[str, Any]:
    case_paths = iter_case_paths(root=root, scenario=scenario)
    results = []
    failures = []
    by_scenario = defaultdict(lambda: Counter(total=0, passed=0, failed=0))

    for case_path in case_paths:
        case = _load_json(case_path)
        scenario_type = case["scenario_type"]
        by_scenario[scenario_type]["total"] += 1
        try:
            result = evaluate_case(case_path)
            results.append(result)
            by_scenario[scenario_type]["passed"] += 1
        except AssertionError as ex:
            failures.append(
                {
                    "case_id": case["case_id"],
                    "scenario_type": scenario_type,
                    "path": str(case_path.relative_to(ROOT)).replace("\\", "/"),
                    "error": str(ex),
                }
            )
            by_scenario[scenario_type]["failed"] += 1

    total = len(case_paths)
    passed = len(results)
    failed = len(failures)
    return {
        "root": str(root.relative_to(ROOT)).replace("\\", "/"),
        "scenario_filter": scenario,
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": failed,
        "status": "PASS" if failed == 0 else "FAIL",
        "results": results,
        "failures": failures,
        "scenario_breakdown": {name: dict(counter) for name, counter in sorted(by_scenario.items())},
    }
