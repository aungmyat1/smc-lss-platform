"""Small, hand-built evidence-bundle set for the existence-check readiness
pass only (`validation/run_st_c3_existence_readiness.py`). Not real market
data and not the R-18 existence-check floor computation — see that module's
docstring.
"""
from __future__ import annotations

import dataclasses

from validation.st_c3.evidence import make_evidence
from validation.st_c3.kernel import EvidenceBundle


def _valid_long() -> EvidenceBundle:
    return EvidenceBundle(
        htf_bias=make_evidence("HTFBiasEvidence", id="R-HTF-1", tf="H4", valid=True, reason="ok", timestamp="t", structure="HHHL", bias="BULLISH"),
        sweep=make_evidence("SweepEvidence", id="R-SWEEP-1", tf=["H4", "M15"], valid=True, reason="ok", timestamp="t", sweep_type="SELL_SIDE", wick_penetration=True, level=1.1),
        sweep_reclaim=make_evidence("SweepReclaimEvidence", id="R-RECLAIM-1", tf=["H4", "M15"], valid=True, reason="ok", timestamp="t", reclaim_within_bars=1, max_allowed_bars=3, reclaimed=True),
        displacement=make_evidence("DisplacementEvidence", id="R-DISP-1", tf="M15", valid=True, reason="ok", timestamp="t", impulse_strength=0.7, threshold=0.6),
        bos=make_evidence("BOSEvidence", id="R-BOS-1", tf="M15", valid=True, reason="ok", timestamp="t", bos_direction="UP", body_close_break=True, level=1.11),
        bos_extreme=make_evidence("BOSExtremeEvidence", id="R-BOSX-1", tf="M15", valid=True, reason="ok", timestamp="t", provisional_extreme=1.11, locked_extreme=1.11, pullback_detected=True),
        dealing_range=make_evidence("DealingRangeEvidence", id="R-DR-1", tf="M15", valid=True, reason="ok", timestamp="t", origin=1.1, bos_extreme=1.11, range_size=0.01),
        ote=make_evidence("OTEEvidence", id="R-OTE-1", tf="M15", valid=True, reason="ok", timestamp="t", ote_min=1.102, ote_max=1.103, price_in_ote=True),
        fvg=make_evidence("FVGEvidence", id="R-FVG-1", tf=["H4", "M15"], valid=True, reason="ok", timestamp="t", gap_top=1.103, gap_bottom=1.102, fresh=True, inside_ote=True),
        order_block=make_evidence("OrderBlockEvidence", id="R-OB-1", tf=["H4", "M15"], valid=False, reason="none", timestamp="t", ob_high=0.0, ob_low=0.0, fresh=False, inside_ote=False),
        ltf_confirmation=make_evidence("LTFConfirmationEvidence", id="R-LTF-1", tf=["M3", "M1"], valid=True, reason="ok", timestamp="t", choch_direction="UP", sweep_local_liquidity=True),
        session_window=make_evidence("SessionWindowEvidence", id="R-SESS-1", tf=["M3", "M1"], valid=True, reason="ok", timestamp="t", session="LONDON"),
        entry_window=make_evidence("EntryWindowEvidence", id="R-EW-1", tf=["M3", "M1"], valid=True, reason="ok", timestamp="t", bars_since_ltf_choch=1, max_allowed_bars=5, inside_window=True),
        invalidation_swing=make_evidence("InvalidationSwingEvidence", id="R-INV-1", tf=["M3", "M1"], valid=True, reason="ok", timestamp="t", swing_level=1.101, direction="LONG"),
        target_tp1=make_evidence("TargetEvidence", id="R-TP1-1", tf=["H4", "M15"], valid=True, reason="ok", timestamp="t", target_type="TP1_INTERNAL", level=1.11, rr=3.2),
        target_tp2=make_evidence("TargetEvidence", id="R-TP2-1", tf=["H4", "M15"], valid=True, reason="ok", timestamp="t", target_type="TP2_EXTERNAL", level=1.115, rr=4.0),
        target_tp3=make_evidence("TargetEvidence", id="R-TP3-1", tf=["H4", "M15"], valid=True, reason="ok", timestamp="t", target_type="TP3_HTF", level=1.12, rr=5.5),
        computed_rr=3.2,
        min_rr=3.0,
        entry_price=1.1025,
        risk_per_trade_pct=0.5,
    )


def readiness_bundles() -> list[EvidenceBundle]:
    valid = _valid_long()
    no_sweep = dataclasses.replace(
        valid,
        sweep=make_evidence("SweepEvidence", id="R-SWEEP-BAD", tf=["H4", "M15"], valid=False, reason="no_external_liquidity_sweep", timestamp="t", sweep_type="SELL_SIDE", wick_penetration=False, level=1.1),
    )
    no_ote = dataclasses.replace(
        valid,
        ote=make_evidence("OTEEvidence", id="R-OTE-BAD", tf="M15", valid=False, reason="retrace_outside_ote", timestamp="t", ote_min=1.102, ote_max=1.103, price_in_ote=False),
    )
    rr_too_low = dataclasses.replace(valid, computed_rr=1.0, min_rr=3.0)
    return [valid, no_sweep, no_ote, rr_too_low]
