#!/usr/bin/env python3
"""Investigate repeated Dukascopy Friday 21:00 UTC empty payloads.

This focused source-integrity probe does not write market data, approve data,
change calendars, alter validation, or open replay.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import lzma
import urllib.error
import urllib.request
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Iterable

from tools.st_c3_acquire_dukascopy_dataset import _dukascopy_url
from tools.st_c3_statistical_source_integrity import HISTDATA_CACHE, _histdata_year_minutes
from tools.st_c3_verify_dukascopy_provider import _parse_bi5_ticks

REPORT_JSON = Path("reports/validation/st_c3/data_integrity/FRIDAY_2100_INVESTIGATION_REPORT.json")
REPORT_MD = Path("reports/validation/st_c3/data_integrity/FRIDAY_2100_INVESTIGATION_REPORT.md")
GUARDRAIL = "Friday 21:00 investigation is evidence only; it does not change contracts, validators, calendars, approval, replay, or market data."

DEFAULT_HOURS = (
    # Failed deterministic sample days, with adjacent control hours.
    datetime(2021, 4, 16, 20, tzinfo=UTC),
    datetime(2021, 4, 16, 21, tzinfo=UTC),
    datetime(2021, 4, 16, 22, tzinfo=UTC),
    datetime(2021, 5, 14, 20, tzinfo=UTC),
    datetime(2021, 5, 14, 21, tzinfo=UTC),
    datetime(2021, 5, 14, 22, tzinfo=UTC),
    datetime(2021, 7, 2, 20, tzinfo=UTC),
    datetime(2021, 7, 2, 21, tzinfo=UTC),
    datetime(2021, 7, 2, 22, tzinfo=UTC),
    # DST Friday control not previously attempted in the failed batch.
    datetime(2021, 4, 23, 20, tzinfo=UTC),
    datetime(2021, 4, 23, 21, tzinfo=UTC),
    # Non-Friday and winter controls.
    datetime(2021, 4, 19, 21, tzinfo=UTC),
    datetime(2021, 1, 22, 20, tzinfo=UTC),
    datetime(2021, 1, 22, 21, tzinfo=UTC),
    datetime(2021, 1, 22, 22, tzinfo=UTC),
)


def investigate_friday_2100(
    *,
    symbols: Iterable[str] = ("EURUSD", "GBPUSD"),
    hours: Iterable[datetime] = DEFAULT_HOURS,
    reference_cache: str | Path = HISTDATA_CACHE,
    write_report: bool = True,
    fetcher: Callable[[str], bytes] | None = None,
) -> dict[str, Any]:
    reference_index: dict[tuple[str, int], set[datetime] | None] = {}
    rows = [
        _probe(symbol, hour.astimezone(UTC), Path(reference_cache), reference_index, fetcher=fetcher)
        for hour in hours
        for symbol in sorted(symbols)
    ]
    classification = _classify(rows)
    result = {
        "stage": "friday_2100_source_integrity_investigation",
        "status": "BLOCKED",
        "reason": classification["reason"],
        "next_action": classification["next_action"],
        "recommendation": "CONTINUE_EVIDENCE_COLLECTION",
        "guardrail": GUARDRAIL,
        "details": {
            "provider": "Dukascopy tick datafeed",
            "reference_provider": "HistData.com Generic ASCII M1",
            "probes": rows,
            "summary": _summary(rows),
            "classification": classification,
        },
    }
    if write_report:
        REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
        REPORT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        REPORT_MD.write_text(_markdown(result), encoding="utf-8")
    return result


def _probe(
    symbol: str,
    hour: datetime,
    reference_cache: Path,
    reference_index: dict[tuple[str, int], set[datetime] | None],
    *,
    fetcher: Callable[[str], bytes] | None,
) -> dict[str, Any]:
    url = _dukascopy_url(symbol, hour)
    payload: bytes | None = None
    ticks = []
    status = "UNKNOWN"
    reason = ""
    try:
        payload = (fetcher or _fetch)(url)
        if not payload:
            status = "EMPTY_PAYLOAD"
            reason = "provider returned zero bytes"
        else:
            ticks = _parse_bi5_ticks(payload, hour, symbol)
            status = "PARSED"
            reason = "payload decompressed and parsed"
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, lzma.LZMAError, ValueError, EOFError) as exc:
        ticks = []
        status = "ERROR"
        reason = f"{type(exc).__name__}: {exc}"

    reference = _histdata_hour_reference(symbol, hour, reference_cache, reference_index)
    payload_bytes = len(payload) if payload is not None else None
    return {
        "symbol": symbol,
        "hour_utc": hour.strftime("%Y-%m-%dT%H:00:00Z"),
        "weekday": hour.strftime("%A"),
        "hour_of_day_utc": hour.hour,
        "month": f"{hour.month:02d}",
        "dukascopy_url": url,
        "dukascopy_status": status,
        "dukascopy_reason": reason,
        "payload_bytes": payload_bytes,
        "sha256": hashlib.sha256(payload).hexdigest() if payload else None,
        "tick_count": len(ticks),
        "first_tick": ticks[0].timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if ticks else None,
        "last_tick": ticks[-1].timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if ticks else None,
        "histdata_reference": reference,
    }


def _fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "smc-lss-platform source integrity investigation"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def _histdata_hour_reference(
    symbol: str,
    hour: datetime,
    cache: Path,
    reference_index: dict[tuple[str, int], set[datetime] | None],
) -> dict[str, Any]:
    path = cache / symbol / f"DAT_ASCII_{symbol}_M1_{hour.year}.zip"
    if not path.exists():
        return {"checked": False, "minute_rows": None, "reason": "zip missing"}
    key = (symbol, hour.year)
    if key not in reference_index:
        reference_index[key] = _histdata_year_minutes(path)
    minutes = reference_index[key]
    if minutes is None:
        return {"checked": False, "minute_rows": None, "reason": "csv missing from zip"}
    naive_hour = hour.replace(tzinfo=None)
    count = sum(1 for minute in range(60) if naive_hour.replace(minute=minute) in minutes)
    return {"checked": True, "minute_rows": count, "reason": "reference year indexed"}


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "by_dukascopy_status": _counter(row["dukascopy_status"] for row in rows),
        "by_weekday_hour_status": _counter(f"{row['weekday']} {row['hour_of_day_utc']:02d}:00 {row['dukascopy_status']}" for row in rows),
        "histdata_checked": len([row for row in rows if row["histdata_reference"].get("checked")]),
        "histdata_hour_rows_by_dukascopy_status": _histdata_by_status(rows),
    }


def _histdata_by_status(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    grouped: dict[str, Counter[str]] = {}
    for row in rows:
        reference = row["histdata_reference"]
        if not reference.get("checked"):
            continue
        grouped.setdefault(row["dukascopy_status"], Counter())[str(reference.get("minute_rows"))] += 1
    return {status: dict(counter) for status, counter in sorted(grouped.items())}


def _classify(rows: list[dict[str, Any]]) -> dict[str, str]:
    friday_21 = [row for row in rows if row["weekday"] == "Friday" and row["hour_of_day_utc"] == 21]
    friday_20 = [row for row in rows if row["weekday"] == "Friday" and row["hour_of_day_utc"] == 20]
    winter_friday_21 = [row for row in friday_21 if row["month"] in {"01", "02", "11", "12"}]
    dst_friday_21 = [row for row in friday_21 if row["month"] in {"03", "04", "05", "06", "07", "08", "09", "10"}]
    dst_empty = all(row["dukascopy_status"] == "EMPTY_PAYLOAD" for row in dst_friday_21) if dst_friday_21 else False
    friday_20_parsed = all(row["dukascopy_status"] == "PARSED" for row in friday_20) if friday_20 else False
    winter_21_parsed = all(row["dukascopy_status"] == "PARSED" for row in winter_friday_21) if winter_friday_21 else False
    if dst_empty and friday_20_parsed and winter_21_parsed:
        return {
            "root_cause": "DST_FRIDAY_CLOSE_PROVIDER_CALENDAR_MISMATCH",
            "reason": "Dukascopy returns empty payloads for DST Friday 21:00 UTC while adjacent Friday 20:00 UTC and winter Friday 21:00 UTC controls parse.",
            "next_action": "Document DST Friday close behavior and review the evidence-sample market calendar before resuming larger sample batches.",
        }
    return {
        "root_cause": "UNRESOLVED_FRIDAY_2100_SOURCE_BEHAVIOR",
        "reason": "Friday 21:00 UTC probe pattern is not yet conclusive.",
        "next_action": "Collect additional Friday 21:00 UTC controls before continuing broad evidence acquisition.",
    }


def _counter(values: Iterable[Any]) -> dict[str, int]:
    return {str(key): count for key, count in sorted(Counter(values).items(), key=lambda item: str(item[0]))}


def _markdown(result: dict[str, Any]) -> str:
    details = result["details"]
    classification = details["classification"]
    lines = [
        "# ST-C3 Friday 21:00 UTC Source Integrity Investigation",
        "",
        f"Status: **{result['status']}**",
        "",
        f"Reason: {result['reason']}",
        "",
        f"Recommendation: **{result['recommendation']}**",
        "",
        f"Guardrail: {result['guardrail']}",
        "",
        "## Classification",
        "",
        f"- Root cause: `{classification['root_cause']}`",
        f"- Next action: {classification['next_action']}",
        "",
        "## Summary",
        "",
        f"- By Dukascopy status: `{details['summary']['by_dukascopy_status']}`",
        f"- By weekday/hour/status: `{details['summary']['by_weekday_hour_status']}`",
        f"- HistData reference hours checked: `{details['summary']['histdata_checked']}`",
        f"- HistData hour-row counts by Dukascopy status: `{details['summary']['histdata_hour_rows_by_dukascopy_status']}`",
        "",
        "## Probes",
        "",
        "| Hour UTC | Symbol | Weekday | Dukascopy Status | Bytes | Ticks | HistData M1 Rows |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for row in details["probes"]:
        reference_rows = row["histdata_reference"].get("minute_rows")
        lines.append(
            f"| `{row['hour_utc']}` | `{row['symbol']}` | {row['weekday']} | "
            f"`{row['dukascopy_status']}` | {row['payload_bytes'] if row['payload_bytes'] is not None else ''} | "
            f"{row['tick_count']} | {reference_rows if reference_rows is not None else ''} |"
        )
    lines += [
        "",
        "## Decision",
        "",
        "This report is an interim source-integrity investigation. It does not modify the ST-C3 calendar, contract, validator, approval state, replay state, or historical prices.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-cache", type=Path, default=HISTDATA_CACHE)
    args = parser.parse_args()
    result = investigate_friday_2100(reference_cache=args.reference_cache)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(2)


if __name__ == "__main__":
    main()
