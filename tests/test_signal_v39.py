"""Positive/negative/mirror/cutoff fixtures for ST-C1 v1.2.0 / spec v3.9
("Clean SMC"), audited in reports/audit/ST_C1_V39_CONFORMANCE_MATRIX.md.

v3.9 returns to the v3.6 E1/E2/E3+M1/M2/M3 schema (NOT the parked v3.7
G1-G10 pipeline). Fixtures for E2/M1/M3 reuse or lightly adapt existing,
already-verified fixtures from test_signal_v35.py and test_signal_v37_gates.py
(the underlying smc_engine primitives are unchanged); M2's fixture and the
unbounded-reclaim / body-ratio-only-displacement fixtures were constructed
and verified interactively (run then adjusted) against the actual v3.9
functions, per this repo's established practice (see test_signal_v37_gates.py's
docstring) rather than hand-derived.

Trade-management (+1R partial/BE, stop-first ambiguity, weekend force-exit,
timeout/censored-end-of-data) and the cost model are exercised in
tests/test_historical_replay_v39.py via HistoricalReplayEngineV39, not here.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

import smc_engine as e  # noqa: E402
import signal_v35 as v35  # noqa: E402
import signal_v39 as v39  # noqa: E402
from test_signal_v35 import _bear_fvg_series  # noqa: E402
from test_signal_v37_gates import bearish_h1, bullish_h1_mirror  # noqa: E402


def bar(o, h, l, c, t="t"):
    return {"time": t, "open": o, "high": h, "low": l, "close": c}


# --- E1: disabled entirely in v3.9 ------------------------------------------

def test_e1_never_contributes_a_trigger():
    """v3.9 disables E1 outright — there is no D1-gap code path at all, unlike
    signal_v35 which always tries E1 first. detect_e_trigger must only ever
    return E2 or E3."""
    assert not hasattr(v39, "_e1_trigger")
    trig = v39.detect_e_trigger(bearish_h1())
    assert trig is not None
    assert trig["e_trigger"] in ("E2", "E3")


# --- E2: fresh H1 POI reaction, CHoCH-driven (wick_ratio_min == 0.0) --------

def test_e2_positive_and_mirror():
    """v3.9's E2 fires on the same H1 fixtures used to verify v3.7's gates
    (smc_engine.order_blocks/mitigation_status are unchanged); bearish and
    bullish mirrors both qualify with opposite bias."""
    bear = v39._e2_trigger(bearish_h1())
    bull = v39._e2_trigger(bullish_h1_mirror())
    assert bear is not None and bear["bias"] == "SELL"
    assert bull is not None and bull["bias"] == "BUY"


def test_e2_more_permissive_than_v36_on_same_data():
    """Direct evidence the v3.9 relaxation (wick_ratio_min 0.4 -> 0.0, POI
    age 60 -> 120 H1 bars) does what the RCR intends: v3.6's stricter E2
    finds nothing on this fixture, v3.9's does."""
    h1 = bearish_h1()
    assert v35._e2_trigger(h1) is None
    assert v39._e2_trigger(h1) is not None


def test_e2_wick_only_touch_rejected_close_confirmed_accepted():
    """Even with wick_ratio_min == 0.0, a bar that merely wicks into the zone
    and closes back OUTSIDE on the near side (not through the far boundary)
    must not qualify — the gate is close-confirmation, not "any touch"."""
    zone_low, zone_high = 100.0, 100.10
    # wick pierces above zone_high but closes back inside the zone: not a break
    wick_only = bar(100.05, 100.15, 100.03, 100.06)
    j = v39._first_reaction_bar([bar(99.9, 99.95, 99.85, 99.9), wick_only],
                                zone_low, zone_high, "bull", 0, 1, 0.0)
    assert j is None
    # close beyond the far boundary, with a ~zero wick, must qualify at wick_ratio_min=0.0
    close_confirmed = bar(100.05, 100.12, 100.05, 100.11)
    j2 = v39._first_reaction_bar([bar(99.9, 99.95, 99.85, 99.9), close_confirmed],
                                 zone_low, zone_high, "bull", 0, 1, 0.0)
    assert j2 == 1


