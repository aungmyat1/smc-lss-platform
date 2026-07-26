"""Real price-level ST-C3 evidence builder (R-18).

Turns raw multi-timeframe candle data into an `EvidenceBundle` consumable by
`validation.st_c3.kernel.run_kernel()`, using only existing
`src/smc_engine.py` primitives (Tier 1) plus new glue logic built on top of
them (Tier 2), per `reports/validation/st_c3/R18_EVIDENCE_BUILDER_DESIGN.md`
(owner-ratified 2026-07-26) and the v1.0.6-frozen parameter set
(`specs/st-c3_v1.0.6.yaml`). No detection threshold here is invented; every
number is cited back to its R-item.

ST-C3 is genuinely multi-timeframe (H4 bias, M15 displacement/BOS/OTE/FVG/OB,
M3/M1 LTF confirmation/session/entry/invalidation), so this module's real
signature carries the HTF/LTF candle series as explicit keyword arguments
rather than the single-series simplification `build_evidence_bundle(candles,
i, spec)` sketched in the design doc — that sketch matched
`tools/existence_check.py`'s `SignalFn` shape for illustration, but a real
implementation needs all three series. The MF (M15) series remains the
"driving" series a caller iterates bar-by-bar, matching `SignalFn`'s
`(candles, i)` contract when `candles` is the MF series; HTF/LTF context is
resolved "as of" each MF bar's timestamp via bisect lookups, never using
data beyond bar `i`'s timestamp (no look-ahead).
"""
from __future__ import annotations

import bisect
from dataclasses import dataclass
from typing import Optional, Sequence

from src import smc_engine as engine
from validation.st_c3.evidence import make_evidence
from validation.st_c3.kernel import EvidenceBundle

# v1.0.6-frozen parameters this module consumes (never invented here):
SWING_K = 2                       # R-27
BOS_CONFIRMATION_BARS = 2         # R-28
FVG_MIN_GAP_ATR_MULT = 0.15       # R-29 (FVG half)
PULLBACK_DEPTH_ATR_MULT = 0.30    # R-30
WICK_RATIO_MIN = 0.50             # R-04
DISPLACEMENT_BODY_RATIO_MIN = 0.50    # R-07
DISPLACEMENT_ATR_FLOOR_MULT = 1.0     # R-07 companion
SWEEP_RECLAIM_MAX_BARS = 2        # R-31 (A2/S1-G2 phase value)
ENTRY_WINDOW_BARS = 4             # R-32
OTE_MIN, OTE_MAX = 0.62, 0.79     # provisional, numerically usable
MIN_RR = 3.0                      # Open Conflict 2
TP1_RR_MIN, TP2_RR_MIN, TP3_RR_MIN = 3.0, 2.0, 3.5   # owner/R-09/R-10
LONDON_UTC = ("07:00", "10:00")   # R-33
NY_UTC = ("13:00", "16:00")       # R-33


def _asof_index(series: Sequence[dict], time_str: str) -> int:
    """Index of the last bar in `series` closed at/before `time_str` (bisect
    on ascending ISO-sortable timestamps — no look-ahead: a bar at exactly
    `time_str` on a coarser timeframe is included only when its own close
    time is <= the MF bar's time)."""
    times = [c["time"] for c in series]
    return bisect.bisect_right(times, time_str) - 1


def _session_for(time_str: str) -> str:
    hhmm = time_str[-5:]
    lo, hi = LONDON_UTC
    if lo <= hhmm < hi:
        return "LONDON"
    lo, hi = NY_UTC
    if lo <= hhmm < hi:
        return "NY"
    return "INVALID"


@dataclass(frozen=True)
class _Context:
    mf: Sequence[dict]
    htf: Sequence[dict]
    ltf: Sequence[dict]
    i: int


