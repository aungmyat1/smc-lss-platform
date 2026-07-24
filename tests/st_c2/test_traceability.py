import json
from pathlib import Path

import yaml

from validation.st_c2.traceability import validate_traceability


def test_traceability_current_inventory_reports_missing_mappings_honestly():
    result = validate_traceability()
    assert result.valid
    assert result.missing_mappings == 20


def test_coverage_inventory_has_structured_provenance():
    coverage_data = json.loads(Path("reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json").read_text(encoding="utf-8"))
    required = {"module", "module_version", "source", "validated_by", "last_update"}
    gc2_rules = {
        "STC2-STRUCT-001",
        "STC2-STRUCT-004",
        "STC2-STRUCT-005",
        "STC2-BIAS-001",
        "STC2-BIAS-002",
        "STC2-BIAS-003",
        "STC2-BIAS-004",
        "STC2-BIAS-005",
        "STC2-LIQ-003",
        "STC2-LIQ-004",
        "STC2-LIQ-007",
        "STC2-OTE-001",
        "STC2-OTE-002",
        "STC2-OTE-003",
    }
    gc3_rules = {
        "STC2-FVG-001",
        "STC2-FVG-002",
        "STC2-FVG-003",
        "STC2-FVG-004",
        "STC2-FVG-005",
        "STC2-FVG-006",
        "STC2-LTF-001",
        "STC2-LTF-002",
        "STC2-LTF-003",
        "STC2-LTF-004",
    }
    for item in coverage_data["inventory"]:
        provenance = item.get("provenance")
        assert isinstance(provenance, dict)
        assert required <= set(provenance)
        assert isinstance(provenance["validated_by"], list)
        assert provenance["module_version"] == "v1.0.0"
        assert provenance["last_update"] == "2026-07-24"
        assert "traceability_map" in provenance["validated_by"]
        if item["id"] in gc2_rules:
            assert provenance["module"] == "GC2_structural_module"
            assert provenance["source"] == "st_c2.structural"
            assert "gc2_tests" in provenance["validated_by"]
        elif item["id"] in gc3_rules:
            assert provenance["module"] == "GC3_evidence_module"
            assert provenance["source"] == "st_c2.evidence_gc3"
            assert "gc3_tests" in provenance["validated_by"]
        else:
            assert "gc2_tests" not in provenance["validated_by"]
            assert "gc3_tests" not in provenance["validated_by"]


def test_traceability_invalid_test_detection(tmp_path):
    coverage = Path("reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json")
    map_data = yaml.safe_load(Path("specs/st_c2/rule_to_test_map.yaml").read_text(encoding="utf-8"))
    first_rule = next(iter(map_data["rules"].values()))
    first_rule["tests"] = ["tests/st_c2/does_not_exist.py::test_missing"]
    bad_map = tmp_path / "bad_map.yaml"
    bad_map.write_text(yaml.safe_dump(map_data), encoding="utf-8")
    result = validate_traceability(coverage, bad_map)
    assert not result.valid
    assert any("mapped test does not exist" in error for error in result.errors)


def test_traceability_missing_golden_case_detection(tmp_path):
    coverage = Path("reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json")
    map_data = yaml.safe_load(Path("specs/st_c2/rule_to_test_map.yaml").read_text(encoding="utf-8"))
    first_rule = next(iter(map_data["rules"].values()))
    first_rule["golden_cases"] = ["GC-STC2-MISSING"]
    bad_map = tmp_path / "bad_map.yaml"
    bad_map.write_text(yaml.safe_dump(map_data), encoding="utf-8")
    result = validate_traceability(coverage, bad_map)
    assert not result.valid
    assert any("missing golden case" in error for error in result.errors)


def test_traceability_version_symbol_mismatch_detection(tmp_path):
    coverage_data = json.loads(Path("reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json").read_text(encoding="utf-8"))
    coverage_data["symbol"] = "XAUUSD"
    bad_coverage = tmp_path / "coverage.json"
    bad_coverage.write_text(json.dumps(coverage_data), encoding="utf-8")
    result = validate_traceability(bad_coverage, "specs/st_c2/rule_to_test_map.yaml")
    assert not result.valid
    assert "rule map authority does not match coverage matrix" in result.errors