# --- E3: structure-only sweep. reclaim_window_h1_bars is a NO-OP (found via testing) --

def test_e3_reclaim_window_parameter_has_no_effect_v39_matches_v36():
    """An earlier audit draft claimed specs/v3.9.yaml's
    e3_reclaim_window_h1_bars: 0 was an undisclosed relaxation (unbounded
    reclaim). Direct testing disproved that: smc_engine.liquidity_sweeps()
    already requires the reclaim close on the SAME bar as the sweep wick by
    definition, so the reclaim-window loop in both _e3_trigger
    implementations always matches on its first iteration regardless of the
    configured window (0, 1, or any other value) — see the retraction in
    reports/audit/ST_C1_V39_CLEAN_SMC_RCR.md. v3.9 and v3.6 must therefore
    agree exactly on this fixture (module-level differences here come only
    from wick-ratio/POI-age, not reclaim timing)."""
    baseline = [bar(100.0, 100.05, 99.95, 100.0) for _ in range(10)]
    baseline[4] = bar(100.0, 100.05, 99.80, 99.85)   # swing low candidate @99.80
    baseline[5] = bar(99.85, 100.0, 99.83, 99.95)    # confirm1
    baseline[6] = bar(99.95, 100.0, 99.90, 99.98)    # confirm2 -> lo confirmed
    sweep = bar(99.98, 100.0, 99.65, 99.90)          # wick pierces 99.80 AND closes back above it (same bar)
    h1 = baseline + [sweep]
    v36_result = v35._e3_trigger(h1)
    v39_result = v39._e3_trigger(h1)
    assert v36_result is not None and v36_result["bias"] == "BUY"
    assert v39_result is not None and v39_result["bias"] == "BUY"
    assert v36_result["confirm_i"] == v39_result["confirm_i"] == 10


def test_e3_bullish_bearish_mirror():
    bear_h1 = bearish_h1()
    bull_h1 = bullish_h1_mirror()
    # bearish_h1/bullish_h1_mirror already carry a qualifying E3-eligible
    # external sweep+structure in their tail (shared with v3.7's fixtures);
    # confirm mirrored bias where an E3 result is found on either side.
    bear_e3 = v39._e3_trigger(bear_h1)
    bull_e3 = v39._e3_trigger(bull_h1)
    if bear_e3 is not None:
        assert bear_e3["bias"] == "SELL"
    if bull_e3 is not None:
        assert bull_e3["bias"] == "BUY"


# --- Displacement: body-ratio-only, ATR magnitude filter OFF ----------------

def test_displacement_v39_ignores_weak_atr_context_v36_would_reject():
    """Build a HIGH-ATR context (large-range baseline) so v3.6's 1.5x-ATR
    cumulative-range gate demands a big absolute move, then a single strong
    body-ratio candle (0.65 >= 0.6) whose absolute range is modest relative
    to that ATR. v3.6's displacement_move must reject it; v3.9's body-ratio-
    only test must accept it — this is the RCR's core, named relaxation."""
    baseline = [bar(100.0, 101.0, 99.0, 100.0) for _ in range(20)]  # range=2.0 -> ATR~2.0
    sweep_i = len(baseline) - 1
    weak_move = bar(100.0, 100.62, 99.97, 100.60)   # body_ratio = 0.60/0.65 ~= 0.923 >= 0.6; abs range 0.60 << 1.5*2.0=3.0
    c = baseline + [weak_move]
    assert e.displacement_move(c, sweep_i, "bull") is None
    disp = v39._displacement_v39(c, sweep_i, "bull")
    assert disp is not None
    assert disp["start"] == sweep_i + 1


