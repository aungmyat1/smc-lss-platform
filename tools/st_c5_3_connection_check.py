#!/usr/bin/env python3
"""Provider identity precheck for OP-02 MetaQuotes qualification.

This tool verifies the active MT5 server before a provider history gate runs.
It does not query history, export data, approve datasets, unlock replay, or
modify strategy/validation logic.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tools.st_c5_broker_data_qualification import GUARDRAIL

REPORT_DIR = Path("reports/operations/providers/MetaQuotes/attempt_01")
REQUIRED_SYMBOLS = ("EURUSD", "GBPUSD")


def run_connection_check(
    *,
    expected_provider: str = "MetaQuotes",
    report_dir: str | Path = REPORT_DIR,
    filename_stem: str = "CONNECTION_RECHECK_03",
) -> dict[str, Any]:
    reports = Path(report_dir)
    reports.mkdir(parents=True, exist_ok=True)
    payload = _connection_payload(expected_provider)
    json_path = reports / f"{filename_stem}.json"
    md_path = reports / f"{filename_stem}.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(_connection_markdown(payload), encoding="utf-8")
    return payload


def _connection_payload(expected_provider: str) -> dict[str, Any]:
    generated_at = datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    try:
        import MetaTrader5 as mt5
    except ImportError as exc:
        return _blocked(generated_at, expected_provider, f"MetaTrader5 package unavailable: {exc}")
    if not mt5.initialize():
        return _blocked(generated_at, expected_provider, f"mt5.initialize failed: {mt5.last_error()}")
    try:
        terminal = _as_dict(mt5.terminal_info())
        account = _as_dict(mt5.account_info())
        symbols = {}
        for symbol in REQUIRED_SYMBOLS:
            selected = bool(mt5.symbol_select(symbol, True))
            info = _as_dict(mt5.symbol_info(symbol))
            symbols[symbol] = {
                "selected": selected,
                "symbol_info_available": bool(info),
                "description": info.get("description") if info else None,
                "path": info.get("path") if info else None,
            }
    finally:
        mt5.shutdown()
    server = str(account.get("server") or "")
    company = str(account.get("company") or "")
    provider_match = expected_provider.lower() in server.lower() or expected_provider.lower() in company.lower()
    symbols_ok = all(item["selected"] and item["symbol_info_available"] for item in symbols.values())
    status = "READY_FOR_HISTORY_GATE" if provider_match and symbols_ok and terminal.get("connected") else "PENDING_METAQUOTES_CONNECTION"
    return {
        "stage": "st_c5_3_connection_check",
        "status": status,
        "expected_provider": expected_provider,
        "generated_at_utc": generated_at,
        "server": server,
        "account_company": company,
        "account_type": "Demo",
        "terminal_connected": bool(terminal.get("connected")),
        "terminal_build": terminal.get("build"),
        "symbols": symbols,
        "next_action": "Run python -m tools.st_c5_3_history_sync_gate" if status == "READY_FOR_HISTORY_GATE" else "Connect MT5 to the exact MetaQuotes Demo server before running history gate.",
        "guardrail": GUARDRAIL,
    }


def _blocked(generated_at: str, expected_provider: str, reason: str) -> dict[str, Any]:
    return {
        "stage": "st_c5_3_connection_check",
        "status": "CONNECTION_CHECK_FAILED",
        "expected_provider": expected_provider,
        "generated_at_utc": generated_at,
        "reason": reason,
        "next_action": "Fix MT5 connection precheck before running history gate.",
        "guardrail": GUARDRAIL,
    }


def _as_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if hasattr(value, "_asdict"):
        return dict(value._asdict())
    return dict(value) if isinstance(value, dict) else {}


def _connection_markdown(payload: dict[str, Any]) -> str:
    symbols = payload.get("symbols") or {}
    symbol_lines = [
        f"| {symbol} | {item['selected']} | {item['symbol_info_available']} | {item.get('path') or '-'} |"
        for symbol, item in symbols.items()
    ]
    if not symbol_lines:
        symbol_lines = ["| - | - | - | - |"]
    return "\n".join(
        [
            "# OP-02 MetaQuotes Connection Check",
            "",
            f"Status: **{payload['status']}**",
            "",
            f"Generated UTC: `{payload['generated_at_utc']}`",
            "",
            "## Provider Identity",
            "",
            f"- Expected provider: `{payload.get('expected_provider')}`",
            f"- Active server: `{payload.get('server', '-')}`",
            f"- Account company: `{payload.get('account_company', '-')}`",
            f"- Account type: `{payload.get('account_type', '-')}`",
            f"- Terminal connected: `{payload.get('terminal_connected', '-')}`",
            f"- Terminal build: `{payload.get('terminal_build', '-')}`",
            "",
            "## Symbols",
            "",
            "| Symbol | Selected | Info Available | Path |",
            "| --- | --- | --- | --- |",
            *symbol_lines,
            "",
            "## Next Action",
            "",
            payload["next_action"],
            "",
            "No history gate, export, ST-C3 validation, approval, replay, demo, or live action is performed by this check.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-provider", default="MetaQuotes")
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    parser.add_argument("--filename-stem", default="CONNECTION_RECHECK_03")
    args = parser.parse_args()
    result = run_connection_check(expected_provider=args.expected_provider, report_dir=args.report_dir, filename_stem=args.filename_stem)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["status"] == "READY_FOR_HISTORY_GATE" else 1)


if __name__ == "__main__":
    main()
