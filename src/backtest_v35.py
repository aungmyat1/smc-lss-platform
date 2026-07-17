#!/usr/bin/env python3
"""SMC-LSS v3.5 event-driven backtest — thin vertical slice (M2).

Walks M5 candles bar-by-bar using ONLY closed candles (no look-ahead), calls the
v3.5 engine (signal_v35.analyze) at each step, and simulates a simple trade outcome
(target = rr*risk, stop = signal stop, time-stopped at the variant's max hold).
Emits reports/backtest_v35_<symbol>.json with expectancy, profit factor, win rate,
drawdown, avg R:R, and an explicit caveat when the sample is < 30 trades.

Scope (slice): costs are optional and flat; realism (spread/slippage/commission,
walk-forward split, tick-value sizing) is layered on AFTER this pipeline is trusted.
Deterministic: same CSVs -> identical report.
"""
from __future__ import annotations
import argparse, json, os, datetime
import smc_engine as e
import signal_v35 as v35

M5_PER_HOUR = 12


def normalize_time(ts, broker_offset_hours=0):
    """Shift a 'YYYY-MM-DD HH:MM' broker timestamp to canonical UTC.

    VTMarkets candle stamps run ahead of UTC; pass the broker's offset (e.g. 3)
    to normalize. Offset 0 is a no-op. Returns the normalized 'YYYY-MM-DD HH:MM'.
    """
    if not broker_offset_hours:
        return ts
    dt = datetime.datetime.strptime(ts[:16], "%Y-%m-%d %H:%M")
    dt -= datetime.timedelta(hours=broker_offset_hours)
    return dt.strftime("%Y-%m-%d %H:%M")


def _apply_offset(candles, off):
    if not off:
        return candles
    for c in candles:
        c["time"] = normalize_time(c["time"], off)
    return candles


def simulate_trade(direction, entry, stop, forward, target=None, rr=2.0, max_hold_bars=None):
    """Given entry/stop and the FORWARD M5 bars (after entry), return the outcome
    in R multiples. Target defaults to rr*risk; if an explicit DOL target is given,
    the win pays its true reward:risk. Stop-first if a bar hits both (conservative)."""
    risk = abs(entry - stop)
    if risk <= 0:
        return None
    if target is None:
        target = entry + rr * risk if direction == "BUY" else entry - rr * risk
    reward_r = abs(target - entry) / risk
    horizon = forward if max_hold_bars is None else forward[:max_hold_bars]
    for b in horizon:
        hit_stop = b["low"] <= stop if direction == "BUY" else b["high"] >= stop
        hit_tp = b["high"] >= target if direction == "BUY" else b["low"] <= target
        if hit_stop:
            return -1.0                      # conservative: stop first if both hit
        if hit_tp:
            return round(reward_r, 3)
    return 0.0                                # time-stopped flat (no hit within hold)


