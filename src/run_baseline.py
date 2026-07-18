#!/usr/bin/env python3
"""Re-baseline all three active symbols and print a comparison table.

Usage:
    python src/run_baseline.py

Runs backtest_v35.run_backtest() for EURUSD / XAUUSD-VIP / BTCUSD with
full H1+D1 context and broker_offset=3 (VTMarkets), saves per-symbol JSON
reports, then prints a summary table with per-E-trigger trade counts.
"""
from __future__ import annotations
import json, os, sys, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import smc_engine as e
import backtest_v35 as bt

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
REPORTS = os.path.join(os.path.dirname(__file__), "..", "reports")

SYMBOLS = [
    {
        "symbol": "EURUSD",
        "m5":  "EURUSD_M5.csv",
        "h1":  "EURUSD_H1.csv",
        "d1":  "EURUSD_D1.csv",
        "broker_offset": 3,
    },
    {
        "symbol": "XAUUSD-VIP",
        "m5":  "XAUUSD-VIP_M5.csv",
        "h1":  "XAUUSD-VIP_H1.csv",
        "d1":  "XAUUSD-VIP_D1.csv",
        "broker_offset": 3,
    },
    {
        "symbol": "BTCUSD",
        "m5":  "BTCUSD_M5.csv",
        "h1":  "BTCUSD_H1.csv",
        "d1":  "BTCUSD_D1.csv",
        "broker_offset": 0,   # crypto: broker timestamps already UTC
    },
]

OLD_BASELINE = {
    "EURUSD":     {"trades": 377,  "win_rate_pct": 10.6, "expectancy_R": -0.123},
    "XAUUSD-VIP": {"trades": 816,  "win_rate_pct": 22.8, "expectancy_R": -0.166},
    "BTCUSD":     {"trades": 231,  "win_rate_pct": 10.0, "expectancy_R": -0.182},
}


def _etrigger_counts(trade_log):
    counts = {"E1": 0, "E2": 0, "E3": 0}
    for t in trade_log:
        prefix = t.get("variant", "")[:2]
        if prefix in counts:
            counts[prefix] += 1
    return counts


def run_all():
    os.makedirs(REPORTS, exist_ok=True)
    results = []
    for cfg in SYMBOLS:
        sym = cfg["symbol"]
        print(f"\n{'='*60}")
        print(f"  Running {sym} ...", flush=True)
        m5 = e.load_candles(os.path.join(DATA, cfg["m5"]))
        h1p = os.path.join(DATA, cfg["h1"])
        d1p = os.path.join(DATA, cfg["d1"])
        h1 = e.load_candles(h1p) if os.path.exists(h1p) else None
        d1 = e.load_candles(d1p) if os.path.exists(d1p) else None
        rep = bt.run_backtest(
            sym, m5, h1,
            broker_offset=cfg["broker_offset"],
            d1=d1,
        )
        out_path = os.path.join(REPORTS, f"backtest_v35_{sym}.json")
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(rep, fh, indent=2)
        print(f"  Saved {out_path}", flush=True)
        results.append((sym, rep))

    # --- Summary table ---
    print(f"\n{'='*60}")
    print(f"  BASELINE SUMMARY  (generated {datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')})")
    print(f"{'='*60}")
    hdr = f"{'Symbol':<14} {'Trades':>6} {'Win%':>6} {'ExpR':>7} {'PF':>6} {'MaxDD':>7}  {'E1':>4} {'E2':>4} {'E3':>4}  Caveat"
    print(hdr)
    print("-" * len(hdr))
    for sym, rep in results:
        old = OLD_BASELINE.get(sym, {})
        trades = rep["trades"]
        win    = rep["win_rate_pct"]
        exp    = rep["expectancy_R"]
        pf     = rep["profit_factor"]
        mdd    = rep["max_drawdown_R"]
        caveat = "⚠ SMALL" if rep.get("caveat") else "ok"
        ect    = _etrigger_counts(rep.get("trade_log", []))
        delta_t = f"({trades - old.get('trades', 0):+d})" if old else ""
        delta_e = f"({exp - old.get('expectancy_R', 0):+.3f})" if old else ""
        print(f"{sym:<14} {trades:>6}{delta_t:<8} {win:>6.1f}%  {exp:>+.3f}{delta_e:<9} "
              f"{str(pf) if pf is not None else 'N/A':>6}  {mdd:>+.3f}   "
              f"{ect['E1']:>4} {ect['E2']:>4} {ect['E3']:>4}  {caveat}")
    print(f"{'='*60}")
    print("\nOLD baseline (broken E-trigger, no session/dedup/ordering):")
    print(f"  EURUSD:     377 trades / 10.6% win / -0.123R expectancy")
    print(f"  XAUUSD-VIP: 816 trades / 22.8% win / -0.166R expectancy")
    print(f"  BTCUSD:     231 trades / 10.0% win / -0.182R expectancy")
    print()
    print("NOTE: M2 gate (expectancy >= +0.2R, PF >= 1.3, >= 30 trades, OOS)")
    print("      is NOT evaluated here \u2014 this is a raw IS re-baseline only.")
    print("      Parameter tuning (optimize.py) is a later phase.")


if __name__ == "__main__":
    run_all()
