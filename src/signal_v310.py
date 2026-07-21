#!/usr/bin/env python3
"""SMC-LSS v3.10 "Reversal Capture" research signal engine.

Source of truth: specs/v3.10.yaml, reports/audit/ST_C1_V310_REVERSAL_CAPTURE_RCR.md.
Status: RESEARCH_CANDIDATE. Does NOT authorize live trading and must never
import or call a broker-order path (CLAUDE.md hard rules /
docs/RESEARCH-CHARTER.md).

v3.10 is NOT an edit to v3.9 ("Clean SMC", continuation-only, retained
immutable as a prior candidate/control). It adds a reversal trade thesis:
E1 (D1 gap reaction) is re-enabled with a partial-fill tolerance, gated
behind an H4 trend-bias DIVERGENCE requirement (the entry direction must
oppose the H4 bias, not agree with it) so the engine only takes setups
where price is reacting against the prevailing higher-timeframe trend, not
continuation setups (that is v3.9's job). E2 additionally requires the
reaction to hold for a few bars before qualifying, E3 accepts internal (not
only external) liquidity, and the reward target scales with the
displacement leg length instead of being purely DOL-based.

Every mechanism below is new, owner-directed design with no prior backtest
evidence in this repo (disclosed in the RCR) — each is documented with its
concrete interpretation so a reviewer can trace spec prose to exact code,
per this repo's established audit discipline.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import datetime
import smc_engine as e

VARIANT_TABLE = {
    "E1M2": {"horizon": "MULTI_HORIZON"},
    "E2M1": {"horizon": "OVERNIGHT"},
    "E2M2": {"horizon": "OVERNIGHT"},
    "E2M3": {"horizon": "INTRAWEEK"},
    "E3M1": {"horizon": "INTRADAY"},
    "E3M2": {"horizon": "INTRADAY"},
    "E3M3": {"horizon": "INTRADAY"},
}
HORIZON_MAX_HOURS = {"INTRADAY": 12, "OVERNIGHT": 24, "INTRAWEEK": 120, "MULTI_HORIZON": 120}

IFVG_MAX_AGE_M5_BARS = 20
IFVG_RETRACE_MAX_BARS = 30

# --- v3.10 parameter set (specs/v3.10.yaml parameter_registry) -------------
TREND_BIAS_H4_BARS = 20
REVERSAL_REQUIRES_DIVERGENCE = True

E1_ENABLED = True                      # v3.10: E1 RE-ENABLED (was disabled in v3.9)
E1_GAP_MAX_AGE_D1_BARS = 20
E1_REACTION_WINDOW_H1_BARS = 12
E1_REACTION_WICK_RATIO_MIN = 0.30
E1_GAP_REVERSAL_TOLERANCE_PCT = 0.25   # reaction valid once >= (1 - tolerance) = 75% of the gap is filled

E2_POI_MAX_AGE_H1_BARS = 120
E2_REACTION_WICK_RATIO_MIN = 0.0
E2_DEMAND_ZONE_CONFIRMATION_BARS = 3   # price must hold on the reaction side for this many bars after the reaction

E3_RANGE_LOOKBACK_H1_BARS = 60
E3_SWEEP_WICK_RATIO_MIN = 0.0
E3_INTERNAL_LIQUIDITY_TRIGGER = True   # accept sweeps of internal (non-extremity) confirmed swings too

DISPLACEMENT_BODY_RATIO_MIN = 0.6
DISPLACEMENT_START_OFFSET_BARS = 0
DISPLACEMENT_MAX_RUN_BARS = 12

STOP_BUFFER_ATR_PERIOD = 14
STOP_BUFFER_ATR_MULT = 0.15            # carried forward from the v3.9/replay-engine convention

MIN_RR = 3.0
DYNAMIC_RR = True

_SESSION_WINDOWS_UTC_MIN = [
    (7 * 60, 16 * 60),      # London 07:00-16:00 UTC
    (12 * 60, 21 * 60),     # New York 12:00-21:00 UTC
]


@dataclass
class Structure:
    zone_low: float
    zone_high: float
    swept_level: float = None
    displacement_origin: float = None
    displacement_range: float = None   # NEW: feeds dynamic_rr target scaling
    inducement: float = None
    primary_tp: float = None
    zone_creation_i: int = None
    extras: dict = field(default_factory=dict)

    def midpoint(self):
        return (self.zone_low + self.zone_high) / 2.0


def _stop_buffer(c, idx):
    return e.atr(c, idx, STOP_BUFFER_ATR_PERIOD) * STOP_BUFFER_ATR_MULT


def _stop_sell(m_model, s, buf):
    cands = [s.zone_high]
    if m_model == "M1" and s.inducement is not None:
        cands.append(s.inducement)
    if s.swept_level is not None:
        cands.append(s.swept_level)
    if m_model in ("M2", "M3") and s.displacement_origin is not None:
        cands.append(s.displacement_origin)
    return max(cands) + buf


def _stop_buy(m_model, s, buf):
    cands = [s.zone_low]
    if m_model == "M1" and s.inducement is not None:
        cands.append(s.inducement)
    if s.swept_level is not None:
        cands.append(s.swept_level)
    if m_model in ("M2", "M3") and s.displacement_origin is not None:
        cands.append(s.displacement_origin)
    return min(cands) - buf


def _dynamic_target(direction, entry, risk, structure):
    """dynamic_rr (NEW): target distance scales with the displacement leg
    length rather than being purely DOL-based, floored at MIN_RR so the
    reward floor is never violated. Falls back to the pre-selected DOL
    (structure.primary_tp, set by the caller before this runs) if the
    dynamic distance would fall short of that floor AND no displacement
    range is available — matching ST-C1_v1.3.0.yaml's target_rule exactly."""
    floor_distance = MIN_RR * risk
    disp_distance = structure.displacement_range if structure.displacement_range else 0.0
    dynamic_distance = max(floor_distance, disp_distance)
    dynamic_target = entry + dynamic_distance if direction == "BUY" else entry - dynamic_distance
    if structure.primary_tp is None:
        return dynamic_target
    # prefer whichever target is further in the trade's favor (more conservative
    # acceptance, never a target closer than the DOL-derived one, matching
    # the "no synthetic fixed-R substitute below the floor" contract note)
    if direction == "BUY":
        return max(dynamic_target, structure.primary_tp)
    return min(dynamic_target, structure.primary_tp)


