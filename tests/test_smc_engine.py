"""Tests for the shared detection primitives in src/smc_engine.py.
Run: python -m pytest -q"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import smc_engine as e


def _bar(o, h, l, c):
    return {"time": "t", "open": o, "high": h, "low": l, "close": c}


def _quiet_baseline(n=20, level=100.0):
    """n small-range candles establishing a known-tight ATR (~0.10)."""
    return [_bar(level, level + 0.05, level - 0.05, level) for _ in range(n)]


def test_displacement_move_detects_clear_bullish_run():
    baseline = _quiet_baseline(20, 100.0)
    sweep_i = len(baseline) - 1
    # 3 strong bullish candles: body_ratio 0.9, cumulative range ~2.7 >> 1.5*0.10
    disp = [
        _bar(100.0, 100.95, 99.95, 100.90),
        _bar(100.90, 101.85, 100.85, 101.80),
        _bar(101.80, 102.75, 101.75, 102.70),
    ]
    c = baseline + disp
    mv = e.displacement_move(c, sweep_i, "bull")
    assert mv is not None
    assert mv["start"] == sweep_i + 1
    assert mv["range"] > 1.5 * e.atr(c, sweep_i, 14)


def test_displacement_move_detects_clear_bearish_run():
    baseline = _quiet_baseline(20, 100.0)
    sweep_i = len(baseline) - 1
    disp = [
        _bar(100.0, 100.05, 99.05, 99.10),
        _bar(99.10, 99.15, 98.15, 98.20),
        _bar(98.20, 98.25, 97.25, 97.30),
    ]
    c = baseline + disp
    mv = e.displacement_move(c, sweep_i, "bear")
    assert mv is not None
    assert mv["start"] == sweep_i + 1


def test_displacement_move_none_when_move_too_small():
    baseline = _quiet_baseline(20, 100.0)
    sweep_i = len(baseline) - 1
    # candles same magnitude as the quiet baseline -> never clears 1.5x ATR
    weak = [_bar(100.0, 100.06, 99.96, 100.04) for _ in range(3)]
    c = baseline + weak
    assert e.displacement_move(c, sweep_i, "bull") is None


def test_displacement_move_none_when_direction_wrong():
    baseline = _quiet_baseline(20, 100.0)
    sweep_i = len(baseline) - 1
    bearish_disp = [
        _bar(100.0, 100.05, 99.05, 99.10),
        _bar(99.10, 99.15, 98.15, 98.20),
        _bar(98.20, 98.25, 97.25, 97.30),
    ]
    c = baseline + bearish_disp
    # asking for a BULL displacement over candles that actually move bearish
    assert e.displacement_move(c, sweep_i, "bull") is None


def test_displacement_move_respects_start_offset():
    baseline = _quiet_baseline(20, 100.0)
    sweep_i = len(baseline) - 1
    # two quiet candles, THEN a strong run starting 3 bars after the sweep —
    # outside the default start_offset_bars=2 window (only offsets 1,2 are
    # tried), so it must not match.
    gap = [_bar(100.0, 100.05, 99.95, 100.0), _bar(100.0, 100.05, 99.95, 100.0)]
    disp = [
        _bar(100.0, 100.95, 99.95, 100.90),
        _bar(100.90, 101.85, 100.85, 101.80),
        _bar(101.80, 102.75, 101.75, 102.70),
    ]
    c = baseline + gap + disp
    assert e.displacement_move(c, sweep_i, "bull", start_offset_bars=2) is None
    # but it IS found with a wider offset allowance
    assert e.displacement_move(c, sweep_i, "bull", start_offset_bars=3) is not None


# --- resample() — added for the ST-C1 v3.10 "Reversal Capture" preset,
# which needs H4 candles but this repo's H4 CSVs are missing or too short
# for full-history replay (found while running v3.10's population/existence
# check) — deriving H4 from the full-history H1 series instead.

def test_resample_aggregates_ohlc_correctly():
    c = [_bar(1, 5, 0, 2), _bar(2, 6, 1, 3), _bar(3, 4, 2, 4), _bar(4, 8, 3, 5)]
    out = e.resample(c, 4)
    assert len(out) == 1
    grp = out[0]
    assert grp["open"] == 1       # first bar's open
    assert grp["close"] == 5      # last bar's close
    assert grp["high"] == 8       # max high across the group
    assert grp["low"] == 0        # min low across the group
    assert grp["time"] == c[0]["time"]


def test_resample_drops_incomplete_trailing_group():
    c = [_bar(1, 2, 0, 1)] * 5   # 5 bars, factor=4 -> one full group + 1 leftover, dropped
    out = e.resample(c, 4)
    assert len(out) == 1


def test_resample_empty_input():
    assert e.resample([], 4) == []
