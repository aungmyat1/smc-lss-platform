from __future__ import annotations

import lzma
import struct
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

from tools.st_c3_acquire_dukascopy_dataset import (
    _aggregate,
    _cache_path,
    _download_hour,
    _load_m1_from_cache,
    _ticks_to_m1,
    acquire_dukascopy_dataset,
)
from tools.st_c3_verify_dukascopy_provider import _parse_bi5_ticks


def _record(ms: int, ask: int, bid: int, volume: float = 1.0) -> bytes:
    return struct.pack(">IIIff", ms, ask, bid, volume, volume)


def _payload_for_hour() -> bytes:
    records = []
    for minute in range(60):
        records.append(_record(minute * 60_000 + 1_000, 110000 + minute, 109990 + minute, 1.0))
        records.append(_record(minute * 60_000 + 2_000, 110010 + minute, 110000 + minute, 2.0))
    return lzma.compress(b"".join(records))


def _manifest(root: Path, *, approved: bool = False) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "DATASET_MANIFEST_ST_C3.yaml").write_text(
        yaml.safe_dump(
            {
                "strategy": "ST-C3",
                "spec_version": "1.0.7",
                "approved": approved,
                "approval_status": "APPROVED" if approved else "NOT_APPROVED",
                "approval_date": "2026-07-30" if approved else "",
                "approved_by": "owner" if approved else "",
                "symbols": ["EURUSD", "GBPUSD"],
                "timeframes": ["H4", "M15", "M3"],
                "coverage": {"from": "2018-01-01", "to": "2024-12-31"},
                "sessions": {
                    "london": {"start": "07:00", "end": "10:00"},
                    "new_york": {"start": "13:00", "end": "16:00"},
                },
                "symbol_metadata": {
                    "EURUSD": {"pip_size": 0.0001, "min_tick": 0.00001, "lot_size": 100000},
                    "GBPUSD": {"pip_size": 0.0001, "min_tick": 0.00001, "lot_size": 100000},
                },
                "files": {
                    "EURUSD_H4.csv": {"sha256": "<hash>"},
                    "EURUSD_M15.csv": {"sha256": "<hash>"},
                    "EURUSD_M3.csv": {"sha256": "<hash>"},
                    "GBPUSD_H4.csv": {"sha256": "<hash>"},
                    "GBPUSD_M15.csv": {"sha256": "<hash>"},
                    "GBPUSD_M3.csv": {"sha256": "<hash>"},
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_dukascopy_acquisition_blocks_immutable_approved_manifest(tmp_path: Path):
    data_dir = tmp_path / "data"
    _manifest(data_dir, approved=True)

    result = acquire_dukascopy_dataset(data_dir, download=True, write_report=False)

    assert result["status"] == "BLOCKED"
    assert "already approved" in result["reason"]


def test_download_hour_uses_non_empty_cache_without_network(tmp_path: Path, monkeypatch):
    hour = datetime(2024, 1, 2, 0, tzinfo=UTC)
    cached = _cache_path(tmp_path, "EURUSD", hour)
    cached.parent.mkdir(parents=True)
    cached.write_bytes(_payload_for_hour())

    def fail_urlopen(*_args, **_kwargs):
        raise AssertionError("network should not be called for cached hours")

    monkeypatch.setattr("urllib.request.urlopen", fail_urlopen)

    result = _download_hour("EURUSD", hour, tmp_path, retries=1)

    assert result["status"] == "CACHED_VERIFIED"
    assert result["bytes"] > 6


def test_ticks_to_m1_and_aggregation_use_complete_windows_only():
    hour = datetime(2024, 1, 2, 0, tzinfo=UTC)
    ticks = _parse_bi5_ticks(_payload_for_hour(), hour, "EURUSD")
    m1 = _ticks_to_m1(ticks)

    m3 = _aggregate(m1, "M3")
    m15 = _aggregate(m1, "M15")

    assert len(m1) == 60
    assert len(m3) == 20
    assert len(m15) == 4
    assert m3[0].timestamp == datetime(2024, 1, 2, 0, 0, tzinfo=UTC)
    assert m3[0].open == 1.0999
    assert m3[0].close == 1.10002
    assert m15[0].high == 1.10014


def test_load_m1_from_cache_keeps_missing_hours_missing(tmp_path: Path):
    hour = datetime(2024, 1, 2, 0, tzinfo=UTC)
    path = _cache_path(tmp_path, "EURUSD", hour)
    path.parent.mkdir(parents=True)
    path.write_bytes(_payload_for_hour())

    m1 = _load_m1_from_cache(
        "EURUSD",
        hour,
        hour + timedelta(hours=1, minutes=59),
        tmp_path,
    )

    assert len(m1) == 60
    assert max(m1) == datetime(2024, 1, 2, 0, 59)
