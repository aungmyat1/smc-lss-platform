from __future__ import annotations

import json

from tools import st_c5_pipeline as pipeline


def _sync_result(recommendation: str):
    return {
        "decision": {
            "recommendation": recommendation,
            "reason": "sync reason",
            "replay_status": "BLOCKED",
            "strategy_validation_status": "BLOCKED",
        }
    }


def test_pipeline_stops_at_pending_history_sync(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "run_history_sync_gate", lambda query_mt5=True: _sync_result("REQUIRES_HISTORY_SYNC"))

    result = pipeline.run_st_c5_pipeline(
        candidate_dir=tmp_path / "candidate",
        report_dir=tmp_path / "reports",
        lifecycle_path=tmp_path / "lifecycle.json",
        acquire=True,
    )

    assert result["current_lifecycle_state"] == "PENDING_HISTORY_SYNC"
    assert result["recommendation"] == "REQUIRES_HISTORY_SYNC"
    assert result["replay_status"] == "BLOCKED"
    assert len(result["steps"]) == 1
    assert (tmp_path / "lifecycle.json").exists()
    assert (tmp_path / "reports/ST_C5_PIPELINE_STATUS.json").exists()
    assert (tmp_path / "reports/ST_C5_PIPELINE_DASHBOARD.json").exists()
    assert (tmp_path / "reports/ST_C5_PIPELINE_DASHBOARD.md").exists()


def test_pipeline_pauses_after_history_sync_without_acquire(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "run_history_sync_gate", lambda query_mt5=True: _sync_result("READY_FOR_REEXPORT"))

    result = pipeline.run_st_c5_pipeline(
        candidate_dir=tmp_path / "candidate",
        report_dir=tmp_path / "reports",
        lifecycle_path=tmp_path / "lifecycle.json",
        acquire=False,
    )

    assert result["current_lifecycle_state"] == "HISTORY_SYNCHRONIZED"
    assert result["recommendation"] == "READY_FOR_REEXPORT"
    assert result["steps"][1]["name"] == "broker_export"
    assert result["steps"][1]["status"] == "NOT_REQUESTED"


def test_pipeline_dashboard_summarizes_blocked_stages(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "run_history_sync_gate", lambda query_mt5=True: _sync_result("REQUIRES_HISTORY_SYNC"))

    pipeline.run_st_c5_pipeline(
        candidate_dir=tmp_path / "candidate",
        report_dir=tmp_path / "reports",
        lifecycle_path=tmp_path / "lifecycle.json",
    )

    dashboard = json.loads((tmp_path / "reports/ST_C5_PIPELINE_DASHBOARD.json").read_text(encoding="utf-8"))

    assert dashboard["current_lifecycle_state"] == "PENDING_HISTORY_SYNC"
    assert dashboard["stages"][0]["stage"] == "History Sync"
    assert dashboard["stages"][0]["status"] == "REQUIRES_HISTORY_SYNC"
    assert dashboard["stages"][1]["stage"] == "Export"
    assert dashboard["stages"][1]["status"] == "WAITING"
    assert dashboard["stages"][1]["blocking_reason"] == "Waiting for history sync"
    assert dashboard["stages"][0]["evidence"] == "reports/st_c5_3/MT5_HISTORY_SYNC_REPORT.md"
    assert dashboard["stages"][1]["evidence"] == "reports/st_c5_3/MT5_HISTORY_SYNC_DECISION.json"
    assert dashboard["stages"][-1]["stage"] == "Live"
    assert dashboard["stages"][-1]["status"] == "BLOCKED"
    assert dashboard["stages"][-1]["evidence"] == "reports/st_c5_pipeline/ST_C5_PIPELINE_STATUS.json"


def test_pipeline_runs_acquisition_then_blocks_on_incomplete_export(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, "run_history_sync_gate", lambda query_mt5=True: _sync_result("READY_FOR_REEXPORT"))
    monkeypatch.setattr(
        pipeline,
        "run_broker_data_qualification",
        lambda candidate_dir, acquire, write_reports: {
            "acquisition": {"status": "PASS"},
            "decision": {"recommendation": "READY_FOR_ST_C3", "reason": "acquired"},
        },
    )
    monkeypatch.setattr(
        pipeline,
        "generate_vantage_quality_report",
        lambda candidate_dir: {
            "normalization": {"status": "PASS"},
            "decision": {"recommendation": "REQUIRES_MANUAL_REVIEW", "reason": "quality ready"},
        },
    )
    monkeypatch.setattr(
        pipeline,
        "run_export_completeness_audit",
        lambda candidate_dir, query_mt5=True: {
            "decision": {
                "recommendation": "REQUIRES_REEXPORT",
                "reason": "export incomplete",
            }
        },
    )

    result = pipeline.run_st_c5_pipeline(
        candidate_dir=tmp_path / "candidate",
        report_dir=tmp_path / "reports",
        lifecycle_path=tmp_path / "lifecycle.json",
        acquire=True,
    )

    assert result["current_lifecycle_state"] == "NORMALIZED"
    assert result["recommendation"] == "REQUIRES_REEXPORT"
    assert result["dataset_status"] == "NOT_APPROVED"
    assert result["live_status"] == "BLOCKED"
    assert [step["name"] for step in result["steps"]] == ["history_sync", "broker_export", "normalization", "export_completeness"]
