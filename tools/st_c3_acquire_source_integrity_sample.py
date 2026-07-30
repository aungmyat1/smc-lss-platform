#!/usr/bin/env python3
"""Acquire the deterministic ST-C3 source-integrity evidence sample.

This tool downloads raw Dukascopy evidence-sample hours only. It does not
construct approved dataset files, approve data, change contracts, fill candles,
or open replay.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Iterable

from tools.st_c3_acquire_dukascopy_dataset import RAW_CACHE, _cache_path, _download_hour, _format_time
from tools.st_c3_statistical_source_integrity import _deterministic_sample, _open_hours, _parse_date, _trading_days
from validation.st_c3.dataset_loader import EXPECTED_SYMBOLS

REPORT_JSON = Path("reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_SAMPLE_ACQUISITION.json")
REPORT_MD = Path("reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_SAMPLE_ACQUISITION.md")
GUARDRAIL = "Evidence-sample acquisition downloads raw source files only; it does not approve data, change governance, or open replay."


def acquire_source_integrity_sample(
    *,
    cache_dir: str | Path = RAW_CACHE,
    start_date: date = date(2021, 1, 1),
    end_date: date = date(2025, 12, 31),
    target_sample_days: int = 100,
    seed: int = 107,
    max_days: int | None = None,
    max_hours: int | None = None,
    retries: int = 3,
    write_report: bool = True,
) -> dict[str, Any]:
    cache = Path(cache_dir)
    population = _trading_days(start_date, end_date)
    sample_days = _deterministic_sample(population, target_sample_days, seed)
    completed_before = [day for day in sample_days if _day_cache_complete(cache, day, EXPECTED_SYMBOLS)]
    pending_days = [day for day in sample_days if day not in completed_before]
    selected_days = pending_days[:max_days] if max_days is not None else pending_days
    attempts: list[dict[str, Any]] = []
    processed_hours = 0
    stopped_by_limit = False

    for day in selected_days:
        for hour in _open_hours(day):
            for symbol in sorted(EXPECTED_SYMBOLS):
                if max_hours is not None and processed_hours >= max_hours:
                    stopped_by_limit = True
                    break
                attempts.append(_download_hour(symbol, hour, cache, retries=retries))
                processed_hours += 1
            if stopped_by_limit:
                break
        if stopped_by_limit:
            break

    completed_after = [day for day in sample_days if _day_cache_complete(cache, day, EXPECTED_SYMBOLS)]
    failed = [item for item in attempts if item["status"] == "FAILED"]
    status = "BLOCKED" if failed else "IN_PROGRESS"
    result = {
        "stage": "source_integrity_sample_acquisition",
        "status": status,
        "reason": _reason(failed, completed_after, target_sample_days, stopped_by_limit),
        "next_action": _next_action(failed, completed_after, target_sample_days),
        "details": {
            "coverage": {"from": start_date.isoformat(), "to": end_date.isoformat()},
            "target_sample_days": target_sample_days,
            "sample_seed": seed,
            "completed_sample_days_before": len(completed_before),
            "completed_sample_days_after": len(completed_after),
            "remaining_sample_days": max(target_sample_days - len(completed_after), 0),
            "selected_days": [day.isoformat() for day in selected_days],
            "attempted_hours": len(attempts),
            "downloaded_or_cached_hours": len([item for item in attempts if item["status"] in {"DOWNLOADED", "CACHED_VERIFIED"}]),
            "failed_hours": failed,
            "stopped_by_limit": stopped_by_limit,
            "first_remaining_day": _first_remaining(sample_days, completed_after),
        },
        "guardrail": GUARDRAIL,
        "recommendation": "CONTINUE_EVIDENCE_COLLECTION",
    }
    if write_report:
        REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
        REPORT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        REPORT_MD.write_text(_markdown(result), encoding="utf-8")
    return result


def _day_cache_complete(cache: Path, day: date, symbols: Iterable[str]) -> bool:
    return all(
        (path := _cache_path(cache, symbol, hour)).exists() and path.stat().st_size > 0
        for hour in _open_hours(day)
        for symbol in symbols
    )


def _first_remaining(sample_days: list[date], completed_days: list[date]) -> str | None:
    completed = set(completed_days)
    for day in sample_days:
        if day not in completed:
            return day.isoformat()
    return None


def _reason(failed: list[dict[str, Any]], completed_after: list[date], target: int, stopped_by_limit: bool) -> str:
    if failed:
        first = failed[0]
        return f"{first['symbol']} {first['hour_utc']} evidence-sample download failed: {first['reason']}"
    if len(completed_after) >= target:
        return "deterministic source-integrity evidence sample is fully cached"
    if stopped_by_limit:
        return f"bounded evidence-sample acquisition completed; {len(completed_after)}/{target} target days cached"
    return f"evidence-sample acquisition in progress; {len(completed_after)}/{target} target days cached"


def _next_action(failed: list[dict[str, Any]], completed_after: list[date], target: int) -> str:
    if failed:
        return "Retry failed evidence-sample hours; do not alter dataset policy."
    if len(completed_after) >= target:
        return "Rerun statistical source-integrity report and proceed to evidence review."
    return "Continue deterministic evidence-sample acquisition in bounded batches."


def _markdown(result: dict[str, Any]) -> str:
    details = result["details"]
    lines = [
        "# ST-C3 Source Integrity Sample Acquisition",
        "",
        f"Status: **{result['status']}**",
        "",
        f"Reason: {result['reason']}",
        "",
        f"Recommendation: **{result['recommendation']}**",
        "",
        f"Guardrail: {result['guardrail']}",
        "",
        "## Progress",
        "",
        f"- Target sample days: `{details['target_sample_days']}`",
        f"- Completed before: `{details['completed_sample_days_before']}`",
        f"- Completed after: `{details['completed_sample_days_after']}`",
        f"- Remaining sample days: `{details['remaining_sample_days']}`",
        f"- Attempted source hours: `{details['attempted_hours']}`",
        f"- Downloaded or cached source hours: `{details['downloaded_or_cached_hours']}`",
        f"- Failed source hours: `{len(details['failed_hours'])}`",
        f"- First remaining sample day: `{details['first_remaining_day']}`",
        "",
        "No candles were fabricated, interpolated, or manually inserted.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=RAW_CACHE)
    parser.add_argument("--start-date", type=_parse_date, default=date(2021, 1, 1))
    parser.add_argument("--end-date", type=_parse_date, default=date(2025, 12, 31))
    parser.add_argument("--target-sample-days", type=int, default=100)
    parser.add_argument("--seed", type=int, default=107)
    parser.add_argument("--max-days", type=int, default=None)
    parser.add_argument("--max-hours", type=int, default=None)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--no-report", action="store_true")
    args = parser.parse_args()
    result = acquire_source_integrity_sample(
        cache_dir=args.cache,
        start_date=args.start_date,
        end_date=args.end_date,
        target_sample_days=args.target_sample_days,
        seed=args.seed,
        max_days=args.max_days,
        max_hours=args.max_hours,
        retries=args.retries,
        write_report=not args.no_report,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] == "BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
