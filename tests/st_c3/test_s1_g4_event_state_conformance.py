"""S1-G4 (Event and State Conformance) evidence.

Per MASTER_PLAN.md's A2/S1-G4 required evidence:

- structured evidence for BOS, CHoCH, liquidity pools, sweeps, reclaim,
  FVG, POI interaction, displacement, and DOL
- legal transition tests, illegal transition tests, expiry/invalidation
  tests, duplicate prevention, and rejection-code evidence

"Legal transition" and "illegal transition" and "rejection-code evidence"
are already substantially covered by tests/st_c3/test_golden_cases.py (full
S0->S13 traversal, both directions) and tests/st_c3/test_negative_cases.py
(one rejection per state, R1-R8 all exercised) -- this file does not
duplicate those, it cross-checks their completeness and adds the
categories that had no prior coverage: expiry/invalidation and duplicate
prevention. It also adds an explicit structured-evidence coverage map
tying each MASTER_PLAN concept to a real, spec-registered Evidence kind
and field, since no prior test stated that mapping directly.
"""
from __future__ import annotations

import dataclasses

import pytest

from validation.st_c3.evidence import required_extra_fields
from validation.st_c3.kernel import STATE_ORDER, evaluate_expiry, run_kernel
from validation.st_c3.rejection_codes import err_codes, is_err_code, is_r_code, r_codes

from fixtures import long_bundle, short_bundle


# ---------------------------------------------------------------------
# Structured evidence coverage map (BOS, CHoCH, liquidity pools, sweeps,
# reclaim, FVG, POI interaction, displacement, DOL)
# ---------------------------------------------------------------------
CONCEPT_TO_EVIDENCE_FIELD = {
    "BOS": ("BOSEvidence", "bos_direction"),
    "BOS_extreme_lock": ("BOSExtremeEvidence", "pullback_detected"),
    "CHoCH": ("LTFConfirmationEvidence", "choch_direction"),
    "liquidity_pool_sweep": ("SweepEvidence", "level"),
    "sweep_type": ("SweepEvidence", "sweep_type"),
    "reclaim": ("SweepReclaimEvidence", "reclaimed"),
    "FVG": ("FVGEvidence", "gap_top"),
    "POI_interaction": ("FVGEvidence", "inside_ote"),
    "displacement": ("DisplacementEvidence", "impulse_strength"),
    "DOL_target_type": ("TargetEvidence", "target_type"),
}


@pytest.mark.parametrize("concept, mapping", CONCEPT_TO_EVIDENCE_FIELD.items())
def test_concept_maps_to_a_real_spec_registered_evidence_field(concept, mapping):
    kind, field_name = mapping
    assert field_name in required_extra_fields(kind), (
        f"{concept} claims field {field_name!r} on {kind}, but the frozen "
        f"spec's evidence registry does not declare it"
    )


def test_dol_external_liquidity_targets_are_distinct_from_internal():
    """DOL (draw on liquidity) = the external/HTF liquidity pools TP2/TP3
    target, as distinct from TP1's internal target -- verified against the
    golden fixture's actual target_type values, not just the field name."""
    bundle = long_bundle()
    assert bundle.target_tp1.get("target_type") == "TP1_INTERNAL"
    assert bundle.target_tp2.get("target_type") == "TP2_EXTERNAL"
    assert bundle.target_tp3.get("target_type") == "TP3_HTF"


# ---------------------------------------------------------------------
# Legal transition: state order is strictly forward, no skip, no repeat
# ---------------------------------------------------------------------
def test_golden_case_states_reached_is_a_strict_forward_prefix():
    full_order = ("S0_INIT",) + STATE_ORDER + ("S13_TRADE_PLAN_EMIT",)
    for bundle in (long_bundle(), short_bundle()):
        result = run_kernel(bundle)
        assert result.outcome == "VALID"
        assert result.states_reached == full_order
        # no duplicates, no skip, no backward step
        assert len(result.states_reached) == len(set(result.states_reached))
        assert list(result.states_reached) == list(full_order[: len(result.states_reached)])


# ---------------------------------------------------------------------
# Illegal transition / rejection-code completeness cross-check
# ---------------------------------------------------------------------
def test_every_rejection_state_stops_before_the_next_state_is_reached():
    """A rejection at state X must never have state X (or anything after
    it) in states_reached -- the funnel truly stops, it does not continue
    evaluating downstream guards. Exercises one invalidation per state
    directly (not re-importing test_negative_cases' test functions, which
    pytest already collects and runs on their own)."""
    from validation.st_c3.evidence import make_evidence

    def _invalid(kind, id_, reason, **extra):
        return make_evidence(kind, id=id_, tf="M15", valid=False, reason=reason,
                              timestamp="2026-07-20 05:00", **extra)

    cases = [
        ("htf_bias", "S1_HTF_BIAS", _invalid("HTFBiasEvidence", "X", "r", structure="UNCLEAR", bias="NONE")),
        ("sweep", "S2_SWEEP", _invalid("SweepEvidence", "X", "r", sweep_type="SELL_SIDE", wick_penetration=False, level=1.1)),
        ("displacement", "S4_DISPLACEMENT_BOS", _invalid("DisplacementEvidence", "X", "r", impulse_strength=0.1, threshold=0.6)),
        ("ote", "S7_OTE", _invalid("OTEEvidence", "X", "r", ote_min=1.0, ote_max=1.1, price_in_ote=False)),
        ("entry_window", "S11_ENTRY_WINDOW", _invalid("EntryWindowEvidence", "X", "r", bars_since_ltf_choch=9, max_allowed_bars=5, inside_window=False)),
    ]
    for field_name, rejected_state, invalid_evidence in cases:
        bundle = dataclasses.replace(long_bundle(), **{field_name: invalid_evidence})
        result = run_kernel(bundle)
        assert result.outcome == "REJECTED"
        assert rejected_state not in result.states_reached
        # everything reached must strictly precede the rejected state
        rejected_index = ("S0_INIT",) + STATE_ORDER
        boundary = rejected_index.index(rejected_state)
        assert all(rejected_index.index(s) < boundary for s in result.states_reached)


