#!/usr/bin/env python3
"""Run a statistical ST-C3 source integrity audit over cached Dukascopy days.

This evidence gate does not approve data, change the Dataset Contract, fill
zero-tick minutes, weaken validation, or open replay.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

from tools.st_c3_acquire_dukascopy_dataset import RAW_CACHE, _cache_path, _format_time
from tools.st_c3_verify_dukascopy_provider import _parse_bi5_ticks
from validation.st_c3.dataset_loader import EXPECTED_SYMBOLS

REPORT_JSON = Path("reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_STATISTICAL_REPORT.json")
REPORT_MD = Path("reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_STATISTICAL_REPORT.md")
GUARDRAIL = "Statistical source integrity investigation does not change contracts, validators, approval, replay, or market data."


@dataclass(frozen=True)
class MissingMinute:
    symbol: str
    timestamp: datetime


def run_statistical_source_integrity(
    *,
    cache_dir: str | Path = RAW_CACHE,
    start_date: date = date(2021, 1, 1),
    end_date: date = date(2025, 12, 31),
    target_sample_days: int = 100,
    seed: int = 107,
    write_report: bool = True,
) -> dict[str, Any]:
    cache = Path(cache_dir)
    population = _trading_days(start_date, end_date)
    sample_days = _deterministic_sample(population, target_sample_days, seed)
    cached_complete_days = [day for day in sample_days if _day_cache_complete(cache, day, EXPECTED_SYMBOLS)]
    # Include any extra fully cached days as pilot evidence, but keep the
    # decision benchmark tied to the deterministic target sample.
    extra_cached = [day for day in population if day not in cached_complete_days and _day_cache_complete(cache, day, EXPECTED_SYMBOLS)]
    audited_days = sorted(set(cached_complete_days + extra_cached))
    symbol_results = [_audit_symbol(cache, symbol, audited_days) for symbol in sorted(EXPECTED_SYMBOLS)]
    total_expected = sum(item["expected_minutes"] for item in symbol_results)
    total_missing = sum(item["missing_minutes"] for item in symbol_results)
    statistically_sufficient = len(cached_complete_days) >= target_sample_days
    status = "PASS" if statistically_sufficient and total_missing == 0 else "BLOCKED"
    result = {
        "stage": "source_integrity_statistical_investigation",
        "status": status,
        "reason": _reason(statistically_sufficient, len(cached_complete_days), target_sample_days, total_missing),
        "next_action": _next_action(statistically_sufficient, total_missing),
        "details": {
            "coverage": {"from": start_date.isoformat(), "to": end_date.isoformat()},
            "target_sample_days": target_sample_days,
            "sample_seed": seed,
            "trading_day_population": len(population),
            "deterministic_sample_days": [day.isoformat() for day in sample_days],
            "sample_days_cached_complete": len(cached_complete_days),
            "audited_cached_days": [day.isoformat() for day in audited_days],
            "audited_cached_day_count": len(audited_days),
            "symbols": symbol_results,
            "total_expected_minutes": total_expected,
            "total_missing_minutes": total_missing,
            "missing_minute_rate": (total_missing / total_expected) if total_expected else None,
            "statistically_sufficient": statistically_sufficient,
            "recommendation": "CONTINUE_EVIDENCE_COLLECTION" if not statistically_sufficient else ("PROVIDER_REVIEW_REQUIRED" if total_missing else "PROVIDER_STATISTICAL_SAMPLE_PASS"),
        },
        "guardrail": GUARDRAIL,
    }
    if write_report:
        REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
        REPORT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        REPORT_MD.write_text(_markdown(result), encoding="utf-8")
    return result


def _audit_symbol(cache: Path, symbol: str, days: list[date]) -> dict[str, Any]:
    missing: list[MissingMinute] = []
    expected_count = 0
    audited_hours = 0
    tick_count = 0
    for day in days:
        for hour in _open_hours(day):
            path = _cache_path(cache, symbol, hour)
            ticks = _parse_bi5_ticks(path.read_bytes(), hour, symbol)
            tick_count += len(ticks)
            audited_hours += 1
            present = {tick.timestamp.replace(second=0, microsecond=0).replace(tzinfo=None) for tick in ticks}
            for minute in _expected_minutes_for_hour(hour):
                expected_count += 1
                if minute.replace(tzinfo=None) not in present:
                    missing.append(MissingMinute(symbol, minute.replace(tzinfo=None)))
    return {
        "symbol": symbol,
        "audited_days": len(days),
        "audited_hours": audited_hours,
        "tick_count": tick_count,
        "expected_minutes": expected_count,
        "missing_minutes": len(missing),
        "missing_minute_rate": (len(missing) / expected_count) if expected_count else None,
        "first_missing_minute": _format_time(missing[0].timestamp) if missing else None,
        "missing_samples": [_format_time(item.timestamp) for item in missing[:25]],
        "distribution_by_hour_utc": _counter_payload(item.timestamp.hour for item in missing),
        "distribution_by_weekday": _counter_payload(item.timestamp.strftime("%A") for item in missing),
        "distribution_by_session": _counter_payload(_session_bucket(item.timestamp) for item in missing),
    }


def _trading_days(start: date, end: date) -> list[date]:
    days: list[date] = []
    cursor = start
    while cursor <= end:
        value = datetime(cursor.year, cursor.month, cursor.day)
        if _open_hours(cursor):
            days.append(cursor)
        cursor += timedelta(days=1)
    return days


def _deterministic_sample(population: list[date], sample_size: int, seed: int) -> list[date]:
    if sample_size >= len(population):
        return list(population)
    rng = random.Random(seed)
    return sorted(rng.sample(population, sample_size))


def _day_cache_complete(cache: Path, day: date, symbols: Iterable[str]) -> bool:
    hours = _open_hours(day)
    return bool(hours) and all(
        (path := _cache_path(cache, symbol, hour)).exists() and path.stat().st_size > 0
        for symbol in symbols
        for hour in hours
    )


def _open_hours(day: date) -> list[datetime]:
    rows = []
    for hour in range(24):
        value = datetime(day.year, day.month, day.day, hour, tzinfo=UTC)
        if _market_open_hour(value):
            rows.append(value)
    return rows


def _market_open_hour(value: datetime) -> bool:
    probes = [value.replace(minute=minute) for minute in (0, 30, 59)]
    return any(_market_open_minute(probe) for probe in probes)


def _expected_minutes_for_hour(hour: datetime) -> list[datetime]:
    return [
        hour.replace(minute=minute, second=0, microsecond=0)
        for minute in range(60)
        if _market_open_minute(hour.replace(minute=minute, second=0, microsecond=0))
    ]


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


def _session_bucket(value: datetime) -> str:
    minutes = value.hour * 60 + value.minute
    if 7 * 60 <= minutes < 10 * 60:
        return "LONDON"
    if 13 * 60 <= minutes < 16 * 60:
        return "NY"
    if 21 * 60 <= minutes < 23 * 60:
        return "ROLLOVER"
    return "OTHER"


def _counter_payload(values: Iterable[Any]) -> dict[str, int]:
    return {str(key): count for key, count in sorted(Counter(values).items(), key=lambda item: str(item[0]))}


def _reason(statistically_sufficient: bool, cached_sample: int, target: int, total_missing: int) -> str:
    if not statistically_sufficient:
        return f"insufficient cached deterministic sample: {cached_sample}/{target} target days available"
    if total_missing:
        return f"statistical source integrity sample found {total_missing} zero-tick market-open minutes"
    return "statistical source integrity sample passed"


def _next_action(statistically_sufficient: bool, total_missing: int) -> str:
    if not statistically_sufficient:
        return "Acquire the deterministic 100-day evidence sample; do not change governance or approve data."
    if total_missing:
        return "Review provider suitability using the statistical evidence before any governance change."
    return "Proceed to pilot month acquisition and validation without changing governance."


def _markdown(result: dict[str, Any]) -> str:
    details = result["details"]
    lines = [
        "# ST-C3 Source Integrity Statistical Report",
        "",
        f"Status: **{result['status']}**",
        "",
        f"Reason: {result['reason']}",
        "",
        f"Recommendation: **{details['recommendation']}**",
        "",
        f"Guardrail: {result['guardrail']}",
        "",
        "## Sample",
        "",
        f"- Coverage: `{details['coverage']['from']}` through `{details['coverage']['to']}`",
        f"- Target sample days: `{details['target_sample_days']}`",
        f"- Deterministic sample days cached complete: `{details['sample_days_cached_complete']}`",
        f"- Audited cached day count: `{details['audited_cached_day_count']}`",
        f"- Statistically sufficient: `{details['statistically_sufficient']}`",
        "",
        "## Results",
        "",
        "| Symbol | Days | Hours | Expected Minutes | Missing Minutes | Missing Rate | First Missing |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for symbol in details["symbols"]:
        rate = symbol["missing_minute_rate"]
        lines.append(
            f"| `{symbol['symbol']}` | {symbol['audited_days']} | {symbol['audited_hours']} | "
            f"{symbol['expected_minutes']} | {symbol['missing_minutes']} | "
            f"{rate:.8f}" if rate is not None else "|"
        )
        if rate is not None:
            lines[-1] += f" | {symbol['first_missing_minute'] or ''} |"
    lines += ["", "## Missing Distribution", ""]
    for symbol in details["symbols"]:
        lines += [
            f"### {symbol['symbol']}",
            "",
            f"- By hour UTC: `{symbol['distribution_by_hour_utc']}`",
            f"- By weekday: `{symbol['distribution_by_weekday']}`",
            f"- By session: `{symbol['distribution_by_session']}`",
            f"- Samples: `{symbol['missing_samples']}`",
            "",
        ]
    lines += [
        "## Decision",
        "",
        "This report is not statistically sufficient until the deterministic target sample is cached and audited.",
        "No candles were fabricated, interpolated, or manually inserted.",
    ]
    return "\n".join(lines) + "\n"


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=RAW_CACHE)
    parser.add_argument("--start-date", type=_parse_date, default=date(2021, 1, 1))
    parser.add_argument("--end-date", type=_parse_date, default=date(2025, 12, 31))
    parser.add_argument("--target-sample-days", type=int, default=100)
    parser.add_argument("--seed", type=int, default=107)
    parser.add_argument("--no-report", action="store_true")
    args = parser.parse_args()
    result = run_statistical_source_integrity(
        cache_dir=args.cache,
        start_date=args.start_date,
        end_date=args.end_date,
        target_sample_days=args.target_sample_days,
        seed=args.seed,
        write_report=not args.no_report,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] == "BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