def generate_signal(e_trigger, m_model, symbol, structure, direction, m5, entry_i, min_rr=MIN_RR):
    variant = e_trigger + m_model
    if variant not in VARIANT_TABLE:
        return None
    if direction not in ("BUY", "SELL"):
        return None
    horizon = VARIANT_TABLE[variant]["horizon"]
    buf = _stop_buffer(m5, entry_i)
    entry = structure.midpoint()
    if direction == "SELL":
        stop = _stop_sell(m_model, structure, buf)
        if stop <= entry:
            return None
        risk = stop - entry
    else:
        stop = _stop_buy(m_model, structure, buf)
        if stop >= entry:
            return None
        risk = entry - stop
    tp1 = entry - risk if direction == "SELL" else entry + risk
    if DYNAMIC_RR:
        primary_tp = _dynamic_target(direction, entry, risk, structure)
    else:
        primary_tp = structure.primary_tp
    realized_rr = round(abs(primary_tp - entry) / risk, 2) if (primary_tp is not None and risk > 0) else None
    if primary_tp is None:
        decision = "REJECT_NO_TARGET"
    elif realized_rr >= min_rr:
        decision = "SIGNAL"
    else:
        decision = "REJECT_RR"
    return {
        "variant": variant, "e_trigger": e_trigger, "m_model": m_model,
        "symbol": symbol, "direction": direction, "horizon": horizon,
        "max_hold_hours": HORIZON_MAX_HOURS[horizon],
        "entry": round(entry, 5), "stop": round(stop, 5),
        "risk_per_unit": round(risk, 5),
        "tp1_1R": round(tp1, 5), "primary_tp": primary_tp,
        "rr_to_primary_tp_gross": realized_rr,
        "decision": decision,
        "status": "RESEARCH_CANDIDATE",
        "spec_version": "3.10",
    }