def run_backtest(symbol, m5, h1=None, rr=2.0, min_rr=2.0, warmup=40,
                 broker_offset=0, cost_r=0.0, m5_lookback=500, h1_lookback=300):
    """Walk M5 bar-by-bar and call the v3.5 engine at each step.

    Detection windows are bounded to `m5_lookback`/`h1_lookback` trailing bars
    (rather than the full history-to-date) so a multi-month CSV runs in O(n):
    re-slicing/re-scanning the whole series on every bar is O(n^2) and, at
    tens of thousands of bars, effectively never finishes. SMC structure
    (swings/FVG/OB/sweeps) is a recent-price-action read anyway, so bounding
    the lookback does not change what a live run would see.
    """
    m5 = _apply_offset(list(m5), broker_offset)
    h1 = _apply_offset(list(h1), broker_offset) if h1 else None
    trades = []
    i = warmup
    n = len(m5)
    h1_end = 0                                        # count of h1 bars with time <= m5[i]["time"]
    while i < n - 1:
        window = m5[max(0, i + 1 - m5_lookback): i + 1]  # closed candles, bounded lookback
        if h1:
            while h1_end < len(h1) and h1[h1_end]["time"] <= m5[i]["time"]:
                h1_end += 1
            h1ctx = h1[max(0, h1_end - h1_lookback): h1_end]
        else:
            h1ctx = None
        sig = v35.analyze(symbol, window, h1ctx)
        if not sig.get("detected"):
            i += 1
            continue
        entry = m5[i + 1]["open"]                     # act on next bar's open (no look-ahead)
        stop = sig["stop"]
        direction = sig["direction"]
        target = sig.get("primary_tp")                 # DOL target (None -> rr*risk fallback)
        max_hold = v35.HORIZON_MAX_HOURS[sig["horizon"]] * M5_PER_HOUR
        forward = m5[i + 1:]
        r = simulate_trade(direction, entry, stop, forward, target, rr, max_hold)
        if r is None:
            i += 1
            continue
        # spread cost as an R-drag on entry+exit (2x half-spread ~= 1 spread)
        risk = abs(entry - stop)
        spread = v35.profile_for(symbol).get("spread", 0.0)
        r -= (spread / risk) if (risk and cost_r == 0.0) else cost_r
        exit_i = i + 1
        trades.append({"i": i, "variant": sig["variant"], "dir": direction,
                       "entry": round(entry, 5), "stop": round(stop, 5), "r": round(r, 3)})
        # jump past the trade window so trades don't overlap (flat before next entry)
        i = exit_i + 1
    return _metrics(symbol, trades, rr, broker_offset)


def _metrics(symbol, trades, rr, broker_offset):
    n = len(trades)
    rs = [t["r"] for t in trades]
    wins = [x for x in rs if x > 0]
    losses = [x for x in rs if x < 0]
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    expectancy = round(sum(rs) / n, 3) if n else None
    pf = round(gross_win / gross_loss, 2) if gross_loss else (None if not wins else float("inf"))
    winrate = round(100 * len(wins) / n, 1) if n else None
    # max drawdown on the cumulative-R equity curve
    eq, peak, mdd = 0.0, 0.0, 0.0
    for x in rs:
        eq += x
        peak = max(peak, eq)
        mdd = min(mdd, eq - peak)
    caveat = None
    if n < 30:
        caveat = f"SAMPLE TOO SMALL (n={n} < 30): metrics indicative only, NOT a validation pass."
    return {
        "symbol": symbol, "strategy_spec": "specs/v3.5.yaml", "status": "RESEARCH_CANDIDATE",
        "generated_utc": datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "broker_offset_hours": broker_offset, "rr_target": rr,
        "trades": n, "wins": len(wins), "losses": len(losses),
        "win_rate_pct": winrate, "expectancy_R": expectancy,
        "profit_factor": pf, "avg_rr": rr, "max_drawdown_R": round(mdd, 3),
        "caveat": caveat, "trade_log": trades,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="EURUSD")
    ap.add_argument("--m5", required=True)
    ap.add_argument("--h1")
    ap.add_argument("--rr", type=float, default=2.0)
    ap.add_argument("--warmup", type=int, default=40)
    ap.add_argument("--broker_offset", type=int, default=0)
    ap.add_argument("--m5_lookback", type=int, default=500)
    ap.add_argument("--h1_lookback", type=int, default=300)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    m5 = e.load_candles(a.m5)
    h1 = e.load_candles(a.h1) if a.h1 else None
    rep = run_backtest(a.symbol, m5, h1, a.rr, warmup=a.warmup, broker_offset=a.broker_offset,
                       m5_lookback=a.m5_lookback, h1_lookback=a.h1_lookback)
    out = a.out or f"reports/backtest_v35_{a.symbol}.json"
    os.makedirs("reports", exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=2)
    print(json.dumps({k: rep[k] for k in
          ("symbol", "trades", "win_rate_pct", "expectancy_R", "profit_factor",
           "max_drawdown_R", "caveat")}, indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
