"""Tests for the ST-C1 contract validation scaffold."""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from validation.strategy_contract_validator import (  # noqa: E402
    load_contract,
    validate_contract,
    validate_contract_file,
    write_validation_report,
)


CONTRACT_PATH = os.path.join(ROOT, "strategies", "candidates", "ST-C1_v1.yaml")


def _load_repo_contract() -> dict:
    return load_contract(CONTRACT_PATH)


def test_repo_contract_is_ready_for_backtest(tmp_path):
    result = validate_contract_file(CONTRACT_PATH, report_path=str(tmp_path / "report.md"))
    assert result.ok is True
    assert result.status == "READY_FOR_BACKTEST"
    assert result.issues == ()


def test_validation_report_is_written(tmp_path):
    result = validate_contract_file(CONTRACT_PATH, report_path=str(tmp_path / "report.md"))
    report = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "READY_FOR_BACKTEST" in report
    assert result.status in report


def test_missing_strategy_id_is_blocked():
    contract = _load_repo_contract()
    del contract["strategy"]["strategy_id"]
    result = validate_contract(contract)
    assert result.status == "BLOCKED"
    assert any(issue.path == "strategy.strategy_id" for issue in result.issues)


def test_wrong_status_is_blocked():
    contract = _load_repo_contract()
    contract["strategy"]["status"] = "approved"
    result = validate_contract(contract)
    assert result.status == "BLOCKED"
    assert any(issue.path == "strategy.status" for issue in result.issues)


def test_missing_market_timeframes_is_blocked():
    contract = _load_repo_contract()
    del contract["market_universe"]["timeframes"]
    result = validate_contract(contract)
    assert result.status == "BLOCKED"
    assert any(issue.path == "market_universe.timeframes" for issue in result.issues)


def test_missing_entry_invalidation_is_blocked():
    contract = _load_repo_contract()
    del contract["entry_model"]["long"]["invalidation"]
    result = validate_contract(contract)
    assert result.status == "BLOCKED"
    assert any(issue.path == "entry_model.long.invalidation" for issue in result.issues)


def test_missing_risk_requirement_is_blocked():
    contract = _load_repo_contract()
    del contract["risk_contract"]["minimum_rr"]
    result = validate_contract(contract)
    assert result.status == "BLOCKED"
    assert any(issue.path == "risk_contract.minimum_rr" for issue in result.issues)


def test_subjective_language_scan_blocks_obvious_terms():
    contract = _load_repo_contract()
    contract["poi"]["order_block"]["trade_action"] = "use a strong setup"
    contract["machine_validation"]["no_subjective_language"] = True
    result = validate_contract(contract)
    assert result.status == "BLOCKED"
    assert any(issue.code == "SUBJECTIVE_LANGUAGE" for issue in result.issues)


def test_report_writer_includes_all_issues(tmp_path):
    contract = _load_repo_contract()
    contract["strategy"]["version"] = ""
    result = validate_contract(contract)
    path = write_validation_report(result, path=str(tmp_path / "report.md"))
    assert os.path.exists(path)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    assert "BLOCKED" in text
    assert "strategy.version" in text
