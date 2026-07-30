#!/usr/bin/env python3
"""Validate ST-C3 Dukascopy M1 reconstruction and H4/M15/M3 aggregation.

This is a diagnostic gate. It does not approve data, open replay, or change
dataset validation rules.
"""
from __future__ import annotations

import argparse
import json
from collections import OrderedDict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

from tools.st_c3_acquire_dukascopy_dataset import (
    RAW_CACHE,
    Candle,
    _aggregate,
    _cache_path,
    _date_end,
    _date_start,
    _format_time,
    _hour_requires_source,
    _iter_hours,
    _load_m1_from_cache,
)
from tools.st_c3_verify_dukascopy_provider import _parse_bi5_ticks
from validation.st_c3.dataset_loader import EXPECTED_SYMBOLS, EXPECTED_TIMEFRAMES, TIMEFRAME_DELTAS

REPORT = Path("reports/validation/st_c3/data_integrity/AGGREGATION_VALIDATION_REPORT.json")
MARKDOWN_REPORT = Path("reports/validation/st_c3/data_integrity/AGGREGATION_VALIDATION_REPORT.md")
GUARDRAIL = "Aggregation validation does not approve data, open replay, or weaken dataset validation."


def validate_aggregation(
    *,
    cache_dir: str | Path = RAW_CACHE,
    start: datetime,
    end: datetime,
    symbols: Iterable[str] = EXPECTED_SYMBOLS,
    write_report: bool = True,
) -> dict[str, Any]:
    cache = Path(cache_dir)
    selected_symbols = tuple(sorted(symbols))
    symbol_results = [_validate_symbol(symbol, start, end, cache) for symbol in selected_symbols]
    status = "PASS" if all(item["status"] == "PASS" for item in symbol_results) else "BLOCKED"
    result = {
        "stage": "aggregation_validation",
        "status": status,
        "reason": _reason(symbol_results),
        "next_action": "Continue pilot expansion." if status == "PASS" else "Resolve source-minute gaps or aggregation defects before full download.",
        "details": {
            "coverage_start_utc": _format_time(start.replace(tzinfo=None)),
            "coverage_end_utc": _format_time(end.replace(tzinfo=None)),
            "symbols": symbol_results,
        },
        "guardrail": GUARDRAIL,
    }
    if write_report:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        MARKDOWN_REPORT.write_text(_markdown(result), encoding="utf-8")
    return result


def _validate_symbol(symbol: str, start: datetime, end: datetime, cache: Path) -> dict[str, Any]:
    source_hours = _inspect_source_hours(symbol, start, end, cache)
    m1 = _load_m1_from_cache(symbol, start, end, cache)
    expected_m1 = _expected_minutes(start, end)
    missing_m1 = [item for item in expected_m1 if item not in m1]
    timeframe_results = []
    for timeframe in sorted(EXPECTED_TIMEFRAMES):
        timeframe_results.append(_validate_timeframe(timeframe, m1, start, end))
    status = "PASS" if not missing_m1 and all(item["status"] == "PASS" for item in timeframe_results) else "BLOCKED"
    return {
        "symbol": symbol,
        "status": status,
        "source_hours": source_hours,
        "m1_rows": len(m1),
        "expected_m1_rows": len(expected_m1),
        "missing_m1_count": len(missing_m1),
        "first_missing_m1": _format_time(missing_m1[0]) if missing_m1 else None,
        "missing_m1_samples": [_format_time(item) for item in missing_m1[:20]],
        "timeframes": timeframe_results,
    }