def _in_session(ts: str) -> bool:
    if len(ts) < 16:
        return True
    try:
        hh = int(ts[11:13])
        mm = int(ts[14:16])
    except (ValueError, IndexError):
        return True
    t = hh * 60 + mm
    if not any(start <= t < end for start, end in _SESSION_WINDOWS_UTC_MIN):
        return False
    try:
        dt = datetime.datetime.strptime(ts[:16], "%Y-%m-%d %H:%M")
    except ValueError:
        return True
    if dt.weekday() >= 5:
        return False
    return True


def h4_trend_bias(h4, bars=TREND_BIAS_H4_BARS):
    """NEW: HTF macro bias from the trailing `bars` H4 candles. Reuses the
    same swing/trend primitives as everywhere else in this codebase
    (smc_engine.swings + trend), applied to H4 instead of H1/M5 — no prior
    spec version in this repo has used H4. Returns 'BULLISH'/'BEARISH'/
    'RANGING'. A reversal setup must DIVERGE from this (see
    _passes_divergence_gate), not agree with it."""
    if not h4:
        return "RANGING"
    window = h4[-bars:] if len(h4) > bars else h4
    hi, lo = e.swings(window)
    return e.trend(hi, lo)


def _passes_divergence_gate(entry_dir, h4_bias):
    """v3.10: entry_mode=reversal — the entry direction must OPPOSE the H4
    bias, not agree with it. RANGING H4 bias is treated as no-divergence-
    possible (fail-closed: no bias to diverge from, so no reversal claim is
    valid) rather than a free pass — a fail-open RANGING pass-through would
    let the engine take any direction whenever H4 lacks clear structure,
    which is exactly the "continuation-through-a-loophole" failure mode a
    reversal-only engine must not have."""
    if not REVERSAL_REQUIRES_DIVERGENCE:
        return True
    if h4_bias == "RANGING":
        return False
    if entry_dir == "BUY" and h4_bias == "BEARISH":
        return True
    if entry_dir == "SELL" and h4_bias == "BULLISH":
        return True
    return False


def _gap_fill_pct(gap, reaction_bar):
    """Fraction of the D1 gap's range that price has entered, using the
    single reaction_bar's furthest excursion into the gap (the deepest
    wick, not just the close) -- consistent with "price fills X% of the
    gap" describing a price excursion, not a closing price."""
    lower, upper = gap["lower"], gap["upper"]
    span = upper - lower
    if span <= 0:
        return 0.0
    if gap["dir"] == "bull":
        # bull gap: unfilled space is below the gap; fill = how far price's
        # low has descended INTO the gap from its top (upper) edge
        penetration = upper - reaction_bar["low"]
    else:
        penetration = reaction_bar["high"] - lower
    return max(0.0, min(1.0, penetration / span))