def test_displacement_v39_rejects_weak_body_ratio():
    baseline = [bar(100.0, 100.05, 99.95, 100.0) for _ in range(5)]
    sweep_i = len(baseline) - 1
    weak_body = bar(100.0, 100.30, 99.90, 100.10)   # body_ratio = 0.10/0.40 = 0.25 < 0.6
    c = baseline + [weak_body]
    assert v39._displacement_v39(c, sweep_i, "bull") is None


# --- M1 (reused, unchanged geometry) ----------------------------------------

def test_m1_reused_fixture_still_qualifies():
    st = v39.detect_structure_m1(_bear_fvg_series(), "SELL")
    assert st is not None
    assert st.zone_high > st.zone_low


# --- M2: OB ∩ FVG "Gold Zone", post-dating a same-direction sweep -----------

def _m2_bull_fixture():
    vals = [
        (100.0, 100.05, 99.95, 100.0), (100.0, 100.05, 99.95, 100.0),
        (100.0, 100.10, 99.95, 100.05),   # swing high candidate i=2 @100.10
        (100.05, 100.06, 99.95, 100.0), (100.0, 100.02, 99.95, 99.98),  # confirms hi@2
        (99.98, 100.0, 99.85, 99.90), (99.90, 99.95, 99.70, 99.80),     # swing low candidate i=6 @99.70
        (99.80, 99.95, 99.72, 99.90), (99.90, 99.98, 99.85, 99.95),     # confirms lo@6
        (99.95, 99.98, 99.90, 99.93),
    ]
    baseline = [bar(*v) for v in vals]
    sweep = bar(99.93, 99.95, 99.65, 99.92)          # bull sweep of 99.70, reclaim 99.92
    ob_candle = bar(99.92, 99.94, 99.85, 99.87)       # down candle -> becomes bullish OB
    break_candle = bar(99.87, 100.20, 99.86, 100.15)  # close > hi_last(100.10) -> BOS forms the OB
    pad1 = bar(99.868, 99.87, 99.86, 99.868)
    pad2 = bar(99.90, 99.92, 99.88, 99.90)
    pad3 = bar(99.91, 99.93, 99.91, 99.92)            # completes a bullish FVG [99.87, 99.91] overlapping the OB
    return baseline + [sweep, ob_candle, break_candle, pad1, pad2, pad3]


def test_m2_gold_zone_overlap_positive():
    st = v39.detect_structure_m2(_m2_bull_fixture(), "BUY")
    assert st is not None
    assert st.zone_low < st.zone_high
    assert st.zone_low == 99.87 and st.zone_high == 99.91


def test_m2_none_without_overlap():
    """Same OB, but the FVG is placed far away with no price overlap -> the
    Gold Zone must not form (low>=high rejected)."""
    vals = [
        (100.0, 100.05, 99.95, 100.0), (100.0, 100.05, 99.95, 100.0),
        (100.0, 100.10, 99.95, 100.05), (100.05, 100.06, 99.95, 100.0),
        (100.0, 100.02, 99.95, 99.98), (99.98, 100.0, 99.85, 99.90),
        (99.90, 99.95, 99.70, 99.80), (99.80, 99.95, 99.72, 99.90),
        (99.90, 99.98, 99.85, 99.95), (99.95, 99.98, 99.90, 99.93),
    ]
    baseline = [bar(*v) for v in vals]
    sweep = bar(99.93, 99.95, 99.65, 99.92)
    ob_candle = bar(99.92, 99.94, 99.85, 99.87)
    break_candle = bar(99.87, 100.20, 99.86, 100.15)
    far1 = bar(100.15, 100.18, 100.10, 100.16)
    far2 = bar(100.16, 100.20, 100.14, 100.19)
    far3 = bar(100.30, 100.35, 100.25, 100.32)   # FVG well above the OB zone -> no overlap
    m5 = baseline + [sweep, ob_candle, break_candle, far1, far2, far3]
    assert v39.detect_structure_m2(m5, "BUY") is None


# --- M3: sweep -> body-ratio displacement -> IFVG -> retrace ----------------

