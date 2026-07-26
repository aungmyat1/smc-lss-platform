"""Hand-curated ST-C3 evidence bundles for golden/negative-case tests.

These are constructed directly as Evidence objects (not derived from raw
candle detection) because several ST-C3 detection thresholds are still
`UNRESOLVED`/`PROVISIONAL` in the frozen `specs/st-c3_v1.0.1.yaml` — see
`validation/st_c3/__init__.py` for why. Each field value below is a
deliberately chosen, internally-consistent stand-in for "evidence a
detection module would have produced," not a claim about real price data.
"""
from __future__ import annotations

from validation.st_c3.evidence import make_evidence
from validation.st_c3.kernel import EvidenceBundle


def long_bundle() -> EvidenceBundle:
    return EvidenceBundle(
        htf_bias=make_evidence(
            "HTFBiasEvidence", id="HTF_BIAS-L1", tf="H4", valid=True,
            reason="valid_bullish_structure", timestamp="2026-07-20 00:00",
            structure="HHHL", bias="BULLISH",
        ),
        sweep=make_evidence(
            "SweepEvidence", id="SWEEP-L1", tf=["H4", "M15"], valid=True,
            reason="sell_side_liquidity_swept", timestamp="2026-07-20 04:00",
            sweep_type="SELL_SIDE", wick_penetration=True, level=1.1000,
        ),
        sweep_reclaim=make_evidence(
            "SweepReclaimEvidence", id="SWEEP_RECLAIM-L1", tf=["H4", "M15"], valid=True,
            reason="reclaimed_within_window", timestamp="2026-07-20 04:15",
            reclaim_within_bars=2, max_allowed_bars=3, reclaimed=True,
        ),
        displacement=make_evidence(
            "DisplacementEvidence", id="DISPLACEMENT-L1", tf="M15", valid=True,
            reason="impulsive_move_confirmed", timestamp="2026-07-20 05:00",
            impulse_strength=0.75, threshold=0.6,
        ),
        bos=make_evidence(
            "BOSEvidence", id="BOS-L1", tf="M15", valid=True,
            reason="body_close_break_up", timestamp="2026-07-20 05:15",
            bos_direction="UP", body_close_break=True, level=1.1050,
        ),
        bos_extreme=make_evidence(
            "BOSExtremeEvidence", id="BOS_EXTREME-L1", tf="M15", valid=True,
            reason="extreme_locked_after_pullback", timestamp="2026-07-20 06:00",
            provisional_extreme=1.1080, locked_extreme=1.1080, pullback_detected=True,
        ),
        dealing_range=make_evidence(
            "DealingRangeEvidence", id="DEALING_RANGE-L1", tf="M15", valid=True,
            reason="range_defined_origin_to_extreme", timestamp="2026-07-20 06:00",
            origin=1.1000, bos_extreme=1.1080, range_size=0.0080,
        ),
        ote=make_evidence(
            "OTEEvidence", id="OTE-L1", tf="M15", valid=True,
            reason="price_retraced_into_ote", timestamp="2026-07-20 07:00",
            ote_min=1.1017, ote_max=1.1030, price_in_ote=True,
        ),
        fvg=make_evidence(
            "FVGEvidence", id="FVG-L1", tf=["H4", "M15"], valid=True,
            reason="fresh_fvg_inside_ote", timestamp="2026-07-20 07:05",
            gap_top=1.1028, gap_bottom=1.1020, fresh=True, inside_ote=True,
        ),
        order_block=make_evidence(
            "OrderBlockEvidence", id="OB-L1", tf=["H4", "M15"], valid=False,
            reason="no_order_block_present", timestamp="2026-07-20 07:05",
            ob_high=0.0, ob_low=0.0, fresh=False, inside_ote=False,
        ),
        ltf_confirmation=make_evidence(
            "LTFConfirmationEvidence", id="LTF_CONF-L1", tf=["M3", "M1"], valid=True,
            reason="m3_choch_up_with_local_sweep", timestamp="2026-07-20 07:10",
            choch_direction="UP", sweep_local_liquidity=True,
        ),
        session_window=make_evidence(
            "SessionWindowEvidence", id="SESSION-L1", tf=["M3", "M1"], valid=True,
            reason="inside_london_window", timestamp="2026-07-20 07:10",
            session="LONDON",
        ),
        entry_window=make_evidence(
            "EntryWindowEvidence", id="ENTRY_WINDOW-L1", tf=["M3", "M1"], valid=True,
            reason="within_max_entry_bars", timestamp="2026-07-20 07:12",
            bars_since_ltf_choch=2, max_allowed_bars=5, inside_window=True,
        ),
        invalidation_swing=make_evidence(
            "InvalidationSwingEvidence", id="INVALIDATION-L1", tf=["M3", "M1"], valid=True,
            reason="m3_swing_defines_structural_stop", timestamp="2026-07-20 07:10",
            swing_level=1.1015, direction="LONG",
        ),
        target_tp1=make_evidence(
            "TargetEvidence", id="TARGET_TP1-L1", tf=["H4", "M15"], valid=True,
            reason="internal_liquidity_target", timestamp="2026-07-20 07:12",
            target_type="TP1_INTERNAL", level=1.1080, rr=3.2,
        ),
        target_tp2=make_evidence(
            "TargetEvidence", id="TARGET_TP2-L1", tf=["H4", "M15"], valid=True,
            reason="external_liquidity_target", timestamp="2026-07-20 07:12",
            target_type="TP2_EXTERNAL", level=1.1120, rr=4.5,
        ),
        target_tp3=make_evidence(
            "TargetEvidence", id="TARGET_TP3-L1", tf=["H4", "M15"], valid=True,
            reason="htf_liquidity_target", timestamp="2026-07-20 07:12",
            target_type="TP3_HTF", level=1.1200, rr=6.0,
        ),
        computed_rr=3.2,
        min_rr=3.0,
        entry_price=1.1022,
        risk_per_trade_pct=0.5,
    )


