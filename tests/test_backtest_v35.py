"""Thin-slice tests for the v3.5 backtest harness (M2).
Run: python -m pytest -q"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import backtest_v35 as bt


def _bar(h, l):
    return {"time": "t", "open": (h + l) / 2, "high": h, "low": l, "close": (h + l) / 2}


def test_normalize_time_shifts_offset():
    assert bt.normalize_time("2026-07-17 10:00", 3) == "2026-07-17 07:00"
    assert bt.normalize_time("2026-07-17 10:00", 0) == "2026-07-17 10:00"


def test_simulate_trade_take_profit_sell():
    # SELL entry 100, stop 102 (risk 2), target = 100 - 2*2 = 96. A bar that reaches 96 -> +2R
    r = bt.simulate_trade("SELL", 100.0, 102.0, [_bar(101, 95)], rr=2.0)
    assert r == 2.0


def test_simulate_trade_stop_loss_sell():
    # first bar hits stop 102 (high>=102) but not target -> -1R
    r = bt.simulate_trade("SELL", 100.0, 102.0, [_bar(103, 99)], rr=2.0)
    assert r == -1.0


def test_simulate_trade_timeout_flat():
    # neither stop nor target within the (truncated) hold window -> 0R
    r = bt.simulate_trade("SELL", 100.0, 102.0, [_bar(101, 99)], rr=2.0, max_hold_bars=1)
    assert r == 0.0


def test_simulate_trade_zero_risk_returns_none():
    assert bt.simulate_trade("BUY", 100.0, 100.0, [_bar(101, 99)]) is None


def test_run_backtest_report_shape_on_real_csv():
    m5 = None
    csv = os.path.join(os.path.dirname(__file__), "..", "data", "EURUSD_M5.csv")
    import smc_engine as e
    m5 = e.load_candles(csv)
    rep = bt.run_backtest("EURUSD", m5, warmup=20)
    for k in ("symbol", "trades", "win_rate_pct", "expectancy_R", "profit_factor",
              "max_drawdown_R", "caveat", "trade_log"):
        assert k in rep, k
    assert rep["trades"] >= 0
    if rep["trades"] < 30:
        assert rep["caveat"] and "SAMPLE TOO SMALL" in rep["caveat"]
