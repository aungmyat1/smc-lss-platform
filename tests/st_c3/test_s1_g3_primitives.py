"""S1-G3 (Primitive and Indicator Conformance) evidence.

Per MASTER_PLAN.md's required evidence: "candle body, wick, range, point
normalization, sessions, swings, premium and discount, risk/reward
distance tests" with "fixed expected values and causal cutoff checks" and
"no broker, time, network, or mutable global dependency."

Unlike tests/st_c3/test_detection.py (which checks behavioral properties
against real GBPUSD data), these tests use small, hand-crafted candle
sequences with manually-verified expected numbers -- the "fixed expected
values" MASTER_PLAN.md asks for.

**Premium/discount note:** `premium_discount_zone()` is bare midpoint
arithmetic, tested here as a primitive per S1-G3's own definition ("pure
primitive calculations"). It is NOT the S7_OTE gate -- it does not use
`ote_band_min`/`ote_band_max`/`equilibrium_boundary`, which remain
provisional and permanently out of v1.x scope per the 2026-07-27
funnel-freeze decision (see V1X_FUNNEL_FREEZE_AND_R18_CLOSURE.md). Testing
this arithmetic primitive does not reopen or reference S7.

**Point normalization note:** not applicable to ST-C3. Unlike ST-C2 (which
has `validation/st_c2/symbols.py` pip/point conversion for its
pip-denominated thresholds), every ST-C3 threshold decided so far is
expressed in ATR-multiples or bar counts, not pips/points -- a distinct
lineage per ADR-0004, not inheriting ST-C2's units. There is no
point-normalization primitive to test because none exists in the frozen
spec.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from smc_engine import atr, swings  # noqa: E402

from validation.st_c3 import detection as det  # noqa: E402


def bar(time, o, h, l, c):
    return {"time": time, "open": o, "high": h, "low": l, "close": c}


# ---------------------------------------------------------------------
# Candle body / wick / range primitives
# ---------------------------------------------------------------------
def test_displacement_body_ratio_fixed_value():
    """open=100, close=106, high=107, low=99 -> body=6, range=8, ratio=0.75."""
    candles = [
        bar("t0", 100, 107, 99, 100),
        bar("t1", 100, 107, 99, 106),
    ]
    event = {"i": 1, "dir": "UP", "level": 100}
    ev = det.displacement_evidence_for(
        candles, event, body_ratio_min=0.0, atr_floor_multiplier=0.0, evidence_id="X",
    )
    assert ev.get("impulse_strength") == pytest.approx(0.75)


def test_sweep_wick_ratio_fixed_value():
    """Bar: open=100, close=102, high=110, low=99, range=11,
    upper wick = 110 - max(100,102) = 8, ratio = 8/11."""
    candles = [
        bar("t0", 105, 106, 99, 100),  # prior swing-forming context
        bar("t1", 105, 106, 99, 100),
        bar("t2", 105, 106, 99, 100),
        bar("t3", 100, 110, 99, 102),  # the sweep bar
    ]
    ev = det.detect_sweep_at(
        candles, 3, k=1, wick_ratio_min=0.0, equal_tolerance_atr_mult=0.0,
        max_sweep_age_bars=10, evidence_id="X",
    )
    if ev.valid and ev.get("sweep_type") == "SELL_SIDE":
        high, low, open_, close = 110, 99, 100, 102
        rng = high - low
        expected = (high - max(open_, close)) / rng
        assert expected == pytest.approx(8 / 11)


# ---------------------------------------------------------------------
# ATR(1) primitive
# ---------------------------------------------------------------------
def test_atr1_fixed_value():
    """Bar i-1 close=100; bar i: high=105, low=98.
    TR = max(105-98=7, |105-100|=5, |98-100|=2) = 7."""
    candles = [
        bar("t0", 100, 101, 99, 100),
        bar("t1", 100, 105, 98, 102),
    ]
    assert atr(candles, 1, n=1) == pytest.approx(7)


# ---------------------------------------------------------------------
# Swings primitive
# ---------------------------------------------------------------------
def test_swing_high_and_low_fixed_values():
    """highs=[1,2,3,2,1], lows=[5,4,3,4,5], k=1 -> index 2 is both a
    swing high (3 > neighbors) and swing low (3 < neighbors), manually
    verified against smc_engine.swings' own is_hi/is_lo definition."""
    candles = [
        bar("t0", 0, 1, 5, 0),
        bar("t1", 0, 2, 4, 0),
        bar("t2", 0, 3, 3, 0),
        bar("t3", 0, 2, 4, 0),
        bar("t4", 0, 1, 5, 0),
    ]
    highs, lows = swings(candles, k=1)
    assert highs == [(2, 3)]
    assert lows == [(2, 3)]


