from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import yaml

from tools import st_c3_download_mt5_dataset
from tools.st_c3_dataset_contract import validate_dataset_contract
from tools.st_c3_download_mt5_dataset import Candle, download_st_c3_mt5_dataset
from validation.st_c3 import dataset_loader


def _write_manifest(root: Path, *, approved: bool) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / dataset_loader.MANIFEST_NAME).write_text(
        yaml.safe_dump(
            {
                "strategy": "ST-C3",
                "spec_version": "1.0.7",
                "approved": approved,
                "approval_status": "APPROVED" if approved else "NOT_APPROVED",
                "symbols": sorted(dataset_loader.EXPECTED_SYMBOLS),
                "timeframes": sorted(dataset_loader.EXPECTED_TIMEFRAMES),
                "coverage": {"from": "2018-01-01", "to": "2024-12-31"},
                "files": {
                    f"{symbol}_{timeframe}.csv": {"sha256": "<hash>"}
                    for symbol in sorted(dataset_loader.EXPECTED_SYMBOLS)
                    for timeframe in sorted(dataset_loader.EXPECTED_TIMEFRAMES)
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_contract_rejects_manifest_approval_when_contract_is_blocked(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    _write_manifest(data_dir, approved=True)
    contract = tmp_path / "DATASET_CONTRACT.yaml"
    contract.write_text(
        yaml.safe_dump(
            {
                "contract_id": "ST-C3-DATASET-CONTRACT",
                "contract_version": "test",
                "strategy": "ST-C3",
                "spec_version": "1.0.7",
                "status": "BLOCKED",
                "approval_status": "NOT_APPROVED",
                "approved_scope": {},
                "expected_files": {},
                "approval_gate": {"replay_prohibited_unless_approved": True},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr("tools.st_c3_dataset_contract.inspect_dataset", lambda _data_dir: [])

    result = validate_dataset_contract(contract, data_dir)

    assert result["status"] == "REJECTED"
    assert result["reason"] == "manifest claims approval while dataset contract is not approved"


def test_mt5_downloader_allows_unapproved_candidate_manifest(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    _write_manifest(data_dir, approved=False)
    fake_mt5 = SimpleNamespace(
        initialize=lambda: True,
        shutdown=lambda: None,
        symbol_select=lambda symbol, enabled: True,
        last_error=lambda: "no error",
    )
    monkeypatch.setitem(sys.modules, "MetaTrader5", fake_mt5)
    monkeypatch.setattr(
        st_c3_download_mt5_dataset,
        "_copy_candles",
        lambda mt5, symbol, timeframe, start, end: [
            Candle(
                timestamp=datetime(2018, 1, 1, 0, 0),
                open=1.0,
                high=1.1,
                low=0.9,
                close=1.05,
                volume=10,
            )
        ],
    )
    monkeypatch.setattr(
        st_c3_download_mt5_dataset,
        "prepare_dataset_manifest",
        lambda root, write: {"status": "PASS", "files": [], "guardrail": "test"},
    )

    result = download_st_c3_mt5_dataset(data_dir)

    assert result["status"] == "PASS"
    assert (data_dir / "EURUSD_H4.csv").exists()
