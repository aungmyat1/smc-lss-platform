#!/usr/bin/env python3
"""SMC-LSS v3.5 signal engine - one parameterized procedure for all 9 ExM variants.

Source of truth: docs/strategy/SMC-LSS-v3.5-SIGNAL-RULESET.md, specs/v3.5.yaml.
Status: RESEARCH_CANDIDATE. This engine does NOT authorize live trading.

Two layers: a deterministic FORMULA layer (generate_signal) and a best-effort
DETECTION layer (analyze) over closed candles. No look-ahead, closed candles only.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import smc_engine as e

# v3.6 spec Sec 1: direction is NOT stored per variant. v3.5 hard-locked one
# direction per cell (e.g. E1M1 always SELL) because each variant was
# reverse-engineered from a single historical chart — meaning e.g. E1M1
# could structurally never trade BUY even in a bull regime. Direction is now
# always a live Stage-3 output, computed from the E-trigger's own reaction
# (see detect_e_trigger). Only horizon remains a fixed per-variant property
# (a timing archetype of the E×M combination, not a bias artifact).
VARIANT_TABLE = {
    "E1M1": {"horizon": "INTRADAY"},
    "E1M2": {"horizon": "INTRAWEEK"},
    "E1M3": {"horizon": "MULTI_HORIZON"},
    "E2M1": {"horizon": "INTRADAY"},
    "E2M2": {"horizon": "OVERNIGHT"},
    "E2M3": {"horizon": "INTRAWEEK"},
    "E3M1": {"horizon": "INTRADAY"},
    "E3M2": {"horizon": "INTRADAY"},
    "E3M3": {"horizon": "INTRADAY"},
}
HORIZON_MAX_HOURS = {"INTRADAY": 12, "OVERNIGHT": 24, "INTRAWEEK": 120, "MULTI_HORIZON": 120}

# v3.6 spec (docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md) numeric defaults —
# TUNABLE via backtest-researcher/validation, never hand-edited ad hoc.
IFVG_MAX_AGE_M5_BARS = 20      # Sec 6: FVG -> inversion close, max age
IFVG_RETRACE_MAX_BARS = 30     # Sec 6/7: inversion -> retrace entry, max wait

INSTRUMENT_PROFILES = {
    "fx_major": {"point": 0.00001, "buffer": 0.00030, "spread": 0.00008},
    "fx_jpy":   {"point": 0.001,   "buffer": 0.030, "spread": 0.010},
    "metal":    {"point": 0.01,    "buffer": 0.50, "spread": 0.30},
    "crypto":   {"point": 0.01,    "buffer": 60.0, "spread": 20.0},
}
SYMBOL_PROFILE = {
    "EURUSD": "fx_major", "GBPUSD": "fx_major", "EURGBP": "fx_major",
    "GBPJPY": "fx_jpy", "CHFJPY": "fx_jpy", "BTCJPY": "fx_jpy",
    "XAUUSD": "metal", "XAUUSD-VIP": "metal",
    "BTCUSD": "crypto", "BTCUSDT": "crypto", "ETHUSDT": "crypto",
}


def profile_for(symbol):
    return INSTRUMENT_PROFILES[SYMBOL_PROFILE.get(symbol, "fx_major")]


@dataclass
class Structure:
    zone_low: float
    zone_high: float
    swept_level: float = None
    displacement_origin: float = None
    inducement: float = None
    primary_tp: float = None
    zone_creation_i: int = None        # window-local bar index the zone formed at;
                                        # used for one-signal-per-structure dedup (§12)
    extras: dict = field(default_factory=dict)

    def midpoint(self):
        return (self.zone_low + self.zone_high) / 2.0


def _stop_sell(m_model, s, buf):
    cands = [s.zone_high]
    if m_model == "M1" and s.inducement is not None:
        cands.append(s.inducement)
    if s.swept_level is not None:
        cands.append(s.swept_level)
    if m_model == "M3" and s.displacement_origin is not None:
        cands.append(s.displacement_origin)
    return max(cands) + buf


def _stop_buy(m_model, s, buf):
    cands = [s.zone_low]
    if m_model == "M1" and s.inducement is not None:
        cands.append(s.inducement)
    if s.swept_level is not None:
        cands.append(s.swept_level)
    if m_model == "M3" and s.displacement_origin is not None:
        cands.append(s.displacement_origin)
    return min(cands) - buf


def generate_signal(e_trigger, m_model, symbol, structure, direction, rr=2.0, min_rr=2.0):
    """direction: 'BUY' or 'SELL', supplied by the caller (v3.6 Sec 1) — no
    longer looked up from a per-variant table. Required, not defaulted: a
    caller must always know why it's asking (the live E-trigger reaction),
    not fall back to an assumption."""
    variant = e_trigger + m_model
    if variant not in VARIANT_TABLE:
        return None
    if direction not in ("BUY", "SELL"):
        return None
    horizon = VARIANT_TABLE[variant]["horizon"]
    buf = profile_for(symbol)["buffer"]
    entry = structure.midpoint()
    if direction == "SELL":
        stop = _stop_sell(m_model, structure, buf)
        if stop <= entry:
            return None
        risk = stop - entry
        tp1 = entry - risk
    else:
        stop = _stop_buy(m_model, structure, buf)
        if stop >= entry:
            return None
        risk = entry - stop
        tp1 = entry + risk
    primary_tp = structure.primary_tp
    realized_rr = round(abs(primary_tp - entry) / risk, 2) if (primary_tp is not None and risk > 0) else None
    # v3.6 spec §11: no identified DOL is a REJECT, not an automatic pass. A
    # missing primary_tp used to make realized_rr None, which the old gate
    # `(realized_rr is None) or (realized_rr >= min_rr)` treated as "ok" —
    # i.e. a trade with no destination silently cleared the R:R gate.
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
        "rr_to_primary_tp": realized_rr,
        "decision": decision,
        "status": "RESEARCH_CANDIDATE",
    }


def detect_bias(h1):
    hi, lo = e.swings(h1)
    return {"BULLISH": "BUY", "BEARISH": "SELL"}.get(e.trend(hi, lo))


# v3.6 spec (docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md) Sec 2-4 numeric
# defaults. TUNABLE via backtest-researcher/validation, never hand-edited.
E1_GAP_MAX_AGE_D1_BARS = 10
E1_REACTION_WINDOW_H1_BARS = 6
E2_POI_MAX_AGE_H1_BARS = 60
E3_RANGE_LOOKBACK_H1_BARS = 40
E3_RECLAIM_WINDOW_H1_BARS = 1
REACTION_WICK_RATIO_MIN = 0.4
SWEEP_WICK_RATIO_MIN = 0.5


def _first_reaction_bar(htf, zone_low, zone_high, want_dir, start_i, max_i, wick_ratio_min):
    """First bar in (start_i, max_i] that touches [zone_low, zone_high] and
    closes back out on the want_dir side ('bull' -> closes above zone_high,
    'bear' -> closes below zone_low) with wick_ratio >= wick_ratio_min on the
    entering side. Returns that bar's index, or None if no bar in range
    qualifies (keeps scanning through mere touches that don't react — only a
    full close through the FAR side ends the search early, since that's the
    zone dying, not just an unreacted touch)."""
    end = min(max_i, len(htf) - 1)
    for j in range(start_i + 1, end + 1):
        c = htf[j]
        if not (c["low"] <= zone_high and c["high"] >= zone_low):
            continue
        rng = c["high"] - c["low"]
        if rng <= 0:
            continue
        if want_dir == "bull":
            wick = min(c["open"], c["close"]) - c["low"]
            if c["close"] > zone_high and (wick / rng) >= wick_ratio_min:
                return j
            if c["close"] < zone_low:
                return None
        else:
            wick = c["high"] - max(c["open"], c["close"])
            if c["close"] < zone_low and (wick / rng) >= wick_ratio_min:
                return j
            if c["close"] > zone_high:
                return None
    return None


def _e1_trigger(h1, d1):
    """D1 gap (3-candle D1 FVG) fill/reaction at H1 context (Sec 2)."""
    if not d1 or not h1:
        return None
    gaps = e.fvgs(d1)
    n_d1 = len(d1)
    for g in reversed(gaps):
        if (n_d1 - 1) - g["i"] > E1_GAP_MAX_AGE_D1_BARS:
            break                               # gaps are index-ascending; older from here on
        if e.mitigation_status(d1, g["i"], g["lower"], g["upper"], g["dir"]) == "INVALIDATED":
            continue
        gap_time = d1[g["i"]]["time"]
        start_h1 = next((k for k, b in enumerate(h1) if b["time"] > gap_time), None)
        if start_h1 is None:
            continue
        j = _first_reaction_bar(h1, g["lower"], g["upper"], g["dir"],
                                start_h1 - 1, start_h1 - 1 + E1_REACTION_WINDOW_H1_BARS,
                                REACTION_WICK_RATIO_MIN)
        if j is not None:
            return {"e_trigger": "E1", "bias": "BUY" if g["dir"] == "bull" else "SELL", "confirm_i": j}
    return None


def _e2_trigger(h1):
    """H1 reaction at a fresh/mitigated (not invalidated) order-block POI (Sec 3)."""
    obs = e.order_blocks(h1)
    n = len(h1)
    for ob in reversed(obs):
        if (n - 1) - ob["i"] > E2_POI_MAX_AGE_H1_BARS:
            break
        if e.mitigation_status(h1, ob["i"], ob["low"], ob["high"], ob["dir"]) == "INVALIDATED":
            continue
        j = _first_reaction_bar(h1, ob["low"], ob["high"], ob["dir"],
                                ob["i"], n - 1, REACTION_WICK_RATIO_MIN)
        if j is not None:
            return {"e_trigger": "E2", "bias": "BUY" if ob["dir"] == "bull" else "SELL", "confirm_i": j}
    return None


def _e3_trigger(h1):
    """H1 sweep + reclaim of EXTERNAL liquidity — the current dealing-range
    extremity, not an internal/minor swing (Sec 4)."""
    n = len(h1)
    hi, lo = e.swings(h1)
    lookback_start = max(0, n - E3_RANGE_LOOKBACK_H1_BARS)
    hi_in = [p for i, p in hi if i >= lookback_start]
    lo_in = [p for i, p in lo if i >= lookback_start]
    if not hi_in or not lo_in:
        return None
    ext_high, ext_low = max(hi_in), min(lo_in)
    sweeps = e.liquidity_sweeps(h1, min_wick_ratio=SWEEP_WICK_RATIO_MIN)
    for sw in reversed(sweeps):
        if sw["level"] != ext_high and sw["level"] != ext_low:
            continue                           # only the range extremity is EXTERNAL liquidity
        j = sw["i"]
        for k in range(j, min(j + E3_RECLAIM_WINDOW_H1_BARS + 1, n)):
            c = h1[k]
            if sw["dir"] == "bull" and c["close"] > sw["level"]:
                return {"e_trigger": "E3", "bias": "BUY", "confirm_i": k}
            if sw["dir"] == "bear" and c["close"] < sw["level"]:
                return {"e_trigger": "E3", "bias": "SELL", "confirm_i": k}
    return None


def _swept_level(m5, bias):
    want = "bull" if bias == "BUY" else "bear"
    sw = [x for x in e.liquidity_sweeps(m5) if x["dir"] == want]
    return sw[-1]["level"] if sw else None


def detect_structure_m1(m5, bias):
    want = "bull" if bias == "BUY" else "bear"
    fvs = [f for f in e.fvgs(m5) if f["dir"] == want]
    if not fvs:
        return None
    fv = fvs[-1]
    ind = e.inducement(m5)
    inducement = ind["bull_inducement"] if bias == "BUY" else ind["bear_inducement"]
    return Structure(zone_low=fv["lower"], zone_high=fv["upper"],
                     swept_level=_swept_level(m5, bias), inducement=inducement,
                     zone_creation_i=fv["i"])


def detect_structure_m2(m5, bias):
    want = "bull" if bias == "BUY" else "bear"
    obs = [o for o in e.order_blocks(m5) if o["dir"] == want]
    fvs = [f for f in e.fvgs(m5) if f["dir"] == want]
    if not obs or not fvs:
        return None
    ob, fv = obs[-1], fvs[-1]
    low = max(ob["low"], fv["lower"])
    high = min(ob["high"], fv["upper"])
    if low >= high:
        return None
    return Structure(zone_low=low, zone_high=high, swept_level=_swept_level(m5, bias),
                     zone_creation_i=max(ob["i"], fv["i"]))


def detect_structure_m3(m5, bias):
    """M3: sweep -> ATR-qualified displacement -> IFVG inversion -> entry
    after >=50% retrace (v3.6 spec Sec 5-7).

    The source FVG is the OPPOSITE polarity from the trade direction — a
    bearish FVG inverts into bullish support for a BUY, and vice versa —
    per Sec 6. The prior implementation used a same-direction FVG directly
    (no displacement gate, no inversion check at all), which is really M1/M2
    continuation-entry logic mislabeled as M3's inverse-FVG mechanic.
    """
    move_dir = "bull" if bias == "BUY" else "bear"
    source_dir = "bear" if bias == "BUY" else "bull"     # opposite polarity; inverts INTO bias direction
    sweeps = [x for x in e.liquidity_sweeps(m5) if x["dir"] == move_dir]
    if not sweeps:
        return None
    sweep = sweeps[-1]
    disp = e.displacement_move(m5, sweep["i"], move_dir)
    if disp is None:
        return None
    # source FVG must form during/immediately after the displacement (Sec 7)
    candidates = [f for f in e.fvgs(m5) if f["dir"] == source_dir
                 and disp["start"] <= f["i"] <= disp["end"] + 1]
    if not candidates:
        return None
    fv = candidates[-1]
    # inversion: a full CLOSE through the far boundary within the age window
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
                     zone_creation_i=fv["i"])


def detect_e_trigger(h1):
    if e.liquidity_sweeps(h1):
        return "E3"
    if e.order_blocks(h1):
        return "E2"
    return "E1"


_DETECT = {"M1": detect_structure_m1, "M2": detect_structure_m2, "M3": detect_structure_m3}


def _dol_target(m5, direction, entry):
    """Pre-selected DOL proxy: nearest opposing liquidity beyond entry in the
    trade direction (sell-side swing low for SELL, buy-side swing high for BUY)."""
    hi, lo = e.swings(m5)
    if direction == "SELL":
        cands = [p for _, p in lo if p < entry]
        return max(cands) if cands else None
    cands = [p for _, p in hi if p > entry]
    return min(cands) if cands else None


def analyze(symbol, m5, h1=None, d1=None, primary_tp=None, index_offset=0):
    """index_offset: the caller's global bar index that m5[0] corresponds to
    (0 if m5 is the full series). Needed so structure_key (§12) identifies
    the same real zone across a sliding backtest window, not just a
    window-local coordinate that resets every call."""
    htf = h1 if h1 else m5
    bias = detect_bias(htf)
    if bias is None:
        return {"symbol": symbol, "decision": "NO-SIGNAL", "reason": "HTF ranging / no bias"}
    e_trig = detect_e_trigger(htf)
    for m_mod in ("M2", "M1", "M3"):
        variant = e_trig + m_mod
        if VARIANT_TABLE.get(variant, {}).get("direction") != bias:
            continue
        st = _DETECT[m_mod](m5, bias)
        if st is None:
            continue
        direction = VARIANT_TABLE[variant]["direction"]
        st.primary_tp = primary_tp if primary_tp is not None else _dol_target(m5, direction, st.midpoint())
        sig = generate_signal(e_trig, m_mod, symbol, st)
        if sig and sig["decision"] == "SIGNAL":
            sig["detected"] = True
            sig["structure_key"] = (
                (symbol, variant, "zone", index_offset + st.zone_creation_i)
                if st.zone_creation_i is not None else None
            )
            return sig
    return {"symbol": symbol, "decision": "NO-SIGNAL",
            "reason": "bias " + bias + ", e-trigger " + e_trig + ": no matching M-model structure"}


if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--m5"); ap.add_argument("--h1"); ap.add_argument("--d1")
    ap.add_argument("--symbol", default="EURUSD")
    a = ap.parse_args()
    if a.analyze and a.m5:
        m5 = e.load_candles(a.m5)
        h1 = e.load_candles(a.h1) if a.h1 else None
        d1 = e.load_candles(a.d1) if a.d1 else None
        print(json.dumps(analyze(a.symbol, m5, h1, d1), indent=2))
    else:
        s = Structure(zone_low=26649, zone_high=26749, swept_level=26900,
                      displacement_origin=26890, primary_tp=25324.7)
        print(json.dumps(generate_signal("E2", "M3", "BTCUSD", s), indent=2))