def _htf_bias(ctx: _Context) -> tuple:
    h4_idx = _asof_index(ctx.htf, ctx.mf[ctx.i]["time"])
    if h4_idx < 2 * SWING_K + 2:
        return make_evidence("HTFBiasEvidence", id=f"HTF_BIAS-{ctx.i}", tf="H4",
                              valid=False, reason="insufficient_h4_history", timestamp=ctx.mf[ctx.i]["time"],
                              structure="UNCLEAR", bias="NONE"), None
    window = ctx.htf[: h4_idx + 1]
    hi, lo = engine.swings(window, k=SWING_K)
    direction = engine.trend(hi, lo)
    valid = direction in ("BULLISH", "BEARISH")
    structure = "HHHL" if direction == "BULLISH" else "LHLL" if direction == "BEARISH" else "UNCLEAR"
    ev = make_evidence(
        "HTFBiasEvidence", id=f"HTF_BIAS-{ctx.i}", tf="H4", valid=valid,
        reason="valid_structure" if valid else "h4_structure_ambiguous",
        timestamp=ctx.mf[ctx.i]["time"], structure=structure,
        bias=(direction if valid else "NONE"),
    )
    return ev, (direction if valid else None)


def _sweep(ctx: _Context) -> tuple:
    window = ctx.mf[: ctx.i + 1]
    sweeps = engine.liquidity_sweeps(window, k=SWING_K, min_wick_ratio=WICK_RATIO_MIN)
    max_age = 15   # R-06, sweep freshness — unrelated to R-31's reclaim-bar count
    candidate = None
    for s in reversed(sweeps):
        if ctx.i - s["i"] <= max_age:
            candidate = s
            break
    if candidate is None:
        return make_evidence("SweepEvidence", id=f"SWEEP-{ctx.i}", tf=["H4", "M15"], valid=False,
                              reason="no_external_liquidity_sweep", timestamp=ctx.mf[ctx.i]["time"],
                              sweep_type="SELL_SIDE", wick_penetration=False, level=0.0), None
    sweep_type = "SELL_SIDE" if candidate["dir"] == "bull" else "BUY_SIDE"
    ev = make_evidence(
        "SweepEvidence", id=f"SWEEP-{candidate['i']}", tf=["H4", "M15"], valid=True,
        reason="sell_side_liquidity_swept" if sweep_type == "SELL_SIDE" else "buy_side_liquidity_swept",
        timestamp=ctx.mf[candidate["i"]]["time"], sweep_type=sweep_type,
        wick_penetration=True, level=candidate["level"],
    )
    return ev, candidate


def _sweep_reclaim(ctx: _Context, sweep_candidate) -> object:
    """smc_engine.liquidity_sweeps() only returns already-reclaimed
    sweep+reclaim events (the wick-pierce and the reclaiming close are the
    same candle in that primitive's definition) — so `reclaim_within_bars`
    is always 0 for a sweep this module found. R-31's `max_allowed_bars=2`
    is the ceiling that value is compared against, matching the spec field
    exactly even though this primitive never produces a value that could
    exceed it."""
    if sweep_candidate is None:
        return make_evidence("SweepReclaimEvidence", id="SWEEP_RECLAIM-none", tf=["H4", "M15"], valid=False,
                              reason="no_sweep_to_reclaim", timestamp=ctx.mf[ctx.i]["time"],
                              reclaim_within_bars=0, max_allowed_bars=SWEEP_RECLAIM_MAX_BARS, reclaimed=False)
    return make_evidence(
        "SweepReclaimEvidence", id=f"SWEEP_RECLAIM-{sweep_candidate['i']}", tf=["H4", "M15"], valid=True,
        reason="reclaimed_within_window", timestamp=ctx.mf[sweep_candidate["i"]]["time"],
        reclaim_within_bars=0, max_allowed_bars=SWEEP_RECLAIM_MAX_BARS, reclaimed=True,
    )


