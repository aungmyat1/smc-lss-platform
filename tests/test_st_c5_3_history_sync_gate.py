from __future__ import annotations

import tools.st_c5_3_history_sync_gate as gate
from tools.st_c5_3_history_sync_gate import classify_history_sync, history_sync_decision, run_history_sync_gate


def _availability(symbol: str, timeframe: str, first: str, last: str, status: str = "AVAILABLE"):
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "status": status,
        "first_available_bar": first if status == "AVAILABLE" else None,
        "last_available_bar": last if status == "AVAILABLE" else None,
        "total_bars": 1 if status == "AVAILABLE" else None,
        "source": "test",
        "reason": "" if status == "AVAILABLE" else "missing test history",
    }


def _complete_required_availability():
    rows = []
    for symbol in ("EURUSD", "GBPUSD"):
        rows.extend(
            [
                _availability(symbol, "M1", "2021-01-04T00:00:00Z", "2025-12-31T23:59:00Z"),
                _availability(symbol, "M15", "2021-01-04T00:00:00Z", "2025-12-31T23:45:00Z"),
                _availability(symbol, "H4", "2021-01-04T00:00:00Z", "2025-12-31T20:00:00Z"),
            ]
        )
    return rows


def test_history_sync_decision_requires_history_sync_for_missing_required_source():
    rows = classify_history_sync(
        [
            _availability("EURUSD", "M1", "", "", status="BLOCKED"),
            _availability("EURUSD", "M15", "2022-07-26T09:15:00Z", "2025-12-31T23:45:00Z"),
            _availability("EURUSD", "H4", "2021-01-04T00:00:00Z", "2025-12-31T20:00:00Z"),
        ]
    )

    decision = history_sync_decision(rows)

    assert decision["decision"] == "REQUIRES_HISTORY_SYNC"
    assert decision["recommendation"] == "REQUIRES_HISTORY_SYNC"
    assert decision["dataset_status"] == "NOT_APPROVED"
    assert decision["replay_status"] == "BLOCKED"
    assert decision["required_failure_count"] == 2


def test_history_sync_decision_allows_reexport_when_required_sources_are_synced():
    rows = classify_history_sync(_complete_required_availability())

    decision = history_sync_decision(rows)

    assert decision["decision"] == "HISTORY_SYNCHRONIZED"
    assert decision["recommendation"] == "READY_FOR_REEXPORT"
    assert decision["strategy_validation_status"] == "BLOCKED"
    assert decision["required_failure_count"] == 0


def test_history_sync_gate_writes_reports_without_mt5_query(tmp_path):
    result = run_history_sync_gate(report_dir=tmp_path / "reports", query_mt5=False)

    assert result["decision"]["decision"] == "REQUIRES_HISTORY_SYNC"
    assert (tmp_path / "reports/mt5_history_sync_gate.csv").exists()
    assert (tmp_path / "reports/MT5_HISTORY_SYNC_STATUS.json").exists()
    assert (tmp_path / "reports/MT5_HISTORY_SYNC_DECISION.json").exists()
    assert (tmp_path / "reports/MT5_HISTORY_SYNC_REPORT.md").exists()
    assert (tmp_path / "reports/HISTORY_SYNC_RUNBOOK.md").exists()


def test_history_sync_gate_uses_mt5_availability_rows(tmp_path, monkeypatch):
    monkeypatch.setattr(gate, "query_mt5_availability", lambda query_mt5=True: _complete_required_availability())

    result = run_history_sync_gate(report_dir=tmp_path / "reports", query_mt5=True)

    assert result["decision"]["recommendation"] == "READY_FOR_REEXPORT"
