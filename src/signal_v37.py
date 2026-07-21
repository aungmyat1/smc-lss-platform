#!/usr/bin/env python3
"""SMC-LSS v3.7 decision module — pure G1-G9 gate pipeline for ST-C1 v1.1.0.

Source of truth: specs/v3.7.yaml, strategies/candidates/ST-C1_v1.1.0.yaml.
Status: RESEARCH_CANDIDATE. Does NOT authorize live trading.

Scope by design (see IMPLEMENTATION ARCHITECTURE in the task that created this
file): this module owns the gate logic that does NOT need a cost model —
G1 HTF bias, G2 external/protected structure, G3 BOS/CHoCH classification
(folded into G1's break evaluation and reused for G6's M5 confirmation),
G4 premium/discount, G5 HTF POI, G6 M5 trigger sequencing, G7 structural
invalidation (stop), and G9 preselected target. G8 (net reward gate, needs
the cost model) and G10 (management simulation) are deliberately left to the
replay engine layer (validation/historical_replay_engine_v37.py), which
already owns the one cost model and one management simulator — this module
must not duplicate either.

Two-timeframe design: H1 provides G1/G2/G4/G5(H1_ORDER_BLOCK/H1_EXTERNAL_SWEEP)/G7
context; D1 provides G5's D1_GAP origin; M5 provides G6's trigger sequence and
G9's LTF fallback target. Every function here is a pure, deterministic
function of the candle window it is given — no hidden state, no look-ahead
beyond the window boundary the caller supplies (closed-candle windows only).
"""
from __future__ import annotations
from dataclasses import dataclass, field
import smc_engine as e

# --- shared numeric defaults (specs/v3.7.yaml parameter_registry) ----------
DEFAULTS = {
    "pivot_left_bars": 2,
    "pivot_right_bars": 2,
    "close_buffer_atr_mult": 0.10,
    "dealing_range_lookback_h1_bars": 40,
    "equal_high_low_tolerance_atr_mult": 0.05,
    "minimum_gap_size_atr_mult": 0.10,
    "htf_poi_max_age_h1_bars": 60,
    "d1_gap_max_age_d1_bars": 10,
    "d1_reaction_window_h1_bars": 6,
    "h1_reclaim_window_h1_bars": 1,
    "poi_entry_to_sweep_max_m5_bars": 30,
    "displacement_to_choch_max_m5_bars": 5,
    "choch_to_retrace_entry_max_m5_bars": 30,
    "displacement_atr_period": 14,
    "displacement_atr_mult": 1.5,
    "displacement_body_ratio_min": 0.5,
    "displacement_start_offset_bars": 2,
    "displacement_max_run_bars": 3,
    "stop_buffer_atr_mult": 0.15,
    "sweep_wick_ratio_min": 0.5,
}


def _p(params, key):
    return params.get(key, DEFAULTS[key])


def _displacement_kwargs(params):
    return {
        "atr_period": int(_p(params, "displacement_atr_period")),
        "atr_mult": float(_p(params, "displacement_atr_mult")),
        "body_ratio_min": float(_p(params, "displacement_body_ratio_min")),
        "start_offset_bars": int(_p(params, "displacement_start_offset_bars")),
        "max_run_bars": int(_p(params, "displacement_max_run_bars")),
    }


# ---------------------------------------------------------------------------
# G1 (bias) + G3 (BOS/CHoCH/MSS/WICK_REJECTION classification, shared helper)
# ---------------------------------------------------------------------------

def _break_events(candles, k, buffer):
    """Close-through break events vs. the most-recently-confirmed swing on the
    opposite side, at the time of each candle (point-in-time: only swings
    confirmed strictly before bar i are consulted, mirroring
    smc_engine.order_blocks'/liquidity_sweeps' pointer-walk pattern).
    Returns an index-ascending list of {'i', 'dir': 'bull'|'bear', 'level'}.
    """
    hi_all, lo_all = e.swings(candles, k)
    out = []
    hi_ptr, lo_ptr = 0, 0
    n_hi, n_lo = len(hi_all), len(lo_all)
    for i in range(k + 1, len(candles)):
        while hi_ptr < n_hi and hi_all[hi_ptr][0] + k <= i:
            hi_ptr += 1
        while lo_ptr < n_lo and lo_all[lo_ptr][0] + k <= i:
            lo_ptr += 1
        hi_last = hi_all[hi_ptr - 1][1] if hi_ptr else None
        lo_last = lo_all[lo_ptr - 1][1] if lo_ptr else None
        c = candles[i]
        if hi_last is not None and c["close"] > hi_last + buffer:
            out.append({"i": i, "dir": "bull", "level": hi_last})
        elif lo_last is not None and c["close"] < lo_last - buffer:
            out.append({"i": i, "dir": "bear", "level": lo_last})
    return out


