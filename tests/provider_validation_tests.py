from __future__ import annotations

import csv
import json
import zipfile

from tools.st_c4_provider_benchmark import (
    BENCHMARK_XLSX,
    ProviderCandidate,
    quality_score,
    readiness_decision,
    run_st_c4_benchmark,
)


def test_quality_score_uses_weighted_metrics():
    candidate = ProviderCandidate(
        provider="Example",
        status="TEST",
        historical_coverage="full",
        timestamp_precision="minute",
        timezone_policy="UTC",
        sample_status="VALIDATED_SAMPLE_PASS",
        missing_rate=0.0,
        duplicate_rate=0.0,
        longest_gap_minutes=0,
        unexpected_gap_pct=0.0,
        historical_completeness=100,
        continuity=80,
        timestamp_accuracy=60,
        automation=40,
        documentation=20,
        cost=10,
        licensing=0,
        evidence="fixture",
        blocker="none",
        source_url="fixture",
    )

    assert quality_score(candidate) == 67.5


def test_readiness_requires_passing_sample_score_and_missing_rate():
    rows = [
        {"sample_status": "VALIDATED_SAMPLE_PASS", "missing_rate": 0.0005, "quality_score": 80.0},
        {"sample_status": "VALIDATED_SAMPLE_FAIL", "missing_rate": 0.0, "quality_score": 100.0},
    ]

    assert readiness_decision(rows) == "READY_FOR_ST_C3"

    rows[0]["missing_rate"] = 0.002
    assert readiness_decision(rows) == "NOT_READY_FOR_ST_C3"


def test_benchmark_generation_creates_required_artifacts(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = run_st_c4_benchmark()

    assert result["recommendation"] == "NOT_READY_FOR_ST_C3"
    assert (tmp_path / "docs/data/CANONICAL_DATA_SPECIFICATION.md").exists()
    assert (tmp_path / "reports/st_c4/provider_benchmark.csv").exists()
    assert (tmp_path / "reports/st_c4/provider_benchmark.xlsx").exists()
    assert (tmp_path / "reports/st_c4/provider_benchmark_matrix.xlsx").exists()
    assert (tmp_path / "reports/st_c4/provider_benchmark.md").exists()
    assert (tmp_path / "reports/st_c4/provider_quality_statistics.json").exists()
    assert (tmp_path / "reports/st_c4/DATASET_BUILD_REPORT.md").exists()
    assert (tmp_path / "reports/st_c4/ST_C3_READINESS_REPORT.md").exists()
    assert (tmp_path / "reports/st_c4/CANONICAL_PROVIDER_SELECTION.md").exists()
    assert (tmp_path / "research_data/raw/dukascopy/.gitkeep").exists()
    assert (tmp_path / "research_data/metadata/ST_C4_SAMPLE_INDEX.json").exists()

    with (tmp_path / "reports/st_c4/provider_benchmark.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert {row["provider"] for row in rows} >= {"Dukascopy", "HistData", "TrueFX", "Tiingo FX"}

    quality = json.loads((tmp_path / "reports/st_c4/provider_quality_statistics.json").read_text(encoding="utf-8"))
    assert quality["readiness"] == "NOT_READY_FOR_ST_C3"

    with zipfile.ZipFile(tmp_path / BENCHMARK_XLSX) as archive:
        assert "xl/worksheets/sheet1.xml" in archive.namelist()
