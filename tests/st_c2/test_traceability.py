import json
from pathlib import Path

import yaml

from validation.st_c2.traceability import validate_traceability


def test_traceability_current_inventory_reports_missing_mappings_honestly():
    result = validate_traceability()
    assert result.valid
    assert result.missing_mappings == 37


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
