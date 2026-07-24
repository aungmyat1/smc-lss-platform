"""Immutable evidence schemas for ST-C2 A2 conformance."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from validation.st_c2.identifiers import stable_id


Direction = Literal["long", "short", "none"]
Status = Literal["candidate", "confirmed", "invalidated", "expired", "rejected"]


@dataclass(frozen=True)
class EvidenceBase:
    event_id: str
    strategy_id: str
    strategy_version: str
    symbol: str
    timeframe: str
    rule_id: str
    event_type: str
    direction: Direction
    source_indices: tuple[int, ...]
    source_timestamps: tuple[str, ...]
    confirmation_timestamp: str | None
    causal_cutoff: str
    reference_levels: dict[str, str] = field(default_factory=dict)
    status: Status = "candidate"
    invalidation_reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StructuralEvent(EvidenceBase):
    pass


@dataclass(frozen=True)
class LiquidityPool(EvidenceBase):
    pass


@dataclass(frozen=True)
class LiquiditySweep(EvidenceBase):
    pass


@dataclass(frozen=True)
class FVGEvent(EvidenceBase):
    pass


@dataclass(frozen=True)
class ConfirmationEvent(EvidenceBase):
    pass


@dataclass(frozen=True)
class StateTransition:
    transition_id: str
    strategy_id: str
    strategy_version: str
    symbol: str
    previous_state: str
    new_state: str
    triggering_event_id: str | None
    rule_id: str
    timestamp: str
    causal_cutoff: str
    rejection_code: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SignalCandidate:
    signal_id: str
    strategy_id: str
    strategy_version: str
    symbol: str
    direction: Direction
    signal_timestamp: str
    causal_cutoff: str
    source_event_ids: tuple[str, ...]
    rule_ids: tuple[str, ...]
    status: Status
    rejection_code: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LogicalTradePlan:
    trade_plan_id: str
    signal_id: str
    strategy_id: str
    strategy_version: str
    symbol: str
    direction: Direction
    signal_timestamp: str
    entry_type: str | None
    entry_price: str | None
    stop_loss: str | None
    stop_reference: str | None
    stop_buffer_points: str | None
    target_1: str | None
    target_2: str | None
    gross_reward_risk: str | None
    estimated_cost_points: str | None
    net_reward_risk: str | None
    expiration_time: str | None
    source_event_ids: tuple[str, ...]
    rule_ids: tuple[str, ...]
    status: Status
    rejection_code: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RejectionEvidence:
    rejection_id: str
    strategy_id: str
    strategy_version: str
    symbol: str
    rule_id: str
    rejection_code: str
    reason: str
    timestamp: str
    causal_cutoff: str
    source_event_ids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evidence_id(object_type: str, attrs: dict[str, Any]) -> str:
    return stable_id(object_type, attrs)
