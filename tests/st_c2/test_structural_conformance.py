from __future__ import annotations

from decimal import Decimal

from validation import st_c2_reference as stc2
from validation.st_c2.structure import (
    DealingRange,
    build_liquidity_pools,
    classify_htf_bias,
    detect_htf_structure,
    detect_sweep_and_reclaim,
    evaluate_ote_location,
    select_liquidity_pool,
    structural_context,
)
from validation.st_c2.symbols import load_symbol_metadata


def bar(t, o, h, l, c):
    return {"time": t, "open": o, "high": h, "low": l, "close": c}


def gc2_long_htf():
    return [
        bar("2026-01-01 00:00", 1.1000, 1.1050, 1.0980, 1.1010),
        bar("2026-01-01 04:00", 1.1010, 1.1080, 1.0990, 1.1060),
        bar("2026-01-01 08:00", 1.1060, 1.1120, 1.1040, 1.1100),
        bar("2026-01-01 12:00", 1.1100, 1.1200, 1.1080, 1.1150),
        bar("2026-01-01 16:00", 1.1150, 1.1160, 1.1060, 1.1080),
        bar("2026-01-01 20:00", 1.1080, 1.1100, 1.1010, 1.1030),
        bar("2026-01-02 00:00", 1.1030, 1.1060, 1.0980, 1.1000),
        bar("2026-01-02 04:00", 1.1000, 1.1040, 1.0950, 1.0980),
        bar("2026-01-02 08:00", 1.0980, 1.1050, 1.0970, 1.1030),
        bar("2026-01-02 12:00", 1.1030, 1.1120, 1.1020, 1.1100),
        bar("2026-01-02 16:00", 1.1100, 1.1230, 1.1090, 1.1210),
        bar("2026-01-02 20:00", 1.1000, 1.1030, 1.0940, 1.1010),
        bar("2026-01-03 00:00", 1.1010, 1.1180, 1.1000, 1.1120),
    ]


def gc2_long_mf(close=1.1010):
    return [bar("2026-01-02 00:45", 1.1010, 1.1011, 1.0992, close)]


def _spec_meta():
    return stc2.load_spec(), load_symbol_metadata("GBPUSD")


def test_htf_bias_uses_closed_candle_bos_choch_not_wick_only():
    spec, meta = _spec_meta()
    valid_events = detect_htf_structure(gc2_long_htf(), spec=spec, symbol_metadata=meta)
    valid_bias = classify_htf_bias(valid_events, spec=spec, symbol_metadata=meta)
    assert valid_bias.direction == "long"
    assert valid_bias.reason == "BULLISH_BOS"
    assert valid_bias.bias_evidence_type == "BOS"

    wick_only = list(gc2_long_htf())
    wick_only[10] = bar("2026-01-02 16:00", 1.1100, 1.1230, 1.1090, 1.1190)
    rejected_events = detect_htf_structure(wick_only, spec=spec, symbol_metadata=meta)
    rejected_bias = classify_htf_bias(rejected_events, spec=spec, symbol_metadata=meta)
    assert rejected_bias.direction == "none"


def test_choch_flip_requires_displacement_threshold():
    spec, meta = _spec_meta()
    htf = gc2_long_htf() + [
        bar("2026-01-03 04:00", 1.1120, 1.1180, 1.1100, 1.1160),
        bar("2026-01-03 08:00", 1.1160, 1.1190, 1.1080, 1.1130),
        bar("2026-01-03 12:00", 1.0945, 1.1140, 1.0930, 1.0940),
    ]
    events = detect_htf_structure(htf, spec=spec, symbol_metadata=meta)
    bias = classify_htf_bias(events, spec=spec, symbol_metadata=meta)
    rejected = [ev for ev in events if ev.event_type == "CHOCH_REJECTED"]
    assert rejected
    assert rejected[-1].metadata["rejection_code"] == "INSUFFICIENT_CHOCH_DISPLACEMENT"
    assert bias.direction == "long"


