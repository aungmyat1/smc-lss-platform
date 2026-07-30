from __future__ import annotations

import lzma
import struct
from datetime import UTC, datetime
from pathlib import Path

from tools.st_c3_acquire_dukascopy_dataset import _cache_path
from tools.st_c3_validate_aggregation import validate_aggregation


def _record(ms: int, ask: int, bid: int) -> bytes:
    return struct.pack(">IIIff", ms, ask, bid, 1.0, 1.0)


def _payload(*, missing_minute: int | None = None) -> bytes:
    records = []
    for minute in range(60):
        if minute == missing_minute:
            continue
        records.append(_record(minute * 60_000 + 1_000, 110000 + minute, 109990 + minute))
        records.append(_record(minute * 60_000 + 2_000, 110010 + minute, 110000 + minute))
    return lzma.compress(b"".join(records))


def _write_hour(cache: Path, symbol: str, hour: datetime, *, missing_minute: int | None = None) -> None:
    path = _cache_path(cache, symbol, hour)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_payload(missing_minute=missing_minute))


def test_aggregation_validation_passes_complete_hour(tmp_path: Path):
    hour = datetime(2021, 1, 4, 0, tzinfo=UTC)
    _write_hour(tmp_path, "EURUSD", hour)
    _write_hour(tmp_path, "GBPUSD", hour)

    result = validate_aggregation(
        cache_dir=tmp_path,
        start=hour,
        end=datetime(2021, 1, 4, 0, 59, 59, tzinfo=UTC),
        write_report=False,
    )

    assert result["status"] == "PASS"
    eurusd = result["details"]["symbols"][0]
    assert eurusd["missing_m1_count"] == 0
    assert {item["timeframe"]: item["mismatch_count"] for item in eurusd["timeframes"]} == {
        "H4": 0,
        "M15": 0,
        "M3": 0,
    }


def test_aggregation_validation_identifies_sparse_source_minute(tmp_path: Path):
    hour = datetime(2021, 1, 4, 22, tzinfo=UTC)
    _write_hour(tmp_path, "EURUSD", hour, missing_minute=45)
    _write_hour(tmp_path, "GBPUSD", hour)

    result = validate_aggregation(
        cache_dir=tmp_path,
        start=hour,
        end=datetime(2021, 1, 4, 22, 59, 59, tzinfo=UTC),
        write_report=False,
    )

    assert result["status"] == "BLOCKED"
    assert result["reason"] == "EURUSD missing M1 source candle 2021-01-04T22:45:00Z"
    eurusd = result["details"]["symbols"][0]
    assert eurusd["source_hours"][0]["status"] == "SPARSE_TICKS"
    assert eurusd["timeframes"][1]["first_missing"] == "2021-01-04T22:45:00Z"
