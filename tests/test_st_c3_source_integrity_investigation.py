from __future__ import annotations

import lzma
import struct
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from tools.st_c3_acquire_dukascopy_dataset import _cache_path
from tools.st_c3_investigate_source_integrity import Probe, investigate_source_integrity


def _record(ms: int, ask: int, bid: int) -> bytes:
    return struct.pack(">IIIff", ms, ask, bid, 1.0, 1.0)


def _write_dukascopy_hour(cache: Path, symbol: str, hour: datetime, *, missing_minute: int) -> None:
    records = []
    for minute in range(60):
        if minute == missing_minute:
            continue
        records.append(_record(minute * 60_000 + 1_000, 110000 + minute, 109990 + minute))
    path = _cache_path(cache, symbol, hour)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(lzma.compress(b"".join(records)))


def _write_histdata_zip(cache: Path, symbol: str, *, include_minute: bool) -> None:
    path = cache / symbol / "DAT_ASCII_EURUSD_M1_2021.zip"
    if symbol == "GBPUSD":
        path = cache / symbol / "DAT_ASCII_GBPUSD_M1_2021.zip"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["20210104 174400;1.10000;1.10010;1.09990;1.10005;1\n"]
    if include_minute:
        lines.append("20210104 174500;1.10001;1.10011;1.09991;1.10006;1\n")
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(f"DAT_ASCII_{symbol}_M1_2021.csv", "".join(lines))


def test_source_integrity_identifies_reference_absent_sparse_minute(tmp_path: Path):
    probe = Probe("EURUSD", datetime(2021, 1, 4, 22, 45, tzinfo=UTC))
    _write_dukascopy_hour(tmp_path / "dukas", "EURUSD", datetime(2021, 1, 4, 22, tzinfo=UTC), missing_minute=45)
    _write_histdata_zip(tmp_path / "hist", "EURUSD", include_minute=False)

    result = investigate_source_integrity(
        probes=[probe],
        dukascopy_cache=tmp_path / "dukas",
        histdata_cache=tmp_path / "hist",
        fresh_download=False,
        write_report=False,
    )

    assert result["status"] == "BLOCKED"
    assert result["details"]["parser_audit"] == "PASS"
    assert result["details"]["cross_source_reference"] == "ABSENT"
    assert result["details"]["probes"][0]["verdict"] == "DUKASCOPY_AND_REFERENCE_ABSENT"


def test_source_integrity_flags_reference_bar_when_present(tmp_path: Path):
    probe = Probe("EURUSD", datetime(2021, 1, 4, 22, 45, tzinfo=UTC))
    _write_dukascopy_hour(tmp_path / "dukas", "EURUSD", datetime(2021, 1, 4, 22, tzinfo=UTC), missing_minute=45)
    _write_histdata_zip(tmp_path / "hist", "EURUSD", include_minute=True)

    result = investigate_source_integrity(
        probes=[probe],
        dukascopy_cache=tmp_path / "dukas",
        histdata_cache=tmp_path / "hist",
        fresh_download=False,
        write_report=False,
    )

    assert result["details"]["cross_source_reference"] == "PRESENT"
    assert result["details"]["probes"][0]["verdict"] == "REFERENCE_HAS_MINUTE_DUKASCOPY_SPARSE"
