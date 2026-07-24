"""Deterministic stable identifiers for ST-C2 conformance objects."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from typing import Any


NON_DEFINING_FIELDS = {"metadata", "diagnostics", "notes", "debug"}


def canonicalize(value: Any, *, include_non_defining: bool = False) -> Any:
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    if isinstance(value, tuple):
        return [canonicalize(v, include_non_defining=include_non_defining) for v in value]
    if isinstance(value, list):
        return [canonicalize(v, include_non_defining=include_non_defining) for v in value]
    if isinstance(value, dict):
        return {
            str(k): canonicalize(v, include_non_defining=include_non_defining)
            for k, v in sorted(value.items(), key=lambda item: str(item[0]))
            if include_non_defining or str(k) not in NON_DEFINING_FIELDS
        }
    return value


def stable_id(object_type: str, attributes: dict[str, Any]) -> str:
    payload = {
        "object_type": object_type,
        "attributes": canonicalize(attributes),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return f"{object_type.upper()}-{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:24]}"


def structure_id(attributes: dict[str, Any]) -> str:
    return stable_id("structure", attributes)


def liquidity_pool_id(attributes: dict[str, Any]) -> str:
    return stable_id("liquidity_pool", attributes)


def sweep_id(attributes: dict[str, Any]) -> str:
    return stable_id("sweep", attributes)


def fvg_id(attributes: dict[str, Any]) -> str:
    return stable_id("fvg", attributes)


def confirmation_id(attributes: dict[str, Any]) -> str:
    return stable_id("confirmation", attributes)


def state_transition_id(attributes: dict[str, Any]) -> str:
    return stable_id("state_transition", attributes)


def signal_candidate_id(attributes: dict[str, Any]) -> str:
    return stable_id("signal_candidate", attributes)


def trade_plan_id(attributes: dict[str, Any]) -> str:
    return stable_id("trade_plan", attributes)


def golden_case_id(attributes: dict[str, Any]) -> str:
    return stable_id("golden_case", attributes)
