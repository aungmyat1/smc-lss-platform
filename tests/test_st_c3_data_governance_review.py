from __future__ import annotations

from datetime import datetime

from tools.st_c3_data_governance_review import (
    MissingMinuteRow,
    calculate_statistics,
    classify_cluster,
    cluster_missing_minutes,
    governance_decision,
)


def _row(symbol: str, value: str) -> MissingMinuteRow:
    return MissingMinuteRow(symbol=symbol, timestamp=datetime.fromisoformat(value), previous_tick_count=1, next_tick_count=1)


def test_cluster_missing_minutes_merges_consecutive_symbol_minutes():
    rows = [
        _row("EURUSD", "2025-01-02T09:31:00"),
        _row("EURUSD", "2025-01-02T09:32:00"),
        _row("EURUSD", "2025-01-02T09:34:00"),
        _row("GBPUSD", "2025-01-02T09:32:00"),
    ]

    clusters = cluster_missing_minutes(rows)

    assert [cluster.duration_minutes for cluster in clusters] == [2, 1, 1]
    assert clusters[0].start == datetime(2025, 1, 2, 9, 31)
    assert clusters[0].end == datetime(2025, 1, 2, 9, 32)
    assert clusters[0].cluster_id == "MM-00001"


def test_classify_cluster_marks_fixed_holiday_expected_without_reference_cache():
    cluster = cluster_missing_minutes([_row("EURUSD", "2025-12-25T09:31:00")])[0]

    result = classify_cluster(cluster, reference_cache=None)

    assert result["classification"] == "EXPECTED"
    assert result["calendar_event"] == "Holiday"
    assert result["market_expected_open"] is False


def test_classify_cluster_detects_dst_transition_window():
    cluster = cluster_missing_minutes([_row("EURUSD", "2025-03-14T21:00:00")])[0]

    result = classify_cluster(cluster, reference_cache=None)

    assert result["classification"] == "EXPECTED"
    assert result["calendar_event"] == "DST transition"
    assert result["confidence"] == 0.9


def test_calculate_statistics_and_decision_require_manual_review_for_unknowns():
    clusters = cluster_missing_minutes(
        [
            _row("EURUSD", "2025-01-02T09:31:00"),
            _row("EURUSD", "2025-01-02T09:32:00"),
            _row("EURUSD", "2025-12-25T09:31:00"),
        ]
    )
    validations = [
        {
            "classification": "UNKNOWN",
            "calendar_event": "Unexpected market-open period",
            "duration_minutes": 2,
        },
        {
            "classification": "EXPECTED",
            "calendar_event": "Holiday",
            "duration_minutes": 1,
        },
    ]

    stats = calculate_statistics(
        [minute for cluster in clusters for minute in cluster.minutes],
        clusters,
        validations,
        total_expected_minutes=1000,
        original_missing_rate=0.003,
        threshold=0.001,
    )
    decision = governance_decision(stats, validations, 0.001)

    assert stats["explained_missing_minutes"] == 1
    assert stats["unexplained_missing_minutes"] == 2
    assert stats["effective_missing_rate"] == 0.002
    assert decision["recommendation"] == "REQUIRES_MANUAL_REVIEW"
    assert decision["dataset_status"] == "NOT_APPROVED"
    assert decision["replay_status"] == "BLOCKED"


def test_governance_decision_rejects_when_no_unknowns_and_rate_exceeds_threshold():
    stats = {
        "unknown_minutes": 0,
        "effective_missing_rate": 0.002,
    }
    decision = governance_decision(stats, [], 0.001)

    assert decision["recommendation"] == "REJECT_DATASET"
    assert decision["dataset_status"] == "REJECTED"


def test_governance_decision_approves_only_below_threshold_without_unknowns():
    stats = {
        "unknown_minutes": 0,
        "effective_missing_rate": 0.0005,
    }
    decision = governance_decision(stats, [], 0.001)

    assert decision["recommendation"] == "APPROVE_DATASET"
    assert decision["dataset_status"] == "APPROVED"
    assert decision["replay_status"] == "READY"
