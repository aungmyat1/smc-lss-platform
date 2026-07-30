from __future__ import annotations

import lzma
import struct
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


def test_statistical_source_integrity_blocks_for_missing_minutes(tmp_path: Path):
    day = date(2021, 1, 4)
    _write_day(tmp_path, "EURUSD", day, missing_hour=22, missing_minute=45)
    _write_day(tmp_path, "GBPUSD", day)

    result = run_statistical_source_integrity(
        cache_dir=tmp_path,
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