def short_bundle() -> EvidenceBundle:
    return EvidenceBundle(
        htf_bias=make_evidence(
            "HTFBiasEvidence", id="HTF_BIAS-S1", tf="H4", valid=True,
            reason="valid_bearish_structure", timestamp="2026-07-21 00:00",
            structure="LHLL", bias="BEARISH",
        ),
        sweep=make_evidence(
            "SweepEvidence", id="SWEEP-S1", tf=["H4", "M15"], valid=True,
            reason="buy_side_liquidity_swept", timestamp="2026-07-21 04:00",
            sweep_type="BUY_SIDE", wick_penetration=True, level=1.2000,
        ),
        sweep_reclaim=make_evidence(
            "SweepReclaimEvidence", id="SWEEP_RECLAIM-S1", tf=["H4", "M15"], valid=True,
            reason="reclaimed_within_window", timestamp="2026-07-21 04:15",
            reclaim_within_bars=1, max_allowed_bars=3, reclaimed=True,
        ),
        displacement=make_evidence(
            "DisplacementEvidence", id="DISPLACEMENT-S1", tf="M15", valid=True,
            reason="impulsive_move_confirmed", timestamp="2026-07-21 05:00",
            impulse_strength=0.80, threshold=0.6,
        ),
        bos=make_evidence(
            "BOSEvidence", id="BOS-S1", tf="M15", valid=True,
            reason="body_close_break_down", timestamp="2026-07-21 05:15",
            bos_direction="DOWN", body_close_break=True, level=1.1950,
        ),
        bos_extreme=make_evidence(
            "BOSExtremeEvidence", id="BOS_EXTREME-S1", tf="M15", valid=True,
            reason="extreme_locked_after_pullback", timestamp="2026-07-21 06:00",
            provisional_extreme=1.1920, locked_extreme=1.1920, pullback_detected=True,
        ),
        dealing_range=make_evidence(
            "DealingRangeEvidence", id="DEALING_RANGE-S1", tf="M15", valid=True,
            reason="range_defined_origin_to_extreme", timestamp="2026-07-21 06:00",
            origin=1.2000, bos_extreme=1.1920, range_size=0.0080,
        ),
        ote=make_evidence(
            "OTEEvidence", id="OTE-S1", tf="M15", valid=True,
            reason="price_retraced_into_ote", timestamp="2026-07-21 07:00",
            ote_min=1.1970, ote_max=1.1983, price_in_ote=True,
        ),
        fvg=make_evidence(
            "FVGEvidence", id="FVG-S1", tf=["H4", "M15"], valid=True,
            reason="fresh_fvg_inside_ote", timestamp="2026-07-21 07:05",
            gap_top=1.1980, gap_bottom=1.1972, fresh=True, inside_ote=True,
        ),
        order_block=make_evidence(
            "OrderBlockEvidence", id="OB-S1", tf=["H4", "M15"], valid=False,
            reason="no_order_block_present", timestamp="2026-07-21 07:05",
            ob_high=0.0, ob_low=0.0, fresh=False, inside_ote=False,
        ),
        ltf_confirmation=make_evidence(
            "LTFConfirmationEvidence", id="LTF_CONF-S1", tf=["M3", "M1"], valid=True,
            reason="m3_choch_down_with_local_sweep", timestamp="2026-07-21 07:10",
            choch_direction="DOWN", sweep_local_liquidity=True,
        ),
        session_window=make_evidence(
            "SessionWindowEvidence", id="SESSION-S1", tf=["M3", "M1"], valid=True,
            reason="inside_ny_window", timestamp="2026-07-21 07:10",
            session="NY",
        ),
        entry_window=make_evidence(
            "EntryWindowEvidence", id="ENTRY_WINDOW-S1", tf=["M3", "M1"], valid=True,
            reason="within_max_entry_bars", timestamp="2026-07-21 07:12",
            bars_since_ltf_choch=1, max_allowed_bars=5, inside_window=True,
        ),
        invalidation_swing=make_evidence(
            "InvalidationSwingEvidence", id="INVALIDATION-S1", tf=["M3", "M1"], valid=True,
            reason="m3_swing_defines_structural_stop", timestamp="2026-07-21 07:10",
            swing_level=1.1985, direction="SHORT",
        ),
        target_tp1=make_evidence(
            "TargetEvidence", id="TARGET_TP1-S1", tf=["H4", "M15"], valid=True,
            reason="internal_liquidity_target", timestamp="2026-07-21 07:12",
            target_type="TP1_INTERNAL", level=1.1920, rr=3.1,
        ),
        target_tp2=make_evidence(
            "TargetEvidence", id="TARGET_TP2-S1", tf=["H4", "M15"], valid=True,
            reason="external_liquidity_target", timestamp="2026-07-21 07:12",
            target_type="TP2_EXTERNAL", level=1.1880, rr=4.2,
        ),
        target_tp3=make_evidence(
            "TargetEvidence", id="TARGET_TP3-S1", tf=["H4", "M15"], valid=True,
            reason="htf_liquidity_target", timestamp="2026-07-21 07:12",
            target_type="TP3_HTF", level=1.1800, rr=5.8,
        ),
        computed_rr=3.1,
        min_rr=3.0,
        entry_price=1.1976,
        risk_per_trade_pct=0.5,
    )
