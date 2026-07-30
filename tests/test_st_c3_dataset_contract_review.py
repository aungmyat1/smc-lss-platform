from __future__ import annotations

import json
from pathlib import Path

import yaml

from tools.st_c3_dataset_contract_review import review_dataset_contract


def _contract(path: Path) -> None:
    path.write_text(
        yaml.safe_dump(
            {
                "dataset_version": "Dataset_v1.0_5Y",
                "approval_status": "NOT_APPROVED",
                "replay_status": "BLOCKED",
                "checks": {"missing_timestamps": "required"},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def _source_report(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "details": {
                    "probes": [
                        {
                            "symbol": "EURUSD",
                            "timestamp_utc": "2021-01-04T22:45:00Z",
                            "verdict": "DUKASCOPY_AND_REFERENCE_ABSENT",
                            "dukascopy_fresh": {"status": "MATCHED_CACHE"},
                            "histdata_reference": {"present": False},
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )


def _aggregation_report(path: Path, *, mismatches: int = 0) -> None:
    path.write_text(
        json.dumps(
            {
                "details": {
                    "symbols": [
                        {
                            "symbol": "EURUSD",
                            "timeframes": [{"timeframe": "M15", "mismatch_count": mismatches}],
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )


def test_dataset_contract_review_blocks_strict_contract_with_zero_tick_evidence(tmp_path: Path):
    contract = tmp_path / "contract.yaml"
    source = tmp_path / "source.json"
    aggregation = tmp_path / "aggregation.json"
    _contract(contract)
    _source_report(source)
    _aggregation_report(aggregation)

    result = review_dataset_contract(
        contract_path=contract,
        source_report_path=source,
        aggregation_report_path=aggregation,
        write_report=False,
    )

    assert result["status"] == "BLOCKED"
    assert result["recommendation"] == "OPEN_GOVERNANCE_CHANGE_REQUEST"
    assert result["details"]["missing_timestamps_check"] == "required"
    assert result["details"]["zero_tick_probe_count"] == 1


def test_dataset_contract_review_prioritizes_aggregation_mismatches(tmp_path: Path):
    contract = tmp_path / "contract.yaml"
    source = tmp_path / "source.json"
    aggregation = tmp_path / "aggregation.json"
    _contract(contract)
    _source_report(source)
    _aggregation_report(aggregation, mismatches=1)

    result = review_dataset_contract(
        contract_path=contract,
        source_report_path=source,
        aggregation_report_path=aggregation,
        write_report=False,
    )

    assert "aggregation mismatches remain" in result["reason"]
    assert result["details"]["aggregation_mismatch_count"] == 1
