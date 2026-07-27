"""S1-G5 (Signal and Trade-Plan Conformance) evidence.

Per MASTER_PLAN.md's A2/S1-G5 purpose (its only stated requirement --
there is no separate "Required evidence" bullet list for this gate,
unlike S1-G3/S1-G4; see S1_G5_READINESS_CHECKLIST.md for that
verification):

    verify BUY/SELL, entry, stop, target, RR, expiration, source event
    IDs, and rejection reasons match the frozen strategy contract.

Each concept below maps to one or more TRADE_PLAN fields
(`validation/st_c3/trade_plan.py`, populated by
`kernel.py::_emit_trade_plan()`) or a rejection field
(`kernel.py::Rejection`), tested against the frozen
`specs/st-c3_v1.0.7.yaml` trade_plan.schema and the hand-built golden/
negative fixtures. Some fields (direction, entry_zone_type, computed_rr
inequality, target_type, evidence_chain length) already had coverage in
test_golden_cases.py/test_negative_cases.py; this file adds the exact-value
checks those files did not perform (e.g. SL price for the LONG case,
per-target price/rr/target_id, entry_price, rejection.reason text, and
evidence_chain ID-by-ID ordering).
"""
from __future__ import annotations

import dataclasses

import pytest

from validation.st_c3.evidence import make_evidence
from validation.st_c3.kernel import run_kernel

from fixtures import long_bundle, short_bundle


# ---------------------------------------------------------------------
# BUY/SELL (direction)
# ---------------------------------------------------------------------
def test_bullish_htf_bias_maps_to_long_direction():
    tp = run_kernel(long_bundle()).trade_plan
    assert tp.direction == "LONG"


def test_bearish_htf_bias_maps_to_short_direction():
    tp = run_kernel(short_bundle()).trade_plan
    assert tp.direction == "SHORT"


# ---------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------
def test_entry_price_and_zone_match_bundle_inputs_exactly():
    bundle = long_bundle()
    tp = run_kernel(bundle).trade_plan
    assert tp.entry["entry_price"] == bundle.entry_price
    assert tp.entry["entry_zone_type"] == "FVG"
    assert tp.entry["entry_zone_id"] == bundle.fvg.id
    assert tp.entry["entry_window_id"] == bundle.entry_window.id
    assert tp.entry["max_entry_bars"] == bundle.entry_window.get("max_allowed_bars")
    assert tp.entry["bars_since_ltf_choch"] == bundle.entry_window.get("bars_since_ltf_choch")


def test_entry_uses_order_block_id_when_fvg_invalid():
    base = long_bundle()
    bundle = dataclasses.replace(
        base,
        fvg=make_evidence(
            "FVGEvidence", id="FVG-NONE", tf=["H4", "M15"], valid=False,
            reason="no_fresh_fvg", timestamp="2026-07-20 07:05",
            gap_top=0.0, gap_bottom=0.0, fresh=False, inside_ote=False,
        ),
        order_block=make_evidence(
            "OrderBlockEvidence", id="OB-VALID", tf=["H4", "M15"], valid=True,
            reason="fresh_ob_inside_ote", timestamp="2026-07-20 07:05",
            ob_high=1.1030, ob_low=1.1018, fresh=True, inside_ote=True,
        ),
    )
    tp = run_kernel(bundle).trade_plan
    assert tp.entry["entry_zone_type"] == "ORDERBLOCK"
    assert tp.entry["entry_zone_id"] == "OB-VALID"


# ---------------------------------------------------------------------
# Stop
# ---------------------------------------------------------------------
def test_stop_price_and_type_match_bundle_for_long():
    bundle = long_bundle()
    tp = run_kernel(bundle).trade_plan
    assert tp.risk["sl_price"] == bundle.invalidation_swing.get("swing_level")
    assert tp.risk["sl_price"] == pytest.approx(1.1015)
    assert tp.risk["sl_type"] == "STRUCTURAL_INVALIDATION"


