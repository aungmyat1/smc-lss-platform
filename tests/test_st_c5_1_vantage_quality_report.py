from __future__ import annotations

import csv

import yaml

from tools.st_c5_1_vantage_quality_report import (
    build_data_inventory,
    build_normalization_report,
    generate_vantage_quality_report,
    governance_decision,
)


def _write_candidate_file(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time", "open", "high", "low", "close", "volume", "session", "news_flag"])
        writer.writerows(rows)


def test_inventory_reports_files_checksums_and_missing_files(tmp_path):
    _write_candidate_file(
        tmp_path / "EURUSD_M15.csv",
        [["2025-01-02T07:00:00Z", 1, 1, 1, 1, 10, "LONDON", "false"]],
    )

    inventory = build_data_inventory(tmp_path)

    assert inventory["symbols"] == ["EURUSD"]
    assert inventory["timeframes"] == ["M15"]
    assert inventory["files"][0]["checksum_sha256"]
    assert "GBPUSD_M15.csv" in inventory["missing_files"]


def test_normalization_detects_duplicates(tmp_path):
    _write_candidate_file(
        tmp_path / "EURUSD_M15.csv",
        [
            ["2025-01-02T07:00:00Z", 1, 1, 1, 1, 10, "LONDON", "false"],
            ["2025-01-02T07:00:00Z", 1, 1, 1, 1, 10, "LONDON", "false"],
        ],
    )

    report = build_normalization_report(tmp_path)

    eurusd = [item for item in report["files"] if item["file"] == "EURUSD_M15.csv"][0]
    assert report["status"] == "FAIL"
    assert eurusd["duplicates"] == 1


def test_governance_rejects_blocked_integrity():
    decision = governance_decision(
        {"missing_files": []},
        {"status": "PASS"},
        {"status": "BLOCKED"},
    )

    assert decision["decision"] == "REJECT_DATASET"
    assert decision["replay_status"] == "BLOCKED"


def test_quality_report_writes_required_artifacts(tmp_path):
    manifest = {
        "dataset_version": "fixture",
        "provider": "Vantage MT5",
        "coverage": {"from": "2025-01-02", "to": "2025-01-02"},
        "symbols": ["EURUSD", "GBPUSD"],
        "timeframes": ["H4", "M15", "M3"],
        "files": {name: {"sha256": "<pending>"} for name in ["EURUSD_H4.csv", "EURUSD_M15.csv", "EURUSD_M3.csv", "GBPUSD_H4.csv", "GBPUSD_M15.csv", "GBPUSD_M3.csv"]},
    }
    (tmp_path / "DATASET_MANIFEST_ST_C3.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")

    result = generate_vantage_quality_report(candidate_dir=tmp_path, report_dir=tmp_path / "reports")

    assert result["decision"]["decision"] == "REJECT_DATASET"
    assert (tmp_path / "reports/data_inventory.json").exists()
    assert (tmp_path / "reports/VANTAGE_DATA_QUALITY_REPORT.md").exists()
    assert (tmp_path / "reports/DATASET_GOVERNANCE_DECISION.json").exists()
    assert (tmp_path / "reports/dataset_manifest.json").exists()
    assert (tmp_path / "reports/normalization_report.md").exists()
