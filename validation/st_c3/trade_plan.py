"""ST-C3 TRADE_PLAN object, matching `specs/st-c3_v1.0.1.yaml`'s `trade_plan`
schema (§5), emitted only at `S13_TRADE_PLAN_EMIT`.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class TradePlan:
    strategy_id: str
    direction: str
    context: Mapping[str, str]
    entry: Mapping[str, Any]
    risk: Mapping[str, Any]
    targets: Mapping[str, Mapping[str, Any]]
    expiry: Mapping[str, Any]
    evidence_chain: tuple[str, ...]
    status: Mapping[str, Any]
    meta: Mapping[str, Any]

    def to_dict(self) -> dict:
        return asdict(self)