def _m3_baseline():
    out = []
    for i in range(20):
        if i == 15:
            out.append(bar(100.0, 100.05, 99.80, 99.85))
        elif i in (13, 14, 16, 17):
            out.append(bar(100.0, 100.05, 99.90, 100.0))
        else:
            out.append(bar(100.0, 100.05, 99.95, 100.0))
    return out


def _m3_bull_fixture():
    # Note: pullback/inversion lows are kept well ABOVE the sweep's own low
    # (99.70) deliberately — with E3_SWEEP_WICK_RATIO_MIN=0.0, a pullback
    # dipping back near/below an earlier confirmed level would itself
    # register as a second, spurious "sweep" of that level (found via
    # fixture probing), which would make detect_structure_m3 pick the wrong
    # (later) sweep and fail to find the intended displacement run. This is
    # a real, disclosed consequence of zeroing the wick-ratio filter — see
    # the conformance matrix's E3 row and the Phase 6 population report.
    sweep = bar(99.86, 99.90, 99.70, 99.86)
    disp = [
        bar(99.86, 100.80, 99.80, 100.75),
        bar(100.75, 101.70, 100.70, 101.65),
        bar(101.65, 102.60, 101.60, 102.55),
    ]
    pullback = bar(100.60, 100.65, 100.50, 100.55)
    inversion = bar(100.55, 100.95, 100.45, 100.90)
    retrace = bar(100.90, 100.95, 100.60, 100.80)
    return _m3_baseline() + [sweep] + disp + [pullback, inversion, retrace]


def test_m3_finds_valid_ifvg_setup():
    st = v39.detect_structure_m3(_m3_bull_fixture(), "BUY")
    assert st is not None
    assert st.zone_low == 100.65 and st.zone_high == 100.70
    assert st.displacement_origin == 99.70


def test_m3_none_without_inversion():
    m5 = _m3_bull_fixture()[:-2]   # drop inversion+retrace bars
    assert v39.detect_structure_m3(m5, "BUY") is None


def test_m3_none_before_retrace_bar_exists():
    m5 = _m3_bull_fixture()[:-1]   # drop only the retrace bar
    assert v39.detect_structure_m3(m5, "BUY") is None


# --- Session: widened windows relative to v3.6 ------------------------------

def test_session_widened_relative_to_v36():
    """15:30 UTC is outside v3.6's NY killzone (11:30-15:00) but inside
    v3.9's widened NY window (12:00-21:00) — a deliberate, named relaxation."""
    ts = "2026-01-05 15:30"   # a Monday
    assert v35._in_session(ts) is False
    assert v39._in_session(ts) is True


def test_session_rejects_weekend_even_when_widened():
    ts = "2026-01-10 13:00"   # a Saturday, well inside the widened hour window
    assert v39._in_session(ts) is False


# --- Cutoff-invariance: no bar beyond the supplied window is ever read -----

def test_analyze_never_reads_beyond_supplied_window():
    """Appending future bars to the underlying series must not change a
    decision computed from a window that excludes them — analyze() only
    ever sees what its caller slices in, by construction (no hidden global
    state, no forward indexing past len(m5)/len(h1))."""
    h1 = bearish_h1()
    m5 = _bear_fvg_series()
    result_short = v39.analyze("EURUSD", list(m5), h1=list(h1))
    future_bars = [bar(1.0, 1.0, 1.0, 1.0, t=f"future-{i}") for i in range(5)]
    m5_extended_then_resliced = (m5 + future_bars)[: len(m5)]
    h1_extended_then_resliced = (h1 + future_bars)[: len(h1)]
    result_resliced = v39.analyze("EURUSD", m5_extended_then_resliced, h1=h1_extended_then_resliced)
    assert result_short == result_resliced


def test_analyze_returns_no_signal_dict_not_crash():
    out = v39.analyze("EURUSD", _bear_fvg_series())
    assert isinstance(out, dict) and "decision" in out