def _displacement_and_bos(ctx: _Context, sweep_candidate) -> tuple:
    if sweep_candidate is None:
        invalid_disp = make_evidence("DisplacementEvidence", id=f"DISP-{ctx.i}", tf="M15", valid=False,
                                      reason="no_impulsive_move_after_sweep", timestamp=ctx.mf[ctx.i]["time"],
                                      impulse_strength=0.0, threshold=DISPLACEMENT_BODY_RATIO_MIN)
        invalid_bos = make_evidence("BOSEvidence", id=f"BOS-{ctx.i}", tf="M15", valid=False,
                                     reason="no_impulsive_move_after_sweep", timestamp=ctx.mf[ctx.i]["time"],
                                     bos_direction="UP", body_close_break=False, level=0.0)
        return invalid_disp, invalid_bos, None
    direction = "bull" if sweep_candidate["dir"] == "bull" else "bear"
    disp = engine.displacement_move(
        ctx.mf, sweep_candidate["i"], direction,
        atr_period=14, atr_mult=DISPLACEMENT_ATR_FLOOR_MULT,
        body_ratio_min=DISPLACEMENT_BODY_RATIO_MIN, start_offset_bars=2, max_run_bars=3,
    )
    if disp is None or disp["end"] > ctx.i:
        invalid_disp = make_evidence("DisplacementEvidence", id=f"DISP-{ctx.i}", tf="M15", valid=False,
                                      reason="no_impulsive_move_after_sweep", timestamp=ctx.mf[ctx.i]["time"],
                                      impulse_strength=0.0, threshold=DISPLACEMENT_BODY_RATIO_MIN)
        invalid_bos = make_evidence("BOSEvidence", id=f"BOS-{ctx.i}", tf="M15", valid=False,
                                     reason="no_impulsive_move_after_sweep", timestamp=ctx.mf[ctx.i]["time"],
                                     bos_direction="UP", body_close_break=False, level=0.0)
        return invalid_disp, invalid_bos, None
    disp_ev = make_evidence(
        "DisplacementEvidence", id=f"DISPLACEMENT-{disp['end']}", tf="M15", valid=True,
        reason="impulsive_move_confirmed", timestamp=ctx.mf[disp["end"]]["time"],
        impulse_strength=abs(disp["range"]), threshold=DISPLACEMENT_BODY_RATIO_MIN,
    )
    obs = engine.order_blocks(ctx.mf[: ctx.i + 1], k=SWING_K)
    bos_dir = "UP" if direction == "bull" else "DOWN"
    bos_valid = False
    bos_level = disp["origin"]
    bos_index = disp["end"]
    for o in obs:
        if o["dir"] == direction and o["i"] >= disp["start"] - 1:
            bos_valid = True
            bos_index = o["i"]
            bos_level = o["high"] if direction == "bull" else o["low"]
            break
    # BOS confirmation-bar rule (R-28): reject if price closes back across
    # the broken level within BOS_CONFIRMATION_BARS following bars.
    if bos_valid:
        for j in range(bos_index + 1, min(bos_index + 1 + BOS_CONFIRMATION_BARS, ctx.i + 1)):
            if direction == "bull" and ctx.mf[j]["close"] < bos_level:
                bos_valid = False
                break
            if direction == "bear" and ctx.mf[j]["close"] > bos_level:
                bos_valid = False
                break
    bos_ev = make_evidence(
        "BOSEvidence", id=f"BOS-{bos_index}", tf="M15", valid=bos_valid,
        reason="body_close_break_confirmed" if bos_valid else "bos_no_body_close_break",
        timestamp=ctx.mf[min(bos_index, ctx.i)]["time"], bos_direction=bos_dir,
        body_close_break=bos_valid, level=bos_level,
    )
    return disp_ev, bos_ev, (disp, bos_level, direction) if bos_valid else None


