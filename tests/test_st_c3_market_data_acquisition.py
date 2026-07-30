from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import zipfile

import yaml

from tools.st_c3_acquire_histdata_dataset import Candle, _read_histdata_zip, _resample, acquire_histdata_dataset
from validation.st_c3.dataset_loader import EXPECTED_SYMBOLS, EXPECTED_TIMEFRAMES, MANIFEST_NAME


def _write_manifest(root: Path, *, approved: bool) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / MANIFEST_NAME).write_text(
        yaml.safe_dump(
            {
                "strategy": "ST-C3",
                "spec_version": "1.0.7",
                "approved": approved,
                "approval_status": "APPROVED" if approved else "NOT_APPROVED",
                "symbols": sorted(EXPECTED_SYMBOLS),
                "timeframes": sorted(EXPECTED_TIMEFRAMES),
                "coverage": {"from": "2018-01-01", "to": "2024-12-31"},
                "files": {
                    f"{symbol}_{timeframe}.csv": {"sha256": "<hash>"}
                    for symbol in sorted(EXPECTED_SYMBOLS)
                    for timeframe in sorted(EXPECTED_TIMEFRAMES)
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_histdata_resample_builds_closed_m3_candle_only():
    source = [
        Candle(datetime(2024, 1, 2, 0, 0) + timedelta(minutes=i), 1.0 + i, 1.2 + i, 0.9 + i, 1.1 + i, 10)
        for i in range(4)
    ]

    candles = _resample(source, "M3")

    assert len(candles) == 1
    assert candles[0].timestamp == datetime(2024, 1, 2, 0, 0)
    assert candles[0].open == 1.0
    assert candles[0].high == 3.2
    assert candles[0].low == 0.9
    assert candles[0].close == 3.1
    assert candles[0].volume == 30


def test_histdata_reader_converts_est_no_dst_to_utc(tmp_path):
    zip_path = tmp_path / "DAT_ASCII_EURUSD_M1_2018.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("DAT_ASCII_EURUSD_M1_2018.csv", "20180101 000000;1.0;1.1;0.9;1.0;0\n")

    candles = list(_read_histdata_zip(zip_path))

    assert candles[0].timestamp == datetime(2018, 1, 1, 5, 0)


def test_histdata_acquisition_refuses_approved_manifest(tmp_path):
    data_dir = tmp_path / "data"
    _write_manifest(data_dir, approved=True)

    result = acquire_histdata_dataset(data_dir, write_files=True)

    assert result["status"] == "BLOCKED"
    assert "immutable" in result["reason"]


def test_histdata_acquisition_dry_run_blocks_before_download(tmp_path):
    data_dir = tmp_path / "data"
    _write_manifest(data_dir, approved=False)

    result = acquire_histdata_dataset(data_dir, write_files=False)

    assert result["status"] == "BLOCKED"
    assert "dry run" in result["reason"]
    assert result["details"]["recommended_source"] == "HistData.com Generic ASCII M1"