def _inspect_source_hours(symbol: str, start: datetime, end: datetime, cache: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for hour in _iter_hours(start, end):
        if not _hour_requires_source(hour):
            continue
        path = _cache_path(cache, symbol, hour)
        row: dict[str, Any] = {
            "hour_utc": _format_time(hour.replace(tzinfo=None)),
            "path": str(path),
            "exists": path.exists(),
            "bytes": path.stat().st_size if path.exists() else 0,
            "ticks": 0,
            "minute_bars": 0,
            "missing_minutes": [],
            "status": "MISSING_FILE",
        }
        if path.exists() and path.stat().st_size > 0:
            ticks = _parse_bi5_ticks(path.read_bytes(), hour.replace(tzinfo=UTC), symbol)
            minutes = {tick.timestamp.replace(second=0, microsecond=0).replace(tzinfo=None) for tick in ticks}
            expected = [hour.replace(tzinfo=None) + timedelta(minutes=offset) for offset in range(60)]
            missing = [item for item in expected if start.replace(tzinfo=None) <= item <= end.replace(tzinfo=None) and item not in minutes]
            row.update(
                {
                    "ticks": len(ticks),
                    "minute_bars": len(minutes),
                    "missing_minutes": [_format_time(item) for item in missing[:20]],
                    "missing_minute_count": len(missing),
                    "status": "PASS" if not missing else "SPARSE_TICKS",
                }
            )
        rows.append(row)
    return rows


def _validate_timeframe(timeframe: str, m1: OrderedDict[datetime, Candle], start: datetime, end: datetime) -> dict[str, Any]:
    aggregated = OrderedDict((item.timestamp, item) for item in _aggregate(m1, timeframe))
    expected = _expected_candle_starts(timeframe, start, end)
    missing = [item for item in expected if item not in aggregated]
    mismatches: list[dict[str, Any]] = []
    for timestamp, candle in aggregated.items():
        if timestamp not in expected:
            continue
        expected_candle = _expected_from_m1(m1, timestamp, TIMEFRAME_DELTAS[timeframe])
        if expected_candle is None:
            continue
        mismatch = _compare_candles(candle, expected_candle)
        if mismatch:
            mismatches.append({"timestamp": _format_time(timestamp), "fields": mismatch})
    return {
        "timeframe": timeframe,
        "status": "PASS" if not missing and not mismatches else "BLOCKED",
        "aggregated_rows": len(aggregated),
        "expected_rows": len(expected),
        "missing_count": len(missing),
        "first_missing": _format_time(missing[0]) if missing else None,
        "missing_samples": [_format_time(item) for item in missing[:20]],
        "mismatch_count": len(mismatches),
        "mismatch_samples": mismatches[:5],
    }


def _expected_from_m1(source: OrderedDict[datetime, Candle], timestamp: datetime, delta: timedelta) -> Candle | None:
    window: list[Candle] = []
    cursor = timestamp
    while cursor < timestamp + delta:
        candle = source.get(cursor)
        if candle is None:
            return None
        window.append(candle)
        cursor += timedelta(minutes=1)
    return Candle(
        timestamp=timestamp,
        open=window[0].open,
        high=max(item.high for item in window),
        low=min(item.low for item in window),
        close=window[-1].close,
        volume=sum(item.volume for item in window),
    )


def _compare_candles(left: Candle, right: Candle) -> list[str]:
    fields = []
    for field in ("open", "high", "low", "close", "volume"):
        if abs(getattr(left, field) - getattr(right, field)) > 1e-9:
            fields.append(field)
    return fields


def _expected_minutes(start: datetime, end: datetime) -> list[datetime]:
    cursor = start.replace(tzinfo=None, second=0, microsecond=0)
    last = end.replace(tzinfo=None, second=0, microsecond=0)
    rows: list[datetime] = []
    while cursor <= last:
        if _market_open_minute(cursor):
            rows.append(cursor)
        cursor += timedelta(minutes=1)
    return rows


def _expected_candle_starts(timeframe: str, start: datetime, end: datetime) -> list[datetime]:
    delta = TIMEFRAME_DELTAS[timeframe]
    span_minutes = int(delta.total_seconds() // 60)
    cursor = start.replace(tzinfo=None, second=0, microsecond=0)
    last = end.replace(tzinfo=None, second=0, microsecond=0)
    rows: list[datetime] = []
    while cursor + delta - timedelta(minutes=1) <= last:
        total_minutes = cursor.hour * 60 + cursor.minute
        if total_minutes % span_minutes == 0 and _all_market_open(cursor, delta):
            rows.append(cursor)
        cursor += timedelta(minutes=1)
    return rows


def _all_market_open(start: datetime, delta: timedelta) -> bool:
    cursor = start
    while cursor < start + delta:
        if not _market_open_minute(cursor):
            return False
        cursor += timedelta(minutes=1)
    return True


def _market_open_minute(value: datetime) -> bool:
    if (value.month, value.day) in {(1, 1), (12, 25)}:
        return False
    if value.weekday() == 5:
        return False
    if value.weekday() == 6:
        return False
    if value.weekday() == 4 and value.hour >= 22:
        return False
    return True


def _reason(symbol_results: list[dict[str, Any]]) -> str:
    for symbol in symbol_results:
        if symbol["missing_m1_count"]:
            return f"{symbol['symbol']} missing M1 source candle {symbol['first_missing_m1']}"
        for timeframe in symbol["timeframes"]:
            if timeframe["missing_count"]:
                return f"{symbol['symbol']} {timeframe['timeframe']} missing aggregated candle {timeframe['first_missing']}"
            if timeframe["mismatch_count"]:
                return f"{symbol['symbol']} {timeframe['timeframe']} aggregation mismatch"
    return "aggregation validation passed"


def _markdown(result: dict[str, Any]) -> str:
    lines = [
        "# ST-C3 Aggregation Validation Report",
        "",
        f"Status: **{result['status']}**",
        "",
        f"Reason: {result['reason']}",
        "",
        f"Guardrail: {result['guardrail']}",
        "",
        "| Symbol | M1 Rows | Expected M1 | Missing M1 | First Missing M1 |",
        "|---|---:|---:|---:|---|",
    ]
    for symbol in result["details"]["symbols"]:
        lines.append(
            f"| `{symbol['symbol']}` | {symbol['m1_rows']} | {symbol['expected_m1_rows']} | "
            f"{symbol['missing_m1_count']} | {symbol['first_missing_m1'] or ''} |"
        )
    lines += ["", "## Timeframes", "", "| Symbol | Timeframe | Rows | Expected | Missing | Mismatches | First Missing |", "|---|---|---:|---:|---:|---:|---|"]
    for symbol in result["details"]["symbols"]:
        for timeframe in symbol["timeframes"]:
            lines.append(
                f"| `{symbol['symbol']}` | `{timeframe['timeframe']}` | {timeframe['aggregated_rows']} | "
                f"{timeframe['expected_rows']} | {timeframe['missing_count']} | "
                f"{timeframe['mismatch_count']} | {timeframe['first_missing'] or ''} |"
            )
    lines += ["", "## First Sparse Source Hours", ""]
    for symbol in result["details"]["symbols"]:
        sparse = [item for item in symbol["source_hours"] if item["status"] != "PASS"]
        if sparse:
            first = sparse[0]
            lines.append(
                f"- `{symbol['symbol']}` `{first['hour_utc']}` status `{first['status']}` "
                f"missing minutes: {', '.join(first.get('missing_minutes') or [])}"
            )
    return "\n".join(lines) + "\n"


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=RAW_CACHE)
    parser.add_argument("--start", type=_parse_utc, default=_date_start("2021-01-04"))
    parser.add_argument("--end", type=_parse_utc, default=_date_end("2021-01-04"))
    parser.add_argument("--no-report", action="store_true")
    args = parser.parse_args()
    result = validate_aggregation(cache_dir=args.cache, start=args.start, end=args.end, write_report=not args.no_report)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
