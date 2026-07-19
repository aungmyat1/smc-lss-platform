#!/usr/bin/env python3
"""Mechanical validator for the ST-C1 candidate strategy contract.

This gate checks that the normalized contract is structurally complete and
deterministic enough for historical testing. It does not backtest, optimize, or
approve the strategy.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


FORBIDDEN_SUBJECTIVE_TERMS = {
    "clean",
    "strong",
    "significant",
    "institutional",
    "obvious",
    "discretionary",
    "best",
    "reasonable",
    "optimal",
}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    contract_path: str
    status: str
    issues: tuple[ValidationIssue, ...] = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        return self.status == "READY_FOR_BACKTEST" and not self.issues


def load_contract(path: str) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("strategy contract must be a top-level mapping")
    return data


def _issue(code: str, path: str, message: str) -> ValidationIssue:
    return ValidationIssue(code=code, path=path, message=message)


def _require(mapping: Any, key: str, path: str, issues: list[ValidationIssue], expected_type: type | tuple[type, ...] | None = None) -> Any:
    if not isinstance(mapping, dict):
        issues.append(_issue("INVALID_CONTAINER", path, "expected a mapping"))
        return None
    if key not in mapping:
        issues.append(_issue("MISSING_KEY", f"{path}.{key}", "missing required key"))
        return None
    value = mapping[key]
    if expected_type is not None and not isinstance(value, expected_type):
        issues.append(_issue("INVALID_TYPE", f"{path}.{key}", f"expected {expected_type}, got {type(value).__name__}"))
        return None
    return value


def _require_all(mapping: Any, keys: tuple[str, ...], path: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(mapping, dict):
        issues.append(_issue("INVALID_CONTAINER", path, "expected a mapping"))
        return
    for key in keys:
        if key not in mapping:
            issues.append(_issue("MISSING_KEY", f"{path}.{key}", "missing required key"))


def _require_list_nonempty(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, list) or not value:
        issues.append(_issue("INVALID_LIST", path, "expected a non-empty list"))


def _require_bool(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, bool):
        issues.append(_issue("INVALID_TYPE", path, "expected boolean"))


def _scan_subjective_language(node: Any, path: str, issues: list[ValidationIssue]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            _scan_subjective_language(value, f"{path}.{key}", issues)
    elif isinstance(node, list):
        for idx, item in enumerate(node):
            _scan_subjective_language(item, f"{path}[{idx}]", issues)
    elif isinstance(node, str):
        lowered = node.lower()
        for term in FORBIDDEN_SUBJECTIVE_TERMS:
            if term in lowered:
                issues.append(_issue("SUBJECTIVE_LANGUAGE", path, f"contains subjective term '{term}'"))
                break


def validate_contract(contract: dict[str, Any], contract_path: str = "<memory>") -> ValidationResult:
    issues: list[ValidationIssue] = []

    strategy = contract.get("strategy")
    if not isinstance(strategy, dict):
        issues.append(_issue("MISSING_SECTION", "strategy", "missing strategy section"))
    else:
        if strategy.get("strategy_id") != "ST-C1":
            issues.append(_issue("INVALID_VALUE", "strategy.strategy_id", "must equal ST-C1"))
        if not isinstance(strategy.get("version"), str) or not strategy["version"]:
            issues.append(_issue("INVALID_VALUE", "strategy.version", "must be a non-empty string"))
        if strategy.get("status") != "candidate":
            issues.append(_issue("INVALID_VALUE", "strategy.status", "must equal candidate"))
        source = strategy.get("source")
        if not isinstance(source, dict):
            issues.append(_issue("MISSING_SECTION", "strategy.source", "missing source mapping"))
        else:
            _require_all(source, ("specification", "research_spec", "execution_spec"), "strategy.source", issues)

    market = contract.get("market_universe")
    if not isinstance(market, dict):
        issues.append(_issue("MISSING_SECTION", "market_universe", "missing market universe section"))
    else:
        _require_list_nonempty(market.get("instruments"), "market_universe.instruments", issues)
        _require_list_nonempty(market.get("sessions"), "market_universe.sessions", issues)
        timeframes = market.get("timeframes")
        if not isinstance(timeframes, dict):
            issues.append(_issue("MISSING_SECTION", "market_universe.timeframes", "missing timeframes mapping"))
        else:
            _require_all(timeframes, ("bias", "setup", "confirmation", "execution"), "market_universe.timeframes", issues)

    structure = contract.get("structure")
    if not isinstance(structure, dict):
        issues.append(_issue("MISSING_SECTION", "structure", "missing structure section"))
    else:
        _require_all(structure, ("swing_high", "swing_low", "bos", "choch"), "structure", issues)
        for key in ("swing_high", "swing_low", "bos", "choch"):
            section = structure.get(key)
            if isinstance(section, dict):
                _require_all(section, ("input_condition", "deterministic_rule", "boolean_decision", "trade_action"), f"structure.{key}", issues)

    liquidity = contract.get("liquidity")
    if not isinstance(liquidity, dict):
        issues.append(_issue("MISSING_SECTION", "liquidity", "missing liquidity section"))
    else:
        _require_all(liquidity, ("liquidity_pool", "sweep"), "liquidity", issues)
        for key in ("liquidity_pool", "sweep"):
            section = liquidity.get(key)
            if isinstance(section, dict):
                _require_all(section, ("input_condition", "deterministic_rule", "boolean_decision", "trade_action"), f"liquidity.{key}", issues)

    poi = contract.get("poi")
    if not isinstance(poi, dict):
        issues.append(_issue("MISSING_SECTION", "poi", "missing poi section"))
    else:
        _require_all(poi, ("order_block", "fair_value_gap", "premium_discount"), "poi", issues)
        for key in ("order_block", "fair_value_gap", "premium_discount"):
            section = poi.get(key)
            if isinstance(section, dict):
                _require_all(section, ("input_condition", "deterministic_rule", "boolean_decision", "trade_action"), f"poi.{key}", issues)

    entry_model = contract.get("entry_model")
    if not isinstance(entry_model, dict):
        issues.append(_issue("MISSING_SECTION", "entry_model", "missing entry model section"))
    else:
        _require_all(entry_model, ("long", "short", "stage_mapping"), "entry_model", issues)
        for side in ("long", "short"):
            section = entry_model.get(side)
            if isinstance(section, dict):
                _require_all(
                    section,
                    ("input_condition", "deterministic_rule", "boolean_decision", "trade_action", "confirmation_candle", "entry_price", "invalidation", "timeout_bars"),
                    f"entry_model.{side}",
                    issues,
                )

    exit_model = contract.get("exit_model")
    if not isinstance(exit_model, dict):
        issues.append(_issue("MISSING_SECTION", "exit_model", "missing exit model section"))
    else:
        _require_all(exit_model, ("stop_loss", "take_profit", "management"), "exit_model", issues)
        for key in ("stop_loss", "take_profit"):
            section = exit_model.get(key)
            if isinstance(section, dict):
                _require_all(section, ("input_condition", "deterministic_rule", "boolean_decision", "trade_action"), f"exit_model.{key}", issues)

    risk = contract.get("risk_contract")
    if not isinstance(risk, dict):
        issues.append(_issue("MISSING_SECTION", "risk_contract", "missing risk contract section"))
    else:
        _require_all(risk, ("risk_per_trade", "max_daily_loss_pct", "max_weekly_loss_pct", "max_positions", "portfolio_heat_pct", "minimum_rr", "position_sizing", "execution_limits"), "risk_contract", issues)

    machine_validation = contract.get("machine_validation")
    if not isinstance(machine_validation, dict):
        issues.append(_issue("MISSING_SECTION", "machine_validation", "missing machine validation section"))
    else:
        for key in (
            "every_rule_measurable",
            "every_parameter_externalizable",
            "no_subjective_language",
            "entry_conditions_boolean",
            "exit_conditions_deterministic",
            "risk_rules_explicit",
            "strategy_codable_without_interpretation",
        ):
            _require_bool(machine_validation.get(key), f"machine_validation.{key}", issues)
        if machine_validation.get("no_subjective_language") is True:
            _scan_subjective_language(contract, "contract", issues)

    status = "READY_FOR_BACKTEST" if not issues else "BLOCKED"
    return ValidationResult(contract_path=contract_path, status=status, issues=tuple(issues))


def write_validation_report(result: ValidationResult, path: str = "reports/ST-C1_CONTRACT_VALIDATION_REPORT.md") -> str:
    lines = [
        "# ST-C1 Contract Validation Report",
        "",
        f"- Contract: `{result.contract_path}`",
        f"- Status: `{result.status}`",
        f"- Issues: `{len(result.issues)}`",
        "",
        "## Result",
        "",
        "READY_FOR_BACKTEST" if result.ok else "BLOCKED",
        "",
        "## Issues",
        "",
    ]
    if result.issues:
        for issue in result.issues:
            lines.append(f"- `{issue.code}` at `{issue.path}`: {issue.message}")
    else:
        lines.append("- None")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def validate_contract_file(contract_path: str, report_path: str = "reports/ST-C1_CONTRACT_VALIDATION_REPORT.md") -> ValidationResult:
    contract = load_contract(contract_path)
    result = validate_contract(contract, contract_path=contract_path)
    write_validation_report(result, path=report_path)
    return result