def classify_breaks(candles, k, buffer):
    """Walk break events in order, labeling each BOS / CHOCH / MSS per
    specs/v3.7.yaml G3: first counter-trend break = CHOCH (flips bias), the
    immediately following same-direction break = MSS (confirms the flip,
    audit-only label), everything else = BOS."""
    events = _break_events(candles, k, buffer)
    labeled = []
    current_bias = None
    just_flipped = False
    for ev in events:
        if current_bias is None:
            label = "BOS"
            current_bias = ev["dir"]
        elif ev["dir"] == current_bias:
            label = "MSS" if just_flipped else "BOS"
            just_flipped = False
        else:
            label = "CHOCH"
            current_bias = ev["dir"]
            just_flipped = True
        labeled.append({**ev, "label": label})
    return labeled, current_bias


def evaluate_g1_bias(h1, params=None):
    """G1: HTF bias — BULLISH/BEARISH/NEUTRAL. Requires BOTH a confirmed
    HH+HL (or LH+LL) swing pattern AND a matching break-event chain; any
    disagreement or insufficient data is NEUTRAL (hard reject downstream)."""
    params = params or {}
    k = int(_p(params, "pivot_left_bars"))
    hi, lo = e.swings(h1, k)
    if len(hi) < 2 or len(lo) < 2:
        return {"state": "NEUTRAL", "reason": "insufficient confirmed swings"}
    swing_trend = e.trend(hi, lo)
    atr_val = e.atr(h1, len(h1) - 1, int(_p(params, "displacement_atr_period")))
    buffer = float(_p(params, "close_buffer_atr_mult")) * atr_val
    breaks, break_bias = classify_breaks(h1, k, buffer)
    break_state = {"bull": "BULLISH", "bear": "BEARISH"}.get(break_bias)
    if swing_trend == "RANGING" or break_state is None or break_state != swing_trend:
        return {"state": "NEUTRAL", "reason": "conflicting or absent bias evidence",
                "swing_trend": swing_trend, "break_state": break_state}
    protected_low = lo[-1][1] if swing_trend == "BULLISH" else None
    protected_high = hi[-1][1] if swing_trend == "BEARISH" else None
    last_break = breaks[-1] if breaks else None
    return {
        "state": swing_trend,
        "protected_low": protected_low,
        "protected_high": protected_high,
        "last_break": last_break,
        "structure_classification": "HH_HL" if swing_trend == "BULLISH" else "LH_LL",
    }


# ---------------------------------------------------------------------------
# G2 — external / protected structure
# ---------------------------------------------------------------------------

def evaluate_g2_external_structure(h1, params=None):
    params = params or {}
    k = int(_p(params, "pivot_left_bars"))
    lookback = int(_p(params, "dealing_range_lookback_h1_bars"))
    n = len(h1)
    lookback_start = max(0, n - lookback)
    hi, lo = e.swings(h1, k)
    hi_in = [(i, p) for i, p in hi if i >= lookback_start]
    lo_in = [(i, p) for i, p in lo if i >= lookback_start]
    if not hi_in or not lo_in:
        return None
    ext_high_i, ext_high = max(hi_in, key=lambda x: x[1])
    ext_low_i, ext_low = min(lo_in, key=lambda x: x[1])
    if ext_low >= ext_high:
        return None
    return {
        "range_id": f"{h1[ext_low_i]['time']}|{h1[ext_high_i]['time']}",
        "dealing_range_low": ext_low, "dealing_range_high": ext_high,
        "low_anchor_time": h1[ext_low_i]["time"], "high_anchor_time": h1[ext_high_i]["time"],
        "low_index": ext_low_i, "high_index": ext_high_i,
    }