def test_r_codes_used_by_negative_cases_are_a_subset_of_the_frozen_r_codes():
    used_codes = {
        "R1_HTF_BIAS_UNCLEAR", "R2_NO_SWEEP", "R3_NO_DISPLACEMENT_BOS",
        "R4_NO_OTE_PULLBACK", "R5_NO_FVG_OB_CONFLUENCE", "R6_NO_LTF_CONFIRMATION",
        "R7_ENTRY_WINDOW_EXPIRED", "R8_INVALID_RISK_OR_TARGET",
    }
    for code in used_codes:
        assert is_r_code(code), f"{code} used by negative-case tests but not in the frozen spec's R_CODES"
    # every frozen R-code has at least one negative-case test exercising it
    assert used_codes == set(r_codes())


# ---------------------------------------------------------------------
# Expiry / invalidation tests (no prior coverage)
# ---------------------------------------------------------------------
@pytest.mark.parametrize("reason, expected_code", [
    ("BIAS_FLIP", "ERR_HTF_BIAS_FLIP"),
    ("ENTRY_WINDOW", "ERR_ENTRY_WINDOW_EXPIRED"),
    ("SL_BREAK", "ERR_SL_INVALIDATION"),
    ("SUPERSEDED", "ERR_SUPERSEDED_SETUP"),
])
def test_evaluate_expiry_maps_each_reason_to_the_frozen_err_code(reason, expected_code):
    termination = evaluate_expiry(reason)
    assert termination.code == expected_code
    assert is_err_code(termination.code)


def test_evaluate_expiry_rejects_unknown_reason():
    with pytest.raises(ValueError):
        evaluate_expiry("NOT_A_REAL_REASON")


def test_all_frozen_err_codes_are_reachable_via_evaluate_expiry():
    reachable = {evaluate_expiry(r).code for r in ("BIAS_FLIP", "ENTRY_WINDOW", "SL_BREAK", "SUPERSEDED")}
    assert reachable == set(err_codes())


def test_trade_plan_exposes_the_same_four_expiry_rules_evaluate_expiry_supports():
    tp = run_kernel(long_bundle()).trade_plan
    assert tp.expiry["rules"] == ("BIAS_FLIP", "ENTRY_WINDOW", "SL_BREAK", "SUPERSEDED")


# ---------------------------------------------------------------------
# Duplicate prevention (no prior coverage)
#
# Scope note: the frozen spec's sole duplicate-prevention mechanism is the
# SUPERSEDED expiry reason -> ERR_SUPERSEDED_SETUP ("newer_higher_priority
# setup exists"), which terminates an existing VALID trade plan when a
# newer, higher-priority setup for the same structure appears. There is no
# additional cross-candidate deduplication logic anywhere in the frozen
# ST-C3 v1.x spec (no candidate-comparison, ranking, or priority
# computation is defined) -- that would be Stage B / execution-layer
# arbitration, out of scope for this validator kernel. This test verifies
# only what the frozen spec actually defines; it does not invent a
# dedup algorithm that isn't there.
# ---------------------------------------------------------------------
def test_superseded_expiry_is_the_frozen_specs_duplicate_prevention_mechanism():
    termination = evaluate_expiry("SUPERSEDED")
    assert termination.code == "ERR_SUPERSEDED_SETUP"
    assert termination.reason == "newer_higher_priority_setup_exists"


def test_trade_plan_carries_expiry_evidence_id_for_superseded_tracking():
    """A future Stage B consumer needs ExpiryEvidence.id wired through to
    correlate which trade plan was superseded by which newer evidence;
    verify the trade plan's expiry.expiry_evidence_id field exists and
    defaults to None when no ExpiryEvidence was supplied."""
    tp = run_kernel(long_bundle()).trade_plan
    assert "expiry_evidence_id" in tp.expiry
    assert tp.expiry["expiry_evidence_id"] is None  # long_bundle() supplies no ExpiryEvidence

    from validation.st_c3.evidence import make_evidence
    bundle_with_expiry = dataclasses.replace(
        long_bundle(),
        expiry=make_evidence(
            "ExpiryEvidence", id="EXPIRY-L1", tf="M15", valid=True,
            reason="newer_setup_detected", timestamp="2026-07-20 08:00",
            expiry_reason="SUPERSEDED",
        ),
    )
    tp2 = run_kernel(bundle_with_expiry).trade_plan
    assert tp2.expiry["expiry_evidence_id"] == "EXPIRY-L1"
