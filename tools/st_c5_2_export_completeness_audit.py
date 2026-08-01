#!/usr/bin/env python3
"""ST-C5.2 broker export completeness audit.

This audit determines whether the Vantage MT5 candidate failed because the
provider is unsuitable or because the export is incomplete. It does not approve
data, alter ST-C3, unlock replay, or modify strategy logic.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tools.st_c3_data_integrity import inspect_dataset
from tools.st_c3_download_mt5_dataset import _format_time
from tools.st_c5_broker_data_qualification import DEFAULT_CANDIDATE_DIR, GUARDRAIL

REPORT_DIR = Path("reports/st_c5_2")
SYMBOLS = ("EURUSD", "GBPUSD")
AUDIT_TIMEFRAMES = ("M1", "M5", "M15", "H1", "H4", "D1")
CANONICAL_TIMEFRAMES = ("H4", "M15", "M3")
START = datetime(2021, 1, 1, tzinfo=UTC)
END = datetime(2025, 12, 31, 23, 59, 59, tzinfo=UTC)


def run_export_completeness_audit(
    *,
    candidate_dir: str | Path = DEFAULT_CANDIDATE_DIR,
    report_dir: str | Path = REPORT_DIR,
    query_mt5: bool = True,
) -> dict[str, Any]:
    candidate = Path(candidate_dir)
    reports = Path(report_dir)
    reports.mkdir(parents=True, exist_ok=True)
    mt5_rows = query_mt5_availability(query_mt5=query_mt5)
    export_rows = export_inventory(candidate)
    integrity_rows = missing_timestamp_classification(candidate)
    reconciliation = reconcile_exports(mt5_rows, export_rows)
    decision = completeness_decision(reconciliation, integrity_rows)
    result = {
        "stage": "st_c5_2_export_completeness_audit",
        "status": "COMPLETE",
        "candidate_dir": str(candidate),
        "mt5_query_status": _mt5_query_status(mt5_rows),
        "decision": decision,
        "summary": {
            "mt5_rows": len(mt5_rows),
            "export_rows": len(export_rows),
            "missing_timestamp_rows": len(integrity_rows),
            "reconciliation_rows": len(reconciliation),
        },
        "guardrail": GUARDRAIL,
    }
    _write_csv(reports / "mt5_history_availability.csv", mt5_rows)
    _write_csv(reports / "export_reconciliation.csv", reconciliation)
    _write_csv(reports / "missing_timestamp_classification.csv", integrity_rows)
    (reports / "EXPORT_COMPLETENESS_DECISION.json").write_text(json.dumps(decision, indent=2, sort_keys=True), encoding="utf-8")
    (reports / "EXPORT_COMPLETENESS_AUDIT.md").write_text(_audit_markdown(result, mt5_rows, reconciliation, integrity_rows), encoding="utf-8")
    (reports / "REEXPORT_PLAN.md").write_text(_reexport_plan(decision), encoding="utf-8")
    (reports / "EXPORT_COMPLETENESS_STATUS.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def query_mt5_availability(*, query_mt5: bool = True) -> list[dict[str, Any]]:
    if not query_mt5:
        return [_availability_blocked_row(symbol, timeframe, "MT5 query disabled") for symbol in SYMBOLS for timeframe in AUDIT_TIMEFRAMES]
    try:
        import MetaTrader5 as mt5
    except ImportError:
        return [_availability_blocked_row(symbol, timeframe, "MetaTrader5 package is not installed") for symbol in SYMBOLS for timeframe in AUDIT_TIMEFRAMES]
    if not mt5.initialize():
        reason = f"mt5.initialize failed: {mt5.last_error()}"
        return [_availability_blocked_row(symbol, timeframe, reason) for symbol in SYMBOLS for timeframe in AUDIT_TIMEFRAMES]
    rows: list[dict[str, Any]] = []
    try:
        for symbol in SYMBOLS:
            selected = mt5.symbol_select(symbol, True)
            for timeframe in AUDIT_TIMEFRAMES:
                rows.append(_mt5_timeframe_availability(mt5, symbol, timeframe, selected))
    finally:
        mt5.shutdown()
    return rows


def export_inventory(candidate: Path) -> list[dict[str, Any]]:
    rows = []
    for symbol in SYMBOLS:
        for timeframe in CANONICAL_TIMEFRAMES:
            path = candidate / f"{symbol}_{timeframe}.csv"
            if not path.exists():
                rows.append(_export_row(symbol, timeframe, path, "MISSING", 0, None, None))
                continue
            count = 0
            first = None
            last = None
            with path.open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    timestamp = row.get("time") or row.get("timestamp")
                    if count == 0:
                        first = timestamp
                    last = timestamp
                    count += 1
            rows.append(_export_row(symbol, timeframe, path, "PRESENT", count, first, last))
    return rows


def missing_timestamp_classification(candidate: Path) -> list[dict[str, Any]]:
    rows = []
    for item in inspect_dataset(candidate):
        for timestamp in item.missing_timestamps:
            value = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
            rows.append(
                {
                    "symbol": item.symbol,
                    "timeframe": item.timeframe,
                    "timestamp": timestamp,
                    "classification": classify_missing_timestamp(value),
                    "source_file": Path(item.path).name,
                }
            )
    return rows


def reconcile_exports(mt5_rows: list[dict[str, Any]], export_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mt5_by_key = {(row["symbol"], row["timeframe"]): row for row in mt5_rows}
    rows = []
    for export in export_rows:
        mt5_row = mt5_by_key.get((export["symbol"], export["timeframe"]))
        if mt5_row is None:
            status = "NO_DIRECT_MT5_QUERY"
            mt5_first = None
            mt5_last = None
            mt5_bars = None
            gap = None
        else:
            mt5_first = mt5_row["first_available_bar"]
            mt5_last = mt5_row["last_available_bar"]
            mt5_bars = mt5_row["total_bars"]
            gap = (int(mt5_bars) - int(export["rows"])) if mt5_bars not in {None, ""} else None
            status = _reconciliation_status(export, mt5_row, gap)
        rows.append(
            {
                **export,
                "mt5_first_available_bar": mt5_first,
                "mt5_last_available_bar": mt5_last,
                "mt5_total_bars": mt5_bars,
                "row_count_delta_mt5_minus_export": gap,
                "reconciliation_status": status,
            }
        )
    return rows


def classify_missing_timestamp(value: datetime) -> str:
    if value.weekday() in {5, 6}:
        return "Weekend"
    if (value.month, value.day) in {(1, 1), (12, 25)}:
        return "Holiday"
    if value.weekday() == 4 and value.hour >= 22:
        return "Broker maintenance"
    if value.hour in {21, 22, 23, 0}:
        return "Broker maintenance"
    return "Export omission"


def completeness_decision(reconciliation: list[dict[str, Any]], missing_rows: list[dict[str, Any]]) -> dict[str, Any]:
    missing_count = len(missing_rows)
    coverage_failures = [
        row
        for row in reconciliation
        if row["status"] != "PRESENT"
        or (
            row["first_timestamp"] is None
            or row["first_timestamp"] > "2021-01-04T00:00:00Z"
            or row["last_timestamp"] < "2025-12-31T20:00:00Z"
        )
    ]
    if missing_count or coverage_failures:
        status = "INCOMPLETE_EXPORT"
        recommendation = "REQUIRES_REEXPORT"
        reason = "Vantage MT5 candidate has incomplete timeframe coverage and/or missing expected timestamps."
    else:
        status = "EXPORT_COMPLETE_PENDING_ST_C3"
        recommendation = "READY_FOR_ST_C3"
        reason = "Export inventory has no missing expected timestamps; full unchanged ST-C3 still required."
    return {
        "decision": status,
        "recommendation": recommendation,
        "dataset_status": "NOT_APPROVED",
        "replay_status": "BLOCKED",
        "strategy_validation_status": "BLOCKED",
        "demo_status": "BLOCKED",
        "live_status": "BLOCKED",
        "missing_timestamp_count": missing_count,
        "coverage_failure_count": len(coverage_failures),
        "reason": reason,
        "guardrail": GUARDRAIL,
    }


def _mt5_timeframe_availability(mt5: Any, symbol: str, timeframe: str, selected: bool) -> dict[str, Any]:
    if not selected:
        return _availability_blocked_row(symbol, timeframe, f"symbol_select failed: {mt5.last_error()}")
    timeframe_id = _timeframe_id(mt5, timeframe)
    if timeframe_id is None:
        return _availability_blocked_row(symbol, timeframe, "timeframe unsupported by local MetaTrader5 package")
    rates = mt5.copy_rates_range(symbol, timeframe_id, START, END)
    if rates is None or len(rates) == 0:
        return _availability_blocked_row(symbol, timeframe, f"copy_rates_range returned no bars: {mt5.last_error()}")
    first = datetime.fromtimestamp(int(rates[0]["time"]), tz=UTC)
    last = datetime.fromtimestamp(int(rates[-1]["time"]), tz=UTC)
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "status": "AVAILABLE",
        "first_available_bar": _format_time(first.replace(tzinfo=None)),
        "last_available_bar": _format_time(last.replace(tzinfo=None)),
        "total_bars": int(len(rates)),
        "source": "MetaTrader5.copy_rates_range",
        "reason": "",
    }


def _timeframe_id(mt5: Any, timeframe: str) -> int | None:
    mapping = {
        "M1": "TIMEFRAME_M1",
        "M5": "TIMEFRAME_M5",
        "M15": "TIMEFRAME_M15",
        "H1": "TIMEFRAME_H1",
        "H4": "TIMEFRAME_H4",
        "D1": "TIMEFRAME_D1",
    }
    return getattr(mt5, mapping[timeframe], None)


def _availability_blocked_row(symbol: str, timeframe: str, reason: str) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "status": "BLOCKED",
        "first_available_bar": None,
        "last_available_bar": None,
        "total_bars": None,
        "source": "MetaTrader5.copy_rates_range",
        "reason": reason,
    }


def _export_row(symbol: str, timeframe: str, path: Path, status: str, rows: int, first: str | None, last: str | None) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "file": str(path),
        "status": status,
        "rows": rows,
        "first_timestamp": first,
        "last_timestamp": last,
    }


def _reconciliation_status(export: dict[str, Any], mt5_row: dict[str, Any], gap: int | None) -> str:
    if mt5_row["status"] != "AVAILABLE":
        return "MT5_QUERY_BLOCKED"
    if gap is not None and gap > 0:
        return "EXPORT_HAS_FEWER_ROWS_THAN_MT5"
    if export["first_timestamp"] and mt5_row["first_available_bar"] and export["first_timestamp"] > mt5_row["first_available_bar"]:
        return "EXPORT_STARTS_AFTER_MT5"
    return "RECONCILED_OR_TERMINAL_LIMITED"


def _mt5_query_status(rows: list[dict[str, Any]]) -> str:
    return "AVAILABLE" if any(row["status"] == "AVAILABLE" for row in rows) else "BLOCKED"


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _audit_markdown(
    result: dict[str, Any],
    mt5_rows: list[dict[str, Any]],
    reconciliation: list[dict[str, Any]],
    missing_rows: list[dict[str, Any]],
) -> str:
    classifications = Counter(row["classification"] for row in missing_rows)
    return "\n".join(
        [
            "# ST-C5.2 Broker Export Completeness Audit",
            "",
            f"Decision: **{result['decision']['decision']}**",
            "",
            f"Reason: {result['decision']['reason']}",
            "",
            "## MT5 Availability",
            "",
            f"- Query status: `{result['mt5_query_status']}`",
            f"- Availability rows: `{len(mt5_rows)}`",
            "",
            "## Export Reconciliation",
            "",
            f"- Reconciliation rows: `{len(reconciliation)}`",
            f"- Coverage failures: `{result['decision']['coverage_failure_count']}`",
            "",
            "## Missing Timestamp Classification",
            "",
            f"- Missing timestamps: `{len(missing_rows)}`",
            f"- Classifications: `{dict(sorted(classifications.items()))}`",
            "",
            "## Governance",
            "",
            "Dataset remains not approved. Replay and strategy validation remain blocked.",
            "",
        ]
    )


def _reexport_plan(decision: dict[str, Any]) -> str:
    return f"""# ST-C5.2 Re-export Plan

Current decision: **{decision['decision']}**

Recommended acquisition actions:

1. In MT5, open EURUSD and GBPUSD charts for M1, M5, M15, H1, H4, and D1.
2. Scroll each chart back to at least 2021-01-01 to force local history synchronization.
3. Increase terminal chart/history bar limits if needed.
4. Rerun `python -m tools.st_c5_broker_data_qualification --acquire`.
5. Rerun `python -m tools.st_c5_1_vantage_quality_report`.
6. Rerun `python -m tools.st_c5_2_export_completeness_audit`.

No replay or strategy validation may start until a fresh unchanged ST-C3 run approves the dataset.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path, default=DEFAULT_CANDIDATE_DIR)
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    parser.add_argument("--no-mt5-query", action="store_true")
    args = parser.parse_args()
    result = run_export_completeness_audit(
        candidate_dir=args.candidate_dir,
        report_dir=args.report_dir,
        query_mt5=not args.no_mt5_query,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["decision"]["recommendation"] == "READY_FOR_ST_C3" else 1)


if __name__ == "__main__":
    main()