# ---------------------------------------------------------------------------
# G4 — premium / discount location
# ---------------------------------------------------------------------------

def evaluate_g4_location(direction, entry, dealing_range):
    low, high = dealing_range["dealing_range_low"], dealing_range["dealing_range_high"]
    midpoint = low + 0.5 * (high - low)
    if entry == midpoint:
        location = "neutral"
    else:
        location = "discount" if entry < midpoint else "premium"
    valid = (location == "discount") if direction == "long" else (location == "premium")
    return {"valid": valid, "midpoint": midpoint, "location": location,
            "range_id": dealing_range["range_id"],
            "dealing_range_low": low, "dealing_range_high": high,
            "low_anchor_time": dealing_range["low_anchor_time"],
            "high_anchor_time": dealing_range["high_anchor_time"]}


# ---------------------------------------------------------------------------
# G5 — HTF area of interest (HTF POI), one of three causal origins
# ---------------------------------------------------------------------------

def _htf_order_block_poi(h1, direction, params):
    k = int(_p(params, "pivot_left_bars"))
    max_age = int(_p(params, "htf_poi_max_age_h1_bars"))
    want = "bull" if direction == "long" else "bear"
    obs = e.order_blocks(h1, k)
    n = len(h1)
    for ob in reversed(obs):
        if ob["dir"] != want:
            continue
        if (n - 1) - ob["i"] > max_age:
            break
        status = e.mitigation_status(h1, ob["i"], ob["low"], ob["high"], ob["dir"])
        if status == "INVALIDATED":
            continue
        return {"poi_origin": "H1_ORDER_BLOCK", "low": ob["low"], "high": ob["high"],
                "index": ob["i"], "time": h1[ob["i"]]["time"], "freshness": status,
                "displacement_ref_i": ob["i"]}
    return None


def _htf_d1_gap_poi(d1, direction, params):
    if not d1:
        return None
    max_age = int(_p(params, "d1_gap_max_age_d1_bars"))
    want = "bull" if direction == "long" else "bear"
    gaps = e.fvgs(d1)
    n_d1 = len(d1)
    for g in reversed(gaps):
        if g["dir"] != want:
            continue
        if (n_d1 - 1) - g["i"] > max_age:
            break
        status = e.mitigation_status(d1, g["i"], g["lower"], g["upper"], g["dir"])
        if status == "INVALIDATED":
            continue
        return {"poi_origin": "D1_GAP", "low": g["lower"], "high": g["upper"],
                "index": g["i"], "time": d1[g["i"]]["time"], "freshness": status,
                "displacement_ref_i": g["i"]}
    return None


def _htf_external_sweep_poi(h1, direction, dealing_range, params):
    k = int(_p(params, "pivot_left_bars"))
    want = "bull" if direction == "long" else "bear"
    sweeps = e.liquidity_sweeps(h1, k, min_wick_ratio=float(_p(params, "sweep_wick_ratio_min")))
    ext_level = dealing_range["dealing_range_low"] if want == "bull" else dealing_range["dealing_range_high"]
    for sw in reversed(sweeps):
        if sw["dir"] != want or sw["level"] != ext_level:
            continue          # only the range extremity is EXTERNAL liquidity
        i = sw["i"]
        c = h1[i]
        lo_ = min(c["low"], c["open"], c["close"])
        hi_ = max(c["high"], c["open"], c["close"])
        return {"poi_origin": "H1_EXTERNAL_SWEEP", "low": lo_, "high": hi_,
                "index": i, "time": c["time"], "freshness": "FRESH",
                "displacement_ref_i": i}
    return None


def _causal_displacement_ok(h1, poi, direction, params):
    """G5 causal_relationship_required: a qualifying displacement must exist
    immediately around the POI's own creation.

    Two distinct relationships, not one formula: an order-block/external-sweep
    POI's index IS the last opposite-polarity candle BEFORE the directional
    move (smc_engine.order_blocks/liquidity_sweeps semantics) — the
    displacement must start shortly AFTER it. A D1_GAP POI's index is a
    D1-array index and cannot be compared against H1 bar bounds directly
    (cross-timeframe) — translate to the first H1 bar at/after the gap's own
    timestamp and check for displacement from there."""
    want = "bull" if direction == "long" else "bear"
    if poi["poi_origin"] == "D1_GAP":
        start_h1 = next((idx for idx, b in enumerate(h1) if b["time"] > poi["time"]), None)
        if start_h1 is None:
            return False
        disp = e.displacement_move(h1, max(0, start_h1 - 1), want, **_displacement_kwargs(params))
        return disp is not None
    disp = e.displacement_move(h1, poi["index"], want, **_displacement_kwargs(params))
    return disp is not None


