"""ST-C3 A2/S1-G2 negative-case tests (Phase 4).

Each case starts from the valid `long_bundle()` golden fixture and invalidates
exactly one evidence object, asserting the funnel stops at the corresponding
state with exactly one R-code and no TRADE_PLAN emission.
"""
from __future__ import annotations

import dataclasses

from validation.st_c3.evidence import make_evidence
from validation.st_c3.kernel import run_kernel

from fixtures import long_bundle


def _invalid(kind: str, id_: str, reason: str, **extra_fields):
    return make_evidence(
        kind, id=id_, tf="M15", valid=False, reason=reason,
        timestamp="2026-07-20 05:00", **extra_fields,
    )


def test_invalid_htf_bias_rejects_r1():
    bundle = dataclasses.replace(
        long_bundle(),
        htf_bias=_invalid("HTFBiasEvidence", "HTF_BIAS-BAD", "h4_structure_ambiguous", structure="UNCLEAR", bias="NONE"),
    )
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R1_HTF_BIAS_UNCLEAR"
    assert result.rejection.state == "S1_HTF_BIAS"
    assert result.states_reached == ("S0_INIT",)
    assert result.trade_plan is None


def test_invalid_sweep_rejects_r2():
    bundle = dataclasses.replace(
        long_bundle(),
        sweep=_invalid("SweepEvidence", "SWEEP-BAD", "sweep_wick_does_not_penetrate_level", sweep_type="SELL_SIDE", wick_penetration=False, level=1.1000),
    )
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R2_NO_SWEEP"
    assert result.rejection.state == "S2_SWEEP"
    assert result.trade_plan is None


def test_sweep_not_reclaimed_rejects_r2():
    bundle = dataclasses.replace(
        long_bundle(),
        sweep_reclaim=_invalid(
            "SweepReclaimEvidence", "SWEEP_RECLAIM-BAD", "sweep_reclaim_exceeds_n_sweep",
            reclaim_within_bars=5, max_allowed_bars=3, reclaimed=False,
        ),
    )
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R2_NO_SWEEP"
    assert result.rejection.state == "S3_SWEEP_RECLAIM"
    assert result.trade_plan is None


def test_invalid_displacement_rejects_r3():
    bundle = dataclasses.replace(
        long_bundle(),
        displacement=_invalid("DisplacementEvidence", "DISPLACEMENT-BAD", "no_impulsive_move_after_sweep", impulse_strength=0.1, threshold=0.6),
    )
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R3_NO_DISPLACEMENT_BOS"
    assert result.rejection.state == "S4_DISPLACEMENT_BOS"
    assert result.trade_plan is None


def test_invalid_bos_rejects_r3():
    bundle = dataclasses.replace(
        long_bundle(),
        bos=_invalid("BOSEvidence", "BOS-BAD", "bos_no_body_close_break", bos_direction="UP", body_close_break=False, level=1.1050),
    )
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R3_NO_DISPLACEMENT_BOS"
    assert result.rejection.state == "S4_DISPLACEMENT_BOS"
    assert result.trade_plan is None


def test_no_bos_extreme_pullback_rejects_r3():
    bundle = dataclasses.replace(
        long_bundle(),
        bos_extreme=_invalid(
            "BOSExtremeEvidence", "BOS_EXTREME-BAD", "bos_extreme_pullback_not_detected",
            provisional_extreme=1.1080, locked_extreme=None, pullback_detected=False,
        ),
    )
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R3_NO_DISPLACEMENT_BOS"
    assert result.rejection.state == "S5_BOS_EXTREME_LOCK"
    assert result.trade_plan is None


def test_invalid_dealing_range_rejects_r4():
    bundle = dataclasses.replace(
        long_bundle(),
        dealing_range=_invalid(
            "DealingRangeEvidence", "DEALING_RANGE-BAD", "dealing_range_invalid_or_undefined",
            origin=None, bos_extreme=None, range_size=0.0,
        ),
    )
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R4_NO_OTE_PULLBACK"
    assert result.rejection.state == "S6_DEALING_RANGE"
    assert result.trade_plan is None