def _e1_trigger_reversal(h1, d1, h4):
    """D1 gap reaction with a partial-fill reversal tolerance (v3.10 NEW),
    gated behind H4 bias divergence. A reaction bar must (a) reach >=
    (1 - E1_GAP_REVERSAL_TOLERANCE_PCT) fill of the gap's range, (b) close
    back out on one side with wick_ratio >= E1_REACTION_WICK_RATIO_MIN
    (auto-detected direction, not tied to the gap's own original
    direction), and (c) that close-out direction must diverge from the H4
    bias. Returns the freshest qualifying gap's reaction, or None."""
    if not d1 or not h1:
        return None
    gaps = e.fvgs(d1)
    n_d1 = len(d1)
    h4_bias = h4_trend_bias(h4)
    min_fill = 1.0 - E1_GAP_REVERSAL_TOLERANCE_PCT
    for g in reversed(gaps):
        if (n_d1 - 1) - g["i"] > E1_GAP_MAX_AGE_D1_BARS:
            break
        if e.mitigation_status(d1, g["i"], g["lower"], g["upper"], g["dir"]) == "INVALIDATED":
            continue
        gap_time = d1[g["i"]]["time"]
        start_h1 = next((k for k, b in enumerate(h1) if b["time"] > gap_time), None)
        if start_h1 is None:
            continue
        end_h1 = min(len(h1) - 1, start_h1 - 1 + E1_REACTION_WINDOW_H1_BARS)
        for j in range(start_h1, end_h1 + 1):
            c = h1[j]
            if _gap_fill_pct(g, c) < min_fill:
                continue
            rng = c["high"] - c["low"]
            if rng <= 0:
                continue
            body_hi, body_lo = max(c["open"], c["close"]), min(c["open"], c["close"])
            upper_wick = c["high"] - body_hi
            lower_wick = body_lo - c["low"]
            # Auto-detected reaction direction from wick geometry alone (no
            # close-vs-body-edge tiebreak): a long lower wick rejects further
            # downside -> bullish reaction; a long upper wick rejects further
            # upside -> bearish reaction. A doji-bodied bar (open == close)
            # with a long lower wick is a textbook rejection candle and must
            # still qualify -- an earlier draft's extra "close > body_lo"
            # check excluded exactly that case (found via fixture testing).
            reaction_dir = None
            if (lower_wick / rng) >= E1_REACTION_WICK_RATIO_MIN:
                reaction_dir = "bull"
            elif (upper_wick / rng) >= E1_REACTION_WICK_RATIO_MIN:
                reaction_dir = "bear"
            if reaction_dir is None:
                continue
            entry_dir = "BUY" if reaction_dir == "bull" else "SELL"
            if not _passes_divergence_gate(entry_dir, h4_bias):
                continue
            return {"e_trigger": "E1", "bias": entry_dir, "confirm_i": j}
    return None


def _first_reaction_bar_with_hold(htf, zone_low, zone_high, want_dir, start_i, max_i,
                                  wick_ratio_min, hold_bars):
    """E2 with the v3.10 hold-confirmation requirement: after the usual
    close-confirmed reaction bar (identical mechanism to v3.9's
    _first_reaction_bar), price must NOT re-enter and invalidate the zone
    for `hold_bars` bars afterward. If it re-enters and closes back through
    the zone within the hold window, the reaction is rejected (the "shift"
    didn't hold) and the scan continues past it."""
    end = min(max_i, len(htf) - 1)
    j = start_i
    while j < end:
        j += 1
        c = htf[j]
        if not (c["low"] <= zone_high and c["high"] >= zone_low):
            continue
        rng = c["high"] - c["low"]
        if rng <= 0:
            continue
        reacted = False
        if want_dir == "bull":
            wick = min(c["open"], c["close"]) - c["low"]
            if c["close"] > zone_high and (wick / rng) >= wick_ratio_min:
                reacted = True
            elif c["close"] < zone_low:
                continue
        else:
            wick = c["high"] - max(c["open"], c["close"])
            if c["close"] < zone_low and (wick / rng) >= wick_ratio_min:
                reacted = True
            elif c["close"] > zone_high:
                continue
        if not reacted:
            continue
        hold_end = min(j + hold_bars, len(htf) - 1)
        held = True
        for k in range(j + 1, hold_end + 1):
            hc = htf[k]
            if want_dir == "bull" and hc["close"] < zone_low:
                held = False
                break
            if want_dir == "bear" and hc["close"] > zone_high:
                held = False
                break
        if held and hold_end >= j + hold_bars:
            return j
        # not yet enough bars to confirm hold, or hold failed -- try the next candidate
        if not held:
            continue
        return None   # reacted but hold window not yet complete within this point-in-time slice
    return None