def evaluate_g5_htf_poi(h1, d1, direction, dealing_range, params=None):
    params = params or {}
    for finder, needs_range in ((_htf_d1_gap_poi, False), (_htf_order_block_poi, False),
                                 (_htf_external_sweep_poi, True)):
        poi = finder(d1, direction, params) if finder is _htf_d1_gap_poi else (
            finder(h1, direction, dealing_range, params) if needs_range else finder(h1, direction, params)
        )
        if poi is None:
            continue
        if not _causal_displacement_ok(h1, poi, direction, params):
            continue
        return poi
    return None


# ---------------------------------------------------------------------------
# G6 — M5 trigger sequencing (strict order, first qualifying bar only)
# ---------------------------------------------------------------------------

def evaluate_g6_m5_trigger(m5, direction, poi, params=None):
    params = params or {}
    k = int(_p(params, "pivot_left_bars"))
    want = "bull" if direction == "long" else "bear"

    poi_entry_i = None
    for idx, c in enumerate(m5):
        if c["low"] <= poi["high"] and c["high"] >= poi["low"]:
            poi_entry_i = idx
            break
    if poi_entry_i is None:
        return None

    max_sweep_gap = int(_p(params, "poi_entry_to_sweep_max_m5_bars"))
    sweeps = [s for s in e.liquidity_sweeps(m5, k, min_wick_ratio=float(_p(params, "sweep_wick_ratio_min")))
              if s["dir"] == want and poi_entry_i <= s["i"] <= poi_entry_i + max_sweep_gap]
    if not sweeps:
        return None
    sweep = sweeps[0]                    # first qualifying bar only

    disp = e.displacement_move(m5, sweep["i"], want, **_displacement_kwargs(params))
    if disp is None:
        return None

    max_choch_gap = int(_p(params, "displacement_to_choch_max_m5_bars"))
    choch_i = None
    ref_high = m5[disp["start"]]["high"]
    ref_low = m5[disp["start"]]["low"]
    for j in range(disp["end"] + 1, min(disp["end"] + 1 + max_choch_gap, len(m5))):
        c = m5[j]
        if want == "bull" and c["close"] > ref_high:
            choch_i = j
            break
        if want == "bear" and c["close"] < ref_low:
            choch_i = j
            break
    if choch_i is None:
        return None

    max_retrace_gap = int(_p(params, "choch_to_retrace_entry_max_m5_bars"))
    last_i = len(m5) - 1
    if last_i <= choch_i or last_i - choch_i > max_retrace_gap:
        return None
    mid = (disp["origin"] + m5[disp["end"]]["close"]) / 2.0
    last_close = m5[-1]["close"]
    retraced = last_close <= mid if want == "bull" else last_close >= mid
    if not retraced:
        return None

    return {
        "poi_entry_i": poi_entry_i, "sweep_i": sweep["i"], "sweep_level": sweep["level"],
        "disp_start": disp["start"], "disp_end": disp["end"], "disp_origin": disp["origin"],
        "choch_i": choch_i, "retrace_entry_i": last_i,
        "events": [
            {"event": "poi_entry", "bar_index": poi_entry_i, "time": m5[poi_entry_i]["time"]},
            {"event": "sweep", "bar_index": sweep["i"], "time": m5[sweep["i"]]["time"]},
            {"event": "displacement", "bar_index": disp["start"], "time": m5[disp["start"]]["time"]},
            {"event": "choch_or_bos", "bar_index": choch_i, "time": m5[choch_i]["time"]},
            {"event": "retrace_entry", "bar_index": last_i, "time": m5[last_i]["time"]},
        ],
    }


# ---------------------------------------------------------------------------
# G7 — structural invalidation (stop)
# ---------------------------------------------------------------------------

