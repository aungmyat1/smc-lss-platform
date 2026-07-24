"""Golden-case manifest loading and validation for ST-C2."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


MANIFEST_PATH = Path("validation/st_c2/golden_cases/manifests/st_c2_gbp_manifest.yaml")


@dataclass(frozen=True)
class GoldenCase:
    case_id: str
    strategy_id: str
    strategy_version: str
    symbol: str
    category: str
    fixture_paths: tuple[str, ...]
    expected_signal: dict[str, Any] | None
    expected_rejection: dict[str, Any] | None
    rule_ids: tuple[str, ...]


REQUIRED_FIELDS = {
    "case_id",
    "strategy_id",
    "strategy_version",
    "symbol",
    "timeframes",
    "category",
    "description",
    "source_type",
    "source_data_hashes",
    "fixture_paths",
    "causal_cutoff",
    "expected_events",
    "expected_transitions",
    "expected_signal",
    "expected_rejection",
    "expected_trade_plan",
    "tolerance_policy",
    "rule_ids",
}


def load_manifest(path: Path | str = MANIFEST_PATH) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if data["strategy_id"] != "ST-C2" or data["strategy_version"] != "1.2.0" or data["symbol"] != "GBPUSD":
        raise ValueError("golden-case manifest authority mismatch")
    return data


def validate_manifest(path: Path | str = MANIFEST_PATH) -> list[str]:
    manifest = load_manifest(path)
    errors: list[str] = []
    base = Path(path).parent.parent
    seen: set[str] = set()
    for case in manifest.get("cases", []):
        missing = sorted(REQUIRED_FIELDS - set(case))
        if missing:
            errors.append(f"{case.get('case_id', '<missing>')}: missing fields {missing}")
        case_id = case.get("case_id")
        if case_id in seen:
            errors.append(f"{case_id}: duplicate case id")
        seen.add(case_id)
        for fixture in case.get("fixture_paths", []):
            fixture_path = (base / fixture).resolve()
            if not fixture_path.exists():
                errors.append(f"{case_id}: missing fixture {fixture}")
            elif fixture_path.suffix == ".json":
                json.loads(fixture_path.read_text(encoding="utf-8"))
    return errors


def load_cases(path: Path | str = MANIFEST_PATH) -> tuple[GoldenCase, ...]:
    errors = validate_manifest(path)
    if errors:
        raise ValueError("; ".join(errors))
    manifest = load_manifest(path)
    return tuple(
        GoldenCase(
            case_id=case["case_id"],
            strategy_id=case["strategy_id"],
            strategy_version=case["strategy_version"],
            symbol=case["symbol"],
            category=case["category"],
            fixture_paths=tuple(case["fixture_paths"]),
            expected_signal=case["expected_signal"],
            expected_rejection=case["expected_rejection"],
            rule_ids=tuple(case["rule_ids"]),
        )
        for case in manifest["cases"]
    )


def case_ids(path: Path | str = MANIFEST_PATH) -> set[str]:
    return {case.case_id for case in load_cases(path)}
