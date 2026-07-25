from __future__ import annotations

import json
from pathlib import Path

import yaml

from validation.st_c2.traceability import load_contract, validate_contract_traceability


def test_st_c2_contract_traceability_matches_a2_inventory():
    result = validate_contract_traceability()
    assert result.valid, result.errors
    assert result.incomplete_rules


def test_st_c2_contract_declares_a2_not_complete_until_gaps_close():
    result = validate_contract_traceability()
    contract = load_contract()
    assert contract["strategy"]["conformance_stage"] == "A2"
    assert "A2 closes only when every contract rule" in contract["strategy"]["completion_policy"]
    assert set(result.incomplete_rules) == {
        rule_id
        for rule_id, entry in contract["traceability"].items()
        if entry["conformance_status"] != "implemented_tested"
    }


def test_contract_rules_match_coverage_rules_exactly():
    contract = load_contract()
    coverage = json.loads(Path("reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json").read_text(encoding="utf-8"))
    assert set(contract["traceability"]) == {item["id"] for item in coverage["inventory"]}


def test_contract_stage_rule_ids_are_unique_and_traceable():
    contract = load_contract()
    assigned = []
    for stage in contract["funnel_stages"]:
        assigned.extend(stage["deterministic_rules"])
    assert len(assigned) == len(set(assigned))
    assert set(assigned) == set(contract["traceability"])


def test_contract_output_shape_is_explicit_for_every_stage():
    contract = load_contract()
    for stage in contract["funnel_stages"]:
        assert stage["required_inputs"], stage["key"]
        assert stage["required_outputs"], stage["key"]
        assert all(isinstance(output, str) and output for output in stage["required_outputs"])
    assert "trade_plan_id" in contract["funnel_stages"][-1]["required_outputs"]


def test_contract_failure_codes_cover_frozen_rejection_codes():
    contract = load_contract()
    spec = yaml.safe_load(Path("specs/st-c2_v1.2.0.yaml").read_text(encoding="utf-8"))
    stage_failure_codes = {
        code
        for stage in contract["funnel_stages"]
        for code in stage["failure_codes"]
    }
    assert set(spec["rejection_codes"]) <= stage_failure_codes
    for stage in contract["funnel_stages"]:
        assert stage["failure_codes"], stage["key"]


def test_contract_guardrail_detects_rule_id_drift(tmp_path):
    contract = load_contract()
    contract["traceability"].pop("STC2-BIAS-001")
    bad_contract = tmp_path / "bad_contract.yaml"
    bad_contract.write_text(yaml.safe_dump(contract), encoding="utf-8")
    result = validate_contract_traceability(contract_path=bad_contract)
    assert not result.valid
    assert "STC2-BIAS-001: coverage rule missing from contract" in result.errors


def test_contract_guardrail_detects_missing_test_for_complete_rule(tmp_path):
    contract = load_contract()
    contract["traceability"]["STC2-BIAS-001"]["tests"] = []
    bad_contract = tmp_path / "bad_contract.yaml"
    bad_contract.write_text(yaml.safe_dump(contract), encoding="utf-8")
    result = validate_contract_traceability(contract_path=bad_contract)
    assert not result.valid
    assert "STC2-BIAS-001: complete rule lacks tests" in result.errors


def test_contract_guardrail_detects_missing_validation_metric(tmp_path):
    contract = load_contract()
    contract["traceability"]["STC2-BIAS-001"]["validation_metric"] = ""
    bad_contract = tmp_path / "bad_contract.yaml"
    bad_contract.write_text(yaml.safe_dump(contract), encoding="utf-8")
    result = validate_contract_traceability(contract_path=bad_contract)
    assert not result.valid
    assert "STC2-BIAS-001: missing validation metric" in result.errors
