#!/usr/bin/env python3
"""ST-C5 operational pipeline orchestrator.

This runner wires together the existing ST-C5 gates in a reproducible order and
persists dataset lifecycle state. It does not introduce new validation rules,
approve datasets, unlock replay, or modify strategy logic.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tools.st_c5_1_vantage_quality_report import generate_vantage_quality_report
from tools.st_c5_2_export_completeness_audit import run_export_completeness_audit
from tools.st_c5_3_history_sync_gate import run_history_sync_gate
from tools.st_c5_broker_data_qualification import DEFAULT_CANDIDATE_DIR, GUARDRAIL, run_broker_data_qualification

REPORT_DIR = Path("reports/st_c5_pipeline")
LIFECYCLE_PATH = Path("research_data/metadata/ST_C5_DATASET_LIFECYCLE.json")


def run_st_c5_pipeline(
    *,
    candidate_dir: str | Path = DEFAULT_CANDIDATE_DIR,
    report_dir: str | Path = REPORT_DIR,
    lifecycle_path: str | Path = LIFECYCLE_PATH,
    acquire: bool = False,
    query_mt5: bool = True,
) -> dict[str, Any]:
    reports = Path(report_dir)
    reports.mkdir(parents=True, exist_ok=True)
    candidate = Path(candidate_dir)
    steps: list[dict[str, Any]] = []

    history_sync = run_history_sync_gate(query_mt5=query_mt5)
    steps.append(_step("history_sync", history_sync["decision"]["recommendation"], history_sync["decision"]))
    if history_sync["decision"]["recommendation"] != "READY_FOR_REEXPORT":
        result = _pipeline_result(
            candidate,
            "PENDING_HISTORY_SYNC",
            "BLOCKED",
            "REQUIRES_HISTORY_SYNC",
            "Synchronize MT5 terminal history before broker re-export.",
            steps,
        )
        return _write_pipeline_reports(result, reports, Path(lifecycle_path))

    if not acquire:
        steps.append(
            _step(
                "broker_export",
                "NOT_REQUESTED",
                {
                    "reason": "history synchronized, but acquisition was not requested; rerun with --acquire to re-export",
                    "replay_status": "BLOCKED",
                    "strategy_validation_status": "BLOCKED",
                },
            )
        )
        result = _pipeline_result(
            candidate,
            "HISTORY_SYNCHRONIZED",
            "PAUSED",
            "READY_FOR_REEXPORT",
            "Run the pipeline with --acquire to perform the guarded broker export.",
            steps,
        )
        return _write_pipeline_reports(result, reports, Path(lifecycle_path))

    acquisition = run_broker_data_qualification(candidate_dir=candidate, acquire=True, write_reports=True)
    steps.append(_step("broker_export", acquisition["decision"]["recommendation"], acquisition["decision"]))
    if acquisition["acquisition"].get("status") != "PASS":
        result = _pipeline_result(
            candidate,
            "HISTORY_SYNCHRONIZED",
            "BLOCKED",
            acquisition["decision"]["recommendation"],
            acquisition["decision"]["reason"],
            steps,
        )
        return _write_pipeline_reports(result, reports, Path(lifecycle_path))

    quality = generate_vantage_quality_report(candidate_dir=candidate)
    steps.append(_step("normalization", quality["normalization"]["status"], quality["normalization"]))
    state = "NORMALIZED" if quality["normalization"]["status"] == "PASS" else "EXPORTED"

    export_audit = run_export_completeness_audit(candidate_dir=candidate, query_mt5=query_mt5)
    steps.append(_step("export_completeness", export_audit["decision"]["recommendation"], export_audit["decision"]))
    if export_audit["decision"]["recommendation"] != "READY_FOR_ST_C3":
        result = _pipeline_result(
            candidate,
            state,
            "BLOCKED",
            export_audit["decision"]["recommendation"],
            export_audit["decision"]["reason"],
            steps,
        )
        return _write_pipeline_reports(result, reports, Path(lifecycle_path))

    st_c3_ready = quality["decision"]["recommendation"]
    steps.append(_step("st_c3_governance", st_c3_ready, quality["decision"]))
    result = _pipeline_result(
        candidate,
        "VALIDATED" if st_c3_ready != "REJECT_DATASET" else "NORMALIZED",
        "COMPLETE",
        st_c3_ready,
        quality["decision"]["reason"],
        steps,
    )
    return _write_pipeline_reports(result, reports, Path(lifecycle_path))


def _pipeline_result(
    candidate: Path,
    lifecycle_state: str,
    status: str,
    recommendation: str,
    reason: str,
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "stage": "st_c5_operational_pipeline",
        "status": status,
        "current_lifecycle_state": lifecycle_state,
        "candidate_dir": str(candidate),
        "recommendation": recommendation,
        "reason": reason,
        "dataset_status": "NOT_APPROVED",
        "replay_status": "BLOCKED",
        "strategy_validation_status": "BLOCKED",
        "demo_status": "BLOCKED",
        "live_status": "BLOCKED",
        "steps": steps,
        "updated_at_utc": datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "guardrail": GUARDRAIL,
    }


def _step(name: str, status: str, detail: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "detail": detail,
    }


def _write_pipeline_reports(result: dict[str, Any], report_dir: Path, lifecycle_path: Path) -> dict[str, Any]:
    lifecycle_path.parent.mkdir(parents=True, exist_ok=True)
    lifecycle = {
        "current_lifecycle_state": result["current_lifecycle_state"],
        "candidate_dir": result["candidate_dir"],
        "recommendation": result["recommendation"],
        "dataset_status": result["dataset_status"],
        "replay_status": result["replay_status"],
        "strategy_validation_status": result["strategy_validation_status"],
        "demo_status": result["demo_status"],
        "live_status": result["live_status"],
        "updated_at_utc": result["updated_at_utc"],
        "guardrail": GUARDRAIL,
    }
    report_dir.mkdir(parents=True, exist_ok=True)
    dashboard = build_pipeline_dashboard(result)
    (report_dir / "ST_C5_PIPELINE_STATUS.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (report_dir / "ST_C5_PIPELINE_REPORT.md").write_text(_pipeline_markdown(result), encoding="utf-8")
    (report_dir / "ST_C5_PIPELINE_DASHBOARD.json").write_text(json.dumps(dashboard, indent=2, sort_keys=True), encoding="utf-8")
    (report_dir / "ST_C5_PIPELINE_DASHBOARD.md").write_text(_dashboard_markdown(dashboard), encoding="utf-8")
    lifecycle_path.write_text(json.dumps(lifecycle, indent=2, sort_keys=True), encoding="utf-8")
    return result


def build_pipeline_dashboard(result: dict[str, Any]) -> dict[str, Any]:
    steps = {step["name"]: step for step in result["steps"]}
    history = steps.get("history_sync")
    export = steps.get("broker_export")
    normalization = steps.get("normalization")
    audit = steps.get("export_completeness")
    governance = steps.get("st_c3_governance")
    stages = [
        _dashboard_stage("History Sync", history, result["updated_at_utc"], result["reason"]),
        _dashboard_stage("Export", export, result["updated_at_utc"], "Waiting for history sync"),
        _dashboard_stage("Normalization", normalization, result["updated_at_utc"], "Export not complete"),
        _dashboard_stage("Export Audit", audit, result["updated_at_utc"], "Export not complete"),
        _dashboard_stage("ST-C3", governance, result["updated_at_utc"], "Export not complete"),
        {
            "stage": "Replay",
            "status": result["replay_status"],
            "last_run": "",
            "blocking_reason": "Dataset not approved",
        },
        {
            "stage": "Strategy Validation",
            "status": result["strategy_validation_status"],
            "last_run": "",
            "blocking_reason": "Replay blocked",
        },
        {
            "stage": "Demo",
            "status": result["demo_status"],
            "last_run": "",
            "blocking_reason": "Strategy validation blocked",
        },
        {
            "stage": "Live",
            "status": result["live_status"],
            "last_run": "",
            "blocking_reason": "Demo blocked",
        },
    ]
    return {
        "current_lifecycle_state": result["current_lifecycle_state"],
        "recommendation": result["recommendation"],
        "updated_at_utc": result["updated_at_utc"],
        "stages": stages,
        "guardrail": GUARDRAIL,
    }


def _dashboard_stage(step_name: str, step: dict[str, Any] | None, last_run: str, waiting_reason: str) -> dict[str, str]:
    if step is None:
        return {
            "stage": step_name,
            "status": "WAITING",
            "last_run": "",
            "blocking_reason": waiting_reason,
        }
    detail = step.get("detail") or {}
    return {
        "stage": step_name,
        "status": str(step["status"]),
        "last_run": last_run,
        "blocking_reason": str(detail.get("reason") or ""),
    }


def _pipeline_markdown(result: dict[str, Any]) -> str:
    step_lines = [f"- {step['name']}: `{step['status']}`" for step in result["steps"]]
    return "\n".join(
        [
            "# ST-C5 Operational Pipeline Status",
            "",
            f"Lifecycle State: **{result['current_lifecycle_state']}**",
            "",
            f"Recommendation: **{result['recommendation']}**",
            "",
            f"Reason: {result['reason']}",
            "",
            "## Steps",
            "",
            *step_lines,
            "",
            "## Governance",
            "",
            "Dataset remains not approved. Replay, strategy validation, demo, and live remain blocked.",
            "",
        ]
    )


def _dashboard_markdown(dashboard: dict[str, Any]) -> str:
    lines = [
        "# ST-C5 Pipeline Dashboard",
        "",
        f"Lifecycle State: **{dashboard['current_lifecycle_state']}**",
        "",
        f"Recommendation: **{dashboard['recommendation']}**",
        "",
        "| Stage | Status | Last Run | Blocking Reason |",
        "| --- | --- | --- | --- |",
    ]
    for stage in dashboard["stages"]:
        lines.append(
            f"| {stage['stage']} | {stage['status']} | {stage['last_run'] or '-'} | {stage['blocking_reason'] or '-'} |"
        )
    lines.extend(
        [
            "",
            "Dataset remains not approved. Replay, strategy validation, demo, and live remain blocked.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, default=DEFAULT_CANDIDATE_DIR)
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    parser.add_argument("--lifecycle-path", type=Path, default=LIFECYCLE_PATH)
    parser.add_argument("--acquire", action="store_true")
    parser.add_argument("--no-mt5-query", action="store_true")
    args = parser.parse_args()
    result = run_st_c5_pipeline(
        candidate_dir=args.candidate_dir,
        report_dir=args.report_dir,
        lifecycle_path=args.lifecycle_path,
        acquire=args.acquire,
        query_mt5=not args.no_mt5_query,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["recommendation"] in {"READY_FOR_ST_C3", "REQUIRES_MANUAL_REVIEW"} else 1)


if __name__ == "__main__":
    main()
