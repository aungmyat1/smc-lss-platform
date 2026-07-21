"""Positive/negative/mirror fixtures for ST-C1 v1.3.0 / spec v3.10
("Reversal Capture"), per reports/audit/ST_C1_V310_REVERSAL_CAPTURE_RCR.md.

v3.10 is NOT an edit to v3.9 ("Clean SMC", continuation-only, retained
immutable — see tests/test_signal_v39.py). It adds: H4 trend-bias
divergence gating, E1 re-enabled with a partial-fill reversal tolerance, E2
hold-confirmation, E3 internal-liquidity acceptance, auto displacement
direction, and a dynamic R:R target. All fixtures here were constructed and
verified interactively against the actual v3.10 functions (run, then
adjusted), per this repo's established practice — including one real bug
this process caught: an early E1 reaction-direction check silently excluded
doji-bodied rejection candles (open == close), fixed in
src/signal_v310.py's _e1_trigger_reversal.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

import signal_v310 as v310  # noqa: E402
from test_signal_v37_gates import bearish_h1, bullish_h1_mirror  # noqa: E402


def bar(o, h, l, c, t="t"):
    return {"time": t, "open": o, "high": h, "low": l, "close": c}


# --- H4 trend bias -----------------------------------------------------

def _bearish_h4_20():
    vals = [
        (100.0, 100.05, 99.95, 100.0), (100.0, 100.10, 99.95, 100.05),
        (100.05, 100.20, 100.00, 100.15), (100.15, 100.16, 100.05, 100.10),
        (100.10, 100.11, 100.00, 100.05), (100.05, 100.06, 99.90, 99.95),
        (99.95, 99.96, 99.70, 99.75), (99.75, 99.85, 99.72, 99.80),
        (99.80, 99.90, 99.75, 99.85), (99.85, 99.95, 99.80, 99.90),
        (99.90, 100.05, 99.85, 100.00), (100.00, 100.01, 99.90, 99.95),
        (99.95, 99.96, 99.85, 99.90), (99.90, 99.91, 99.75, 99.80),
        (99.80, 99.81, 99.60, 99.65), (99.65, 99.75, 99.62, 99.70),
        (99.70, 99.80, 99.65, 99.75), (99.75, 99.80, 99.70, 99.75),
        (99.75, 99.80, 99.70, 99.75), (99.75, 99.80, 99.70, 99.75),
    ]
    return [bar(*v) for v in vals]


def _bullish_h4_20(center=99.9):
    def m(v):
        return round(2 * center - v, 5)
    vals = [
        (100.0, 100.05, 99.95, 100.0), (100.0, 100.10, 99.95, 100.05),
        (100.05, 100.20, 100.00, 100.15), (100.15, 100.16, 100.05, 100.10),
        (100.10, 100.11, 100.00, 100.05), (100.05, 100.06, 99.90, 99.95),
        (99.95, 99.96, 99.70, 99.75), (99.75, 99.85, 99.72, 99.80),
        (99.80, 99.90, 99.75, 99.85), (99.85, 99.95, 99.80, 99.90),
        (99.90, 100.05, 99.85, 100.00), (100.00, 100.01, 99.90, 99.95),
        (99.95, 99.96, 99.85, 99.90), (99.90, 99.91, 99.75, 99.80),
        (99.80, 99.81, 99.60, 99.65), (99.65, 99.75, 99.62, 99.70),
        (99.70, 99.80, 99.65, 99.75), (99.75, 99.80, 99.70, 99.75),
        (99.75, 99.80, 99.70, 99.75), (99.75, 99.80, 99.70, 99.75),
    ]
    mirrored = [(m(o), m(l), m(h), m(c)) for (o, h, l, c) in vals]
    return [bar(*v) for v in mirrored]


def test_h4_trend_bias_bullish_and_bearish_mirror():
    assert v310.h4_trend_bias(_bearish_h4_20()) == "BEARISH"
    assert v310.h4_trend_bias(_bullish_h4_20()) == "BULLISH"


def test_h4_trend_bias_ranging_when_insufficient_swings():
    flat = [bar(100.0, 100.05, 99.95, 100.0) for _ in range(20)]
    assert v310.h4_trend_bias(flat) == "RANGING"


# --- divergence gate: RANGING must fail-closed, not pass-through --------

def test_divergence_gate_fails_closed_on_ranging_bias():
    assert v310._passes_divergence_gate("BUY", "RANGING") is False
    assert v310._passes_divergence_gate("SELL", "RANGING") is False


def test_divergence_gate_requires_opposition_not_agreement():
    assert v310._passes_divergence_gate("BUY", "BEARISH") is True
    assert v310._passes_divergence_gate("BUY", "BULLISH") is False
    assert v310._passes_divergence_gate("SELL", "BULLISH") is True
    assert v310._passes_divergence_gate("SELL", "BEARISH") is False


# --- E1: gap-reversal tolerance + H4 divergence -------------------------

def _e1_fixture():
    d1 = [
        bar(99.0, 100.0, 98.5, 99.5, t="2026-01-01 00:00"),
        bar(100.5, 101.0, 100.2, 100.8, t="2026-01-02 00:00"),
        bar(102.0, 102.5, 102.0, 102.3, t="2026-01-03 00:00"),  # bull D1 gap [100, 102]
    ]
    h1 = [
        bar(102.2, 102.3, 102.0, 102.1, t="2026-01-03 01:00"),
        bar(102.0, 102.0, 101.5, 101.6, t="2026-01-03 02:00"),
        bar(101.6, 101.6, 101.0, 101.1, t="2026-01-03 03:00"),
        bar(101.1, 101.1, 100.6, 100.7, t="2026-01-03 04:00"),
        # reaction bar: dips to 100.3 (85% of the gap filled, >= 75% floor),
        # doji body (open==close) with a strong lower wick -> bullish reaction
        bar(100.6, 100.65, 100.3, 100.6, t="2026-01-03 05:00"),
    ]
    return d1, h1


def test_e1_gap_reversal_positive_and_mirror():
    d1, h1 = _e1_fixture()
    assert v310._e1_trigger_reversal(h1, d1, _bearish_h4_20()) == {
        "e_trigger": "E1", "bias": "BUY", "confirm_i": 4,
    }
    assert v310._e1_trigger_reversal(h1, d1, _bullish_h4_20()) is None


def test_e1_gap_reversal_rejects_insufficient_fill():
    """Same gap, but the reaction bar only reaches ~35% fill (well under the
    75% floor) -- must not qualify even though the wick geometry would
    otherwise pass."""
    d1, _ = _e1_fixture()
    h1_shallow = [
        bar(102.2, 102.3, 102.0, 102.1, t="2026-01-03 01:00"),
        bar(102.0, 102.0, 101.9, 101.95, t="2026-01-03 02:00"),
        bar(101.95, 101.98, 101.3, 101.9, t="2026-01-03 03:00"),  # low=101.3 -> fill=(102-101.3)/2=0.35
    ]
    assert v310._e1_trigger_reversal(h1_shallow, d1, _bearish_h4_20()) is None


# --- E2: hold confirmation + H4 divergence ------------------------------

def test_e2_hold_confirmed_positive_and_mirror():
    h1_bear = bearish_h1()
    h1_bull = bullish_h1_mirror()
    assert v310._e2_trigger_reversal(h1_bear, _bullish_h4_20()) == {
        "e_trigger": "E2", "bias": "SELL", "confirm_i": 20,
    }
    assert v310._e2_trigger_reversal(h1_bear, _bearish_h4_20()) is None
    bull_result = v310._e2_trigger_reversal(h1_bull, _bearish_h4_20())
    assert bull_result is not None and bull_result["bias"] == "BUY"


# --- E3: internal liquidity + H4 divergence -----------------------------

def _e3_sweep_fixture():
    baseline = [bar(100.0, 100.05, 99.95, 100.0) for _ in range(10)]
    baseline[4] = bar(100.0, 100.05, 99.80, 99.85)
    baseline[5] = bar(99.85, 100.0, 99.83, 99.95)
    baseline[6] = bar(99.95, 100.0, 99.90, 99.98)
    sweep = bar(99.98, 100.0, 99.65, 99.99)
    return baseline + [sweep]


def test_e3_internal_liquidity_positive_and_negative():
    h1 = _e3_sweep_fixture()
    assert v310._e3_trigger_reversal(h1, _bearish_h4_20()) == {
        "e_trigger": "E3", "bias": "BUY", "confirm_i": 10,
    }
    assert v310._e3_trigger_reversal(h1, _bullish_h4_20()) is None


# --- Dynamic R:R target --------------------------------------------------

def test_dynamic_rr_uses_displacement_range_when_larger_than_floor():
    s = v310.Structure(zone_low=99.0, zone_high=99.2, displacement_range=5.0, primary_tp=105.0)
    assert v310._dynamic_target("BUY", 100.0, 1.0, s) == 105.0


def test_dynamic_rr_falls_back_to_min_rr_floor_when_displacement_small():
    s = v310.Structure(zone_low=99.0, zone_high=99.2, displacement_range=1.0, primary_tp=101.5)
    # floor = min_rr(3.0) * risk(1.0) = 3.0 -> target = entry + 3.0 = 103.0,
    # which is further than primary_tp's 101.5, so the max() picks 103.0
    assert v310._dynamic_target("BUY", 100.0, 1.0, s) == 103.0


def test_dynamic_rr_short_side_mirrors_long_side():
    s = v310.Structure(zone_low=99.0, zone_high=99.2, displacement_range=5.0, primary_tp=95.0)
    assert v310._dynamic_target("SELL", 100.0, 1.0, s) == 95.0


# --- M2 (primary reversal model) reused geometry ------------------------

def test_m2_gold_zone_still_detects_with_displacement_range_recorded():
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
    pad1 = bar(99.868, 99.87, 99.86, 99.868)
    pad2 = bar(99.90, 99.92, 99.88, 99.90)
    pad3 = bar(99.91, 99.93, 99.91, 99.92)
    m5 = baseline + [sweep, ob_candle, break_candle, pad1, pad2, pad3]
    st = v310.detect_structure_m2(m5, "BUY")
    assert st is not None
    assert st.zone_low == 99.87 and st.zone_high == 99.91
    assert st.displacement_range is not None   # recorded, even if 0.0 on this particular fixture


# --- No broker import (research-only, matching the v3.9 precedent) -----

def test_no_broker_order_import():
    with open(v310.__file__, encoding="utf-8") as fh:
        text = fh.read()
    assert "mt5." not in text.lower()
    assert "place_order" not in text.lower()
    assert "MetaTrader5" not in text
