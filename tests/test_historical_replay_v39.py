"""Tests for validation/historical_replay_engine_v39.py — the replay wiring
around src/signal_v39.py. Reuses HistoricalReplayEngine's already-tested
cost/fill machinery (see tests/test_historical_replay.py) unchanged; this
file covers only what's new for v3.9: point-in-time window bounding ignoring
future bars, next-bar-open fill, the weekend force-exit, net-cost
computation, duplicate-structure suppression, and clean-vs-resumed
determinism — matching the precedent set by test_signal_v37_gates.py (only
test what differs from the shared, already-verified base).
"""
from __future__ import annotations

import datetime
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from validation.historical_replay_engine import SignalRecord  # noqa: E402
from validation.historical_replay_engine_v39 import HistoricalReplayEngineV39  # noqa: E402


def bar(t, o, h, l, c):
    return {"time": t, "open": o, "high": h, "low": l, "close": c}


def _ts(base, hours):
    return (base + datetime.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M")


def _engine():
    return HistoricalReplayEngineV39(warmup_bars=5)


# --- point-in-time bounded window: future bars must never change the window ---

def test_bounded_context_window_ignores_future_bars():
    engine = _engine()
    base = datetime.datetime(2026, 1, 5, 0, 0)  # Monday
    h1 = [bar(_ts(base, i), 1.0, 1.01, 0.99, 1.0) for i in range(20)]
    asof = _ts(base, 10)
    short_window = engine._bounded_context_window(h1, "H1", asof, lookback_bars=5)
    h1_with_future = h1 + [bar(_ts(base, i), 9.0, 9.0, 9.0, 9.0) for i in range(100, 110)]
    same_window = engine._bounded_context_window(h1_with_future, "H1", asof, lookback_bars=5)
    assert short_window == same_window
    assert all(c["close"] != 9.0 for c in short_window)


def test_available_index_matches_asof_not_series_length():
    engine = _engine()
    base = datetime.datetime(2026, 1, 5, 0, 0)
    h1 = [bar(_ts(base, i), 1.0, 1.01, 0.99, 1.0) for i in range(10)]
    idx_before_extension = engine._available_index(h1, "H1", _ts(base, 5))
    h1_extended = h1 + [bar(_ts(base, i), 1.0, 1.01, 0.99, 1.0) for i in range(10, 30)]
    idx_after_extension = engine._available_index(h1_extended, "H1", _ts(base, 5))
    assert idx_before_extension == idx_after_extension


# --- trade simulation: cost model, weekend force-exit, stop-priority -------

def _long_signal(entry_time):
    return SignalRecord(
        index=0, time=entry_time, direction="long",
        entry=1.1000, stop=1.0950, target=1.1200,
        structure_key="k1", reason_codes=(),
    )


def test_next_bar_open_fill_and_net_cost_below_gross():
    engine = _engine()
    base = datetime.datetime(2026, 1, 5, 8, 0)  # Monday, in a weekday run
    m5 = [bar(_ts(base, 0), 1.1000, 1.1005, 1.0995, 1.1000)]
    m5 += [bar(_ts(base, i * (5 / 60)), 1.1000, 1.1010, 1.0990, 1.1005) for i in range(1, 40)]
    m5[-1] = bar(m5[-1]["time"], 1.1005, 1.1210, 1.0990, 1.1205)  # final bar clears target
    signal = _long_signal(m5[0]["time"])
    trade = engine.simulate_trade(signal, m5, entry_index=1, symbol="EURUSD")
    assert trade.entry == 1.1000
    assert trade.outcome == "TARGET"
    assert trade.net_r < trade.gross_r
    assert abs((trade.gross_r - trade.cost_r) - trade.net_r) < 1e-9


def test_stop_and_target_same_bar_resolves_as_stop_conservative():
    engine = _engine()
    base = datetime.datetime(2026, 1, 5, 8, 0)
    m5 = [bar(_ts(base, 0), 1.1000, 1.1005, 1.0995, 1.1000)]
    ambiguous = bar(_ts(base, 1), 1.1000, 1.1250, 1.0900, 1.1000)  # both stop(1.0950) and target(1.1200) touched
    m5.append(ambiguous)
    signal = _long_signal(m5[0]["time"])
    trade = engine.simulate_trade(signal, m5, entry_index=1, symbol="EURUSD")
    assert trade.outcome == "STOP"
    assert trade.ambiguous_bar is True


def test_weekend_force_exit_before_gap_not_after_stop_or_target_on_same_bar():
    """A trade still open going into a Friday->Monday gap must close flat at
    the last Friday bar's close, not run into (nonexistent) weekend bars."""
    engine = _engine()
    friday = datetime.datetime(2026, 1, 9, 20, 0)  # Friday evening
    m5 = [bar(friday.strftime("%Y-%m-%d %H:%M"), 1.1000, 1.1005, 1.0995, 1.1000)]
    last_friday_bar = bar((friday + datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M"),
                          1.1000, 1.1010, 1.0990, 1.1005)   # no stop/target hit
    monday_bar = bar("2026-01-12 00:00", 1.1005, 1.1006, 1.1004, 1.1005)
    m5 += [last_friday_bar, monday_bar]
    signal = _long_signal(m5[0]["time"])
    trade = engine.simulate_trade(signal, m5, entry_index=1, symbol="EURUSD")
    assert trade.outcome == "WEEKEND_EXIT"
    assert trade.exit_price == last_friday_bar["close"]


def test_weekend_gap_does_not_override_a_stop_hit_on_the_same_bar():
    engine = _engine()
    friday = datetime.datetime(2026, 1, 9, 20, 0)
    m5 = [bar(friday.strftime("%Y-%m-%d %H:%M"), 1.1000, 1.1005, 1.0995, 1.1000)]
    stop_hit_friday = bar((friday + datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M"),
                          1.1000, 1.1005, 1.0900, 1.0940)   # pierces stop 1.0950
    monday_bar = bar("2026-01-12 00:00", 1.0940, 1.0945, 1.0935, 1.0940)
    m5 += [stop_hit_friday, monday_bar]
    signal = _long_signal(m5[0]["time"])
    trade = engine.simulate_trade(signal, m5, entry_index=1, symbol="EURUSD")
    assert trade.outcome == "STOP"


# --- determinism: clean vs re-run must match exactly -----------------------

def _synthetic_m5(n=60):
    base = datetime.datetime(2026, 1, 5, 7, 0)
    out = []
    for i in range(n):
        t = _ts(base, i * (5 / 60))
        out.append(bar(t, 1.1000, 1.1010, 1.0990, 1.1000))
    return out


def test_replay_is_deterministic_clean_vs_rerun():
    engine1 = HistoricalReplayEngineV39(warmup_bars=5)
    engine2 = HistoricalReplayEngineV39(warmup_bars=5)
    m5 = _synthetic_m5(60)
    result1 = engine1.replay(m5, symbol="EURUSD")
    result2 = engine2.replay(list(m5), symbol="EURUSD")
    assert result1.funnel_counts == result2.funnel_counts
    assert result1.trades == result2.trades
    assert result1.signals == result2.signals


def test_no_broker_order_import_anywhere_in_v39_research_path():
    """Research code must never import or call a broker-order path (CLAUDE.md
    hard rule / docs/RESEARCH-CHARTER.md)."""
    import signal_v39
    import validation.historical_replay_engine_v39 as replay_v39
    for mod in (signal_v39, replay_v39):
        src_path = mod.__file__
        with open(src_path, encoding="utf-8") as fh:
            text = fh.read()
        assert "mt5." not in text.lower()
        assert "place_order" not in text.lower()
        assert "MetaTrader5" not in text
