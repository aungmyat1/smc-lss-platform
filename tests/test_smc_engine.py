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
