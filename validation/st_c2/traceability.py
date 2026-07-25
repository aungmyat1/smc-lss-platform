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
CONTRACT_PATH = Path("specs/st_c2/st_c2_contract.yaml")


@dataclass(frozen=True)
class TraceabilityResult:
    valid: bool
    errors: tuple[str, ...]
    missing_mappings: int


@dataclass(frozen=True)
class ContractTraceabilityResult:
    valid: bool
    errors: tuple[str, ...]
    incomplete_rules: tuple[str, ...]


def _attribute_exists(dotted: str) -> bool:
    if "::" in dotted:
        module_name, attr_name = dotted.split("::", 1)
    elif "." in dotted:
        module_name, attr_name = dotted.rsplit(".", 1)
    else:
        return False
    module_name = module_name.replace("/", ".").removesuffix(".py")
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return False
    current: Any = module
    for part in attr_name.split("."):
        if not hasattr(current, part):
            return False
        current = getattr(current, part)
    return True


def _function_exists(dotted: str) -> bool:
    return _attribute_exists(dotted)


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


def load_contract(path: Path | str = CONTRACT_PATH) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def validate_contract_traceability(
    coverage_path: Path | str = COVERAGE_PATH,
    contract_path: Path | str = CONTRACT_PATH,
) -> ContractTraceabilityResult:
    """Validate contract -> implementation/test/metric traceability.

    This guardrail is drift-focused. It permits known incomplete A2 rules only
    when the contract declares an incomplete conformance status explicitly.
    """
    coverage = json.loads(Path(coverage_path).read_text(encoding="utf-8"))
    contract = load_contract(contract_path)
    errors: list[str] = []
    incomplete_rules: list[str] = []

    strategy = contract.get("strategy", {})
    if strategy.get("id") != coverage.get("strategy"):
        errors.append("contract strategy does not match coverage matrix")
    if strategy.get("version") != coverage.get("version"):
        errors.append("contract version does not match coverage matrix")
    if strategy.get("symbol") != coverage.get("symbol"):
        errors.append("contract symbol does not match coverage matrix")
    if strategy.get("execution_authority") != "none":
        errors.append("contract must not grant execution authority")

    coverage_ids = {item["id"] for item in coverage.get("inventory", [])}
    traceability = contract.get("traceability", {})
    contract_ids = set(traceability)
    missing_from_contract = sorted(coverage_ids - contract_ids)
    extra_contract_rules = sorted(contract_ids - coverage_ids)
    for rule_id in missing_from_contract:
        errors.append(f"{rule_id}: coverage rule missing from contract")
    for rule_id in extra_contract_rules:
        errors.append(f"{rule_id}: contract rule missing from coverage")

    stage_rule_ids: set[str] = set()
    stage_keys = {stage.get("key") for stage in contract.get("funnel_stages", [])}
    for stage in contract.get("funnel_stages", []):
        key = stage.get("key")
        if not stage.get("required_inputs"):
            errors.append(f"{key}: missing required inputs")
        if not stage.get("required_outputs"):
            errors.append(f"{key}: missing required outputs")
        if not stage.get("failure_codes"):
            errors.append(f"{key}: missing failure codes")
        if not stage.get("validation_metrics"):
            errors.append(f"{key}: missing validation metrics")
        for rule_id in stage.get("deterministic_rules", []):
            if rule_id in stage_rule_ids:
                errors.append(f"{rule_id}: rule appears in more than one funnel stage")
            stage_rule_ids.add(rule_id)

    if stage_rule_ids != contract_ids:
        for rule_id in sorted(stage_rule_ids - contract_ids):
            errors.append(f"{rule_id}: stage rule missing traceability entry")
        for rule_id in sorted(contract_ids - stage_rule_ids):
            errors.append(f"{rule_id}: traceability entry missing from funnel stages")

    complete_statuses = {"implemented_tested"}
    incomplete_statuses = {
        "not_implemented",
        "implemented_missing_tests",
        "partial_missing_tests",
        "partial_tested",
    }
    for rule_id, entry in traceability.items():
        stage = entry.get("stage")
        if stage not in stage_keys:
            errors.append(f"{rule_id}: unknown funnel stage {stage}")
        if not entry.get("component"):
            errors.append(f"{rule_id}: missing component")
        if not entry.get("validation_metric"):
            errors.append(f"{rule_id}: missing validation metric")
        status = entry.get("conformance_status")
        if status not in complete_statuses | incomplete_statuses:
            errors.append(f"{rule_id}: unknown conformance status {status}")
            continue
        implementation = entry.get("implementation")
        tests = entry.get("tests") or []
        if implementation and not _attribute_exists(implementation):
            errors.append(f"{rule_id}: implementation mapping does not exist: {implementation}")
        for test in tests:
            if not _test_exists(test):
                errors.append(f"{rule_id}: mapped test does not exist: {test}")
        if status in complete_statuses:
            if not implementation:
                errors.append(f"{rule_id}: complete rule lacks implementation mapping")
            if not tests:
                errors.append(f"{rule_id}: complete rule lacks tests")
        else:
            incomplete_rules.append(rule_id)

    return ContractTraceabilityResult(
        valid=not errors,
        errors=tuple(errors),
        incomplete_rules=tuple(sorted(incomplete_rules)),
    )


if __name__ == "__main__":
    result = validate_traceability()
    contract_result = validate_contract_traceability()
    print(
        json.dumps(
            {
                "valid": result.valid and contract_result.valid,
                "legacy_errors": result.errors,
                "missing_mappings": result.missing_mappings,
                "contract_errors": contract_result.errors,
                "contract_incomplete_rules": contract_result.incomplete_rules,
            },
            indent=2,
        )
    )
    raise SystemExit(0 if result.valid and contract_result.valid else 1)