def test_liquidity_pool_selection_is_stable_and_directional():
    spec, meta = _spec_meta()
    events = detect_htf_structure(gc2_long_htf(), spec=spec, symbol_metadata=meta)
    pools = build_liquidity_pools(events, spec=spec, symbol_metadata=meta, causal_cutoff="2026-01-03 00:00")
    selected = select_liquidity_pool(pools, current_price=Decimal("1.1120"), direction="long")
    rerun = select_liquidity_pool(pools, current_price=Decimal("1.1120"), direction="long")
    assert selected == rerun
    assert selected is not None
    assert selected.event_id.startswith("LIQUIDITY_POOL-")
    assert selected.metadata["pool_type"] == "SELL_SIDE"
    assert selected.reference_levels["price_level"] == "1.095"


def test_sweep_requires_pierce_reclaim_wick_ratio_and_age():
    spec, meta = _spec_meta()
    events = detect_htf_structure(gc2_long_htf(), spec=spec, symbol_metadata=meta)
    pool = select_liquidity_pool(
        build_liquidity_pools(events, spec=spec, symbol_metadata=meta, causal_cutoff="2026-01-03 00:00"),
        current_price=Decimal("1.1120"),
        direction="long",
    )
    sweep = detect_sweep_and_reclaim(gc2_long_htf(), pool, spec=spec, symbol_metadata=meta, causal_cutoff="2026-01-03 00:00")
    assert sweep is not None
    assert sweep.status == "confirmed"
    assert sweep.metadata["reclaim_status"] == "reclaimed"

    weak_wick = list(gc2_long_htf())
    weak_wick[11] = bar("2026-01-02 20:00", 1.1000, 1.1050, 1.0940, 1.1010)
    rejected = detect_sweep_and_reclaim(weak_wick, pool, spec=spec, symbol_metadata=meta, causal_cutoff="2026-01-03 00:00")
    assert rejected is not None
    assert rejected.status == "rejected"
    assert rejected.invalidation_reason == "SWEEP_WICK_RATIO_INSUFFICIENT"


def test_structural_dealing_range_ote_boundaries_are_deterministic():
    spec, _meta = _spec_meta()
    dr = DealingRange(
        range_id="DR-TEST",
        direction="long",
        anchor_high_event_id="H",
        anchor_low_event_id="L",
        high=Decimal("2.0"),
        low=Decimal("1.0"),
        equilibrium=Decimal("1.5"),
        creation_timestamp="2026-01-01 00:00",
        confirmation_timestamp="2026-01-01 00:00",
        age_bars=0,
        status="confirmed",
        invalidation_reason=None,
        causal_cutoff="2026-01-01 00:00",
    )
    assert evaluate_ote_location(Decimal("1.214"), dr, direction="long", spec=spec, causal_cutoff=dr.causal_cutoff).ote_eligible
    assert evaluate_ote_location(Decimal("1.500"), dr, direction="long", spec=spec, causal_cutoff=dr.causal_cutoff).ote_eligible
    assert not evaluate_ote_location(Decimal("1.100"), dr, direction="long", spec=spec, causal_cutoff=dr.causal_cutoff).ote_eligible
    assert evaluate_ote_location(Decimal("1.786"), dr, direction="short", spec=spec, causal_cutoff=dr.causal_cutoff).ote_eligible
    assert evaluate_ote_location(Decimal("1.500"), dr, direction="short", spec=spec, causal_cutoff=dr.causal_cutoff).ote_eligible
    assert not evaluate_ote_location(Decimal("1.900"), dr, direction="short", spec=spec, causal_cutoff=dr.causal_cutoff).ote_eligible


def test_structural_context_is_causal_and_deterministic():
    spec, _meta = _spec_meta()
    htf = gc2_long_htf()
    mf = gc2_long_mf()
    original = structural_context(htf, mf, spec=spec)
    resliced = structural_context((htf + [bar("2099-01-01 00:00", 9, 10, 8, 9)])[: len(htf)], mf, spec=spec)
    rerun = structural_context(htf, mf, spec=spec)
    assert original == resliced
    assert original == rerun
    assert original["bias"].bias_event_id
    assert original["sweep"].status == "confirmed"
    assert original["ote"].ote_eligible
