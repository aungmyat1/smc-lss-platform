#!/usr/bin/env python3
"""Run the ST-C4.1 provider qualification program."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from providers.common.registry import load_provider_registry
from providers.common.validation import provider_passes_st_c3, quality_score
from providers.darwinex import DarwinexAdapter
from providers.dukascopy import DukascopyAdapter
from providers.histdata import HistDataAdapter
from providers.mt5 import MT5Adapter
from providers.tiingo import TiingoAdapter
from providers.truefx import TrueFXAdapter

REPORT_DIR = Path("reports/st_c4_1")
SCORECARD_DIR = REPORT_DIR / "provider_scorecards"
THRESHOLD = 0.001
GUARDRAIL = "ST-C4.1 qualification only; rejected dataset remains rejected and replay remains blocked."


def run_provider_qualification(
    *,
    registry_path: str | Path = "providers/provider_registry.yaml",
    output_dir: str | Path = REPORT_DIR,
) -> dict[str, Any]:
    registry = load_provider_registry(registry_path)
    output = Path(output_dir)
    scorecards = output / "provider_scorecards"
    scorecards.mkdir(parents=True, exist_ok=True)
    adapters = [DukascopyAdapter(), TrueFXAdapter(), TiingoAdapter(), HistDataAdapter(), DarwinexAdapter(), MT5Adapter()]
    rows = []
    metrics: dict[str, Any] = {}
    for adapter in adapters:
        health = adapter.health_check()
        validation = adapter.validate(output / "normalized" / adapter.name)
        score = quality_score(validation) if validation.get("st_c3_status") != "NOT_RUN" else 0.0
        passed = provider_passes_st_c3(validation, threshold=THRESHOLD)
        row = {
            "provider": adapter.metadata().provider,
            "adapter": adapter.name,
            "health_status": health.status,
            "health_ok": health.ok,
            "evaluation_status": registry["providers"][adapter.name]["evaluation_status"],
            "st_c3_status": validation.get("st_c3_status"),
            "missing_minute_rate": validation.get("missing_minute_rate"),
            "duplicate_rate": validation.get("duplicate_rate"),
            "technical_readiness": _technical_readiness(health, validation),
            "download_reliability": _download_reliability(adapter.name, health),
            "normalization_quality": _normalization_quality(validation),
            "historical_coverage": _historical_coverage(adapter.name),
            "timestamp_accuracy": _timestamp_accuracy(adapter.name, validation),
            "gap_rate": _gap_rate_score(validation),
            "session_accuracy": _session_accuracy(adapter.name, validation),
            "dst_accuracy": _dst_accuracy(adapter.name, validation),
            "automation_readiness": validation.get("automation_score", 0.0),
            "licensing_risk": _licensing_risk(registry["providers"][adapter.name]["license"]),
            "operational_cost": registry["providers"][adapter.name]["cost"],
            "overall_quality_score": score,
            "qualifies": passed,
            "blocker": validation.get("reason", health.reason),
            "evidence_path": health.evidence_path,
        }
        rows.append(row)
        metrics[adapter.name] = row
        (scorecards / f"{adapter.name}.md").write_text(_scorecard(row), encoding="utf-8")
    decision = _decision(rows)
    output.mkdir(parents=True, exist_ok=True)
    _write_csv(output / "provider_qualification_matrix.csv", rows)
    _write_csv(output / "cross_provider_gap_analysis.csv", _cross_provider_rows(rows))
    (output / "provider_quality_metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
    (output / "provider_registry.md").write_text(_registry_markdown(registry), encoding="utf-8")
    (output / "CANONICAL_PROVIDER_DECISION.md").write_text(_decision_markdown(decision, rows), encoding="utf-8")
    (output / "ST_C3_READINESS_REPORT.md").write_text(_readiness_markdown(decision), encoding="utf-8")
    return {
        "stage": "st_c4_1_provider_qualification",
        "status": "COMPLETE",
        "guardrail": GUARDRAIL,
        "qualified_providers": [row["provider"] for row in rows if row["qualifies"]],
        "rejected_or_blocked_providers": [row["provider"] for row in rows if not row["qualifies"]],
        "decision": decision,
        "recommendation": decision["recommendation"],
    }


def _decision(rows: list[dict[str, Any]]) -> dict[str, Any]:
    qualified = [row for row in rows if row["qualifies"]]
    if qualified:
        best = sorted(qualified, key=lambda row: row["overall_quality_score"], reverse=True)[0]
        return {
            "recommendation": "READY_FOR_ST_C3",
            "canonical_provider": best["provider"],
            "dataset_status": "NOT_BUILT_IN_THIS_RUN",
            "reason": "At least one provider passed mandatory ST-C3 qualification criteria.",
            "next_acquisition_plan": [],
        }
    return {
        "recommendation": "NO_CANONICAL_PROVIDER",
        "canonical_provider": "NONE",
        "dataset_status": "REJECTED",
        "reason": "No provider passed unchanged ST-C3 qualification criteria with reproducible acquisition evidence.",
        "next_acquisition_plan": [
            "Tiingo FX: configure TIINGO_API_TOKEN, approve API license for research, acquire 100 deterministic EURUSD/GBPUSD days.",
            "TrueFX: create/approve account or subscription, document terms, acquire 100 deterministic tick days.",
            "Darwinex: obtain live-account FTP credentials and terms approval, acquire 100 deterministic tick days.",
            "Broker MT5 Export: provide complete broker terminal history export with server-timezone documentation and checksums.",
        ],
    }


def _technical_readiness(health: Any, validation: dict[str, Any]) -> float:
    if validation.get("st_c3_status") == "PASS":
        return 100.0
    if validation.get("st_c3_status") == "FAIL":
        return 45.0 if health.ok else 25.0
    return 10.0


def _download_reliability(name: str, health: Any) -> float:
    if name == "dukascopy" and health.ok:
        return 90.0
    if name == "histdata" and health.ok:
        return 45.0
    return 0.0


def _normalization_quality(validation: dict[str, Any]) -> float:
    return 85.0 if validation.get("stable_normalization") else 0.0


def _historical_coverage(name: str) -> float:
    return {"dukascopy": 95.0, "histdata": 70.0, "truefx": 85.0, "tiingo": 65.0, "darwinex": 75.0, "mt5": 45.0}[name]


def _timestamp_accuracy(name: str, validation: dict[str, Any]) -> float:
    if validation.get("st_c3_status") == "FAIL":
        return 45.0
    return {"truefx": 80.0, "tiingo": 70.0, "darwinex": 75.0, "mt5": 45.0, "histdata": 35.0, "dukascopy": 70.0}[name]


def _gap_rate_score(validation: dict[str, Any]) -> float:
    rate = validation.get("missing_minute_rate")
    if rate is None:
        return 0.0
    return max(0.0, round(100.0 * (1.0 - float(rate)), 2))


def _session_accuracy(name: str, validation: dict[str, Any]) -> float:
    if name == "dukascopy":
        return 35.0
    if name == "histdata":
        return 25.0
    return 0.0


def _dst_accuracy(name: str, validation: dict[str, Any]) -> float:
    if name == "dukascopy":
        return 35.0
    if name == "histdata":
        return 20.0
    return 0.0


def _licensing_risk(license_status: str) -> str:
    if "required" in license_status or "review" in license_status:
        return "HIGH"
    return "LOW"


def _cross_provider_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "gap_scope": "ST-C3 rejected Dukascopy unexplained/provider-specific gaps",
            "provider_a": "Dukascopy",
            "provider_b": row["provider"],
            "provider_b_status": row["health_status"],
            "conclusion": "comparison_blocked_no_validated_sample" if row["provider"] != "HistData" else "reference_available_but_not_canonical_pass",
            "confidence": "HIGH" if row["provider"] == "HistData" else "LOW",
        }
        for row in rows
        if row["provider"] != "Dukascopy"
    ]


def _scorecard(row: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# ST-C4.1 Provider Scorecard: {row['provider']}",
            "",
            f"- ST-C3 status: `{row['st_c3_status']}`",
            f"- Missing-minute rate: `{row['missing_minute_rate']}`",
            f"- Overall quality score: `{row['overall_quality_score']}`",
            f"- Qualifies: `{row['qualifies']}`",
            f"- Blocker: {row['blocker']}",
            "",
        ]
    )


def _registry_markdown(registry: dict[str, Any]) -> str:
    lines = ["# ST-C4.1 Provider Registry", "", f"Guardrail: {registry['guardrail']}", "", "| Provider | Status | Evaluation | API | Cost |", "|---|---|---|---|---|"]
    for name, provider in registry["providers"].items():
        lines.append(f"| {name} | {provider['status']} | {provider['evaluation_status']} | {provider['api']} | {provider['cost']} |")
    return "\n".join(lines) + "\n"


def _decision_markdown(decision: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    plan = "\n".join(f"- {item}" for item in decision["next_acquisition_plan"]) or "- None"
    return f"""# ST-C4.1 Canonical Provider Decision

Recommendation: **{decision['recommendation']}**

Canonical Provider: **{decision['canonical_provider']}**

Reason: {decision['reason']}

Dataset Status: **{decision['dataset_status']}**

## Prioritized Acquisition Plan

{plan}
"""


def _readiness_markdown(decision: dict[str, Any]) -> str:
    readiness = "READY_FOR_ST_C3" if decision["recommendation"] == "READY_FOR_ST_C3" else "NOT_READY_FOR_ST_C3"
    return f"""# ST-C4.1 ST-C3 Readiness Report

Decision: **{readiness}**

Canonical Provider: **{decision['canonical_provider']}**

Reason: {decision['reason']}

Replay remains blocked. Strategy validation remains blocked. Demo and live remain blocked.
"""


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("providers/provider_registry.yaml"))
    parser.add_argument("--output-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args()
    result = run_provider_qualification(registry_path=args.registry, output_dir=args.output_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["recommendation"] == "READY_FOR_ST_C3" else 1)


if __name__ == "__main__":
    main()