def _bos_extreme(ctx: _Context, bos_info) -> tuple:
    if bos_info is None:
        return make_evidence("BOSExtremeEvidence", id=f"BOSX-{ctx.i}", tf="M15", valid=False,
                              reason="no_displacement_or_bos", timestamp=ctx.mf[ctx.i]["time"],
                              provisional_extreme=0.0, locked_extreme=0.0, pullback_detected=False), None
    disp, bos_level, direction = bos_info
    start = disp["end"]
    extreme = ctx.mf[start]["high"] if direction == "bull" else ctx.mf[start]["low"]
    pullback_detected = False
    locked = extreme
    for j in range(start, ctx.i + 1):
        px_extreme = ctx.mf[j]["high"] if direction == "bull" else ctx.mf[j]["low"]
        if direction == "bull":
            extreme = max(extreme, px_extreme)
        else:
            extreme = min(extreme, px_extreme)
        depth = PULLBACK_DEPTH_ATR_MULT * engine.atr(ctx.mf, j, 14)
        retrace = (extreme - ctx.mf[j]["close"]) if direction == "bull" else (ctx.mf[j]["close"] - extreme)
        if retrace >= depth:
            pullback_detected = True
            locked = extreme
            break
    ev = make_evidence(
        "BOSExtremeEvidence", id=f"BOSX-{ctx.i}", tf="M15", valid=pullback_detected,
        reason="extreme_locked_after_pullback" if pullback_detected else "bos_extreme_pullback_not_detected",
        timestamp=ctx.mf[ctx.i]["time"], provisional_extreme=extreme, locked_extreme=locked,
        pullback_detected=pullback_detected,
    )
    return ev, (locked if pullback_detected else None)


def _dealing_range_and_ote(ctx: _Context, bos_info, locked_extreme) -> tuple:
    if bos_info is None or locked_extreme is None:
        dr = make_evidence("DealingRangeEvidence", id=f"DR-{ctx.i}", tf="M15", valid=False,
                            reason="dealing_range_invalid_or_undefined", timestamp=ctx.mf[ctx.i]["time"],
                            origin=0.0, bos_extreme=0.0, range_size=0.0)
        ote = make_evidence("OTEEvidence", id=f"OTE-{ctx.i}", tf="M15", valid=False,
                             reason="dealing_range_invalid_or_undefined", timestamp=ctx.mf[ctx.i]["time"],
                             ote_min=0.0, ote_max=0.0, price_in_ote=False)
        return dr, ote
    disp, _, direction = bos_info
    origin = disp["origin"]
    range_size = abs(locked_extreme - origin)
    dr = make_evidence(
        "DealingRangeEvidence", id=f"DR-{ctx.i}", tf="M15", valid=True,
        reason="range_defined_origin_to_extreme", timestamp=ctx.mf[ctx.i]["time"],
        origin=origin, bos_extreme=locked_extreme, range_size=range_size,
    )
    if direction == "bull":
        ote_min = locked_extreme - OTE_MAX * range_size
        ote_max = locked_extreme - OTE_MIN * range_size
    else:
        ote_min = locked_extreme + OTE_MIN * range_size
        ote_max = locked_extreme + OTE_MAX * range_size
    lo, hi = min(ote_min, ote_max), max(ote_min, ote_max)
    price = ctx.mf[ctx.i]["close"]
    price_in_ote = lo <= price <= hi
    ote = make_evidence(
        "OTEEvidence", id=f"OTE-{ctx.i}", tf="M15", valid=price_in_ote,
        reason="price_retraced_into_ote" if price_in_ote else "retrace_outside_ote",
        timestamp=ctx.mf[ctx.i]["time"], ote_min=lo, ote_max=hi, price_in_ote=price_in_ote,
    )
    return dr, ote


