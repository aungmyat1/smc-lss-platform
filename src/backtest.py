#!/usr/bin/env python3
"""Deterministic SMC-LSS backtest runner (operational, multi-file aggregate).

Strategy: LONG on confirmed bullish BOS in discount; SHORT mirror in premium.
Stop = recent confirmed swing; target = entry +/- rr*risk. Stop-first fill.
Runs one file (--data) or aggregates every data/*.csv (--all) into a combined
portfolio result plus a per-file breakdown.
"""
import argparse, glob, json, os, statistics
import smc_engine as e


def collect(c, rr, k, window):
    hi_all, lo_all = e.swings(c, k)
    trades, pos = [], None
    for i in range(k + 1, len(c)):
        px = c[i]["close"]
        if pos:
            if pos["dir"] == "long":
                hit_stop, hit_tgt = c[i]["low"] <= pos["stop"], c[i]["high"] >= pos["tgt"]
            else:
                hit_stop, hit_tgt = c[i]["high"] >= pos["stop"], c[i]["low"] <= pos["tgt"]
            if hit_stop:
                trades.append(-1.0); pos = None
            elif hit_tgt:
                trades.append(rr); pos = None
            continue
        hi = e.confirmed_before(hi_all, i, k)
        lo = e.confirmed_before(lo_all, i, k)
        if not hi or not lo:
            continue
        eq, _, _ = e.equilibrium(c, i, window)
        sh, sl = hi[-1][1], lo[-1][1]
        if px > sh and px < eq and sl < px:
            pos = {"dir": "long", "stop": sl, "tgt": px + rr * (px - sl)}
        elif px < sl and px > eq and sh > px:
            pos = {"dir": "short", "stop": sh, "tgt": px - rr * (sh - px)}
    return trades


def metrics(rs, rr, min_trades=30):
    if not rs:
        return {"status": "NO_TRADES", "trades": 0}
    wins = [r for r in rs if r > 0]
    gl = abs(sum(r for r in rs if r <= 0))
    cum = peak = mdd = 0.0
    for r in rs:
        cum += r; peak = max(peak, cum); mdd = min(mdd, cum - peak)
    return {
        "status": "OK" if len(rs) >= min_trades else "LOW_SAMPLE",
        "trades": len(rs),
        "win_rate": round(len(wins) / len(rs), 3),
        "expectancy_R": round(statistics.mean(rs), 3),
        "profit_factor": round(sum(wins) / gl, 3) if gl else None,
        "max_drawdown_R": round(mdd, 3),
        "total_R": round(sum(rs), 3),
        "rr": rr,
        "_caveat": None if len(rs) >= min_trades else str(len(rs)) + " trades (<" + str(min_trades) + "); low sample.",
    }


def run_paths(paths, rr, k, window):
    per_file, combined = {}, []
    for p in sorted(paths):
        c = e.load_candles(p)
        if len(c) < 3 * k + 5:
            per_file[os.path.basename(p)] = {"status": "NEEDS_MORE_DATA", "bars": len(c)}
            continue
        rs = collect(c, rr, k, window)
        m = metrics(rs, rr); m["bars"] = len(c)
        per_file[os.path.basename(p)] = m
        combined += rs
    return {"combined": metrics(combined, rr), "per_file": per_file, "files": len(per_file)}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default=None)
    p.add_argument("--all", action="store_true", help="aggregate data/*.csv")
    p.add_argument("--rr", type=float, default=2.0)
    p.add_argument("--k", type=int, default=2)
    p.add_argument("--window", type=int, default=40)
    a = p.parse_args()
    paths = sorted(glob.glob("data/*.csv")) if a.all or not a.data else [a.data]
    res = run_paths(paths, a.rr, a.k, a.window)
    os.makedirs("reports", exist_ok=True)
    with open("reports/backtest_result.json", "w") as f:
        json.dump(res, f, indent=2)
    print(json.dumps(res, indent=2))
