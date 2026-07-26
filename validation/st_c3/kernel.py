"""ST-C3 reference conformance kernel (A2/S1-G2 scoped).

Deterministic, side-effect-free implementation of the 16-state ST-C3 funnel
described in `docs/strategy/st_c3/ST-C3_STATE_MACHINE.md` and
`docs/strategy/st_c3/ST-C3_EVIDENCE_BINDINGS.md`, matching
`specs/st-c3_v1.0.1.yaml`'s `state_machine` section exactly. It consumes a
pre-built `EvidenceBundle` (Evidence objects a caller supplies) and applies
guards in state order S1 -> S12, emitting a `TRADE_PLAN` at S13 or exactly
one R-code before it / ERR-code after it. It never computes structure from
price data itself (`validator_never_computes_structure` /
`detection_modules_produce_evidence` per the spec's own `validator_rules`).

No execution, sizing, order placement, or optimization logic exists here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from validation.st_c3.evidence import Evidence
from validation.st_c3.trade_plan import TradePlan

STATE_ORDER = (
    "S1_HTF_BIAS",
    "S2_SWEEP",
    "S3_SWEEP_RECLAIM",
    "S4_DISPLACEMENT_BOS",
    "S5_BOS_EXTREME_LOCK",
    "S6_DEALING_RANGE",
    "S7_OTE",
    "S8_FVG_OB_CONFLUENCE",
    "S9_LTF_CONFIRMATION",
    "S10_SESSION_GATEKEEPER",
    "S11_ENTRY_WINDOW",
    "S12_RISK_SLTP",
)


@dataclass(frozen=True)
class EvidenceBundle:
    """One candidate setup's worth of pre-built ST-C3 evidence.

    `computed_rr`/`min_rr` are supplied directly rather than derived, since
    the spec's MIN_RR parameter is still `provisional` and RR computation
    from raw price is out of this kernel's scope (see module docstring).
    """

    htf_bias: Evidence
    sweep: Evidence
    sweep_reclaim: Evidence
    displacement: Evidence
    bos: Evidence
    bos_extreme: Evidence
    dealing_range: Evidence
    ote: Evidence
    fvg: Evidence
    order_block: Evidence
    ltf_confirmation: Evidence
    session_window: Evidence
    entry_window: Evidence
    invalidation_swing: Evidence
    target_tp1: Evidence
    target_tp2: Evidence
    target_tp3: Evidence
    computed_rr: float
    min_rr: float
    entry_price: float
    risk_per_trade_pct: float
    session_open: bool = True
    instrument_enabled: bool = True
    expiry: Optional[Evidence] = None


@dataclass(frozen=True)
class Rejection:
    state: str
    code: str
    reason: str
    evidence_id: Optional[str]


@dataclass(frozen=True)
class Termination:
    code: str
    reason: str


@dataclass(frozen=True)
class KernelResult:
    outcome: str  # "NOT_STARTED" | "REJECTED" | "VALID"
    states_reached: tuple[str, ...]
    rejection: Optional[Rejection] = None
    trade_plan: Optional[TradePlan] = None


def _fail(state: str, code: str, reason: str, evidence_id: Optional[str], reached: tuple[str, ...]) -> KernelResult:
    return KernelResult(
        outcome="REJECTED",
        states_reached=reached,
        rejection=Rejection(state=state, code=code, reason=reason, evidence_id=evidence_id),
    )


def run_kernel(bundle: EvidenceBundle) -> KernelResult:
    """Run the ST-C3 S0-S13 funnel over `bundle`.

    Evaluates guards in strict forward order (`no_state_can_be_skipped_or_revisited`);
    stops at the first failed guard with exactly one R-code
    (`any_failed_guard_triggers_exactly_one_r_code_or_err_code`).
    """
    reached: list[str] = []

    if not (bundle.session_open and bundle.instrument_enabled):
        return KernelResult(outcome="NOT_STARTED", states_reached=tuple(reached))
    reached.append("S0_INIT")

    # S1_HTF_BIAS
    if not bundle.htf_bias.valid:
        return _fail("S1_HTF_BIAS", "R1_HTF_BIAS_UNCLEAR", bundle.htf_bias.reason, bundle.htf_bias.id, tuple(reached))
    reached.append("S1_HTF_BIAS")

    # S2_SWEEP
    if not bundle.sweep.valid:
        return _fail("S2_SWEEP", "R2_NO_SWEEP", bundle.sweep.reason, bundle.sweep.id, tuple(reached))
    reached.append("S2_SWEEP")

    # S3_SWEEP_RECLAIM
    if not (bundle.sweep_reclaim.valid and bundle.sweep_reclaim.get("reclaimed")):
        return _fail("S3_SWEEP_RECLAIM", "R2_NO_SWEEP", bundle.sweep_reclaim.reason, bundle.sweep_reclaim.id, tuple(reached))
    reached.append("S3_SWEEP_RECLAIM")

    # S4_DISPLACEMENT_BOS
    if not (bundle.displacement.valid and bundle.bos.valid):
        failing = bundle.displacement if not bundle.displacement.valid else bundle.bos
        return _fail("S4_DISPLACEMENT_BOS", "R3_NO_DISPLACEMENT_BOS", failing.reason, failing.id, tuple(reached))
    reached.append("S4_DISPLACEMENT_BOS")

    # S5_BOS_EXTREME_LOCK
    if not (bundle.bos_extreme.valid and bundle.bos_extreme.get("pullback_detected")):
        return _fail("S5_BOS_EXTREME_LOCK", "R3_NO_DISPLACEMENT_BOS", bundle.bos_extreme.reason, bundle.bos_extreme.id, tuple(reached))
    reached.append("S5_BOS_EXTREME_LOCK")

    # S6_DEALING_RANGE
    if not bundle.dealing_range.valid:
        return _fail("S6_DEALING_RANGE", "R4_NO_OTE_PULLBACK", bundle.dealing_range.reason, bundle.dealing_range.id, tuple(reached))
    reached.append("S6_DEALING_RANGE")

    # S7_OTE
    if not (bundle.ote.valid and bundle.ote.get("price_in_ote")):
        return _fail("S7_OTE", "R4_NO_OTE_PULLBACK", bundle.ote.reason, bundle.ote.id, tuple(reached))
    reached.append("S7_OTE")

    # S8_FVG_OB_CONFLUENCE
    fvg_or_ob_valid = bundle.fvg.valid or bundle.order_block.valid
    inside_ote = (bundle.fvg.valid and bundle.fvg.get("inside_ote")) or (
        bundle.order_block.valid and bundle.order_block.get("inside_ote")
    )
    if not (fvg_or_ob_valid and inside_ote):
        failing = bundle.fvg if not bundle.fvg.valid else bundle.order_block
        return _fail("S8_FVG_OB_CONFLUENCE", "R5_NO_FVG_OB_CONFLUENCE", failing.reason, failing.id, tuple(reached))
    reached.append("S8_FVG_OB_CONFLUENCE")

    # S9_LTF_CONFIRMATION
    if not (bundle.ltf_confirmation.valid and bundle.ltf_confirmation.get("sweep_local_liquidity")):
        return _fail(
            "S9_LTF_CONFIRMATION",
            "R6_NO_LTF_CONFIRMATION",
            bundle.ltf_confirmation.reason,
            bundle.ltf_confirmation.id,
            tuple(reached),
        )
    reached.append("S9_LTF_CONFIRMATION")

    # S10_SESSION_GATEKEEPER
    if not (bundle.session_window.valid and bundle.session_window.get("session") in ("LONDON", "NY")):
        return _fail(
            "S10_SESSION_GATEKEEPER",
            "R6_NO_LTF_CONFIRMATION",
            bundle.session_window.reason,
            bundle.session_window.id,
            tuple(reached),
        )
    reached.append("S10_SESSION_GATEKEEPER")

    # S11_ENTRY_WINDOW
    if not (bundle.entry_window.valid and bundle.entry_window.get("inside_window")):
        return _fail(
            "S11_ENTRY_WINDOW",
            "R7_ENTRY_WINDOW_EXPIRED",
            bundle.entry_window.reason,
            bundle.entry_window.id,
            tuple(reached),
        )
    reached.append("S11_ENTRY_WINDOW")

    # S12_RISK_SLTP
    targets_valid = bundle.target_tp1.valid and bundle.target_tp2.valid and bundle.target_tp3.valid
    if not (bundle.invalidation_swing.valid and targets_valid and bundle.computed_rr >= bundle.min_rr):
        failing = bundle.invalidation_swing if not bundle.invalidation_swing.valid else bundle.target_tp1
        return _fail("S12_RISK_SLTP", "R8_INVALID_RISK_OR_TARGET", failing.reason, failing.id, tuple(reached))
    reached.append("S12_RISK_SLTP")

    # S13_TRADE_PLAN_EMIT
    trade_plan = _emit_trade_plan(bundle)
    reached.append("S13_TRADE_PLAN_EMIT")
    return KernelResult(outcome="VALID", states_reached=tuple(reached), trade_plan=trade_plan)


def _emit_trade_plan(bundle: EvidenceBundle) -> TradePlan:
    entry_zone_type = "FVG" if bundle.fvg.valid else "ORDERBLOCK"
    entry_zone_id = bundle.fvg.id if bundle.fvg.valid else bundle.order_block.id
    direction = bundle.htf_bias.get("bias")

    evidence_chain = (
        bundle.htf_bias.id,
        bundle.sweep.id,
        bundle.sweep_reclaim.id,
        bundle.displacement.id,
        bundle.bos.id,
        bundle.bos_extreme.id,
        bundle.dealing_range.id,
        bundle.ote.id,
        bundle.fvg.id,
        bundle.order_block.id,
        bundle.ltf_confirmation.id,
        bundle.session_window.id,
        bundle.entry_window.id,
        bundle.invalidation_swing.id,
        bundle.target_tp1.id,
    )

    return TradePlan(
        strategy_id="ST-C3",
        direction="LONG" if direction == "BULLISH" else "SHORT",
        context={
            "htf_bias_id": bundle.htf_bias.id,
            "sweep_id": bundle.sweep.id,
            "sweep_reclaim_id": bundle.sweep_reclaim.id,
            "bos_id": bundle.bos.id,
            "bos_extreme_id": bundle.bos_extreme.id,
            "dealing_range_id": bundle.dealing_range.id,
            "ote_id": bundle.ote.id,
            "fvg_id": bundle.fvg.id,
            "orderblock_id": bundle.order_block.id,
            "ltf_confirmation_id": bundle.ltf_confirmation.id,
            "session_window_id": bundle.session_window.id,
        },
        entry={
            "entry_zone_type": entry_zone_type,
            "entry_zone_id": entry_zone_id,
            "entry_price": bundle.entry_price,
            "entry_window_id": bundle.entry_window.id,
            "max_entry_bars": bundle.entry_window.get("max_allowed_bars"),
            "bars_since_ltf_choch": bundle.entry_window.get("bars_since_ltf_choch"),
        },
        risk={
            "sl_price": bundle.invalidation_swing.get("swing_level"),
            "sl_type": "STRUCTURAL_INVALIDATION",
            "risk_per_trade_pct": bundle.risk_per_trade_pct,
            "min_rr_required": bundle.min_rr,
            "computed_rr": bundle.computed_rr,
        },
        targets={
            "tp1": {
                "target_id": bundle.target_tp1.id,
                "target_type": "TP1_INTERNAL",
                "price": bundle.target_tp1.get("level"),
                "rr": bundle.target_tp1.get("rr"),
            },
            "tp2": {
                "target_id": bundle.target_tp2.id,
                "target_type": "TP2_EXTERNAL",
                "price": bundle.target_tp2.get("level"),
                "rr": bundle.target_tp2.get("rr"),
            },
            "tp3": {
                "target_id": bundle.target_tp3.id,
                "target_type": "TP3_HTF",
                "price": bundle.target_tp3.get("level"),
                "rr": bundle.target_tp3.get("rr"),
            },
        },
        expiry={
            "rules": ("BIAS_FLIP", "ENTRY_WINDOW", "SL_BREAK", "SUPERSEDED"),
            "expiry_evidence_id": bundle.expiry.id if bundle.expiry else None,
        },
        evidence_chain=evidence_chain,
        status={"state": "VALID", "code": None, "reason": None},
        meta={
            "tf_stack": ("H4", "M15", "M3", "M1"),
            "session": bundle.session_window.get("session"),
            "provenance": "STC3_v1",
        },
    )


def evaluate_expiry(expiry_reason: str) -> Termination:
    """Deterministic post-S13 expiry-reason -> ERR-code mapping
    (`expiry_termination_map` in the frozen spec). No monitoring loop, no
    execution — a pure lookup for use by a future Stage B consumer.
    """
    mapping = {
        "BIAS_FLIP": ("ERR_HTF_BIAS_FLIP", "macro_structure_changed"),
        "ENTRY_WINDOW": ("ERR_ENTRY_WINDOW_EXPIRED", "trade_timing_invalidated"),
        "SL_BREAK": ("ERR_SL_INVALIDATION", "setup_structurally_broken"),
        "SUPERSEDED": ("ERR_SUPERSEDED_SETUP", "newer_higher_priority_setup_exists"),
    }
    if expiry_reason not in mapping:
        raise ValueError(f"Unknown expiry reason: {expiry_reason!r}")
    code, reason = mapping[expiry_reason]
    return Termination(code=code, reason=reason)
