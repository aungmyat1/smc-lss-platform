from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

from tools.st_c3_acquire_dukascopy_dataset import _cache_path
from tools.st_c3_acquire_source_integrity_sample import acquire_source_integrity_sample


def _write_day(cache: Path, symbol: str, day: date) -> None:
    for hour in range(24):
        timestamp = datetime(day.year, day.month, day.day, hour, tzinfo=UTC)
        path = _cache_path(cache, symbol, timestamp)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"cached")


def _write_source_required_day(cache: Path, symbol: str, day: date) -> None:
    for hour in range(24):
        if day.weekday() == 4 and day.month in {4, 5, 6, 7, 8, 9, 10} and hour == 21:
            continue
        timestamp = datetime(day.year, day.month, day.day, hour, tzinfo=UTC)
        path = _cache_path(cache, symbol, timestamp)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"cached")


def test_sample_acquisition_counts_completed_days_without_download(tmp_path: Path):
    day = date(2021, 1, 4)
    _write_day(tmp_path, "EURUSD", day)
    _write_day(tmp_path, "GBPUSD", day)

    result = acquire_source_integrity_sample(
        cache_dir=tmp_path,
        start_date=day,
        end_date=day,
        target_sample_days=1,
        max_days=1,
        write_report=False,
    )

    assert result["status"] == "IN_PROGRESS"
    assert result["details"]["completed_sample_days_before"] == 1
    assert result["details"]["completed_sample_days_after"] == 1
    assert result["details"]["attempted_hours"] == 0


def test_sample_acquisition_downloads_bounded_pending_hours(tmp_path: Path, monkeypatch):
    calls = []

    def fake_download(symbol: str, hour: datetime, cache: Path, *, retries: int):
        calls.append((symbol, hour))
        path = _cache_path(cache, symbol, hour)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"cached")
        return {
            "symbol": symbol,
            "hour_utc": hour.strftime("%Y-%m-%dT%H:00:00Z"),
            "status": "DOWNLOADED",
            "reason": "downloaded",
        }

    monkeypatch.setattr("tools.st_c3_acquire_source_integrity_sample._download_hour", fake_download)

    result = acquire_source_integrity_sample(
        cache_dir=tmp_path,
        start_date=date(2021, 1, 4),
        end_date=date(2021, 1, 5),
        target_sample_days=2,
        max_hours=4,
        write_report=False,
    )

    assert result["status"] == "IN_PROGRESS"
    assert result["details"]["attempted_hours"] == 4
    assert len(calls) == 4
    assert result["details"]["execution"]["mode"] == "sequential"


def test_sample_acquisition_blocks_on_failed_download(tmp_path: Path, monkeypatch):
    def fake_download(symbol: str, hour: datetime, cache: Path, *, retries: int):
        return {
            "symbol": symbol,
            "hour_utc": hour.strftime("%Y-%m-%dT%H:00:00Z"),
            "status": "FAILED",
            "reason": "network",
        }

    monkeypatch.setattr("tools.st_c3_acquire_source_integrity_sample._download_hour", fake_download)

    result = acquire_source_integrity_sample(
        cache_dir=tmp_path,
        start_date=date(2021, 1, 4),
        end_date=date(2021, 1, 4),
        target_sample_days=1,
        max_hours=1,
        write_report=False,
    )

    assert result["status"] == "BLOCKED"
    assert "failed" in result["reason"]


def test_sample_acquisition_counts_dst_friday_21_as_provider_excluded(tmp_path: Path):
    day = date(2021, 4, 16)
    _write_source_required_day(tmp_path, "EURUSD", day)
    _write_source_required_day(tmp_path, "GBPUSD", day)

    result = acquire_source_integrity_sample(
        cache_dir=tmp_path,
        start_date=day,
        end_date=day,
        target_sample_days=1,
        max_days=1,
        write_report=False,
    )

    assert result["details"]["completed_sample_days_before"] == 1
    assert result["details"]["provider_calendar_exclusions"]["symbol_hour_count"] == 0
    assert result["details"]["attempted_hours"] == 0


def test_parallel_sample_acquisition_uses_deterministic_non_overlapping_tasks(tmp_path: Path, monkeypatch):
    calls = []

    def fake_download(symbol: str, hour: datetime, cache: Path, *, retries: int):
        calls.append((symbol, hour))
        path = _cache_path(cache, symbol, hour)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"cached")
        return {
            "symbol": symbol,
            "hour_utc": hour.strftime("%Y-%m-%dT%H:00:00Z"),
            "status": "DOWNLOADED",
            "reason": "downloaded",
        }

    monkeypatch.setattr("tools.st_c3_acquire_source_integrity_sample._download_hour", fake_download)

    result = acquire_source_integrity_sample(
        cache_dir=tmp_path,
        start_date=date(2021, 1, 4),
        end_date=date(2021, 1, 4),
        target_sample_days=1,
        max_hours=8,
        workers=4,
        write_report=False,
    )

    parallel = result["details"]["parallel_execution"]
    assert result["details"]["execution"]["mode"] == "parallel"
    assert parallel["workers"] == 4
    assert parallel["planned_tasks"] == 8
    assert parallel["duplicate_task_count"] == 0
    assert parallel["planned_by_worker"] == {"1": 2, "2": 2, "3": 2, "4": 2}
    assert len(set(calls)) == 8


def test_parallel_and_sequential_preserve_task_order(tmp_path: Path, monkeypatch):
    def fake_download(symbol: str, hour: datetime, cache: Path, *, retries: int):
        path = _cache_path(cache, symbol, hour)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"cached")
        return {
            "symbol": symbol,
            "hour_utc": hour.strftime("%Y-%m-%dT%H:00:00Z"),
            "status": "DOWNLOADED",
            "reason": "downloaded",
        }

    monkeypatch.setattr("tools.st_c3_acquire_source_integrity_sample._download_hour", fake_download)

    sequential = acquire_source_integrity_sample(
        cache_dir=tmp_path / "seq",
        start_date=date(2021, 1, 4),
        end_date=date(2021, 1, 4),
        target_sample_days=1,
        max_hours=6,
        workers=1,
        write_report=False,
    )
    parallel = acquire_source_integrity_sample(
        cache_dir=tmp_path / "par",
        start_date=date(2021, 1, 4),
        end_date=date(2021, 1, 4),
        target_sample_days=1,
        max_hours=6,
        workers=3,
        write_report=False,
    )

    seq_order = sequential["details"]["parallel_execution"]["completed_task_order"]
    par_order = parallel["details"]["parallel_execution"]["completed_task_order"]
    assert seq_order == par_order
    assert sequential["details"]["parallel_execution"]["task_order_matches_plan"] is True
    assert parallel["details"]["parallel_execution"]["task_order_matches_plan"] is True
    assert sequential["details"]["attempted_hours"] == parallel["details"]["attempted_hours"] == 6