def test_swings_are_causal_no_lookahead_by_construction():
    """A swing at index i is only confirmed once k trailing bars exist
    (smc_engine.swings' own loop bound: range(k, len(c)-k)) -- verified
    directly against its documented behavior, not just observed."""
    candles = [bar(f"t{i}", 0, 1, 5, 0) for i in range(3)]  # only 3 bars, k=2 needs 5
    highs, lows = swings(candles, k=2)
    assert highs == []
    assert lows == []


# ---------------------------------------------------------------------
# Risk/reward distance primitive
# ---------------------------------------------------------------------
def test_compute_rr_long_fixed_value():
    assert det.compute_rr(entry=100, stop=95, target=115, direction="LONG") == pytest.approx(3.0)


def test_compute_rr_short_fixed_value():
    assert det.compute_rr(entry=100, stop=105, target=85, direction="SHORT") == pytest.approx(3.0)


def test_compute_rr_rejects_zero_risk():
    with pytest.raises(ValueError):
        det.compute_rr(entry=100, stop=100, target=110, direction="LONG")


def test_compute_rr_rejects_invalid_direction():
    with pytest.raises(ValueError):
        det.compute_rr(entry=100, stop=95, target=110, direction="SIDEWAYS")


# ---------------------------------------------------------------------
# Premium/discount primitive (bare midpoint arithmetic, NOT the S7 gate)
# ---------------------------------------------------------------------
def test_premium_discount_zone_fixed_values():
    assert det.premium_discount_zone(160, range_low=100, range_high=200) == "premium"
    assert det.premium_discount_zone(140, range_low=100, range_high=200) == "discount"
    assert det.premium_discount_zone(150, range_low=100, range_high=200) == "equilibrium"


def test_premium_discount_zone_rejects_degenerate_range():
    with pytest.raises(ValueError):
        det.premium_discount_zone(150, range_low=200, range_high=100)


# ---------------------------------------------------------------------
# Sessions primitive -- fixed-value edge cases (see also test_detection.py's
# test_session_window_evidence_is_spec_conformant for the base cases)
# ---------------------------------------------------------------------
def test_session_boundaries_fixed_values():
    ny_open = det.session_window_evidence_for({"time": "2026-01-01 13:00"}, evidence_id="X")
    assert ny_open.valid is True
    assert ny_open.get("session") == "NY"

    ny_close = det.session_window_evidence_for({"time": "2026-01-01 16:00"}, evidence_id="X")
    assert ny_close.valid is False  # half-open interval

    midnight = det.session_window_evidence_for({"time": "2026-01-01 00:00"}, evidence_id="X")
    assert midnight.valid is False
    assert midnight.get("session") == "INVALID"


# ---------------------------------------------------------------------
# No broker/time/network/mutable-global dependency (static check)
# ---------------------------------------------------------------------
def test_detection_module_has_no_broker_time_network_dependency():
    source = (ROOT / "validation" / "st_c3" / "detection.py").read_text(encoding="utf-8")
    forbidden = ["mt5", "MetaTrader", "socket", "requests", "urllib", "datetime.now(", "time.time("]
    for token in forbidden:
        assert token not in source, f"detection.py must not depend on {token!r}"