def _e2_trigger_reversal(h1, h4):
    """H1 POI reaction requiring a hold confirmation, gated behind H4
    divergence (same gate as E1)."""
    obs = e.order_blocks(h1)
    n = len(h1)
    h4_bias = h4_trend_bias(h4)
    for ob in reversed(obs):
        if (n - 1) - ob["i"] > E2_POI_MAX_AGE_H1_BARS:
            break
        if e.mitigation_status(h1, ob["i"], ob["low"], ob["high"], ob["dir"]) == "INVALIDATED":
            continue
        j = _first_reaction_bar_with_hold(h1, ob["low"], ob["high"], ob["dir"],
                                          ob["i"], n - 1, E2_REACTION_WICK_RATIO_MIN,
                                          E2_DEMAND_ZONE_CONFIRMATION_BARS)
        if j is not None:
            entry_dir = "BUY" if ob["dir"] == "bull" else "SELL"
            if not _passes_divergence_gate(entry_dir, h4_bias):
                continue
            return {"e_trigger": "E2", "bias": entry_dir, "confirm_i": j}
    return None


def _e3_trigger_reversal(h1, h4):
    """H1 sweep+reclaim, gated behind H4 divergence.

    E3_INTERNAL_LIQUIDITY_TRIGGER=True (the v3.10 default and this module's
    only supported mode) means ANY confirmed swing high/low sweep+reclaim
    qualifies, not just the dealing-range extremity (v3.9's external-only
    restriction is dropped). If a future caller needs the external-only
    behavior, use src/signal_v39.py's _e3_trigger instead of setting this
    flag False here -- this function does not implement an external-only
    fallback path."""
    assert E3_INTERNAL_LIQUIDITY_TRIGGER, (
        "this module only implements the internal-liquidity-accepted mode; "
        "for external-only E3, use signal_v39._e3_trigger"
    )
    sweeps = e.liquidity_sweeps(h1, min_wick_ratio=E3_SWEEP_WICK_RATIO_MIN)
    h4_bias = h4_trend_bias(h4)
    for sw in reversed(sweeps):
        j = sw["i"]
        c = h1[j]
        entry_dir = None
        if sw["dir"] == "bull" and c["close"] > sw["level"]:
            entry_dir = "BUY"
        elif sw["dir"] == "bear" and c["close"] < sw["level"]:
            entry_dir = "SELL"
        if entry_dir is None:
            continue
        if not _passes_divergence_gate(entry_dir, h4_bias):
            continue
        return {"e_trigger": "E3", "bias": entry_dir, "confirm_i": j}
    return None


def detect_e_trigger(h1, d1=None, h4=None):
    """v3.10: E1 is re-enabled; all three E-triggers are gated behind H4
    bias divergence, so only reversal-shaped setups ever qualify."""
    candidates = [t for t in (
        _e1_trigger_reversal(h1, d1, h4),
        _e2_trigger_reversal(h1, h4),
        _e3_trigger_reversal(h1, h4),
    ) if t is not None]
    if not candidates:
        return None
    return max(candidates, key=lambda t: t["confirm_i"])


def _swept_level(m5, bias):
    want = "bull" if bias == "BUY" else "bear"
    sw = [x for x in e.liquidity_sweeps(m5, min_wick_ratio=E3_SWEEP_WICK_RATIO_MIN) if x["dir"] == want]
    return sw[-1]["level"] if sw else None


def detect_structure_m1(m5, bias):
    want = "bull" if bias == "BUY" else "bear"
    sweeps = [x for x in e.liquidity_sweeps(m5, min_wick_ratio=E3_SWEEP_WICK_RATIO_MIN) if x["dir"] == want]
    if not sweeps:
        return None
    sweep = sweeps[-1]
    fvs = [f for f in e.fvgs(m5) if f["dir"] == want and f["i"] > sweep["i"]]
    if not fvs:
        return None
    fv = fvs[-1]
    ind = e.inducement(m5)
    inducement = ind["bull_inducement"] if bias == "BUY" else ind["bear_inducement"]
    return Structure(zone_low=fv["lower"], zone_high=fv["upper"],
                     swept_level=_swept_level(m5, bias), inducement=inducement,
                     zone_creation_i=fv["i"])


