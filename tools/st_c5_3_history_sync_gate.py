#!/usr/bin/env python3
"""ST-C5.3 MT5 history synchronization gate.

This operational gate checks whether the local MT5 terminal has enough broker
history to permit a guarded re-export. It does not export data, approve data,
alter ST-C3, unlock replay, or modify strategy logic.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tools.st_c5_2_export_completeness_audit import AUDIT_TIMEFRAMES, SYMBOLS, query_mt5_availability
from tools.st_c5_broker_data_qualification import GUARDRAIL

REPORT_DIR = Path("reports/st_c5_3")
REQUIRED_START = "2021-01-04T00:00:00Z"
EXPECTED_LAST_BY_TIMEFRAME = {
    "M1": "2025-12-31T23:59:00Z",
    "M15": "2025-12-31T23:45:00Z",
    "H4": "2025-12-31T20:00:00Z",
}
EXPORT_SOURCE_REQUIREMENTS = {
    "H4": "direct canonical export",
    "M15": "direct canonical export",
    "M1": "M3 derivation source when broker-native M3 is incomplete or unavailable",
}


def run_history_sync_gate(*, report_dir: str | Path = REPORT_DIR, query_mt5: bool = True) -> dict[str, Any]:
    reports = Path(report_dir)
    reports.mkdir(parents=True, exist_ok=True)
    availability = query_mt5_availability(query_mt5=query_mt5)
    rows = classify_history_sync(availability)
    decision = history_sync_decision(rows)
    result = {
        "stage": "st_c5_3_history_sync_gate",
        "status": "COMPLETE",
        "decision": decision,
        "summary": {
            "availability_rows": len(availability),
            "sync_rows": len(rows),
            "required_failures": decision["required_failure_count"],
        },
        "guardrail": GUARDRAIL,
    }
    _write_csv(reports / "mt5_history_sync_gate.csv", rows)
    (reports / "MT5_HISTORY_SYNC_STATUS.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (reports / "MT5_HISTORY_SYNC_DECISION.json").write_text(json.dumps(decision, indent=2, sort_keys=True), encoding="utf-8")
    (reports / "MT5_HISTORY_SYNC_REPORT.md").write_text(_report_markdown(result, rows), encoding="utf-8")
    (reports / "HISTORY_SYNC_RUNBOOK.md").write_text(_runbook_markdown(decision), encoding="utf-8")
    return result


def classify_history_sync(availability: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in availability:
        timeframe = item["timeframe"]
        required_for_export = timeframe in EXPORT_SOURCE_REQUIREMENTS
        expected_last = EXPECTED_LAST_BY_TIMEFRAME.get(timeframe)
        first = item["first_available_bar"]
        last = item["last_available_bar"]
        start_ok = bool(first and first <= REQUIRED_START)
        last_ok = bool(expected_last is None or (last and last >= expected_last))
        if item["status"] != "AVAILABLE":
            sync_status = "NOT_PRESENT_IN_TERMINAL"
            reason = item["reason"]
        elif required_for_export and not start_ok:
            sync_status = "START_DATE_MISSING"
            reason = f"first available bar is after required start {REQUIRED_START}"
        elif required_for_export and not last_ok:
            sync_status = "END_DATE_MISSING"
            reason = f"last available bar is before expected terminal end {expected_last}"
        else:
            sync_status = "SYNCHRONIZED" if required_for_export else "RECORDED_DIAGNOSTIC"
            reason = ""
        rows.append(
            {
                "symbol": item["symbol"],
                "timeframe": timeframe,
                "terminal_status": item["status"],
                "first_available_bar": first,
                "last_available_bar": last,
                "total_bars": item["total_bars"],
                "required_for_export": str(required_for_export).lower(),
                "export_requirement": EXPORT_SOURCE_REQUIREMENTS.get(timeframe, "diagnostic only"),
                "required_start": REQUIRED_START if required_for_export else "",
                "expected_last": expected_last or "",
                "start_ok": str(start_ok).lower(),
                "last_ok": str(last_ok).lower(),
                "sync_status": sync_status,
                "reason": reason,
            }
        )
    return rows


def history_sync_decision(rows: list[dict[str, Any]]) -> dict[str, Any]:
    required_rows = [row for row in rows if row["required_for_export"] == "true"]
    failures = [row for row in required_rows if row["sync_status"] != "SYNCHRONIZED"]
    if failures:
        decision = "REQUIRES_HISTORY_SYNC"
        recommendation = "REQUIRES_HISTORY_SYNC"
        next_action = "Synchronize MT5 terminal history before running any broker re-export."
        reason = "Local MT5 terminal does not yet contain sufficient in-window history for every export source timeframe."
    else:
        decision = "HISTORY_SYNCHRONIZED"
        recommendation = "READY_FOR_REEXPORT"
        next_action = "Run the guarded broker re-export, then rerun ST-C5.2 and unchanged ST-C3."
        reason = "Required MT5 export source timeframes are synchronized for the configured symbols and date range."
    return {
        "decision": decision,
        "recommendation": recommendation,
        "dataset_status": "NOT_APPROVED",
        "replay_status": "BLOCKED",
        "strategy_validation_status": "BLOCKED",
        "demo_status": "BLOCKED",
        "live_status": "BLOCKED",
        "required_failure_count": len(failures),
        "required_failures": [
            {
                "symbol": row["symbol"],
                "timeframe": row["timeframe"],
                "sync_status": row["sync_status"],
                "reason": row["reason"],
            }
            for row in failures
        ],
        "reason": reason,
        "next_action": next_action,
        "guardrail": GUARDRAIL,
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _report_markdown(result: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    required = [row for row in rows if row["required_for_export"] == "true"]
    diagnostics = [row for row in rows if row["required_for_export"] != "true"]
    failures = result["decision"]["required_failures"]
    failure_lines = [f"- {item['symbol']} {item['timeframe']}: {item['sync_status']} - {item['reason']}" for item in failures]
    if not failure_lines:
        failure_lines = ["- None"]
    return "\n".join(
        [
            "# ST-C5.3 MT5 History Synchronization Gate",
            "",
            f"Decision: **{result['decision']['decision']}**",
            "",
            f"Recommendation: **{result['decision']['recommendation']}**",
            "",
            f"Reason: {result['decision']['reason']}",
            "",
            "## Required Export Sources",
            "",
            f"- Required rows checked: `{len(required)}`",
            f"- Required failures: `{result['decision']['required_failure_count']}`",
            "",
            "## Required Failures",
            "",
            *failure_lines,
            "",
            "## Diagnostic Timeframes",
            "",
            f"- Diagnostic rows recorded: `{len(diagnostics)}`",
            f"- Symbols: `{', '.join(SYMBOLS)}`",
            f"- Timeframes queried: `{', '.join(AUDIT_TIMEFRAMES)}`",
            "",
            "## Governance",
            "",
            "Dataset remains not approved. Replay, strategy validation, demo, and live remain blocked.",
            "",
        ]
    )


def _runbook_markdown(decision: dict[str, Any]) -> str:
    return f"""# ST-C5.3 MT5 History Synchronization Runbook

Current decision: **{decision['decision']}**

Required before re-export:

1. Open the authenticated Vantage MT5 terminal.
2. Select EURUSD and GBPUSD in Market Watch.
3. Open charts for M1, M15, and H4 for each symbol.
4. Force each chart to load history back to `{REQUIRED_START}`.
5. Confirm the terminal has in-window M1 history because M3 may need to be derived from M1.
6. Rerun `python -m tools.st_c5_3_history_sync_gate`.
7. Only if the gate returns `READY_FOR_REEXPORT`, run `python -m tools.st_c5_broker_data_qualification --acquire`.
8. Rerun `python -m tools.st_c5_2_export_completeness_audit`.
9. Rerun unchanged ST-C3 validation.

No dataset approval, replay, strategy validation, demo, or live path may be unlocked by this gate.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    parser.add_argument("--no-mt5-query", action="store_true")
    args = parser.parse_args()
    result = run_history_sync_gate(report_dir=args.report_dir, query_mt5=not args.no_mt5_query)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["decision"]["recommendation"] == "READY_FOR_REEXPORT" else 1)


if __name__ == "__main__":
    main()