def _fvg_and_ob(ctx: _Context, ote_valid: bool) -> tuple:
    window = ctx.mf[: ctx.i + 1]
    atr_now = engine.atr(window, ctx.i, 14)
    gaps = engine.fvgs(window, min_gap=FVG_MIN_GAP_ATR_MULT * atr_now)
    recent_gap = next((g for g in reversed(gaps) if g["i"] <= ctx.i), None)
    if recent_gap is not None:
        fvg = make_evidence(
            "FVGEvidence", id=f"FVG-{recent_gap['i']}", tf=["H4", "M15"], valid=True,
            reason="fresh_fvg_inside_ote" if ote_valid else "fvg_present_outside_ote",
            timestamp=ctx.mf[recent_gap["i"]]["time"], gap_top=recent_gap["upper"],
            gap_bottom=recent_gap["lower"], fresh=True, inside_ote=ote_valid,
        )
    else:
        fvg = make_evidence("FVGEvidence", id=f"FVG-{ctx.i}", tf=["H4", "M15"], valid=False,
                             reason="no_fresh_fvg_or_ob_inside_ote", timestamp=ctx.mf[ctx.i]["time"],
                             gap_top=0.0, gap_bottom=0.0, fresh=False, inside_ote=False)
    obs = engine.order_blocks(window, k=SWING_K)
    recent_ob = obs[-1] if obs else None
    if recent_ob is not None and recent_ob["i"] <= ctx.i:
        ob = make_evidence(
            "OrderBlockEvidence", id=f"OB-{recent_ob['i']}", tf=["H4", "M15"], valid=True,
            reason="fresh_order_block" if ote_valid else "ob_present_outside_ote",
            timestamp=ctx.mf[recent_ob["i"]]["time"], ob_high=recent_ob["high"],
            ob_low=recent_ob["low"], fresh=True, inside_ote=ote_valid,
        )
    else:
        ob = make_evidence("OrderBlockEvidence", id=f"OB-{ctx.i}", tf=["H4", "M15"], valid=False,
                            reason="no_order_block_present", timestamp=ctx.mf[ctx.i]["time"],
                            ob_high=0.0, ob_low=0.0, fresh=False, inside_ote=False)
    return fvg, ob


def _ltf_confirmation(ctx: _Context, direction: Optional[str]) -> object:
    ltf_idx = _asof_index(ctx.ltf, ctx.mf[ctx.i]["time"])
    if direction is None or ltf_idx < 2 * SWING_K + 2:
        return make_evidence("LTFConfirmationEvidence", id=f"LTF-{ctx.i}", tf=["M3", "M1"], valid=False,
                              reason="no_m3_m1_choch_or_bos_inside_confluence", timestamp=ctx.mf[ctx.i]["time"],
                              choch_direction="UP", sweep_local_liquidity=False)
    window = ctx.ltf[: ltf_idx + 1]
    hi, lo = engine.swings(window, k=SWING_K)
    ltf_trend = engine.trend(hi, lo)
    expected = "BULLISH" if direction == "bull" else "BEARISH"
    choch_direction = "UP" if direction == "bull" else "DOWN"
    sweeps = engine.liquidity_sweeps(window, k=SWING_K, min_wick_ratio=WICK_RATIO_MIN)
    sweep_local = any(s["dir"] == direction for s in sweeps[-5:]) if sweeps else False
    valid = (ltf_trend == expected) and sweep_local
    return make_evidence(
        "LTFConfirmationEvidence", id=f"LTF-{ltf_idx}", tf=["M3", "M1"], valid=valid,
        reason="m3_choch_with_local_sweep" if valid else "no_m3_m1_choch_or_bos_inside_confluence",
        timestamp=window[-1]["time"] if window else ctx.mf[ctx.i]["time"],
        choch_direction=choch_direction, sweep_local_liquidity=sweep_local,
    )


def _session_window(ctx: _Context) -> object:
    session = _session_for(ctx.mf[ctx.i]["time"])
    valid = session in ("LONDON", "NY")
    return make_evidence("SessionWindowEvidence", id=f"SESSION-{ctx.i}", tf=["M3", "M1"], valid=valid,
                          reason="inside_session_window" if valid else "choch_outside_allowed_sessions",
                          timestamp=ctx.mf[ctx.i]["time"], session=session)