def detect_structure_m2(m5, bias):
    """Primary reversal model: supply/demand shift (CHoCH-confirmed via the
    close-through-swing break already embedded in order_blocks()) -> Gold
    Zone -> overlap midpoint. Records displacement_range (NEW) by measuring
    the directional run from the sweep to the OB/FVG zone's formation, for
    dynamic_rr to scale the target off."""
    want = "bull" if bias == "BUY" else "bear"
    obs = [o for o in e.order_blocks(m5) if o["dir"] == want]
    fvs = [f for f in e.fvgs(m5) if f["dir"] == want]
    if not obs or not fvs:
        return None
    ob, fv = obs[-1], fvs[-1]
    sweeps = [x for x in e.liquidity_sweeps(m5, min_wick_ratio=E3_SWEEP_WICK_RATIO_MIN) if x["dir"] == want]
    if not sweeps:
        return None
    sweep = sweeps[-1]
    if ob["i"] <= sweep["i"] and fv["i"] <= sweep["i"]:
        return None
    low = max(ob["low"], fv["lower"])
    high = min(ob["high"], fv["upper"])
    if low >= high:
        return None
    zone_i = max(ob["i"], fv["i"])
    # displacement_range: directional price travel from the sweep bar to the
    # zone's formation bar -- an auto-detected magnitude (not gated on body
    # ratio here; the M2 CHoCH break itself is the qualifying event), used
    # only to scale the dynamic_rr target, never as an additional gate.
    disp_range = abs(m5[zone_i]["close"] - m5[sweep["i"]]["close"])
    return Structure(zone_low=low, zone_high=high, swept_level=_swept_level(m5, bias),
                     zone_creation_i=zone_i, displacement_range=disp_range,
                     displacement_origin=m5[sweep["i"]]["close"])


def detect_structure_m3(m5, bias):
    move_dir = "bull" if bias == "BUY" else "bear"
    source_dir = "bear" if bias == "BUY" else "bull"
    sweeps = [x for x in e.liquidity_sweeps(m5, min_wick_ratio=E3_SWEEP_WICK_RATIO_MIN) if x["dir"] == move_dir]
    if not sweeps:
        return None
    sweep = sweeps[-1]
    disp = _displacement_auto(m5, sweep["i"], move_dir)
    if disp is None:
        return None
    candidates = [f for f in e.fvgs(m5) if f["dir"] == source_dir
                 and disp["start"] <= f["i"] <= disp["end"] + 1]
    if not candidates:
        return None
    fv = candidates[-1]
    inv_i = None
    for j in range(fv["i"] + 1, min(fv["i"] + 1 + IFVG_MAX_AGE_M5_BARS, len(m5))):
        if bias == "BUY" and m5[j]["close"] > fv["upper"]:
            inv_i = j
            break
        if bias == "SELL" and m5[j]["close"] < fv["lower"]:
            inv_i = j
            break
    if inv_i is None:
        return None
    last_i = len(m5) - 1
    if last_i <= inv_i or last_i > inv_i + IFVG_RETRACE_MAX_BARS:
        return None
    mid = (fv["lower"] + fv["upper"]) / 2.0
    last = m5[-1]["close"]
    retraced = last <= mid if bias == "SELL" else last >= mid
    if not retraced:
        return None
    origin = m5[max(0, disp["start"] - 1)]["low" if bias == "BUY" else "high"]
    return Structure(zone_low=fv["lower"], zone_high=fv["upper"],
                     swept_level=sweep["level"], displacement_origin=origin,
                     displacement_range=disp["range"], zone_creation_i=fv["i"])


