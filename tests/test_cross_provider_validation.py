from __future__ import annotations

import csv
import json

from tools.st_c4_1_provider_qualification import run_provider_qualification


def test_provider_qualification_outputs_cross_provider_evidence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "providers").mkdir()
    (tmp_path / "providers/provider_registry.yaml").write_text(
        """
schema_version: "st-c4.1-provider-registry-v1"
guardrail: test
providers:
  dukascopy: {status: rejected, license: review, api: public, cost: free, symbols: [EURUSD], timeframes: [tick], evaluation_status: evaluated_failed}
  truefx: {status: blocked, license: required, api: account, cost: subscription, symbols: [EURUSD], timeframes: [tick], evaluation_status: not_evaluated}
  tiingo: {status: blocked, license: required, api: rest, cost: subscription, symbols: [EURUSD], timeframes: [bars], evaluation_status: not_evaluated}
  histdata: {status: rejected, license: review, api: web, cost: free, symbols: [EURUSD], timeframes: [M1], evaluation_status: evaluated_failed}
  darwinex: {status: blocked, license: required, api: ftp, cost: account, symbols: [EURUSD], timeframes: [tick], evaluation_status: not_evaluated}
  mt5: {status: blocked, license: required, api: terminal, cost: broker, symbols: [EURUSD], timeframes: [M15], evaluation_status: not_evaluated}
""",
        encoding="utf-8",
    )

    result = run_provider_qualification()

    assert result["recommendation"] == "NO_CANONICAL_PROVIDER"
    matrix = tmp_path / "reports/st_c4_1/provider_qualification_matrix.csv"
    cross = tmp_path / "reports/st_c4_1/cross_provider_gap_analysis.csv"
    decision = json.loads((tmp_path / "reports/st_c4_1/provider_quality_metrics.json").read_text(encoding="utf-8"))
    assert matrix.exists()
    assert cross.exists()
    assert "dukascopy" in decision
    with cross.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert rows[0]["gap_scope"].startswith("ST-C3 rejected")
