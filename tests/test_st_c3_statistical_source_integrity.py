from __future__ import annotations

import lzma
import struct
import zipfile
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from tools.st_c3_acquire_dukascopy_dataset import _cache_path
from tools.st_c3_statistical_source_integrity import run_statistical_source_integrity


def _record(ms: int, ask: int, bid: int) -> bytes:
    return struct.pack(">IIIff", ms, ask, bid, 1.0, 1.0)


def _payload(*, missing_minute: int | None = None) -> bytes:
    records = []
    for minute in range(60):
        if minute == missing_minute:
            continue
        records.append(_record(minute * 60_000 + 1_000, 110000 + minute, 109990 + minute))
    return lzma.compress(b"".join(records))


def _write_day(cache: Path, symbol: str, day: date, *, missing_hour: int | None = None, missing_minute: int | None = None) -> None:
    for hour in range(24):
        timestamp = datetime(day.year, day.month, day.day, hour, tzinfo=UTC)
        path = _cache_path(cache, symbol, timestamp)
        path.parent.mkdir(parents=True, exist_ok=True)
        minute = missing_minute if missing_hour == hour else None
        path.write_bytes(_payload(missing_minute=minute))


def _write_day_without_hour(cache: Path, symbol: str, day: date, omitted_hour: int) -> None:
    for hour in range(24):
        if hour == omitted_hour:
            continue
        timestamp = datetime(day.year, day.month, day.day, hour, tzinfo=UTC)
        path = _cache_path(cache, symbol, timestamp)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_payload())


def _write_histdata_zip(cache: Path, symbol: str, year: int, rows: list[str]) -> None:
    path = cache / symbol / f"DAT_ASCII_{symbol}_M1_{year}.zip"
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(f"DAT_ASCII_{symbol}_M1_{year}.csv", "\n".join(rows) + "\n")


def test_statistical_source_integrity_passes_complete_target_sample(tmp_path: Path):
    day = date(2021, 1, 4)
    for symbol in ("EURUSD", "GBPUSD"):
        _write_day(tmp_path, symbol, day)

    result = run_statistical_source_integrity(
        cache_dir=tmp_path,
        start_date=day,
        end_date=day,
        target_sample_days=1,
        write_report=False,
    )

    assert result["status"] == "PASS"
    assert result["details"]["statistically_sufficient"] is True
    assert result["details"]["total_missing_minutes"] == 0
    assert result["details"]["decision_framework"]["status"] == "MISSING_RATE_BELOW_THRESHOLD"
    assert result["details"]["decision_framework"]["recommendation"] == "ACCEPT_DUKASCOPY"
    assert result["details"]["sample_stratification"]["by_weekday"] == {"Monday": 1}
    assert result["details"]["cross_source_comparison"]["observations"] == 0


def test_statistical_source_integrity_blocks_for_missing_minutes(tmp_path: Path):
    day = date(2021, 1, 4)
    reference_cache = tmp_path / "reference"
    _write_day(tmp_path, "EURUSD", day, missing_hour=22, missing_minute=45)
    _write_day(tmp_path, "GBPUSD", day)
    _write_histdata_zip(reference_cache, "EURUSD", 2021, ["20210104 174400;1;1;1;1;0"])

    result = run_statistical_source_integrity(
        cache_dir=tmp_path,
        reference_cache_dir=reference_cache,
        start_date=day,
        end_date=day,
        target_sample_days=1,
        write_report=False,
    )

    eurusd = result["details"]["symbols"][0]
    assert result["status"] == "BLOCKED"
    assert result["details"]["total_missing_minutes"] == 1
    assert eurusd["distribution_by_hour_utc"] == {"22": 1}
    assert eurusd["distribution_by_session"] == {"ROLLOVER": 1}
    assert eurusd["distribution_by_root_cause_category"] == {"ROLLOVER_ZERO_TICK": 1}
    observation = result["details"]["missing_observations"][0]
    assert observation["provider"] == "Dukascopy"
    assert observation["market_open"] is True
    assert observation["previous_minute_tick_count"] == 1
    assert observation["next_minute_tick_count"] == 1
    assert observation["cross_source_reference"] == {
        "checked": True,
        "provider": "HistData.com Generic ASCII M1",
        "present": False,
    }
    assert result["details"]["cross_source_comparison"] == {
        "observations": 1,
        "checked": 1,
        "reference_present": 0,
        "reference_absent": 1,
    }
    assert result["details"]["decision_framework"]["recommendation"] == "OPEN_DATA_GOVERNANCE_REVIEW"
    assert result["details"]["missing_minute_rate_confidence_interval_95"]["upper"] > 0


def test_statistical_source_integrity_marks_insufficient_sample(tmp_path: Path):
    day = date(2021, 1, 4)
    for symbol in ("EURUSD", "GBPUSD"):
        _write_day(tmp_path, symbol, day)

    result = run_statistical_source_integrity(
        cache_dir=tmp_path,
        start_date=day,
        end_date=day + timedelta(days=1),
        target_sample_days=2,
        write_report=False,
    )

    assert result["status"] == "BLOCKED"
    assert result["details"]["sample_days_cached_complete"] == 1
    assert result["details"]["statistically_sufficient"] is False
    assert result["details"]["decision_framework"]["recommendation"] == "CONTINUE_EVIDENCE_COLLECTION"


def test_statistical_source_integrity_excludes_dst_friday_21_provider_close(tmp_path: Path):
    day = date(2021, 4, 16)
    for symbol in ("EURUSD", "GBPUSD"):
        _write_day_without_hour(tmp_path, symbol, day, omitted_hour=21)

    result = run_statistical_source_integrity(
        cache_dir=tmp_path,
        start_date=day,
        end_date=day,
        target_sample_days=1,
        write_report=False,
    )

    assert result["details"]["sample_days_cached_complete"] == 1
    assert result["details"]["source_calendar_exclusions"]["unique_hours"] == ["2021-04-16T21:00:00Z"]
    assert result["details"]["source_calendar_exclusions"]["symbol_hour_count"] == 2
    assert result["details"]["source_calendar_exclusions"]["excluded_expected_minutes"] == 120
    assert result["details"]["total_expected_minutes"] == 2520