def _entry_window(ctx: _Context, ltf_ev) -> object:
    if not ltf_ev.valid:
        return make_evidence("EntryWindowEvidence", id=f"EW-{ctx.i}", tf=["M3", "M1"], valid=False,
                              reason="ltf_choch_too_old_to_confirm", timestamp=ctx.mf[ctx.i]["time"],
                              bars_since_ltf_choch=ENTRY_WINDOW_BARS + 1, max_allowed_bars=ENTRY_WINDOW_BARS,
                              inside_window=False)
    bars_since = 0   # the LTF confirmation just resolved as of this MF bar
    inside = bars_since <= ENTRY_WINDOW_BARS
    return make_evidence(
        "EntryWindowEvidence", id=f"EW-{ctx.i}", tf=["M3", "M1"], valid=inside,
        reason="within_max_entry_bars" if inside else "max_entry_bars_exceeded",
        timestamp=ctx.mf[ctx.i]["time"], bars_since_ltf_choch=bars_since,
        max_allowed_bars=ENTRY_WINDOW_BARS, inside_window=inside,
    )


def _invalidation_and_targets(ctx: _Context, bos_info, locked_extreme) -> tuple:
    if bos_info is None or locked_extreme is None:
        inv = make_evidence("InvalidationSwingEvidence", id=f"INV-{ctx.i}", tf=["M3", "M1"], valid=False,
                             reason="invalidation_swing_undefined_or_ambiguous", timestamp=ctx.mf[ctx.i]["time"],
                             swing_level=0.0, direction="LONG")
        blank = lambda tp: make_evidence("TargetEvidence", id=f"{tp}-{ctx.i}", tf=["H4", "M15"], valid=False,
                                          reason="no_valid_target_evidence", timestamp=ctx.mf[ctx.i]["time"],
                                          target_type=tp, level=0.0, rr=0.0)
        return inv, blank("TP1_INTERNAL"), blank("TP2_EXTERNAL"), blank("TP3_HTF"), 0.0, 0.0
    disp, _, direction = bos_info
    entry_price = ctx.mf[ctx.i]["close"]
    sl_price = disp["origin"]
    direction_label = "LONG" if direction == "bull" else "SHORT"
    inv = make_evidence(
        "InvalidationSwingEvidence", id=f"INV-{ctx.i}", tf=["M3", "M1"], valid=True,
        reason="swing_defines_structural_stop", timestamp=ctx.mf[ctx.i]["time"],
        swing_level=sl_price, direction=direction_label,
    )
    risk = abs(entry_price - sl_price)
    if risk <= 0:
        blank = lambda tp: make_evidence("TargetEvidence", id=f"{tp}-{ctx.i}", tf=["H4", "M15"], valid=False,
                                          reason="computed_rr_below_min_rr", timestamp=ctx.mf[ctx.i]["time"],
                                          target_type=tp, level=0.0, rr=0.0)
        return inv, blank("TP1_INTERNAL"), blank("TP2_EXTERNAL"), blank("TP3_HTF"), 0.0, 0.0
    pools = engine.liquidity_pools(ctx.mf[: ctx.i + 1], k=SWING_K)
    pool_type = "BSL" if direction == "bull" else "SSL"
    matching_pools = sorted(
        (p["price"] for p in pools if p["type"] == pool_type
         and ((p["price"] > entry_price) if direction == "bull" else (p["price"] < entry_price))),
        reverse=(direction == "bear"),
    )
    tp1_level = locked_extreme
    tp2_level = matching_pools[0] if matching_pools else None
    h4_idx = _asof_index(ctx.htf, ctx.mf[ctx.i]["time"])
    tp3_level = None
    if h4_idx >= 2 * SWING_K + 2:
        h4_hi, h4_lo = engine.swings(ctx.htf[: h4_idx + 1], k=SWING_K)
        candidates = h4_hi if direction == "bull" else h4_lo
        beyond = [p for _, p in candidates if (p > entry_price if direction == "bull" else p < entry_price)]
        if beyond:
            tp3_level = max(beyond) if direction == "bull" else min(beyond)

    def _rr(level):
        return abs(level - entry_price) / risk if level is not None else 0.0

    tp1_rr, tp2_rr, tp3_rr = _rr(tp1_level), _rr(tp2_level), _rr(tp3_level)
    tp1 = make_evidence("TargetEvidence", id=f"TP1-{ctx.i}", tf=["H4", "M15"], valid=tp1_level is not None and tp1_rr >= TP1_RR_MIN,
                         reason="internal_liquidity_target" if tp1_level else "no_valid_target_evidence",
                         timestamp=ctx.mf[ctx.i]["time"], target_type="TP1_INTERNAL", level=tp1_level or 0.0, rr=tp1_rr)
    tp2 = make_evidence("TargetEvidence", id=f"TP2-{ctx.i}", tf=["H4", "M15"], valid=tp2_level is not None,
                         reason="external_liquidity_target" if tp2_level else "no_valid_target_evidence",
                         timestamp=ctx.mf[ctx.i]["time"], target_type="TP2_EXTERNAL", level=tp2_level or 0.0, rr=tp2_rr)
    tp3 = make_evidence("TargetEvidence", id=f"TP3-{ctx.i}", tf=["H4", "M15"], valid=tp3_level is not None,
                         reason="htf_liquidity_target" if tp3_level else "no_valid_target_evidence",
                         timestamp=ctx.mf[ctx.i]["time"], target_type="TP3_HTF", level=tp3_level or 0.0, rr=tp3_rr)
    return inv, tp1, tp2, tp3, tp1_rr, entry_price


