"""ST-C2 GC4 deterministic state, signal, trade-plan, and rejection evidence."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Sequence

import yaml

from validation.st_c2.evidence_fvg_ltf import FVGChainEvidence, LTFConfirmationEvidence
from validation.st_c2.identifiers import (
    signal_candidate_id,
    stable_id,
    state_transition_id,
    trade_plan_id,
)
from validation.st_c2.schemas import LogicalTradePlan, RejectionEvidence, SignalCandidate, StateTransition
from validation.st_c2.structure import DealingRange, OTEEvidence
from validation.st_c2.symbols import SymbolMetadata, normalize_price, points_to_price, price_to_points


STATE_SEQUENCE = (
    "INELIGIBLE",
    "HTF_BIAS_VALID",
    "LIQUIDITY_SELECTED",
    "SWEEP_CONFIRMED",
    "DEALING_RANGE_VALID",
    "OTE_VALID",
    "FVG_CHAIN_VALID",
    "LTF_CONFIRMATION_VALID",
    "SIGNAL_READY",
    "TRADE_PLAN_READY",
)

REJECTION_SUBCODES = {
    "R1.NO_POOL",
    "R1.SWEEP_NOT_RECLAIMED",
    "R1.STALE_SWEEP",
    "R2.NO_BIAS",
    "R3.WRONG_ZONE",
    "R3.OTE_INVALID",
    "R4.FVG_CHAIN_INVALID",
    "R5.NO_CONFIRMATION",
    "R6.STOP_TOO_SMALL",
    "R6.STOP_TOO_LARGE",
    "R6.TARGET_NOT_FOUND",
    "R6.NET_R_TOO_LOW",
    "R7.SESSION_BUFFER",
    "R7.VOLATILITY_SHOCK",
}


@dataclass(frozen=True)
class GC4DecisionEvidence:
    transitions: tuple[StateTransition, ...]
    signal: SignalCandidate | None
    trade_plan: LogicalTradePlan | None
    rejections: tuple[RejectionEvidence, ...]
    duplicate_signal: bool
    illegal_transition_count: int

    @property
    def valid(self) -> bool:
        return self.signal is not None and self.trade_plan is not None and self.trade_plan.status == "confirmed"


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def _event_id(value: Any) -> str | None:
    if value is None:
        return None
    return getattr(value, "event_id", None) or getattr(value, "id", None) or getattr(value, "range_id", None)


def _source_ids(source_event_ids: Sequence[str | None]) -> tuple[str, ...]:
    return tuple(item for item in source_event_ids if item)


def _load_costs(symbol: str, path: Path | str = "config/research_costs.yaml") -> dict[str, Decimal]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    row = raw.get("symbols", {}).get(symbol)
    if not row:
        raise ValueError(f"missing research cost profile for {symbol}")
    return {
        "spread_points": _decimal(row["spread_points"]),
        "slippage_points": _decimal(row["slippage_points"]),
        "commission_per_lot_usd_round_turn": _decimal(row.get("commission_per_lot_usd_round_turn", 0)),
    }


def _transition(
    *,
    symbol: str,
    previous_state: str,
    new_state: str,
    trigger_event_id: str | None,
    rule_id: str,
    timestamp: str,
    causal_cutoff: str,
    reason: str,
) -> StateTransition:
    attrs = {
        "symbol": symbol,
        "previous_state": previous_state,
        "new_state": new_state,
        "trigger_event_id": trigger_event_id,
        "rule_id": rule_id,
        "timestamp": timestamp,
        "causal_cutoff": causal_cutoff,
        "reason": reason,
    }
    return StateTransition(
        transition_id=state_transition_id(attrs),
        strategy_id="ST-C2",
        strategy_version="1.2.0",
        symbol=symbol,
        previous_state=previous_state,
        new_state=new_state,
        triggering_event_id=trigger_event_id,
        rule_id=rule_id,
        timestamp=timestamp,
        causal_cutoff=causal_cutoff,
        metadata={"reason": reason},
    )


def validate_transition_sequence(transitions: Sequence[StateTransition]) -> tuple[str, ...]:
    errors: list[str] = []
    seen = set()
    expected_pairs = list(zip(STATE_SEQUENCE, STATE_SEQUENCE[1:]))
    for index, transition in enumerate(transitions):
        key = transition.transition_id
        if key in seen:
            errors.append(f"duplicate transition {key}")
        seen.add(key)
        if index >= len(expected_pairs):
            errors.append(f"unexpected transition {transition.previous_state}->{transition.new_state}")
            continue
        if (transition.previous_state, transition.new_state) != expected_pairs[index]:
            errors.append(f"illegal transition {transition.previous_state}->{transition.new_state}")
        if transition.timestamp > transition.causal_cutoff:
            errors.append(f"future transition {transition.transition_id}")
    return tuple(errors)


def build_rejection_evidence(
    *,
    symbol: str,
    rule_id: str,
    rejection_code: str,
    reason: str,
    timestamp: str,
    causal_cutoff: str,
    source_event_ids: Sequence[str | None] = (),
) -> RejectionEvidence:
    if rejection_code not in REJECTION_SUBCODES:
        raise ValueError(f"unsupported ST-C2 rejection subcode: {rejection_code}")
    source_ids = _source_ids(source_event_ids)
    attrs = {
        "symbol": symbol,
        "rule_id": rule_id,
        "rejection_code": rejection_code,
        "timestamp": timestamp,
        "causal_cutoff": causal_cutoff,
        "source_event_ids": source_ids,
    }
    return RejectionEvidence(
        rejection_id=stable_id("rejection", attrs),
        strategy_id="ST-C2",
        strategy_version="1.2.0",
        symbol=symbol,
        rule_id=rule_id,
        rejection_code=rejection_code,
        reason=reason,
        timestamp=timestamp,
        causal_cutoff=causal_cutoff,
        source_event_ids=source_ids,
        metadata={"stable_id_source": attrs},
    )


class DecisionEvidenceBuilder:
    def __init__(self, *, spec: dict[str, Any], symbol_metadata: SymbolMetadata, causal_cutoff: str) -> None:
        self.spec = spec
        self.symbol_metadata = symbol_metadata
        self.causal_cutoff = causal_cutoff

    def build_state_transitions(
        self,
        *,
        bias_event_id: str,
        pool_event_id: str,
        sweep_event_id: str,
        dealing_range_id: str,
        ote_id: str,
        fvg_chain_id: str,
        confirmation_id: str,
        signal_id: str,
        trade_plan_id_value: str,
        timestamp: str,
    ) -> tuple[StateTransition, ...]:
        triggers = (
            (bias_event_id, "STC2-BIAS-001", "HTF BOS/CHoCH bias evidence accepted"),
            (pool_event_id, "STC2-LIQ-007", "directional liquidity pool selected"),
            (sweep_event_id, "STC2-LIQ-003", "liquidity sweep and reclaim confirmed"),
            (dealing_range_id, "STC2-OTE-001", "structural dealing range frozen"),
            (ote_id, "STC2-OTE-002", "OTE location accepted"),
            (fvg_chain_id, "STC2-FVG-005", "FVG chain evidence accepted"),
            (confirmation_id, "STC2-LTF-002", "LTF confirmation accepted"),
            (signal_id, "STC2-DEDUP-001", "signal candidate ready"),
            (trade_plan_id_value, "STC2-ENTRY-001", "logical trade plan ready"),
        )
        transitions = []
        for (previous_state, new_state), (event_id, rule_id, reason) in zip(zip(STATE_SEQUENCE, STATE_SEQUENCE[1:]), triggers):
            transitions.append(
                _transition(
                    symbol=self.symbol_metadata.symbol,
                    previous_state=previous_state,
                    new_state=new_state,
                    trigger_event_id=event_id,
                    rule_id=rule_id,
                    timestamp=timestamp,
                    causal_cutoff=self.causal_cutoff,
                    reason=reason,
                )
            )
        return tuple(transitions)

    def build_signal_candidate(
        self,
        *,
        direction: str,
        signal_timestamp: str,
        source_event_ids: Sequence[str | None],
        rule_ids: Sequence[str],
        status: str = "confirmed",
        rejection_code: str | None = None,
    ) -> SignalCandidate:
        source_ids = _source_ids(source_event_ids)
        attrs = {
            "symbol": self.symbol_metadata.symbol,
            "direction": direction,
            "signal_timestamp": signal_timestamp,
            "causal_cutoff": self.causal_cutoff,
            "source_event_ids": source_ids,
            "rule_ids": tuple(rule_ids),
        }
        return SignalCandidate(
            signal_id=signal_candidate_id(attrs),
            strategy_id="ST-C2",
            strategy_version="1.2.0",
            symbol=self.symbol_metadata.symbol,
            direction=direction,  # type: ignore[arg-type]
            signal_timestamp=signal_timestamp,
            causal_cutoff=self.causal_cutoff,
            source_event_ids=source_ids,
            rule_ids=tuple(rule_ids),
            status=status,  # type: ignore[arg-type]
            rejection_code=rejection_code,
            metadata={"stable_id_source": attrs},
        )

    def build_logical_trade_plan(
        self,
        *,
        signal: SignalCandidate,
        direction: str,
        fvg_chain: FVGChainEvidence,
        sweep: Any,
        dealing_range: DealingRange,
        source_event_ids: Sequence[str | None],
    ) -> tuple[LogicalTradePlan, RejectionEvidence | None]:
        risk = self.spec["pipeline"]["execution_stage"]
        stop_cfg = risk["stop"]
        entry_cfg = risk["entry"]
        targets_cfg = risk["targets"]
        cost = _load_costs(self.symbol_metadata.symbol)
        if fvg_chain.ltf_fvg is None:
            rejection = build_rejection_evidence(
                symbol=self.symbol_metadata.symbol,
                rule_id="STC2-FVG-003",
                rejection_code="R4.FVG_CHAIN_INVALID",
                reason="LTF FVG evidence is required for entry",
                timestamp=signal.signal_timestamp,
                causal_cutoff=self.causal_cutoff,
                source_event_ids=source_event_ids,
            )
            return self._rejected_plan(signal, direction, source_event_ids, rejection), rejection

        lower = _decimal(fvg_chain.ltf_fvg.reference_levels["lower"])
        upper = _decimal(fvg_chain.ltf_fvg.reference_levels["upper"])
        entry_price = normalize_price(lower if direction == "long" else upper, self.symbol_metadata)
        buffer_price = points_to_price(stop_cfg["buffer_pips"], self.symbol_metadata)
        wick = _decimal(sweep.reference_levels["wick_extreme"])
        stop_loss = normalize_price(wick - buffer_price if direction == "long" else wick + buffer_price, self.symbol_metadata)
        target_price = normalize_price(dealing_range.high if direction == "long" else dealing_range.low, self.symbol_metadata)

        risk_distance = abs(entry_price - stop_loss)
        reward_distance = abs(target_price - entry_price)
        if reward_distance <= 0:
            rejection = build_rejection_evidence(
                symbol=self.symbol_metadata.symbol,
                rule_id="STC2-TARGET-001",
                rejection_code="R6.TARGET_NOT_FOUND",
                reason="target is not beyond entry in setup direction",
                timestamp=signal.signal_timestamp,
                causal_cutoff=self.causal_cutoff,
                source_event_ids=source_event_ids,
            )
            return self._rejected_plan(signal, direction, source_event_ids, rejection), rejection
        stop_points = price_to_points(risk_distance, self.symbol_metadata)
        if stop_points < _decimal(stop_cfg["min_stop_distance_points"]):
            rejection = build_rejection_evidence(
                symbol=self.symbol_metadata.symbol,
                rule_id="STC2-STOP-002",
                rejection_code="R6.STOP_TOO_SMALL",
                reason="stop distance below frozen minimum",
                timestamp=signal.signal_timestamp,
                causal_cutoff=self.causal_cutoff,
                source_event_ids=source_event_ids,
            )
            return self._rejected_plan(signal, direction, source_event_ids, rejection), rejection
        if stop_points > _decimal(stop_cfg["max_stop_distance_points"]):
            rejection = build_rejection_evidence(
                symbol=self.symbol_metadata.symbol,
                rule_id="STC2-STOP-002",
                rejection_code="R6.STOP_TOO_LARGE",
                reason="stop distance above frozen maximum",
                timestamp=signal.signal_timestamp,
                causal_cutoff=self.causal_cutoff,
                source_event_ids=source_event_ids,
            )
            return self._rejected_plan(signal, direction, source_event_ids, rejection), rejection

        gross_r = reward_distance / risk_distance
        estimated_cost_points = cost["spread_points"] + cost["slippage_points"]
        net_r = gross_r - (estimated_cost_points / stop_points)
        if net_r < _decimal(self.spec["risk"]["min_rr"]):
            rejection = build_rejection_evidence(
                symbol=self.symbol_metadata.symbol,
                rule_id="STC2-RISK-001",
                rejection_code="R6.NET_R_TOO_LOW",
                reason="net reward/risk below frozen minimum",
                timestamp=signal.signal_timestamp,
                causal_cutoff=self.causal_cutoff,
                source_event_ids=source_event_ids,
            )
            return self._rejected_plan(signal, direction, source_event_ids, rejection), rejection

        expiration = f"{signal.signal_timestamp}+{entry_cfg['expiry_bars_m3']}xM3"
        rule_ids = (
            "STC2-ENTRY-001",
            "STC2-ENTRY-002",
            "STC2-STOP-001",
            "STC2-STOP-002",
            "STC2-TARGET-001",
            "STC2-RISK-001",
        )
        attrs = {
            "signal_id": signal.signal_id,
            "entry_price": str(entry_price),
            "stop_loss": str(stop_loss),
            "target_1": str(target_price),
            "target_2": str(target_price),
            "causal_cutoff": self.causal_cutoff,
            "source_event_ids": _source_ids(source_event_ids),
        }
        return (
            LogicalTradePlan(
                trade_plan_id=trade_plan_id(attrs),
                signal_id=signal.signal_id,
                strategy_id="ST-C2",
                strategy_version="1.2.0",
                symbol=self.symbol_metadata.symbol,
                direction=direction,  # type: ignore[arg-type]
                signal_timestamp=signal.signal_timestamp,
                entry_type=str(entry_cfg["type"]),
                entry_price=str(entry_price),
                stop_loss=str(stop_loss),
                stop_reference=str(wick),
                stop_buffer_points=str(stop_cfg["buffer_pips"]),
                target_1=str(target_price),
                target_2=str(target_price),
                gross_reward_risk=str(gross_r),
                estimated_cost_points=str(estimated_cost_points),
                net_reward_risk=str(net_r),
                expiration_time=expiration,
                source_event_ids=_source_ids(source_event_ids),
                rule_ids=rule_ids,
                status="confirmed",
                metadata={
                    "entry_reason": "ltf_fvg_proximal_boundary",
                    "target_reference": "opposite_structural_dealing_range_extreme",
                    "research_only": True,
                    "no_order_routing": True,
                    "stable_id_source": attrs,
                    "target_selection_policy": targets_cfg["target_selection_policy"],
                },
            ),
            None,
        )

    def _rejected_plan(
        self,
        signal: SignalCandidate,
        direction: str,
        source_event_ids: Sequence[str | None],
        rejection: RejectionEvidence,
    ) -> LogicalTradePlan:
        attrs = {
            "signal_id": signal.signal_id,
            "rejection_id": rejection.rejection_id,
            "causal_cutoff": self.causal_cutoff,
        }
        return LogicalTradePlan(
            trade_plan_id=trade_plan_id(attrs),
            signal_id=signal.signal_id,
            strategy_id="ST-C2",
            strategy_version="1.2.0",
            symbol=self.symbol_metadata.symbol,
            direction=direction,  # type: ignore[arg-type]
            signal_timestamp=signal.signal_timestamp,
            entry_type=None,
            entry_price=None,
            stop_loss=None,
            stop_reference=None,
            stop_buffer_points=None,
            target_1=None,
            target_2=None,
            gross_reward_risk=None,
            estimated_cost_points=None,
            net_reward_risk=None,
            expiration_time=None,
            source_event_ids=_source_ids(source_event_ids),
            rule_ids=(rejection.rule_id,),
            status="rejected",
            rejection_code=rejection.rejection_code,
            metadata={"research_only": True, "no_order_routing": True, "stable_id_source": attrs},
        )

    def build_decision(
        self,
        *,
        direction: str,
        signal_timestamp: str,
        bias_event_id: str,
        pool: Any,
        sweep: Any,
        dealing_range: DealingRange,
        ote: OTEEvidence,
        fvg_chain: FVGChainEvidence,
        confirmation: LTFConfirmationEvidence,
    ) -> GC4DecisionEvidence:
        source_ids = (
            bias_event_id,
            _event_id(pool),
            _event_id(sweep),
            dealing_range.range_id,
            ote.range_id,
            fvg_chain.id,
            confirmation.id,
            _event_id(fvg_chain.mf_fvg),
            _event_id(fvg_chain.ltf_fvg),
            _event_id(confirmation.choch_event),
        )
        rule_ids = (
            "STC2-BIAS-001",
            "STC2-LIQ-007",
            "STC2-LIQ-003",
            "STC2-OTE-001",
            "STC2-OTE-002",
            "STC2-FVG-005",
            "STC2-LTF-002",
            "STC2-DEDUP-001",
        )
        signal = self.build_signal_candidate(
            direction=direction,
            signal_timestamp=signal_timestamp,
            source_event_ids=source_ids,
            rule_ids=rule_ids,
        )
        plan, rejection = self.build_logical_trade_plan(
            signal=signal,
            direction=direction,
            fvg_chain=fvg_chain,
            sweep=sweep,
            dealing_range=dealing_range,
            source_event_ids=source_ids + (signal.signal_id,),
        )
        if rejection is not None:
            return GC4DecisionEvidence((), signal, plan, (rejection,), False, 0)
        transitions = self.build_state_transitions(
            bias_event_id=bias_event_id,
            pool_event_id=_event_id(pool) or "",
            sweep_event_id=_event_id(sweep) or "",
            dealing_range_id=dealing_range.range_id,
            ote_id=ote.range_id,
            fvg_chain_id=fvg_chain.id,
            confirmation_id=confirmation.id,
            signal_id=signal.signal_id,
            trade_plan_id_value=plan.trade_plan_id,
            timestamp=signal_timestamp,
        )
        errors = validate_transition_sequence(transitions)
        return GC4DecisionEvidence(transitions, signal, plan, (), False, len(errors))