def test_stop_price_and_type_match_bundle_for_short():
    bundle = short_bundle()
    tp = run_kernel(bundle).trade_plan
    assert tp.risk["sl_price"] == bundle.invalidation_swing.get("swing_level")
    assert tp.risk["sl_price"] == pytest.approx(1.1985)
    assert tp.risk["sl_type"] == "STRUCTURAL_INVALIDATION"


# ---------------------------------------------------------------------
# Target
# ---------------------------------------------------------------------
@pytest.mark.parametrize("bundle_fn", [long_bundle, short_bundle])
def test_all_three_targets_match_bundle_inputs_exactly(bundle_fn):
    bundle = bundle_fn()
    tp = run_kernel(bundle).trade_plan
    for key, ev in (("tp1", bundle.target_tp1), ("tp2", bundle.target_tp2), ("tp3", bundle.target_tp3)):
        assert tp.targets[key]["target_id"] == ev.id
        assert tp.targets[key]["target_type"] == ev.get("target_type")
        assert tp.targets[key]["price"] == ev.get("level")
        assert tp.targets[key]["rr"] == ev.get("rr")


def test_target_types_are_tp1_internal_tp2_external_tp3_htf():
    tp = run_kernel(long_bundle()).trade_plan
    assert tp.targets["tp1"]["target_type"] == "TP1_INTERNAL"
    assert tp.targets["tp2"]["target_type"] == "TP2_EXTERNAL"
    assert tp.targets["tp3"]["target_type"] == "TP3_HTF"


# ---------------------------------------------------------------------
# RR
# ---------------------------------------------------------------------
def test_computed_rr_and_min_rr_match_bundle_exactly():
    bundle = long_bundle()
    tp = run_kernel(bundle).trade_plan
    assert tp.risk["computed_rr"] == bundle.computed_rr
    assert tp.risk["min_rr_required"] == bundle.min_rr
    assert tp.risk["computed_rr"] >= tp.risk["min_rr_required"]


def test_risk_per_trade_pct_matches_bundle():
    bundle = long_bundle()
    tp = run_kernel(bundle).trade_plan
    assert tp.risk["risk_per_trade_pct"] == bundle.risk_per_trade_pct


def test_rr_exactly_at_minimum_still_passes_s12():
    bundle = dataclasses.replace(long_bundle(), computed_rr=3.0, min_rr=3.0)
    result = run_kernel(bundle)
    assert result.outcome == "VALID"
    assert result.trade_plan.risk["computed_rr"] == 3.0


def test_rr_fractionally_below_minimum_rejects_r8():
    bundle = dataclasses.replace(long_bundle(), computed_rr=2.999, min_rr=3.0)
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.code == "R8_INVALID_RISK_OR_TARGET"


# ---------------------------------------------------------------------
# Expiration
# ---------------------------------------------------------------------
def test_expiry_rules_and_default_evidence_id_on_valid_trade_plan():
    tp = run_kernel(long_bundle()).trade_plan
    assert tp.expiry["rules"] == ("BIAS_FLIP", "ENTRY_WINDOW", "SL_BREAK", "SUPERSEDED")
    assert tp.expiry["expiry_evidence_id"] is None


def test_expiry_evidence_id_populated_when_supplied():
    bundle = dataclasses.replace(
        long_bundle(),
        expiry=make_evidence(
            "ExpiryEvidence", id="EXPIRY-L1", tf="M15", valid=True,
            reason="htf_bias_flipped", timestamp="2026-07-20 08:00",
            expiry_reason="BIAS_FLIP",
        ),
    )
    tp = run_kernel(bundle).trade_plan
    assert tp.expiry["expiry_evidence_id"] == "EXPIRY-L1"


