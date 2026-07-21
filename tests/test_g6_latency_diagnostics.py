"""Tests for the G6 population-feasibility latency diagnostic (R2.1 / v3.8).

Reuses the verified G1/G2/G5/G6 fixtures from test_signal_v37_gates.py rather
than re-deriving new synthetic candle geometry.
"""
from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import signal_v37 as v37  # noqa: E402
from validation.g6_latency_diagnostics import (  # noqa: E402
    trace_g6_candidates,
    _trace_one_poi,
    percentile,
)
from test_signal_v37_gates import bar, bearish_h1, bear_m5, bullish_h1_mirror, bull_m5_mirror  # noqa: E402


def _real_times(candles, start=datetime.datetime(2026, 1, 5, 6, 0), step_minutes=5):
    """bear_m5()/bull_m5_mirror() use the placeholder time 't' (fine for
    tests that call the pure gate functions directly, which never parse
    timestamps) -- the latency diagnostic DOES parse timestamps for session
    filtering / year / data_cutoff, so give these fixtures real ones here
    without touching the shared fixture module."""
    out = []
    for i, c in enumerate(candles):
        t = (start + datetime.timedelta(minutes=step_minutes * i)).strftime("%Y-%m-%d %H:%M")
        out.append({**c, "time": t})
    return out


def _bear_g5_poi_and_range():
    h1 = bearish_h1()
    g2 = v37.evaluate_g2_external_structure(h1, {})
    g5 = v37.evaluate_g5_htf_poi(h1, None, "short", g2, {})
    return g2, g5


def _padded_m5(extra_after=200):
    """bear_m5() ends right at the retrace/entry bar; pad with flat bars,
    real-timestamped, so the tracer has room to search without running into
    end-of-data censoring for cases that are meant to be genuine rejections."""
    m5 = bear_m5()
    last = m5[-1]
    pad = [bar("t", last["close"], last["close"] + 0.0001, last["close"] - 0.0001, last["close"])
           for _ in range(extra_after)]
    return _real_times(m5 + pad)


def test_full_sequence_completes_with_padding():
    g2, g5 = _bear_g5_poi_and_range()
    m5 = _padded_m5()
    rec = _trace_one_poi(m5, 0, "short", g5, g2, "EURUSD", "B0", 30, 3200, 2, m5[-1]["time"])
    assert rec.final_decision == "COMPLETED"
    assert rec.poi_touch_index == 0
    assert rec.sweep_index == 5
    assert rec.choch_index == 9
    assert rec.retrace_index == 10
    assert rec.entry_index == 11


def test_sweep_boundary_30_vs_31():
    """Sweep sits exactly at bar 5 (5 bars after touch@0). A bound of 5
    admits it; a bound of 4 must reject/censor it -- exercises the same
    off-by-one class of boundary the B0/B1/B2=30/72/144 bounds depend on."""
    g2, g5 = _bear_g5_poi_and_range()
    m5 = _padded_m5()
    admits = _trace_one_poi(m5, 0, "short", g5, g2, "EURUSD", "B0", 5, 3200, 2, m5[-1]["time"])
    rejects = _trace_one_poi(m5, 0, "short", g5, g2, "EURUSD", "B0", 4, 3200, 2, m5[-1]["time"])
    assert admits.sweep_index == 5
    assert rejects.final_decision in ("REJECTED_NO_SWEEP", "CENSORED_NO_SWEEP")
    assert rejects.sweep_index is None


def test_wrong_event_order_rejected():
    g2, g5 = _bear_g5_poi_and_range()
    base = bear_m5()
    reordered = _real_times([base[0], base[6], base[7], base[8], base[9], base[10],
                             base[1], base[2], base[3], base[4], base[5]] + [
        bar("t", 1.19, 1.1905, 1.1895, 1.19) for _ in range(200)])
    rec = _trace_one_poi(reordered, 0, "short", g5, g2, "EURUSD", "B0", 30, 3200, 2, reordered[-1]["time"])
    assert rec.final_decision != "COMPLETED"


