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

VARIANT_TABLE = {
    "E1M1": {"direction": "SELL", "horizon": "INTRADAY"},
    "E1M2": {"direction": "BUY",  "horizon": "INTRAWEEK"},
    "E1M3": {"direction": "SELL", "horizon": "MULTI_HORIZON"},
    "E2M1": {"direction": "SELL", "horizon": "INTRADAY"},
    "E2M2": {"direction": "BUY",  "horizon": "OVERNIGHT"},
    "E2M3": {"direction": "SELL", "horizon": "INTRAWEEK"},
    "E3M1": {"direction": "BUY",  "horizon": "INTRADAY"},
    "E3M2": {"direction": "BUY",  "horizon": "INTRADAY"},
    "E3M3": {"direction": "SELL", "horizon": "INTRADAY"},
}
HORIZON_MAX_HOURS = {"INTRADAY": 12, "OVERNIGHT": 24, "INTRAWEEK": 120, "MULTI_HORIZON": 120}

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


def generate_signal(e_trigger, m_model, symbol, structure, rr=2.0, min_rr=2.0):
    variant = e_trigger + m_model
    if variant not in VARIANT_TABLE:
        return None
    direction = VARIANT_TABLE[variant]["direction"]
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
    ok = (realized_rr is None) or (realized_rr >= min_rr)
    return {
        "variant": variant, "e_trigger": e_trigger, "m_model": m_model,
        "symbol": symbol, "direction": direction, "horizon": horizon,
        "max_hold_hours": HORIZON_MAX_HOURS[horizon],
        "entry": round(entry, 5), "stop": round(stop, 5),
        "risk_per_unit": round(risk, 5),
        "tp1_1R": round(tp1, 5), "primary_tp": primary_tp,
        "rr_to_primary_tp": realized_rr,
        "decision": "SIGNAL" if ok else "REJECT_RR",
        "status": "RESEARCH_CANDIDATE",
    }


def detect_bias(h1):
    hi, lo = e.swings(h1)
    return {"BULLISH": "BUY", "BEARISH": "SELL"}.get(e.trend(hi, lo))


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
                     swept_level=_swept_level(m5, bias), inducement=inducement)


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
    return Structure(zone_low=low, zone_high=high, swept_level=_swept_level(m5, bias))


def detect_structure_m3(m5, bias):
    want = "bull" if bias == "BUY" else "bear"
    fvs = [f for f in e.fvgs(m5) if f["dir"] == want]
    sw = [x for x in e.liquidity_sweeps(m5) if x["dir"] == want]
    if not fvs or not sw:
        return None
    fv = fvs[-1]
    if fv["i"] < sw[-1]["i"]:
        return None
    origin = m5[max(0, fv["i"] - 2)]["low" if bias == "BUY" else "high"]
    mid = (fv["lower"] + fv["upper"]) / 2.0
    last = m5[-1]["close"]
    retraced = last <= mid if bias == "SELL" else last >= mid
    if not retraced:
        return None
    return Structure(zone_low=fv["lower"], zone_high=fv["upper"],
                     swept_level=sw[-1]["level"], displacement_origin=origin)


def detect_e1_gap_reaction(h1, bias, reaction_lookback=6):
    """Conservative E1 proxy from source slides 53/55.

    E1 is explicitly "price fills & reacts to gap" on H1.  A direction-aligned
    prior FVG must be touched by a recent closed candle which then closes away
    from the gap midpoint.  This is deliberately stricter than the former E1
    fallback and remains a PLATFORM_INTERPRETATION until more source examples
    are labelled.
    """
    if bias not in ("BUY", "SELL") or len(h1) < 4:
        return False
    want = "bull" if bias == "BUY" else "bear"
    gaps = [gap for gap in e.fvgs(h1) if gap["dir"] == want]
    first_reaction = max(0, len(h1) - reaction_lookback)
    for candle_i in range(len(h1) - 1, first_reaction - 1, -1):
        candle = h1[candle_i]
        for gap in reversed(gaps):
            if gap["i"] >= candle_i:
                continue
            midpoint = (gap["lower"] + gap["upper"]) / 2.0
            touched = candle["low"] <= gap["upper"] and candle["high"] >= gap["lower"]
            if not touched:
                continue
            if bias == "SELL":
                rejected = candle["close"] < midpoint and candle["close"] < candle["open"]
            else:
                rejected = candle["close"] > midpoint and candle["close"] > candle["open"]
            if rejected:
                return True
    return False


def detect_e_trigger(h1, bias=None):
    """Classify an H1 cause without treating E1 as a default catch-all."""
    wanted_sweep = "bull" if bias == "BUY" else "bear" if bias == "SELL" else None
    recent_from = max(0, len(h1) - 12)
    if any(s["i"] >= recent_from and (wanted_sweep is None or s["dir"] == wanted_sweep)
           for s in e.liquidity_sweeps(h1)):
        return "E3"
    if detect_e1_gap_reaction(h1, bias):
        return "E1"
    # E2 remains a first-pass POI proxy.  It must be replaced by a fresh-zone
    # reaction detector before the implementation interlock can be enabled.
    if e.order_blocks(h1):
        return "E2"
    return None


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


def analyze(symbol, m5, h1=None, d1=None, primary_tp=None):
    htf = h1 if h1 else m5
    bias = detect_bias(htf)
    if bias is None:
        return {"symbol": symbol, "decision": "NO-SIGNAL", "reason": "HTF ranging / no bias"}
    e_trig = detect_e_trigger(htf, bias)
    if e_trig is None:
        return {"symbol": symbol, "decision": "NO-SIGNAL",
                "reason": "no confirmed H1 E-trigger (E1 gap reaction / E2 POI / E3 sweep)"}
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
