#!/usr/bin/env python3
"""Build the ST-C3 A2 acceptance audit package from existing evidence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFORMANCE_DIR = ROOT / "evidence" / "conformance"
OUTPUT_DIR = ROOT / "reports" / "validation" / "st_c3"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def build_a2_audit_package() -> dict[str, Any]:
    cycle = _load_json(CONFORMANCE_DIR / "st_c3_a2_orchestration_cycle.json")
    s1_g5_negative = _load_json(CONFORMANCE_DIR / "st_c3_s1_g5_negative_summary.json")
    s1_g6_golden = _load_json(CONFORMANCE_DIR / "st_c3_s1_g6_golden_summary.json")

    gate_checks = {item["gate"]: item for item in cycle["gate_checks"]}
    package = {
        "generated_from": {
            "a2_cycle": str(CONFORMANCE_DIR / "st_c3_a2_orchestration_cycle.json"),
            "s1_g5_negative": str(CONFORMANCE_DIR / "st_c3_s1_g5_negative_summary.json"),
            "s1_g6_golden": str(CONFORMANCE_DIR / "st_c3_s1_g6_golden_summary.json"),
        },
        "strategy": cycle["governance"]["strategy"],
        "spec": cycle["governance"]["spec"],
        "audit_date": "2026-07-28",
        "stage": "A2",
        "focus_gate": cycle["governance"]["focus_gate"],
        "current_gate": cycle["governance"]["current_gate"],
        "authorized_scope": cycle["governance"]["authorized_scope"],
        "accepted_upstream_gates": cycle["conformance_report"]["accepted_gates"],
        "forbidden_until_authorized": cycle["conformance_report"]["forbidden_until_authorized"],
        "s1_g5": {
            "mechanical_status": gate_checks["S1-G5"]["status"],
            "governance_accepted": gate_checks["S1-G5"]["governance_accepted"],
            "negative_cases": {
                "total": s1_g5_negative["total_cases"],
                "passed": s1_g5_negative["passed_cases"],
                "failed": s1_g5_negative["failed_cases"],
                "scenario_breakdown": s1_g5_negative["scenario_breakdown"],
            },
        },
        "s1_g6": {
            "mechanical_status": gate_checks["S1-G6"]["status"],
            "governance_eligible": gate_checks["S1-G6"]["governance_eligible"],
            "golden_cases": {
                "total": s1_g6_golden["total_cases"],
                "passed": s1_g6_golden["passed_cases"],
                "failed": s1_g6_golden["failed_cases"],
                "scenario_breakdown": s1_g6_golden["scenario_breakdown"],
            },
        },
        "fast_track_validation_plan": {
            "status": "planning_material_not_acceptance",
            "plan": "reports/validation/st_c3/ST_C3_ULTRA_FAST_VALIDATION_FUNNEL.md",
            "review": {
                "mode": "consolidated_s1_g5_s1_g6_packet",
                "decision_window_hours": 48,
                "separate_gate_outcomes": True,
                "allowed_outcomes": ["accept", "reject", "defer"],
            },
            "future_a3_standard": {
                "replay_ledger_single_source_of_truth": True,
                "required_replay_fields": [
                    "entry",
                    "exit",
                    "R",
                    "MAE",
                    "MFE",
                    "session",
                    "news_flag",
                    "rationale",
                    "win_loss",
                ],
                "hash_algorithm": "SHA-256",
                "hash_storage": {
                    "packet_header": True,
                    "standalone_path": "evidence/st_c3/replay_hash.txt",
                },
                "downstream_outputs_must_reference_hash": [
                    "statistics",
                    "robustness",
                    "walk_forward_oos",
                ],
                "robustness_threshold_table": "validation/st_c3/robustness_thresholds.yaml",
                "walk_forward_window_method_default": "fixed_year_slices",
                "walk_forward_pass_criteria": (
                    "non-negative expectancy across windows and PF > 1.2 "
                    "in the majority of windows"
                ),
                "engine_versioning_required": [
                    "statistics_engine",
                    "robustness_engine",
                ],
            },
            "guardrail": (
                "Does not accept S1-G5 or S1-G6, pass A2, open A3, or authorize "
                "execution, optimization, broker integration, demo, live trading, or production."
            ),
        },
        "recommendation": "ready_for_owner_review_only",
        "note": (
            "This package summarizes mechanical A2 evidence only. It does not accept "
            "S1-G5, S1-G6, A2, or open A3."
        ),
    }
    return package


def write_a2_audit_package(package: dict[str, Any]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "A2_ACCEPTANCE_AUDIT_PACKAGE.json"
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(package, fh, indent=2)
    return out_path


def main() -> None:
    package = build_a2_audit_package()
    out_path = write_a2_audit_package(package)
    print(json.dumps({"output": str(out_path), "strategy": package["strategy"], "stage": package["stage"]}, indent=2))


if __name__ == "__main__":
    main()