def evaluate_g7_stop(direction, entry, poi, dealing_range, trigger, m5, params=None):
    params = params or {}
    atr_val = e.atr(m5, len(m5) - 1, int(_p(params, "displacement_atr_period")))
    buffer = float(_p(params, "stop_buffer_atr_mult")) * atr_val
    disp_origin = trigger.get("disp_origin")
    if direction == "long":
        candidates = [(dealing_range["dealing_range_low"], "protected_swing"),
                      (poi["low"], "poi_boundary")]
        if disp_origin is not None:
            candidates.append((disp_origin, "displacement_origin"))
        valid = [(lvl, r) for lvl, r in candidates if lvl < entry]
        if not valid:
            return None
        raw_level, reason = max(valid, key=lambda x: x[0])
        final_stop = raw_level - buffer
        if final_stop >= entry:
            return None
    else:
        candidates = [(dealing_range["dealing_range_high"], "protected_swing"),
                      (poi["high"], "poi_boundary")]
        if disp_origin is not None:
            candidates.append((disp_origin, "displacement_origin"))
        valid = [(lvl, r) for lvl, r in candidates if lvl > entry]
        if not valid:
            return None
        raw_level, reason = min(valid, key=lambda x: x[0])
        final_stop = raw_level + buffer
        if final_stop <= entry:
            return None
    structure_id = f"{reason}@{raw_level:.5f}"
    return {"invalidation_structure_id": structure_id, "raw_level": raw_level,
            "buffer": buffer, "final_stop": final_stop, "reason": reason}


# ---------------------------------------------------------------------------
# G9 — preselected target (priority: external HTF liquidity, else LTF fallback)
# ---------------------------------------------------------------------------

def evaluate_g9_target(direction, entry, dealing_range, m5, consumed_levels, params=None):
    params = params or {}
    k = int(_p(params, "pivot_left_bars"))
    if direction == "long":
        level_id = f"{dealing_range['range_id']}:high"
        ext_target = dealing_range["dealing_range_high"]
        if ext_target > entry and level_id not in consumed_levels:
            return {"target": ext_target, "target_is_ltf_fallback": False,
                    "source": "external_htf", "level_id": level_id}
    else:
        level_id = f"{dealing_range['range_id']}:low"
        ext_target = dealing_range["dealing_range_low"]
        if ext_target < entry and level_id not in consumed_levels:
            return {"target": ext_target, "target_is_ltf_fallback": False,
                    "source": "external_htf", "level_id": level_id}
    hi, lo = e.swings(m5, k)
    if direction == "long":
        cands = [p for _, p in hi if p > entry]
        if cands:
            return {"target": min(cands), "target_is_ltf_fallback": True,
                    "source": "m5_swing", "level_id": None}
    else:
        cands = [p for _, p in lo if p < entry]
        if cands:
            return {"target": max(cands), "target_is_ltf_fallback": True,
                    "source": "m5_swing", "level_id": None}
    return None   # REJECT_NO_TARGET — never a synthetic fixed-R substitute


# ---------------------------------------------------------------------------
# Orchestration: G1 -> G2 -> (G4 needs entry) -> G5 -> G6 -> G7 -> G9
# ---------------------------------------------------------------------------

@dataclass
class CandidateResult:
    decision: str                         # "CANDIDATE_READY" or "REJECT_<GATE>"
    direction: str | None = None
    entry: float | None = None
    gates: dict = field(default_factory=dict)
    rejection_code: str | None = None
    secondary_rejection_codes: tuple[str, ...] = field(default_factory=tuple)