# ---------------------------------------------------------------------
# Source event IDs (evidence_chain)
# ---------------------------------------------------------------------
def test_evidence_chain_ids_match_source_evidence_in_declared_order():
    bundle = long_bundle()
    tp = run_kernel(bundle).trade_plan
    expected = (
        bundle.htf_bias.id, bundle.sweep.id, bundle.sweep_reclaim.id,
        bundle.displacement.id, bundle.bos.id, bundle.bos_extreme.id,
        bundle.dealing_range.id, bundle.ote.id, bundle.fvg.id,
        bundle.order_block.id, bundle.ltf_confirmation.id,
        bundle.session_window.id, bundle.entry_window.id,
        bundle.invalidation_swing.id, bundle.target_tp1.id,
    )
    assert tp.evidence_chain == expected
    assert len(tp.evidence_chain) == 15


def test_context_ids_match_source_evidence():
    bundle = long_bundle()
    tp = run_kernel(bundle).trade_plan
    assert tp.context["htf_bias_id"] == bundle.htf_bias.id
    assert tp.context["sweep_id"] == bundle.sweep.id
    assert tp.context["sweep_reclaim_id"] == bundle.sweep_reclaim.id
    assert tp.context["bos_id"] == bundle.bos.id
    assert tp.context["bos_extreme_id"] == bundle.bos_extreme.id
    assert tp.context["dealing_range_id"] == bundle.dealing_range.id
    assert tp.context["ote_id"] == bundle.ote.id
    assert tp.context["fvg_id"] == bundle.fvg.id
    assert tp.context["orderblock_id"] == bundle.order_block.id
    assert tp.context["ltf_confirmation_id"] == bundle.ltf_confirmation.id
    assert tp.context["session_window_id"] == bundle.session_window.id


# ---------------------------------------------------------------------
# Rejection reasons
# ---------------------------------------------------------------------
@pytest.mark.parametrize("field_name, kind, extra, expected_reason, rejected_state, code", [
    ("htf_bias", "HTFBiasEvidence",
     dict(structure="UNCLEAR", bias="NONE"), "h4_structure_ambiguous", "S1_HTF_BIAS", "R1_HTF_BIAS_UNCLEAR"),
    ("sweep", "SweepEvidence",
     dict(sweep_type="SELL_SIDE", wick_penetration=False, level=1.1000), "sweep_wick_does_not_penetrate_level", "S2_SWEEP", "R2_NO_SWEEP"),
    ("displacement", "DisplacementEvidence",
     dict(impulse_strength=0.1, threshold=0.6), "no_impulsive_move_after_sweep", "S4_DISPLACEMENT_BOS", "R3_NO_DISPLACEMENT_BOS"),
    ("ote", "OTEEvidence",
     dict(ote_min=1.1017, ote_max=1.1030, price_in_ote=False), "retrace_outside_ote", "S7_OTE", "R4_NO_OTE_PULLBACK"),
    ("ltf_confirmation", "LTFConfirmationEvidence",
     dict(choch_direction="DOWN", sweep_local_liquidity=False), "no_m3_m1_choch_or_bos_inside_confluence", "S9_LTF_CONFIRMATION", "R6_NO_LTF_CONFIRMATION"),
    ("entry_window", "EntryWindowEvidence",
     dict(bars_since_ltf_choch=9, max_allowed_bars=5, inside_window=False), "max_entry_bars_exceeded", "S11_ENTRY_WINDOW", "R7_ENTRY_WINDOW_EXPIRED"),
])
def test_rejection_reason_text_matches_the_invalidated_evidences_own_reason(
    field_name, kind, extra, expected_reason, rejected_state, code,
):
    invalid_evidence = make_evidence(
        kind, id="X", tf="M15", valid=False, reason=expected_reason,
        timestamp="2026-07-20 05:00", **extra,
    )
    bundle = dataclasses.replace(long_bundle(), **{field_name: invalid_evidence})
    result = run_kernel(bundle)
    assert result.outcome == "REJECTED"
    assert result.rejection.state == rejected_state
    assert result.rejection.code == code
    assert result.rejection.reason == expected_reason
    assert result.rejection.evidence_id == "X"
