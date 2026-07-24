"""Traceability validation for ST-C2 A2 rule inventory and golden cases."""
from __future__ import annotations

import importlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from validation.st_c2.golden_cases import case_ids


COVERAGE_PATH = Path("reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json")
MAP_PATH = Path("specs/st_c2/rule_to_test_map.yaml")


@dataclass(frozen=True)
class TraceabilityResult:
    valid: bool
    errors: tuple[str, ...]
    missing_mappings: int


def _function_exists(dotted: str) -> bool:
    if "::" in dotted:
        module_name, function_name = dotted.split("::", 1)
    elif "." in dotted:
        module_name, function_name = dotted.rsplit(".", 1)
    else:
        return False
    module_name = module_name.replace("/", ".").removesuffix(".py")
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return False
    return hasattr(module, function_name)


def _test_exists(test_ref: str) -> bool:
    path, _, name = test_ref.partition("::")
    if not Path(path).exists() or not name:
        return False
    text = Path(path).read_text(encoding="utf-8")
    return f"def {name}" in text


def validate_traceability(
    coverage_path: Path | str = COVERAGE_PATH,
    map_path: Path | str = MAP_PATH,
) -> TraceabilityResult:
    coverage = json.loads(Path(coverage_path).read_text(encoding="utf-8"))
    rule_map = yaml.safe_load(Path(map_path).read_text(encoding="utf-8"))
    cases = case_ids()
    errors: list[str] = []

    if rule_map["strategy"]["version"] != coverage["version"] or rule_map["strategy"]["symbol"] != coverage["symbol"]:
        errors.append("rule map authority does not match coverage matrix")

    mapped_rules = set(rule_map.get("rules", {}))
    missing_mappings = 0
    for item in coverage["inventory"]:
        rule_id = item["id"]
        if rule_id not in mapped_rules:
            missing_mappings += 1
        for field in ("id", "rule", "classification"):
            if field not in item:
                errors.append(f"{rule_id}: missing required inventory field {field}")

    for rule_id, entry in rule_map.get("rules", {}).items():
        impl = entry.get("implementation") or {}
        module = impl.get("module")
        function = impl.get("function")
        if module and function and not _function_exists(f"{module}::{function}"):
            errors.append(f"{rule_id}: implementation function does not exist")
        tests = entry.get("tests", [])
        for test in tests:
            if not _test_exists(test):
                errors.append(f"{rule_id}: mapped test does not exist: {test}")
        for case_id in entry.get("golden_cases", []):
            if case_id not in cases:
                errors.append(f"{rule_id}: missing golden case {case_id}")
        status = entry.get("mapping_status", "mapped")
        if status == "implemented" and not tests:
            errors.append(f"{rule_id}: implemented rule lacks tests")

    return TraceabilityResult(valid=not errors, errors=tuple(errors), missing_mappings=missing_mappings)


if __name__ == "__main__":
    result = validate_traceability()
    print(json.dumps({"valid": result.valid, "errors": result.errors, "missing_mappings": result.missing_mappings}, indent=2))
    raise SystemExit(0 if result.valid else 1)
