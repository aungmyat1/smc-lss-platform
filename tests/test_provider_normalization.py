from __future__ import annotations

from providers.common.normalization import normalize_rows, validate_normalized_rows


def test_normalization_adds_canonical_schema_and_session():
    rows = [
        {
            "timestamp": "2025-01-02T07:01:00Z",
            "symbol": "EURUSD",
            "open": "1.1",
            "high": "1.2",
            "low": "1.0",
            "close": "1.15",
            "volume": "10",
            "spread": "",
        }
    ]

    normalized = normalize_rows(rows, provider="Fixture")

    assert normalized[0].provider == "Fixture"
    assert normalized[0].tick_volume == 10
    assert normalized[0].session == "LONDON"
    assert normalized[0].schema_version == "st-c4.1-normalized-v1"
    assert validate_normalized_rows(normalized)["status"] == "PASS"


def test_validation_detects_duplicate_bars():
    rows = normalize_rows(
        [
            {"timestamp": "2025-01-02T07:01:00Z", "symbol": "EURUSD", "open": 1, "high": 1, "low": 1, "close": 1},
            {"timestamp": "2025-01-02T07:01:00Z", "symbol": "EURUSD", "open": 1, "high": 1, "low": 1, "close": 1},
        ],
        provider="Fixture",
    )

    assert validate_normalized_rows(rows)["duplicates"] == 1
