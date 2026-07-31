#!/usr/bin/env python3
"""ST-C3 data governance review over source-integrity missing minutes.

This tool classifies the completed source-integrity evidence. It does not
approve market data, modify strategy logic, unlock replay, or change validation
thresholds.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

from tools.st_c3_acquire_dukascopy_dataset import RAW_CACHE, _cache_path, _format_time
from tools.st_c3_statistical_source_integrity import (
    HISTDATA_CACHE,
    REPORT_JSON as STATISTICAL_REPORT_JSON,
    _condition_tags,
    _expected_minutes_for_hour,
    _histdata_year_minutes,
    _histdata_reference,
    _market_open_minute,
    _near_dst_transition,
    _root_cause_category,
    _session_bucket,
    _source_required_hours,
)
from tools.st_c3_verify_dukascopy_provider import _parse_bi5_ticks
from validation.st_c3.dataset_loader import EXPECTED_SYMBOLS

REPORT_DIR = Path("reports/validation/st_c3/data_integrity")
MISSING_MINUTES_CSV = REPORT_DIR / "missing_minutes.csv"
MISSING_CLUSTERS_CSV = REPORT_DIR / "missing_clusters.csv"
SESSION_VALIDATION_CSV = REPORT_DIR / "market_session_validation.csv"
PROVIDER_GAP_ANALYSIS_MD = REPORT_DIR / "provider_gap_analysis.md"
DATASET_STATISTICS_JSON = REPORT_DIR / "DATASET_STATISTICS.json"
GOVERNANCE_DECISION_JSON = REPORT_DIR / "GOVERNANCE_DECISION.json"
GOVERNANCE_REVIEW_MD = REPORT_DIR / "DATA_GOVERNANCE_REVIEW.md"
EXECUTIVE_SUMMARY_MD = REPORT_DIR / "DATA_GOVERNANCE_EXECUTIVE_SUMMARY.md"
THRESHOLD = 0.001
GUARDRAIL = "Governance review only; replay, strategy validation, demo, and live trading remain blocked unless data is approved."


@dataclass(frozen=True)
class MissingMinuteRow:
    symbol: str
    timestamp: datetime
    previous_tick_count: int
    next_tick_count: int


@dataclass(frozen=True)
class MissingCluster:
    cluster_id: str
    symbol: str
    start: datetime
    end: datetime
    duration_minutes: int
    trading_session: str
    weekday: str
    minutes: tuple[MissingMinuteRow, ...]


def run_governance_review(
    *,
    statistical_report: str | Path = STATISTICAL_REPORT_JSON,
    cache_dir: str | Path = RAW_CACHE,
    reference_cache_dir: str | Path = HISTDATA_CACHE,
    output_dir: str | Path = REPORT_DIR,
    threshold: float = THRESHOLD,
) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    report = json.loads(Path(statistical_report).read_text(encoding="utf-8"))
    details = report["details"]
    audited_days = [date.fromisoformat(item) for item in details["audited_cached_days"]]
    symbols = sorted(EXPECTED_SYMBOLS)
    missing = collect_missing_minutes(Path(cache_dir), audited_days, symbols)
    clusters = cluster_missing_minutes(missing)
    reference_index: dict[tuple[str, int], set[datetime] | None] = {}
    validations = [classify_cluster(cluster, Path(reference_cache_dir), reference_index) for cluster in clusters]
    statistics = calculate_statistics(
        missing,
        clusters,
        validations,
        total_expected_minutes=int(details["total_expected_minutes"]),
        original_missing_rate=float(details["missing_minute_rate"]),
        threshold=threshold,
    )
    decision = governance_decision(statistics, validations, threshold)
    write_outputs(output, missing, clusters, validations, statistics, decision)
    return {
        "stage": "st_c3_data_governance_review",
        "status": "COMPLETE",
        "guardrail": GUARDRAIL,
        "missing_minutes": len(missing),
        "clusters": len(clusters),
        "statistics": statistics,
        "decision": decision,
    }


def collect_missing_minutes(cache: Path, audited_days: Iterable[date], symbols: Iterable[str]) -> list[MissingMinuteRow]:
    rows: list[MissingMinuteRow] = []
    for symbol in symbols:
        for day in audited_days:
            counts: Counter[datetime] = Counter()
            expected: list[datetime] = []
            for hour in _source_required_hours(day):
                path = _cache_path(cache, symbol, hour)
                ticks = _parse_bi5_ticks(path.read_bytes(), hour, symbol)
                counts.update(tick.timestamp.replace(second=0, microsecond=0).replace(tzinfo=None) for tick in ticks)
                expected.extend(minute.replace(tzinfo=None) for minute in _expected_minutes_for_hour(hour))
            for minute in sorted(expected):
                if counts[minute] == 0:
                    rows.append(
                        MissingMinuteRow(
                            symbol=symbol,
                            timestamp=minute,
                            previous_tick_count=counts[minute - timedelta(minutes=1)],
                            next_tick_count=counts[minute + timedelta(minutes=1)],
                        )
                    )
    return sorted(rows, key=lambda item: (item.symbol, item.timestamp))


def cluster_missing_minutes(rows: Iterable[MissingMinuteRow]) -> list[MissingCluster]:
    clusters: list[MissingCluster] = []
    current: list[MissingMinuteRow] = []
    last_key: tuple[str, datetime] | None = None
    for row in sorted(rows, key=lambda item: (item.symbol, item.timestamp)):
        key = (row.symbol, row.timestamp)
        if not current or (last_key and key[0] == last_key[0] and key[1] == last_key[1] + timedelta(minutes=1)):
            current.append(row)
        else:
            clusters.append(_cluster_from_rows(len(clusters) + 1, current))
            current = [row]
        last_key = key
    if current:
        clusters.append(_cluster_from_rows(len(clusters) + 1, current))
    return clusters


def classify_cluster(
    cluster: MissingCluster,
    reference_cache: Path | None = None,
    reference_index: dict[tuple[str, int], set[datetime] | None] | None = None,
) -> dict[str, Any]:
    references = [_indexed_histdata_reference(row, reference_cache, reference_index) for row in cluster.minutes]
    reference_checked = [item for item in references if item.get("checked")]
    reference_present = [item for item in reference_checked if item.get("present")]
    reference_absent = [item for item in reference_checked if item.get("present") is False]
    if _is_weekend(cluster.start):
        return _validation(cluster, False, "Weekend", "EXPECTED", "Weekend closure", 1.0, references)
    if _is_fixed_holiday(cluster.start):
        return _validation(cluster, False, "Holiday", "EXPECTED", "New Year or Christmas closure", 1.0, references)
    if _is_good_friday(cluster.start.date()):
        return _validation(cluster, False, "Holiday", "EXPECTED", "Good Friday market-holiday candidate", 0.8, references)
    if cluster.start.weekday() == 4 and cluster.start.hour == 21 and _near_dst_transition(cluster.start.date()):
        return _validation(cluster, False, "DST transition", "EXPECTED", "Known Dukascopy DST Friday close source exclusion window", 0.9, references)
    if reference_present:
        return _validation(cluster, True, "Unexpected market-open period", "UNEXPECTED", "Reference provider contains minute(s) missing in Dukascopy", 0.95, references)
    if cluster.trading_session == "ROLLOVER" and reference_absent and len(reference_checked) == len(cluster.minutes):
        return _validation(cluster, True, "Daily Maintenance", "EXPECTED", "All checked reference minutes absent during rollover window", 0.7, references)
    if reference_absent and len(reference_checked) == len(cluster.minutes):
        return _validation(cluster, True, "Broker maintenance", "UNKNOWN", "All checked reference minutes absent outside primary sessions; provider-specific closure not independently verified", 0.45, references)
    return _validation(cluster, True, "Unexpected market-open period", "UNKNOWN", "Insufficient reference/calendar evidence for deterministic classification", 0.25, references)


def calculate_statistics(
    missing: list[MissingMinuteRow],
    clusters: list[MissingCluster],
    validations: list[dict[str, Any]],
    *,
    total_expected_minutes: int,
    original_missing_rate: float,
    threshold: float,
) -> dict[str, Any]:
    by_classification = Counter(item["classification"] for item in validations for _ in range(int(item["duration_minutes"])))
    by_event = Counter(item["calendar_event"] for item in validations for _ in range(int(item["duration_minutes"])))
    explained = by_classification["EXPECTED"]
    unknown = by_classification["UNKNOWN"]
    unexpected = by_classification["UNEXPECTED"]
    unexplained = unknown + unexpected
    effective_rate = unexplained / total_expected_minutes if total_expected_minutes else None
    return {
        "total_missing_minutes": len(missing),
        "total_clusters": len(clusters),
        "validated_market_open_minutes": total_expected_minutes,
        "explained_missing_minutes": explained,
        "unexplained_missing_minutes": unexplained,
        "weekend_minutes": by_event["Weekend"],
        "holiday_minutes": by_event["Holiday"],
        "maintenance_minutes": by_event["Daily Maintenance"] + by_event["Broker maintenance"],
        "dst_minutes": by_event["DST transition"],
        "unknown_minutes": unknown,
        "unexpected_minutes": unexpected,
        "original_missing_rate": original_missing_rate,
        "explained_missing_rate": explained / total_expected_minutes if total_expected_minutes else None,
        "effective_missing_rate": effective_rate,
        "threshold": threshold,
        "classification_counts": dict(sorted(by_classification.items())),
        "calendar_event_counts": dict(sorted(by_event.items())),
    }


def governance_decision(statistics: dict[str, Any], validations: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    unknown_clusters = [item for item in validations if item["classification"] == "UNKNOWN"]
    effective_rate = statistics["effective_missing_rate"]
    if unknown_clusters:
        recommendation = "REQUIRES_MANUAL_REVIEW"
        dataset_status = "NOT_APPROVED"
        reason = "Unknown gaps remain; stop condition prevents approval or rejection-as-final."
    elif effective_rate is not None and effective_rate < threshold:
        recommendation = "APPROVE_DATASET"
        dataset_status = "APPROVED"
        reason = "Effective missing rate is below threshold after supported exclusions."
    else:
        recommendation = "REJECT_DATASET"
        dataset_status = "REJECTED"
        reason = "Effective missing rate exceeds threshold."
    return {
        "recommendation": recommendation,
        "decision": recommendation,
        "reason": reason,
        "dataset_status": dataset_status,
        "replay_status": "READY" if dataset_status == "APPROVED" else "BLOCKED",
        "strategy_validation_status": "READY" if dataset_status == "APPROVED" else "BLOCKED",
        "demo_status": "BLOCKED",
        "live_status": "BLOCKED",
        "unknown_cluster_count": len(unknown_clusters),
        "unknown_missing_minutes": statistics["unknown_minutes"],
        "effective_missing_rate": effective_rate,
        "threshold": threshold,
        "guardrail": GUARDRAIL,
    }


def write_outputs(
    output: Path,
    missing: list[MissingMinuteRow],
    clusters: list[MissingCluster],
    validations: list[dict[str, Any]],
    statistics: dict[str, Any],
    decision: dict[str, Any],
) -> None:
    cluster_by_minute = {minute: cluster for cluster in clusters for minute in cluster.minutes}
    _write_csv(
        output / "missing_minutes.csv",
        ["symbol", "date", "timestamp", "expected_previous", "expected_next", "gap_length", "session", "weekday", "market_should_be_open"],
        [
            {
                "symbol": row.symbol,
                "date": row.timestamp.date().isoformat(),
                "timestamp": _format_time(row.timestamp),
                "expected_previous": row.previous_tick_count,
                "expected_next": row.next_tick_count,
                "gap_length": cluster_by_minute[row].duration_minutes,
                "session": _session_bucket(row.timestamp),
                "weekday": row.timestamp.strftime("%A"),
                "market_should_be_open": _market_open_minute(row.timestamp.replace(tzinfo=UTC)),
            }
            for row in missing
        ],
    )
    _write_csv(
        output / "missing_clusters.csv",
        ["cluster_id", "symbol", "start", "end", "duration_minutes", "trading_session", "weekday"],
        [
            {
                "cluster_id": cluster.cluster_id,
                "symbol": cluster.symbol,
                "start": _format_time(cluster.start),
                "end": _format_time(cluster.end),
                "duration_minutes": cluster.duration_minutes,
                "trading_session": cluster.trading_session,
                "weekday": cluster.weekday,
            }
            for cluster in clusters
        ],
    )
    _write_csv(
        output / "market_session_validation.csv",
        ["cluster_id", "market_expected_open", "calendar_event", "classification", "reason", "confidence"],
        [
            {
                "cluster_id": item["cluster_id"],
                "market_expected_open": item["market_expected_open"],
                "calendar_event": item["calendar_event"],
                "classification": item["classification"],
                "reason": item["reason"],
                "confidence": item["confidence"],
            }
            for item in validations
        ],
    )
    (output / "DATASET_STATISTICS.json").write_text(json.dumps(statistics, indent=2, sort_keys=True), encoding="utf-8")
    (output / "GOVERNANCE_DECISION.json").write_text(json.dumps(decision, indent=2, sort_keys=True), encoding="utf-8")
    (output / "provider_gap_analysis.md").write_text(_provider_markdown(statistics, decision), encoding="utf-8")
    (output / "DATA_GOVERNANCE_REVIEW.md").write_text(_review_markdown(statistics, decision, validations), encoding="utf-8")
    (output / "DATA_GOVERNANCE_EXECUTIVE_SUMMARY.md").write_text(_executive_markdown(statistics, decision), encoding="utf-8")


def _cluster_from_rows(index: int, rows: list[MissingMinuteRow]) -> MissingCluster:
    start = rows[0].timestamp
    end = rows[-1].timestamp
    return MissingCluster(
        cluster_id=f"MM-{index:05d}",
        symbol=rows[0].symbol,
        start=start,
        end=end,
        duration_minutes=len(rows),
        trading_session=_session_bucket(start),
        weekday=start.strftime("%A"),
        minutes=tuple(rows),
    )


def _validation(
    cluster: MissingCluster,
    market_expected_open: bool,
    event: str,
    classification: str,
    reason: str,
    confidence: float,
    references: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "cluster_id": cluster.cluster_id,
        "symbol": cluster.symbol,
        "start": _format_time(cluster.start),
        "end": _format_time(cluster.end),
        "duration_minutes": cluster.duration_minutes,
        "market_expected_open": market_expected_open,
        "calendar_event": event,
        "classification": classification,
        "reason": reason,
        "confidence": confidence,
        "condition_tags": _condition_tags(cluster.start.date()),
        "root_cause_category": _root_cause_category(cluster.start),
        "reference_checked_minutes": len([item for item in references if item.get("checked")]),
        "reference_present_minutes": len([item for item in references if item.get("present")]),
        "reference_absent_minutes": len([item for item in references if item.get("present") is False]),
    }


def _indexed_histdata_reference(
    row: MissingMinuteRow,
    reference_cache: Path | None,
    reference_index: dict[tuple[str, int], set[datetime] | None] | None,
) -> dict[str, Any]:
    if reference_cache is None:
        return {"checked": False, "provider": "HistData.com Generic ASCII M1"}
    if reference_index is None:
        return _histdata_reference(row, reference_cache)
    path = reference_cache / row.symbol / f"DAT_ASCII_{row.symbol}_M1_{row.timestamp.year}.zip"
    if not path.exists():
        return {"checked": False, "provider": "HistData.com Generic ASCII M1", "present": False, "reason": "zip missing"}
    key = (row.symbol, row.timestamp.year)
    if key not in reference_index:
        reference_index[key] = _histdata_year_minutes(path)
    minutes = reference_index[key]
    if minutes is None:
        return {"checked": False, "provider": "HistData.com Generic ASCII M1", "present": False, "reason": "csv missing from zip"}
    return {"checked": True, "provider": "HistData.com Generic ASCII M1", "present": row.timestamp in minutes}


def _is_weekend(value: datetime) -> bool:
    return value.weekday() in {5, 6}


def _is_fixed_holiday(value: datetime) -> bool:
    return (value.month, value.day) in {(1, 1), (12, 25)}


def _is_good_friday(day: date) -> bool:
    return day == _easter_sunday(day.year) - timedelta(days=2)


def _easter_sunday(year: int) -> date:
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _provider_markdown(statistics: dict[str, Any], decision: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# ST-C3 Provider Gap Analysis",
            "",
            "## Root Cause",
            "",
            "The completed evidence set contains Dukascopy zero-tick missing minutes during market-open periods under the current calendar.",
            "",
            "## Evidence",
            "",
            f"- Total missing minutes: `{statistics['total_missing_minutes']}`",
            f"- Unknown minutes: `{statistics['unknown_minutes']}`",
            f"- Unexpected minutes: `{statistics['unexpected_minutes']}`",
            f"- Effective missing rate: `{statistics['effective_missing_rate']}`",
            "",
            "## Confidence",
            "",
            "Medium. Missing minutes are reproducible from cached source files, but not every cluster has enough independent calendar/provider evidence for final explanation.",
            "",
            "## Recommendation",
            "",
            f"**{decision['recommendation']}**",
            "",
        ]
    )


def _review_markdown(statistics: dict[str, Any], decision: dict[str, Any], validations: list[dict[str, Any]]) -> str:
    return "\n".join(
        [
            "# ST-C3 Data Governance Review",
            "",
            "## Executive Summary",
            "",
            f"Decision: **{decision['decision']}**",
            f"Reason: {decision['reason']}",
            "",
            "## Methodology",
            "",
            "All missing minutes were rederived from cached Dukascopy `.bi5` files using the existing source-integrity calendar and parser, then clustered by consecutive symbol-minute gaps.",
            "",
            "## Dataset",
            "",
            "ST-C3 evidence sample, EURUSD and GBPUSD, 2021-01-01 through 2025-12-31 audited cached days.",
            "",
            "## Provider",
            "",
            "Dukascopy tick datafeed.",
            "",
            "## Evidence",
            "",
            f"- Total clusters: `{statistics['total_clusters']}`",
            f"- Classification counts: `{statistics['classification_counts']}`",
            f"- Calendar event counts: `{statistics['calendar_event_counts']}`",
            "",
            "## Gap Statistics",
            "",
            f"- Total missing minutes: `{statistics['total_missing_minutes']}`",
            f"- Explained missing minutes: `{statistics['explained_missing_minutes']}`",
            f"- Unexplained missing minutes: `{statistics['unexplained_missing_minutes']}`",
            f"- Unknown missing minutes: `{statistics['unknown_minutes']}`",
            "",
            "## Gap Classification",
            "",
            "Every missing minute was assigned to a cluster. Every cluster was classified as EXPECTED, UNEXPECTED, or UNKNOWN.",
            "",
            "## Calendar Validation",
            "",
            "Weekend, New Year, Christmas, Easter/Good Friday, daily maintenance, DST transition, broker maintenance, and unexpected market-open categories were evaluated.",
            "",
            "## DST Validation",
            "",
            "DST transition windows were detected with the existing source-integrity DST helper. No governance threshold was changed.",
            "",
            "## Provider Findings",
            "",
            "Provider evidence is incomplete for final explanation where reference data is absent or unavailable, so unknown clusters remain.",
            "",
            "## Statistical Findings",
            "",
            f"- Original missing rate: `{statistics['original_missing_rate']}`",
            f"- Explained missing rate: `{statistics['explained_missing_rate']}`",
            f"- Effective missing rate: `{statistics['effective_missing_rate']}`",
            f"- Threshold: `{statistics['threshold']}`",
            "",
            "## Risk Assessment",
            "",
            "Unknown gaps remain, and unexplained missing minutes exceed the approval threshold. Dataset approval and replay remain blocked.",
            "",
            "## Recommendation",
            "",
            f"**{decision['recommendation']}**",
            "",
            "## Decision",
            "",
            f"Dataset status: **{decision['dataset_status']}**",
            f"Replay status: **{decision['replay_status']}**",
            "",
        ]
    )


def _executive_markdown(statistics: dict[str, Any], decision: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# ST-C3 Data Governance Executive Summary",
            "",
            "## Current Status",
            "",
            f"Dataset: **{decision['dataset_status']}**. Replay: **{decision['replay_status']}**. Strategy validation: **{decision['strategy_validation_status']}**.",
            "",
            "## Scientific Findings",
            "",
            f"The review classified `{statistics['total_missing_minutes']}` missing market-open minutes across `{statistics['total_clusters']}` clusters. Unknown minutes: `{statistics['unknown_minutes']}`. Effective missing rate: `{statistics['effective_missing_rate']}`.",
            "",
            "## Decision",
            "",
            f"**{decision['decision']}**",
            "",
            "## Next Action",
            "",
            "Manual data-governance review is required before any dataset approval or replay action.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--statistical-report", type=Path, default=STATISTICAL_REPORT_JSON)
    parser.add_argument("--cache", type=Path, default=RAW_CACHE)
    parser.add_argument("--reference-cache", type=Path, default=HISTDATA_CACHE)
    parser.add_argument("--output-dir", type=Path, default=REPORT_DIR)
    parser.add_argument("--threshold", type=float, default=THRESHOLD)
    args = parser.parse_args()
    result = run_governance_review(
        statistical_report=args.statistical_report,
        cache_dir=args.cache,
        reference_cache_dir=args.reference_cache,
        output_dir=args.output_dir,
        threshold=args.threshold,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["decision"]["recommendation"] == "APPROVE_DATASET" else 1)


if __name__ == "__main__":
    main()