def evaluate_candidates(m5, h1, d1, entry_price, consumed_levels, params=None):
    """Evaluate BOTH directions against G1-G9 (excluding G8) for a single
    signal bar, given the already-bounded, closed-candle H1/D1/M5 windows and
    the known next-bar-open entry price. Returns the list of per-direction
    CandidateResult (both may reject; at most one should reach
    CANDIDATE_READY at a time since G1 bias is direction-specific).

    G4 is evaluated but does NOT short-circuit: G5/G6/G7/G9 do not consume
    G4's output, so they can still be computed for evidence even when G4
    fails — this is required so a rejected candidate's trace can record BOTH
    a location failure AND a net-reward failure at once (see this task's
    Example 2 fixture: premium/discount wrong AND net RR below threshold,
    both must appear in the same rejection record). G1/G2 are true structural
    prerequisites for everything downstream and still short-circuit."""
    params = params or {}
    results = []
    g1 = evaluate_g1_bias(h1, params)
    if g1["state"] not in ("BULLISH", "BEARISH"):
        results.append(CandidateResult(decision="REJECT_G1_BIAS", gates={"G1": g1},
                                        rejection_code="G1_NEUTRAL_OR_CONFLICTING"))
        return results
    direction = "long" if g1["state"] == "BULLISH" else "short"

    g2 = evaluate_g2_external_structure(h1, params)
    if g2 is None:
        results.append(CandidateResult(decision="REJECT_G2_STRUCTURE", direction=direction,
                                        gates={"G1": g1}, rejection_code="G2_NO_DEALING_RANGE"))
        return results

    g4 = evaluate_g4_location(direction, entry_price, g2)
    skip_g4 = bool(params.get("_skip_g4", False))   # ablation A0/A2 only — see engine's `ablation` flag
    g4_failed = (not g4["valid"]) and (not skip_g4)

    g5 = evaluate_g5_htf_poi(h1, d1, direction, g2, params)
    if g5 is None:
        results.append(CandidateResult(
            decision="REJECT_G4_LOCATION" if g4_failed else "REJECT_G5_POI",
            direction=direction, entry=entry_price, gates={"G1": g1, "G2": g2, "G4": g4},
            rejection_code="G4_WRONG_SIDE_OF_EQUILIBRIUM" if g4_failed else "G5_NO_FRESH_CAUSAL_HTF_POI",
            secondary_rejection_codes=() if g4_failed else ()))
        return results

    g6 = evaluate_g6_m5_trigger(m5, direction, g5, params)
    if g6 is None:
        results.append(CandidateResult(
            decision="REJECT_G4_LOCATION" if g4_failed else "REJECT_G6_TRIGGER",
            direction=direction, entry=entry_price, gates={"G1": g1, "G2": g2, "G4": g4, "G5": g5},
            rejection_code="G4_WRONG_SIDE_OF_EQUILIBRIUM" if g4_failed else "G6_SEQUENCE_NOT_SATISFIED"))
        return results

    g7 = evaluate_g7_stop(direction, entry_price, g5, g2, g6, m5, params)
    if g7 is None:
        results.append(CandidateResult(
            decision="REJECT_G4_LOCATION" if g4_failed else "REJECT_G7_STOP",
            direction=direction, entry=entry_price, gates={"G1": g1, "G2": g2, "G4": g4, "G5": g5, "G6": g6},
            rejection_code="G4_WRONG_SIDE_OF_EQUILIBRIUM" if g4_failed else "G7_INVALID_STOP_GEOMETRY"))
        return results

    g9 = evaluate_g9_target(direction, entry_price, g2, m5, consumed_levels, params)
    if g9 is None:
        results.append(CandidateResult(
            decision="REJECT_G4_LOCATION" if g4_failed else "REJECT_G9_TARGET",
            direction=direction, entry=entry_price, gates={"G1": g1, "G2": g2, "G4": g4, "G5": g5, "G6": g6, "G7": g7},
            rejection_code="G4_WRONG_SIDE_OF_EQUILIBRIUM" if g4_failed else "REJECT_NO_TARGET"))
        return results

    if g4_failed:
        # G1/G2/G5/G6/G7/G9 all structurally succeeded — only G4 blocks. The
        # engine layer (which owns G8/costs) may still evaluate G8 against
        # this same g7/g9 for combined-evidence purposes (Example 2).
        results.append(CandidateResult(
            decision="REJECT_G4_LOCATION", direction=direction, entry=entry_price,
            gates={"G1": g1, "G2": g2, "G4": g4, "G5": g5, "G6": g6, "G7": g7, "G9": g9},
            rejection_code="G4_WRONG_SIDE_OF_EQUILIBRIUM"))
        return results

    results.append(CandidateResult(
        decision="CANDIDATE_READY", direction=direction, entry=entry_price,
        gates={"G1": g1, "G2": g2, "G4": g4, "G5": g5, "G6": g6, "G7": g7, "G9": g9},
    ))
    return results