def test_first_qualifying_sweep_only_used():
    g2, g5 = _bear_g5_poi_and_range()
    m5 = _padded_m5()
    rec = _trace_one_poi(m5, 0, "short", g5, g2, "EURUSD", "B0", 30, 3200, 2, m5[-1]["time"])
    assert rec.sweep_index == 5   # the only qualifying sweep in the fixture


def test_end_of_data_is_censored_not_rejected():
    g2, g5 = _bear_g5_poi_and_range()
    m5 = _real_times(bear_m5())   # no padding -- data ends right at the retrace bar
    rec = _trace_one_poi(m5, 0, "short", g5, g2, "EURUSD", "B0", 30, 3200, 2, m5[-1]["time"])
    # touch@0, sweep@5 both found within available data; but the retrace/entry
    # step needs one more bar than exists -> CENSORED, never a hidden REJECTED
    assert rec.final_decision in ("CENSORED_NO_ENTRY_BAR", "COMPLETED")


def test_mirror_long_short_symmetry():
    h1_long = bullish_h1_mirror()
    g2_long = v37.evaluate_g2_external_structure(h1_long, {})
    g5_long = v37.evaluate_g5_htf_poi(h1_long, None, "long", g2_long, {})
    last = bull_m5_mirror()[-1]
    padded = _real_times(bull_m5_mirror() + [
        bar("t", last["close"], last["close"] + 0.0001, last["close"] - 0.0001, last["close"])
        for _ in range(200)])
    rec = _trace_one_poi(padded, 0, "long", g5_long, g2_long, "EURUSD", "B0", 30, 3200, 2, padded[-1]["time"])
    assert rec.final_decision == "COMPLETED"
    assert rec.direction == "long"


def test_duplicate_poi_not_retraced_within_full_walk():
    h1 = bearish_h1()
    m5 = _padded_m5(400)
    records = trace_g6_candidates(m5, h1, None, "EURUSD", "B0", 30, warmup_bars=0, m5_poi_entry_search_bars=3200)
    keys = [(r.range_id, r.poi_origin, r.poi_creation_time) for r in records]
    assert len(keys) == len(set(keys))   # each distinct POI traced exactly once


def test_latency_timestamps_never_exceed_data_cutoff():
    g2, g5 = _bear_g5_poi_and_range()
    m5 = _padded_m5()
    rec = _trace_one_poi(m5, 0, "short", g5, g2, "EURUSD", "B0", 30, 3200, 2, m5[-1]["time"])
    for t in (rec.poi_touch_time, rec.sweep_time, rec.displacement_start_time,
              rec.displacement_end_time, rec.choch_time, rec.retrace_time, rec.entry_time):
        if t is not None:
            assert t <= rec.data_cutoff


def test_missing_h1_context_fails_closed_no_candidates():
    m5 = _padded_m5()
    records = trace_g6_candidates(m5, None, None, "EURUSD", "B0", 30, warmup_bars=0)
    assert records == []   # no H1 context -> no G1/G2/G5 possible -> nothing traced, never a silent pass


def test_clean_and_resumed_traces_agree():
    """'Resumed' here = re-running the identical trace from scratch on the
    identical data must reproduce identical decisions -- the tracer carries
    no hidden mutable state across calls."""
    h1 = bearish_h1()
    m5 = _padded_m5(400)
    a = trace_g6_candidates(m5, h1, None, "EURUSD", "B0", 30, warmup_bars=0, m5_poi_entry_search_bars=3200)
    b = trace_g6_candidates(m5, h1, None, "EURUSD", "B0", 30, warmup_bars=0, m5_poi_entry_search_bars=3200)
    assert [r.final_decision for r in a] == [r.final_decision for r in b]
    assert [r.candidate_id for r in a] == [r.candidate_id for r in b]


def test_percentile_helper():
    values = list(range(1, 101))   # 1..100
    assert percentile(values, 50) in (50, 51)
    assert percentile([], 50) is None
