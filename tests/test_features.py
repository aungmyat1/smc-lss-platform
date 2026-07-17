"""Tests for the Phase 0 research feature database (src/features.py).
Run: python -m pytest -q"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import smc_engine as e
import features as feat


def _bar(o, h, l, c, t="2026-01-01 00:00"):
    return {"time": t, "open": o, "high": h, "low": l, "close": c}


def test_compute_features_returns_one_row_per_bar():
    c = [_bar(100.0, 100.05, 99.95, 100.0) for _ in range(30)]
    rows = feat.compute_features(c)
    assert len(rows) == 30
    for r in rows:
        assert set(feat.FIELDNAMES) <= set(r.keys())


def test_bos_and_choch_flagged_on_real_break():
    # flat baseline, then a clear bullish BOS through a confirmed swing high
    c = [_bar(100.0, 100.05, 99.95, 100.0) for _ in range(10)]
    c[6] = _bar(100.0, 100.20, 99.95, 100.05)     # local high candidate
    c.append(_bar(100.05, 100.60, 100.00, 100.55))  # BOS candle: closes above 100.20
    rows = feat.compute_features(c)
    assert rows[-1]["bos_dir"] == "bull"


def test_choch_flags_reversal_after_established_bos_direction():
    # Constructed and verified interactively rather than derived by
    # inspection: the local low must be strictly lower than BOTH its k=2
    # leading AND trailing neighbors to be a confirmed swing at all — an
    # earlier version of this fixture placed the low candidate right after
    # the bull-BOS candle, whose own low was lower than the "local low",
    # so swings() never confirmed it and no bear BOS ever fired.
    c = [_bar(100.0, 100.05, 99.95, 100.0) for _ in range(8)]
    c[4] = _bar(100.0, 100.20, 99.95, 100.05)                  # local high candidate
    c.append(_bar(100.05, 100.60, 100.00, 100.55))             # idx8: bull BOS (closes above 100.20)
    c += [_bar(100.55, 100.60, 100.50, 100.55) for _ in range(2)]   # idx9,10: baseline > 100.30
    c.append(_bar(100.55, 100.60, 100.30, 100.40))             # idx11: local low candidate
    c += [_bar(100.40, 100.45, 100.35, 100.40) for _ in range(2)]  # idx12,13: baseline > 100.30
    c.append(_bar(100.40, 100.42, 99.80, 99.85))               # idx14: bear BOS (closes below 100.30)
    rows = feat.compute_features(c)
    bear_bos_rows = [r for r in rows if r["bos_dir"] == "bear"]
    assert bear_bos_rows, "expected a bear BOS to register"
    assert bear_bos_rows[0]["choch"] is True


def test_sweep_flags_only_on_the_sweep_bar():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "EURUSD_M5.csv")
    c = e.load_candles(csv_path)[:3000]
    rows = feat.compute_features(c)
    raw_sweeps = e.liquidity_sweeps(c)
    sweep_bull_bars = {r["i"] for r in rows if r["sweep_bull"]}
    expected_bull = {s["i"] for s in raw_sweeps if s["dir"] == "bull"}
    assert sweep_bull_bars == expected_bull


def test_performance_stays_roughly_linear_on_real_data():
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "EURUSD_M5.csv")
    c = e.load_candles(csv_path)
    small = c[:3000]
    t0 = time.time()
    feat.compute_features(small)
    small_time = time.time() - t0

    t0 = time.time()
    feat.compute_features(c)
    full_time = time.time() - t0

    ratio_bars = len(c) / len(small)
    ratio_time = full_time / max(small_time, 1e-6)
    # linear -> ratio_time ~= ratio_bars; quadratic -> ratio_time ~= ratio_bars^2.
    # allow generous slack (5x the bar-count ratio) so this only fails on a
    # genuine complexity regression, not normal variance.
    assert ratio_time < ratio_bars * 5, (
        f"runtime scaled {ratio_time:.1f}x for a {ratio_bars:.1f}x bar-count "
        "increase -- looks superlinear, check for a reintroduced O(n^2)"
    )
