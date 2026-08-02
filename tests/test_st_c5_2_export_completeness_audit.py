from __future__ import annotations

import csv
from datetime import UTC, datetime

import tools.st_c5_2_export_completeness_audit as audit
from tools.st_c5_2_export_completeness_audit import (
    classify_missing_timestamp,
    completeness_decision,
    export_inventory,
    reconcile_exports,
    run_export_completeness_audit,
)


def _write_csv(path, timestamps):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time", "open", "high", "low", "close", "volume", "session", "news_flag"])
        for timestamp in timestamps:
            writer.writerow([timestamp, 1, 1, 1, 1, 1, "OTHER", "false"])


def test_missing_timestamp_classification_separates_holiday_and_export_omission():
    assert classify_missing_timestamp(datetime(2025, 12, 25, tzinfo=UTC)) == "Holiday"
    assert classify_missing_timestamp(datetime(2025, 1, 4, tzinfo=UTC)) == "Weekend"
    assert classify_missing_timestamp(datetime(2025, 1, 2, 17, 15, tzinfo=UTC)) == "Export omission"


def test_reconcile_flags_export_with_fewer_rows_than_mt5(tmp_path):
    _write_csv(tmp_path / "EURUSD_M15.csv", ["2025-01-02T00:00:00Z"])
    exports = [row for row in export_inventory(tmp_path) if row["symbol"] == "EURUSD" and row["timeframe"] == "M15"]
    mt5 = [
        {
            "symbol": "EURUSD",
            "timeframe": "M15",
            "status": "AVAILABLE",
            "first_available_bar": "2025-01-02T00:00:00Z",
            "last_available_bar": "2025-01-02T00:15:00Z",
            "total_bars": 2,
        }
    ]

    result = reconcile_exports(mt5, exports)

    assert result[0]["reconciliation_status"] == "EXPORT_HAS_FEWER_ROWS_THAN_MT5"


def test_mt5_availability_uses_chunked_requests(monkeypatch):
    class FakeMT5:
        TIMEFRAME_M1 = 1

        def __init__(self):
            self.calls = []

        def copy_rates_range(self, symbol, timeframe_id, start, end):
            self.calls.append((symbol, timeframe_id, start, end))
            return [
                {"time": int(start.timestamp())},
                {"time": int(end.timestamp())},
            ]

        def last_error(self):
            return (0, "ok")

    fake = FakeMT5()
    monkeypatch.setattr(audit, "START", datetime(2025, 1, 1, tzinfo=UTC))
    monkeypatch.setattr(audit, "END", datetime(2025, 1, 20, 23, 59, 59, tzinfo=UTC))

    result = audit._mt5_timeframe_availability(fake, "EURUSD", "M1", True)

    assert result["status"] == "AVAILABLE"
    assert result["first_available_bar"] == "2025-01-01T00:00:00Z"
    assert result["last_available_bar"] == "2025-01-20T23:59:59Z"
    assert result["total_bars"] == 6
    assert len(fake.calls) == 3


def test_mt5_availability_reports_out_of_window_bars(monkeypatch):
    class FakeMT5:
        TIMEFRAME_M1 = 1

        def copy_rates_range(self, symbol, timeframe_id, start, end):
            return [{"time": int(datetime(2026, 1, 1, tzinfo=UTC).timestamp())}]

        def last_error(self):
            return (1, "Success")

    monkeypatch.setattr(audit, "START", datetime(2025, 1, 1, tzinfo=UTC))
    monkeypatch.setattr(audit, "END", datetime(2025, 1, 1, 23, 59, 59, tzinfo=UTC))

    result = audit._mt5_timeframe_availability(FakeMT5(), "EURUSD", "M1", True)

    assert result["status"] == "BLOCKED"
    assert result["reason"] == "copy_rates_range returned 1 bars outside requested audit window"


def test_completeness_decision_marks_incomplete_export_for_missing_rows():
    decision = completeness_decision([], [{"timestamp": "2025-01-02T00:00:00Z"}])

    assert decision["decision"] == "INCOMPLETE_EXPORT"
    assert decision["recommendation"] == "REQUIRES_REEXPORT"
    assert decision["replay_status"] == "BLOCKED"


def test_export_completeness_audit_writes_reports_without_mt5_query(tmp_path):
    result = run_export_completeness_audit(candidate_dir=tmp_path / "candidate", report_dir=tmp_path / "reports", query_mt5=False)

    assert result["decision"]["decision"] == "INCOMPLETE_EXPORT"
    assert (tmp_path / "reports/mt5_history_availability.csv").exists()
    assert (tmp_path / "reports/export_reconciliation.csv").exists()
    assert (tmp_path / "reports/missing_timestamp_classification.csv").exists()
    assert (tmp_path / "reports/EXPORT_COMPLETENESS_AUDIT.md").exists()
    assert (tmp_path / "reports/EXPORT_COMPLETENESS_DECISION.json").exists()
