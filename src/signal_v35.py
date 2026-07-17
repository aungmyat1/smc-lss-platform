#!/usr/bin/env python3
"""SMC-LSS v3.5 signal engine — one parameterized procedure for all 9 E×M variants.

Source of truth: docs/strategy/SMC-LSS-v3.5-SIGNAL-RULESET.md, specs/v3.5.yaml.
Status: RESEARCH_CANDIDATE. This engine does NOT authorize live trading.

Per §5 of the ruleset, signal generation is ONE function:
    generate_signal(e_trigger, m_model, instrument_profile, structure) -> signal | None
  - E-trigger (E1/E2/E3): higher-timeframe cause -> bias (BUY/SELL) + invalidation context
  - M-model  (M1/M2/M3): M5 confirmation -> entry anchor + stop formula
  - profile: buffer size + point/tick conversion per instrument
  - structure: the resolved zone levels (from detectors below or supplied by a fixture)

Two layers, cleanly separated:
  * FORMULA layer (this file, fully deterministic + unit-tested): given resolved
    structure levels, compute direction, entry, stop, tp1, R:R, horizon.
  * DETECTION layer (detect_structure, best-effort over closed candles via smc_engine):
    extract those levels from live data. Wiring detection to every variant precisely
    is the remaining M1.5 task; the formula layer is complete and locked.

Determinism: no randomness, closed candles only, no look-ahead.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import smc_engine as e

# ---- variant table (frozen from specs/v3.5.yaml) -------------------------------
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

# ---- instrument profiles (buffer in price units; point = min increment) ---------
INSTRUMENT_PROFILES = {
    "fx_major": {"point": 0.00001, "buffer": 0.00030},   # EURUSD, GBPUSD, EURGBP
    "fx_jpy":   {"point": 0.001,   "buffer": 0.030},     # *JPY
    "metal":    {"point": 0.01,    "buffer": 0.50},      # XAUUSD
    "crypto":   {"point": 0.01,    "buffer": 60.0},      # BTCUSD (wide crypto buffer)
}
SYMBOL_PROFILE = {
    "EURUSD": "fx_major", "GBPUSD": "fx_major", "EURGBP": "fx_major",
    "GBPJPY": "fx_jpy", "CHFJPY": "fx_jpy", "BTCJPY": "fx_jpy",
    "XAUUSD": "metal", "XAUUSD-VIP": "metal",
    "BTCUSD": "crypto", "BTCUSDT": "crypto", "ETHUSDT": "crypto",
}


def profile_for(symbol):
    return INSTRUMENT_PROFILES[SYMBOL_PROFILE.get(symbol, "fx_major")]


# ---- structure container -------------------------------------------------------
@dataclass
class Structure:
    """Resolved zone levels for a candidate signal (one execution swing)."""
    zone_low: float                 # entry-zone lower bound (OB/FVG/IFVG/anchor)
    zone_high: float                # entry-zone upper bound
    swept_level: float = None       # the liquidity level taken (BSL for sells, SSL for buys)
    displacement_origin: float = None  # origin of the displacement leg (M3)
    inducement: float = None        # internal lure extreme (M1)
    primary_tp: float = None        # pre-selected DOL, chosen BEFORE entry
    extras: dict = field(default_factory=dict)

    def midpoint(self):
        return (self.zone_low + self.zone_high) / 2.0


# ---- M-model stop formulas (faithful to ruleset §1) ----------------------------
def _stop_sell(m_model, s: Structure, buf: float) -> float:
    cands = [s.zone_high]
    if m_model == "M1" and s.inducement is not None:
        cands += [s.inducement]
    if s.swept_level is not None:
        cands += [s.swept_level]
    if m_model == "M3" and s.displacement_origin is not None:
        cands += [s.displacement_origin]
    return max(cands) + buf


def _stop_buy(m_model, s: Structure, buf: float) -> float:
    cands = [s.zone_low]
    if m_model == "M1" and s.inducement is not None:
        cands += [s.inducement]
    if s.swept_level is not None:
        cands += [s.swept_level]
    if m_model == "M3" and s.displacement_origin is not None:
        cands += [s.displacement_origin]
    return min(cands) - buf


# ---- the one signal function ---------------------------------------------------
def generate_signal(e_trigger, m_model, symbol, structure: Structure,
                    rr=2.0, min_rr=2.0):
    """Return a fully-specified signal dict, or None if inputs are inconsistent.

    e_trigger in {E1,E2,E3}; m_model in {M1,M2,M3}; structure has resolved levels.
    Direction comes from the frozen variant table (E×M). Entry = zone midpoint
    (M3 requires the midpoint to be the post->=50%-retrace anchor, enforced upstream).
    """
    variant = e_trigger + m_model
    if variant not in VARIANT_TABLE:
        return None
    direction = VARIANT_TABLE[variant]["direction"]
    horizon = VARIANT_TABLE[variant]["horizon"]
    prof = profile_for(symbol)
    buf = prof["buffer"]

    entry = structure.midpoint()
    if direction == "SELL":
        stop = _stop_sell(m_model, structure, buf)
        if stop <= entry:
            return None                      # invalid: stop must sit above entry
        risk = stop - entry
        tp1 = entry - risk                   # +1R management partial
        primary_tp = structure.primary_tp    # DOL, below entry for sells
    else:
        stop = _stop_buy(m_model, structure, buf)
        if stop >= entry:
            return None
        risk = entry - stop
        tp1 = entry + risk
        primary_tp = structure.primary_tp

    realized_rr = None
    if primary_tp is not None and risk > 0:
        realized_rr = round(abs(primary_tp - entry) / risk, 2)

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


# ---- best-effort live detection (DETECTION layer, M1.5 in progress) ------------
def detect_bias(h1):
    """E-trigger bias proxy from H1 structure: BULLISH->BUY, BEARISH->SELL."""
    hi, lo = e.swings(h1)
    t = e.trend(hi, lo)
    return {"BULLISH": "BUY", "BEARISH": "SELL"}.get(t)


def detect_structure_m2(m5, bias):
    """M2 gold-zone proxy: latest aligned OB overlapped with an aligned FVG (M5)."""
    want = "bull" if bias == "BUY" else "bear"
    obs = [o for o in e.order_blocks(m5) if o["dir"] == want]
    fvs = [f for f in e.fvgs(m5) if f["dir"] == want]
    if not obs or not fvs:
        return None
    ob, fv = obs[-1], fvs[-1]
    low = max(ob["low"], fv["lower"])
    high = min(ob["high"], fv["upper"])
    if low >= high:
        return None                          # no true overlap
    sw = e.liquidity_sweeps(m5)
    swept = sw[-1]["level"] if sw else None
    return Structure(zone_low=low, zone_high=high, swept_level=swept)


if __name__ == "__main__":
    # Demo: E2M3 BTCUSD from ruleset §3 (zone-level, source-verified numbers)
    s = Structure(zone_low=26699 - 50, zone_high=26699 + 50, swept_level=26900,
                  displacement_origin=26890, primary_tp=25324.7)
    import json
    print(json.dumps(generate_signal("E2", "M3", "BTCUSD", s), indent=2))