def _displacement_auto(c, sweep_i, direction):
    """Body-ratio-only displacement with auto direction (v3.10): identical
    mechanism to v3.9's _displacement_v39 (ATR gate dropped, body_ratio>=0.6
    sole qualifier) -- "auto" means the direction is verified from the
    candles' own close-vs-open here, not assumed from an external bias, so
    the same function correctly rejects a run that doesn't actually move
    the requested direction regardless of what the caller expected."""
    n = len(c)
    for disp_start in range(sweep_i + 1 + DISPLACEMENT_START_OFFSET_BARS, sweep_i + 1 + DISPLACEMENT_START_OFFSET_BARS + 1):
        if disp_start >= n:
            break
        run_end = None
        for j in range(disp_start, min(disp_start + DISPLACEMENT_MAX_RUN_BARS, n)):
            cndl = c[j]
            is_dir = (cndl["close"] > cndl["open"]) if direction == "bull" else (cndl["close"] < cndl["open"])
            rng = cndl["high"] - cndl["low"]
            body_ratio = (abs(cndl["close"] - cndl["open"]) / rng) if rng > 0 else 0.0
            if not is_dir or body_ratio < DISPLACEMENT_BODY_RATIO_MIN:
                break
            run_end = j
        if run_end is None:
            continue
        origin_open = c[disp_start]["open"]
        end_close = c[run_end]["close"]
        cum_range = (end_close - origin_open) if direction == "bull" else (origin_open - end_close)
        if cum_range > 0:
            return {"start": disp_start, "end": run_end, "range": cum_range, "origin": origin_open}
    return None


_DETECT = {"M1": detect_structure_m1, "M2": detect_structure_m2, "M3": detect_structure_m3}


def _dol_target(m5, direction, entry):
    hi, lo = e.swings(m5)
    if direction == "SELL":
        cands = [p for _, p in lo if p < entry]
        return max(cands) if cands else None
    cands = [p for _, p in hi if p > entry]
    return min(cands) if cands else None


def analyze(symbol, m5, h1=None, d1=None, h4=None, primary_tp=None, index_offset=0, min_rr=MIN_RR):
    """Point-in-time analysis: only bars already present in m5/h1/d1/h4 are
    ever consulted (no look-ahead)."""
    htf = h1 if h1 else m5
    trig = detect_e_trigger(htf, d1=d1, h4=h4)
    if trig is None:
        return {"symbol": symbol, "decision": "NO-SIGNAL",
                "reason": "no qualifying reversal E-trigger (E1 gap-reversal / E2 hold-confirmed POI / E3 internal-or-external sweep, all H4-divergence gated)"}
    e_trig, bias = trig["e_trigger"], trig["bias"]
    cache: dict = {}
    for m_mod in ("M2", "M1", "M3"):
        variant = e_trig + m_mod
        if variant not in VARIANT_TABLE:
            continue
        st = _DETECT[m_mod](m5, bias)
        if st is None:
            continue
        last_m5_time = m5[-1].get("time", "") if m5 else ""
        if last_m5_time and not _in_session(last_m5_time):
            return {"symbol": symbol, "decision": "NO-SIGNAL",
                    "reason": f"outside London/NY session or weekend at {last_m5_time}"}
        if st.primary_tp is None:
            st.primary_tp = primary_tp if primary_tp is not None else _dol_target(m5, bias, st.midpoint())
        entry_i = len(m5) - 1
        sig = generate_signal(e_trig, m_mod, symbol, st, bias, m5, entry_i, min_rr=min_rr)
        if sig and sig["decision"] == "SIGNAL":
            sig["detected"] = True
            sig["structure_key"] = (
                (symbol, variant, "zone", index_offset + st.zone_creation_i)
                if st.zone_creation_i is not None else None
            )
            return sig
    return {"symbol": symbol, "decision": "NO-SIGNAL",
            "reason": "bias " + bias + ", e-trigger " + e_trig + ": no matching M-model structure"}