def test_invalid_ote_rejects_r4():
    bundle = dataclasses.replace(
        long_bundle(),
        ote=_invalid("OTEEvidence", "OTE-BAD", "retrace_outside_ote", ote_min=1.1017, ote_max=1.1030, price_in_ote=False),
    )
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R4_NO_OTE_PULLBACK"
    assert result.rejection.state == "S7_OTE"
    assert result.trade_plan is None


def test_invalid_fvg_and_orderblock_rejects_r5():
    base = long_bundle()
    bundle = dataclasses.replace(
        base,
        fvg=_invalid("FVGEvidence", "FVG-BAD", "no_fresh_fvg_or_ob_inside_ote", gap_top=0.0, gap_bottom=0.0, fresh=False, inside_ote=False),
        # order_block already invalid=False in the golden fixture
    )
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R5_NO_FVG_OB_CONFLUENCE"
    assert result.rejection.state == "S8_FVG_OB_CONFLUENCE"
    assert result.trade_plan is None


def test_invalid_ltf_confirmation_rejects_r6():
    bundle = dataclasses.replace(
        long_bundle(),
        ltf_confirmation=_invalid(
            "LTFConfirmationEvidence", "LTF_CONF-BAD", "no_m3_m1_choch_or_bos_inside_confluence",
            choch_direction="DOWN", sweep_local_liquidity=False,
        ),
    )
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R6_NO_LTF_CONFIRMATION"
    assert result.rejection.state == "S9_LTF_CONFIRMATION"
    assert result.trade_plan is None


def test_invalid_session_rejects_r6():
    bundle = dataclasses.replace(
        long_bundle(),
        session_window=_invalid("SessionWindowEvidence", "SESSION-BAD", "choch_outside_allowed_sessions", session="INVALID"),
    )
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R6_NO_LTF_CONFIRMATION"
    assert result.rejection.state == "S10_SESSION_GATEKEEPER"
    assert result.trade_plan is None


def test_entry_window_expired_rejects_r7():
    bundle = dataclasses.replace(
        long_bundle(),
        entry_window=_invalid(
            "EntryWindowEvidence", "ENTRY_WINDOW-BAD", "max_entry_bars_exceeded",
            bars_since_ltf_choch=9, max_allowed_bars=5, inside_window=False,
        ),
    )
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R7_ENTRY_WINDOW_EXPIRED"
    assert result.rejection.state == "S11_ENTRY_WINDOW"
    assert result.trade_plan is None


def test_invalid_structural_invalidation_swing_rejects_r8():
    bundle = dataclasses.replace(
        long_bundle(),
        invalidation_swing=_invalid(
            "InvalidationSwingEvidence", "INVALIDATION-BAD", "invalidation_swing_undefined_or_ambiguous",
            swing_level=None, direction="LONG",
        ),
    )
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R8_INVALID_RISK_OR_TARGET"
    assert result.rejection.state == "S12_RISK_SLTP"
    assert result.trade_plan is None


def test_rr_below_minimum_rejects_r8():
    bundle = dataclasses.replace(long_bundle(), computed_rr=1.5, min_rr=3.0)
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R8_INVALID_RISK_OR_TARGET"
    assert result.rejection.state == "S12_RISK_SLTP"
    assert result.trade_plan is None


def test_session_not_open_does_not_start_funnel():
    bundle = dataclasses.replace(long_bundle(), session_open=False)
    result = run_kernel(bundle)
    assert result.outcome == "NOT_STARTED"
    assert result.states_reached == ()
    assert result.rejection is None
    assert result.trade_plan is None


def test_evidence_construction_rejects_unknown_and_missing_fields():
    import pytest

    with pytest.raises(ValueError):
        make_evidence(
            "HTFBiasEvidence", id="X", tf="H4", valid=True, reason="r",
            timestamp="t", structure="HHHL",  # missing 'bias'
        )
    with pytest.raises(ValueError):
        make_evidence(
            "HTFBiasEvidence", id="X", tf="H4", valid=True, reason="r",
            timestamp="t", structure="HHHL", bias="BULLISH", extra_field="nope",
        )