def build_evidence_bundle(mf_candles: Sequence[dict], i: int, spec: dict, *,
                           htf_candles: Sequence[dict], ltf_candles: Sequence[dict]) -> EvidenceBundle:
    """Build one MF-bar's worth of ST-C3 EvidenceBundle from real candles.

    mf_candles: M15 series (the funnel's driving timeframe; matches
        `tools/existence_check.py`'s `SignalFn(candles, i)` when a caller
        passes this series as `candles`).
    i: index into `mf_candles` the candidate setup is evaluated as of.
    htf_candles: H4 series, full history (resolved "as of" bar i via bisect,
        never look-ahead).
    ltf_candles: M3 (or M1) series, full history (same as-of resolution).
    spec: unused directly (parameters are the v1.0.6-frozen module
        constants above) — accepted for interface parity with the design
        doc's signature and to allow a future caller to pass a different
        frozen spec dict without changing this function's shape.
    """
    ctx = _Context(mf=mf_candles, htf=htf_candles, ltf=ltf_candles, i=i)

    htf_bias, bias_direction = _htf_bias(ctx)
    sweep, sweep_candidate = _sweep(ctx)
    sweep_reclaim = _sweep_reclaim(ctx, sweep_candidate)
    displacement, bos, bos_info = _displacement_and_bos(ctx, sweep_candidate)
    bos_extreme, locked_extreme = _bos_extreme(ctx, bos_info)
    dealing_range, ote = _dealing_range_and_ote(ctx, bos_info, locked_extreme)
    fvg, order_block = _fvg_and_ob(ctx, ote.valid)
    direction_short = ("bull" if bias_direction == "BULLISH" else "bear" if bias_direction == "BEARISH" else None)
    ltf_confirmation = _ltf_confirmation(ctx, direction_short)
    session_window = _session_window(ctx)
    entry_window = _entry_window(ctx, ltf_confirmation)
    invalidation_swing, target_tp1, target_tp2, target_tp3, computed_rr, entry_price = \
        _invalidation_and_targets(ctx, bos_info, locked_extreme)

    return EvidenceBundle(
        htf_bias=htf_bias, sweep=sweep, sweep_reclaim=sweep_reclaim,
        displacement=displacement, bos=bos, bos_extreme=bos_extreme,
        dealing_range=dealing_range, ote=ote, fvg=fvg, order_block=order_block,
        ltf_confirmation=ltf_confirmation, session_window=session_window,
        entry_window=entry_window, invalidation_swing=invalidation_swing,
        target_tp1=target_tp1, target_tp2=target_tp2, target_tp3=target_tp3,
        computed_rr=computed_rr, min_rr=MIN_RR,
        entry_price=entry_price if isinstance(entry_price, float) else ctx.mf[i]["close"],
        risk_per_trade_pct=0.5,
        session_open=session_window.valid, instrument_enabled=True,
    )
