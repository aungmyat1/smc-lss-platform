"""ST-C3 A2/S1-G2 golden-case tests (Phase 3).

Each case must visit every state through S13, and the emitted TRADE_PLAN
must carry the full evidence chain. See fixtures.py for why evidence is
hand-built rather than derived from raw price data.
"""
from __future__ import annotations

from validation.st_c3.kernel import STATE_ORDER, run_kernel

from fixtures import long_bundle, short_bundle

ALL_STATES = STATE_ORDER + ("S13_TRADE_PLAN_EMIT",)


def test_golden_long_reaches_trade_plan_emit():
    result = run_kernel(long_bundle())
    assert result.outcome == "VALID"
    assert result.states_reached == ("S0_INIT",) + ALL_STATES
    assert result.rejection is None
    tp = result.trade_plan
    assert tp is not None
    assert tp.direction == "LONG"
    assert tp.status["state"] == "VALID"
    assert tp.entry["entry_zone_type"] == "FVG"
    assert tp.risk["computed_rr"] >= tp.risk["min_rr_required"]
    assert len(tp.evidence_chain) == 15
    assert all(tp.evidence_chain)


def test_golden_short_reaches_trade_plan_emit():
    result = run_kernel(short_bundle())
    assert result.outcome == "VALID"
    assert result.states_reached == ("S0_INIT",) + ALL_STATES
    tp = result.trade_plan
    assert tp is not None
    assert tp.direction == "SHORT"
    assert tp.meta["session"] == "NY"
    assert tp.risk["sl_price"] == 1.1985
    assert tp.targets["tp1"]["target_type"] == "TP1_INTERNAL"
    assert tp.targets["tp2"]["target_type"] == "TP2_EXTERNAL"
    assert tp.targets["tp3"]["target_type"] == "TP3_HTF"


def test_golden_cases_use_order_block_fallback_when_no_fvg():
    import dataclasses

    from validation.st_c3.evidence import make_evidence

    base = long_bundle()
    bundle = dataclasses.replace(
        base,
        fvg=make_evidence(
            "FVGEvidence", id="FVG-L1-NONE", tf=["H4", "M15"], valid=False,
            reason="no_fresh_fvg", timestamp="2026-07-20 07:05",
            gap_top=0.0, gap_bottom=0.0, fresh=False, inside_ote=False,
        ),
        order_block=make_evidence(
            "OrderBlockEvidence", id="OB-L1-VALID", tf=["H4", "M15"], valid=True,
            reason="fresh_ob_inside_ote", timestamp="2026-07-20 07:05",
            ob_high=1.1030, ob_low=1.1018, fresh=True, inside_ote=True,
        ),
    )
    result = run_kernel(bundle)
    assert result.outcome == "VALID"
    assert result.trade_plan.entry["entry_zone_type"] == "ORDERBLOCK"
    assert result.trade_plan.entry["entry_zone_id"] == "OB-L1-VALID"
