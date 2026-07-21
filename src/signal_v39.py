#!/usr/bin/env python3
"""SMC-LSS v3.9 "Clean SMC" research signal engine.

Source of truth: specs/v3.9.yaml, reports/audit/ST_C1_V39_CLEAN_SMC_RCR.md,
reports/audit/ST_C1_V39_CONFORMANCE_MATRIX.md. Status: RESEARCH_CANDIDATE.
This module does NOT authorize live trading and must never import or call a
broker-order path (see CLAUDE.md hard rules / docs/RESEARCH-CHARTER.md).

v3.9 returns to the v3.6 E1/E2/E3 + M1/M2/M3 schema (NOT the parked v3.7
G1-G10 gate pipeline) with three named relaxations (E1 disabled, E2/E3
wick-ratio filters zeroed, displacement redefined as body-ratio-only). This
module is a v3.9-parameterized sibling of signal_v35.py (which implements
v3.6 despite its filename), not an edit to that file, so v3.6 remains an
immutable historical control.

Note on E3_RECLAIM_WINDOW_H1_BARS: specs/v3.9.yaml sets this to 0
("disabled"). Testing proved this has no observable effect at any value —
smc_engine.liquidity_sweeps() already requires the reclaim close on the same
bar as the sweep wick by definition, so the window loop below always
matches on its first iteration. It is NOT a fourth relaxation (an earlier
audit draft claimed it was; retracted — see the correction in
reports/audit/ST_C1_V39_CLEAN_SMC_RCR.md). Kept at 0 here only for fidelity
to the spec file, not because it changes behavior.

Key finding reused from the conformance audit: v3.9's E2/E3 "qualification
via CHoCH, not wick geometry" is achieved for free by setting
reaction_wick_ratio_min / sweep_wick_ratio_min to 0.0 in the same
close-confirmed reaction-bar test signal_v35.py already uses (wicks are
never required when the ratio floor is 0.0) — no separate CHoCH function is
needed; this module documents that explicitly rather than silently
reinterpreting the term.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import datetime
import smc_engine as e

VARIANT_TABLE = {
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

# --- v3.9 parameter set (specs/v3.9.yaml parameter_registry) ---------------
E1_ENABLED = False                     # v3.9: E1 disabled entirely
E2_POI_MAX_AGE_H1_BARS = 120           # v3.9 (v3.6 was 60)
E2_REACTION_WICK_RATIO_MIN = 0.0       # v3.9: wick filter off (CHoCH-driven, see module docstring)
E3_RANGE_LOOKBACK_H1_BARS = 60         # v3.9 (v3.6 was 40)
E3_SWEEP_WICK_RATIO_MIN = 0.0          # v3.9: wick filter off
E3_RECLAIM_WINDOW_H1_BARS = 0          # v3.9 spec value (0 = "disabled") — proved to be a no-op, not a
                                        # relaxation (see module docstring); kept for spec fidelity only.
MAX_E_TO_M_H1_BARS = 0                 # v3.9: 0 = disabled (v3.6 was 12) — no staleness gate

DISPLACEMENT_BODY_RATIO_MIN = 0.6      # v3.9 (v3.6 was 0.5, plus an ATR gate v3.9 drops)
DISPLACEMENT_START_OFFSET_BARS = 0     # v3.9: evaluate current bar (v3.6 was 2)
DISPLACEMENT_MAX_RUN_BARS = 12         # v3.9 (v3.6 was 3)

STOP_BUFFER_ATR_PERIOD = 14
STOP_BUFFER_ATR_MULT = 0.15            # carried forward from validation/historical_replay_engine.py's
                                        # existing ATR-based convention (conformance matrix "stop buffer" item) —
                                        # NOT signal_v35.py's flat INSTRUMENT_PROFILES constant.

# v3.9 session windows (UTC), widened from v3.6/v3.8's 06-10/11:30-15.
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
    inducement: float = None
    primary_tp: float = None
    zone_creation_i: int = None
    extras: dict = field(default_factory=dict)

    def midpoint(self):
        return (self.zone_low + self.zone_high) / 2.0


def _stop_buffer(c, idx):
    """ATR-based buffer, matching the replay engine's existing convention
    (conformance matrix: reuse, don't reintroduce the flat per-instrument
    constant from signal_v35.py)."""
    return e.atr(c, idx, STOP_BUFFER_ATR_PERIOD) * STOP_BUFFER_ATR_MULT


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


def generate_signal(e_trigger, m_model, symbol, structure, direction, m5, entry_i, min_rr=3.0):
    """Gross-RR screen only (no spread/commission/slippage/swap deduction) —
    this is a necessary-but-not-sufficient detection-time gate. The
    authoritative net-of-cost RR used for any statistical claim is computed
    downstream by validation/historical_replay_engine_v39.py's cost model
    (conformance matrix: reused, not reimplemented here)."""
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
        tp1 = entry - risk
    else:
        stop = _stop_buy(m_model, structure, buf)
        if stop >= entry:
            return None
        risk = entry - stop
        tp1 = entry + risk
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
        "spec_version": "3.9",
    }


def _in_session(ts: str) -> bool:
    """v3.9 widened session windows (fail-open on unparseable timestamps,
    same posture as v3.6). dst_adjusted: false by design (fixed UTC)."""
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


def _first_reaction_bar(htf, zone_low, zone_high, want_dir, start_i, max_i, wick_ratio_min):
    """Identical mechanism to signal_v35.py's function of the same name.
    With wick_ratio_min == 0.0 (v3.9's E2/E3 value) the wick term is always
    satisfied, so this reduces to "first close-confirmed break of the far
    zone boundary" — i.e. CHoCH-style confirmation, not wick geometry. See
    module docstring: this is the resolution of the conformance audit's
    "E2 CHoCH qualifier" open item, not a new mechanism."""
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


def _e2_trigger(h1):
    """H1 reaction at a fresh/mitigated H1 POI. E1 is disabled in v3.9 (see
    module docstring) so E2 is evaluated directly, no E1 fallback path."""
    obs = e.order_blocks(h1)
    n = len(h1)
    for ob in reversed(obs):
        if (n - 1) - ob["i"] > E2_POI_MAX_AGE_H1_BARS:
            break
        if e.mitigation_status(h1, ob["i"], ob["low"], ob["high"], ob["dir"]) == "INVALIDATED":
            continue
        j = _first_reaction_bar(h1, ob["low"], ob["high"], ob["dir"],
                                ob["i"], n - 1, E2_REACTION_WICK_RATIO_MIN)
        if j is not None:
            return {"e_trigger": "E2", "bias": "BUY" if ob["dir"] == "bull" else "SELL", "confirm_i": j}
    return None


def _e3_trigger(h1):
    """H1 sweep + reclaim of EXTERNAL liquidity, structure-only. The reclaim
    window loop below is retained for spec-field fidelity
    (E3_RECLAIM_WINDOW_H1_BARS) but is a no-op in practice: liquidity_sweeps()
    already requires the reclaim close on the same bar as the sweep wick, so
    this always matches at k == sweep_i regardless of the window size (see
    module docstring)."""
    n = len(h1)
    hi, lo = e.swings(h1)
    lookback_start = max(0, n - E3_RANGE_LOOKBACK_H1_BARS)
    hi_in = [p for i, p in hi if i >= lookback_start]
    lo_in = [p for i, p in lo if i >= lookback_start]
    ext_high = max(hi_in) if hi_in else None
    ext_low = min(lo_in) if lo_in else None
    if ext_high is None and ext_low is None:
        return None
    sweeps = e.liquidity_sweeps(h1, min_wick_ratio=E3_SWEEP_WICK_RATIO_MIN)
    reclaim_end = n if E3_RECLAIM_WINDOW_H1_BARS == 0 else None
    for sw in reversed(sweeps):
        is_external = (sw["dir"] == "bear" and ext_high is not None and sw["level"] == ext_high) or \
                     (sw["dir"] == "bull" and ext_low is not None and sw["level"] == ext_low)
        if not is_external:
            continue
        j = sw["i"]
        end_k = reclaim_end if reclaim_end is not None else min(j + E3_RECLAIM_WINDOW_H1_BARS + 1, n)
        for k in range(j, end_k):
            c = h1[k]
            if sw["dir"] == "bull" and c["close"] > sw["level"]:
                return {"e_trigger": "E3", "bias": "BUY", "confirm_i": k}
            if sw["dir"] == "bear" and c["close"] < sw["level"]:
                return {"e_trigger": "E3", "bias": "SELL", "confirm_i": k}
    return None


def detect_e_trigger(h1, d1=None):
    """v3.9: E1 is disabled outright (E1_ENABLED = False) — no D1 gap
    evaluation is performed at all. Only E2/E3 compete; freshest wins."""
    candidates = [t for t in (_e2_trigger(h1), _e3_trigger(h1)) if t is not None]
    if not candidates:
        return None
    return max(candidates, key=lambda t: t["confirm_i"])


def _cached_sweeps(m5, cache):
    """Memoize smc_engine.liquidity_sweeps() within a single analyze() call.
    analyze() tries up to 3 M-models (M2, M1, M3) against the SAME m5
    window; without this, each model independently recomputed the same
    O(window) scan (found to be the dominant cost in a population-ablation
    performance probe: swings()/liquidity_sweeps() together were >85% of
    per-bar runtime). `cache` is a plain dict created fresh per analyze()
    call by the caller (no cross-call/global state, no determinism risk)."""
    if cache is None:
        return e.liquidity_sweeps(m5, min_wick_ratio=E3_SWEEP_WICK_RATIO_MIN)
    if "sweeps" not in cache:
        cache["sweeps"] = e.liquidity_sweeps(m5, min_wick_ratio=E3_SWEEP_WICK_RATIO_MIN)
    return cache["sweeps"]


def _cached_obs(m5, cache):
    if cache is None:
        return e.order_blocks(m5)
    if "obs" not in cache:
        cache["obs"] = e.order_blocks(m5)
    return cache["obs"]


def _cached_fvgs(m5, cache):
    if cache is None:
        return e.fvgs(m5)
    if "fvgs" not in cache:
        cache["fvgs"] = e.fvgs(m5)
    return cache["fvgs"]


def _swept_level(m5, bias, cache=None):
    want = "bull" if bias == "BUY" else "bear"
    sw = [x for x in _cached_sweeps(m5, cache) if x["dir"] == want]
    return sw[-1]["level"] if sw else None


def detect_structure_m1(m5, bias, cache=None):
    want = "bull" if bias == "BUY" else "bear"
    sweeps = [x for x in _cached_sweeps(m5, cache) if x["dir"] == want]
    if not sweeps:
        return None
    sweep = sweeps[-1]
    fvs = [f for f in _cached_fvgs(m5, cache) if f["dir"] == want and f["i"] > sweep["i"]]
    if not fvs:
        return None
    fv = fvs[-1]
    ind = e.inducement(m5)
    inducement = ind["bull_inducement"] if bias == "BUY" else ind["bear_inducement"]
    return Structure(zone_low=fv["lower"], zone_high=fv["upper"],
                     swept_level=_swept_level(m5, bias, cache), inducement=inducement,
                     zone_creation_i=fv["i"])


def detect_structure_m2(m5, bias, cache=None):
    want = "bull" if bias == "BUY" else "bear"
    obs = [o for o in _cached_obs(m5, cache) if o["dir"] == want]
    fvs = [f for f in _cached_fvgs(m5, cache) if f["dir"] == want]
    if not obs or not fvs:
        return None
    ob, fv = obs[-1], fvs[-1]
    sweeps = [x for x in _cached_sweeps(m5, cache) if x["dir"] == want]
    if not sweeps:
        return None
    sweep = sweeps[-1]
    if ob["i"] <= sweep["i"] and fv["i"] <= sweep["i"]:
        return None
    low = max(ob["low"], fv["lower"])
    high = min(ob["high"], fv["upper"])
    if low >= high:
        return None
    return Structure(zone_low=low, zone_high=high, swept_level=_swept_level(m5, bias, cache),
                     zone_creation_i=max(ob["i"], fv["i"]))


def _displacement_v39(c, sweep_i, direction):
    """Body-ratio-only displacement (v3.9): drops v3.6's ATR-cumulative-range
    clause entirely (atr_period=0/atr_mult=0.0 in specs/v3.9.yaml means the
    filter is OFF, not "pass a zero threshold" — reusing
    smc_engine.displacement_move with a degenerate ATR period would instead
    silently skip every candidate, since atr(c,i,0) returns 0.0 and its
    `if ref_atr <= 0: continue` guard would reject the run entirely). This
    is the RCR's named, intentional change — see conformance matrix
    "Displacement" row."""
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


def detect_structure_m3(m5, bias, cache=None):
    move_dir = "bull" if bias == "BUY" else "bear"
    source_dir = "bear" if bias == "BUY" else "bull"
    sweeps = [x for x in _cached_sweeps(m5, cache) if x["dir"] == move_dir]
    if not sweeps:
        return None
    sweep = sweeps[-1]
    disp = _displacement_v39(m5, sweep["i"], move_dir)
    if disp is None:
        return None
    candidates = [f for f in _cached_fvgs(m5, cache) if f["dir"] == source_dir
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
                     zone_creation_i=fv["i"])


_DETECT = {"M1": detect_structure_m1, "M2": detect_structure_m2, "M3": detect_structure_m3}


def _dol_target(m5, direction, entry):
    """Nearest opposing liquidity beyond entry. Price-equal ties are not
    observably ambiguous (see conformance matrix "target tie-break" row) —
    min()/max() over price values is deterministic regardless."""
    hi, lo = e.swings(m5)
    if direction == "SELL":
        cands = [p for _, p in lo if p < entry]
        return max(cands) if cands else None
    cands = [p for _, p in hi if p > entry]
    return min(cands) if cands else None


def analyze(symbol, m5, h1=None, d1=None, primary_tp=None, index_offset=0, min_rr=3.0):
    """Point-in-time analysis: only bars already present in m5/h1/d1 are ever
    consulted (no look-ahead). `d1` is accepted for interface parity with
    signal_v35.analyze but is never read — E1 (the only D1-dependent trigger)
    is disabled in v3.9."""
    htf = h1 if h1 else m5
    trig = detect_e_trigger(htf, d1=None)
    if trig is None:
        return {"symbol": symbol, "decision": "NO-SIGNAL",
                "reason": "no qualifying E-trigger (E1 disabled in v3.9 / E2 POI / E3 external sweep)"}
    e_trig, bias = trig["e_trigger"], trig["bias"]
    if h1 is not None and MAX_E_TO_M_H1_BARS > 0:
        confirm_h1_age = len(h1) - 1 - trig["confirm_i"]
        if confirm_h1_age > MAX_E_TO_M_H1_BARS:
            return {"symbol": symbol, "decision": "NO-SIGNAL",
                    "reason": f"{e_trig} stale: {confirm_h1_age} H1 bars old > {MAX_E_TO_M_H1_BARS}"}
    cache: dict = {}   # shared smc_engine primitive cache across M2/M1/M3 for this m5 window only
    for m_mod in ("M2", "M1", "M3"):
        variant = e_trig + m_mod
        if variant not in VARIANT_TABLE:
            continue
        st = _DETECT[m_mod](m5, bias, cache)
        if st is None:
            continue
        last_m5_time = m5[-1].get("time", "") if m5 else ""
        if last_m5_time and not _in_session(last_m5_time):
            return {"symbol": symbol, "decision": "NO-SIGNAL",
                    "reason": f"outside London/NY session or weekend at {last_m5_time}"}
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
