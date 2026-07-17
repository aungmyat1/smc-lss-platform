#!/usr/bin/env python3
"""Deterministic SMC engine — the code behind the atomic skills.

Pure functions, no randomness, no look-ahead beyond what is explicitly gated.
Same input CSV -> identical output, always. Used by backtest.py and dry_run.py.
"""
from __future__ import annotations
import csv

def load_candles(path):
    """Return candles ascending by time: list of dicts o/h/l/c/time."""
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append({"time": r["time"],
                         "open": float(r["open"]), "high": float(r["high"]),
                         "low": float(r["low"]), "close": float(r["close"])})
    rows.sort(key=lambda x: x["time"])
    return rows

def swings(c, k=2):
    """Fractal swing points. Returns (highs, lows) as lists of (index, price).
    A swing at center index i is only *confirmed* after k following bars."""
    hi, lo = [], []
    for i in range(k, len(c) - k):
        h, l = c[i]["high"], c[i]["low"]
        if all(h >  c[j]["high"] for j in range(i-k, i)) and \
           all(h >= c[j]["high"] for j in range(i+1, i+k+1)):
            hi.append((i, h))
        if all(l <  c[j]["low"] for j in range(i-k, i)) and \
           all(l <= c[j]["low"] for j in range(i+1, i+k+1)):
            lo.append((i, l))
    return hi, lo

def confirmed_before(swing_list, idx, k=2):
    """Swings whose center is confirmed by bar `idx` (center + k <= idx)."""
    return [s for s in swing_list if s[0] + k <= idx]

def equilibrium(c, i, window=40):
    """50% of the dealing range over the trailing `window` bars up to bar i."""
    lo = min(x["low"]  for x in c[max(0, i-window):i+1])
    hi = max(x["high"] for x in c[max(0, i-window):i+1])
    return (hi + lo) / 2, hi, lo

def atr(c, i, n=14):
    if i < 1:
        return c[i]["high"] - c[i]["low"]
    trs = []
    for j in range(max(1, i-n+1), i+1):
        h, l, pc = c[j]["high"], c[j]["low"], c[j-1]["close"]
        trs.append(max(h-l, abs(h-pc), abs(l-pc)))
    return sum(trs) / len(trs) if trs else 0.0

def trend(hi, lo):
    if len(hi) >= 2 and len(lo) >= 2:
        if hi[-1][1] > hi[-2][1] and lo[-1][1] > lo[-2][1]:
            return "BULLISH"
        if hi[-1][1] < hi[-2][1] and lo[-1][1] < lo[-2][1]:
            return "BEARISH"
    return "RANGING"


def fvgs(c, min_gap=0.0):
    """Fair value gaps (3-candle imbalance). dir bull/bear with zone bounds."""
    out = []
    for i in range(2, len(c)):
        if c[i-2]["high"] < c[i]["low"] and (c[i]["low"] - c[i-2]["high"]) >= min_gap:
            out.append({"i": i, "dir": "bull", "lower": c[i-2]["high"], "upper": c[i]["low"]})
        elif c[i-2]["low"] > c[i]["high"] and (c[i-2]["low"] - c[i]["high"]) >= min_gap:
            out.append({"i": i, "dir": "bear", "lower": c[i]["high"], "upper": c[i-2]["low"]})
    return out


def order_blocks(c, k=2):
    """Order blocks: last opposing candle before a close that breaks a confirmed swing."""
    hi_all, lo_all = swings(c, k)
    obs = []
    for i in range(k + 1, len(c)):
        hi = confirmed_before(hi_all, i, k)
        lo = confirmed_before(lo_all, i, k)
        if hi and c[i]["close"] > hi[-1][1]:            # bullish BOS
            j = i - 1
            while j > 0 and c[j]["close"] >= c[j]["open"]:
                j -= 1                                   # walk back to last down candle
            obs.append({"i": j, "dir": "bull", "low": c[j]["low"], "high": c[j]["high"]})
        elif lo and c[i]["close"] < lo[-1][1]:           # bearish BOS
            j = i - 1
            while j > 0 and c[j]["close"] <= c[j]["open"]:
                j -= 1
            obs.append({"i": j, "dir": "bear", "low": c[j]["low"], "high": c[j]["high"]})
    return obs


def liquidity_pools(c, k=2, tol=0.0002):
    """Equal highs (BSL) / equal lows (SSL) within tol -> resting liquidity."""
    hi, lo = swings(c, k)
    pools = []
    for arr, typ in ((hi, "BSL"), (lo, "SSL")):
        for a in range(len(arr)):
            for b in range(a + 1, len(arr)):
                if abs(arr[a][1] - arr[b][1]) <= tol:
                    pools.append({"type": typ, "price": round((arr[a][1] + arr[b][1]) / 2, 5)})
    return pools


def liquidity_sweeps(c, k=2, min_wick_ratio=0.5):
    """Sweep + reclaim events (adapted from Signal-Execution-Labs liquidity-sweep spec).

    Bullish sweep: candle wick pierces a prior confirmed swing LOW, body closes
    back ABOVE it, and the lower wick is >= min_wick_ratio of the candle range.
    Bearish sweep: mirror above a prior confirmed swing HIGH. Deterministic.
    """
    hi_all, lo_all = swings(c, k)
    out = []
    for i in range(k + 1, len(c)):
        rng = c[i]["high"] - c[i]["low"]
        if rng <= 0:
            continue
        body_lo = min(c[i]["open"], c[i]["close"])
        body_hi = max(c[i]["open"], c[i]["close"])
        lo = confirmed_before(lo_all, i, k)
        hi = confirmed_before(hi_all, i, k)
        if lo:
            lvl = lo[-1][1]
            lower_wick = body_lo - c[i]["low"]
            if c[i]["low"] < lvl and c[i]["close"] > lvl and lower_wick >= min_wick_ratio * rng:
                out.append({"i": i, "dir": "bull", "level": round(lvl, 5), "reclaim": round(c[i]["close"], 5)})
        if hi:
            lvl = hi[-1][1]
            upper_wick = c[i]["high"] - body_hi
            if c[i]["high"] > lvl and c[i]["close"] < lvl and upper_wick >= min_wick_ratio * rng:
                out.append({"i": i, "dir": "bear", "level": round(lvl, 5), "reclaim": round(c[i]["close"], 5)})
    return out


def inducement(c, k=2):
    """Nearest confirmed minor liquidity that is typically swept before the POI.
    Returns the most recent confirmed swing high (sell-side lure) and low (buy-side lure)."""
    hi, lo = swings(c, k)
    return {"bear_inducement": hi[-1][1] if hi else None,
            "bull_inducement": lo[-1][1] if lo else None}


def mitigation_status(c, from_i, low, high, direction):
    """Status of a POI zone [low,high] after bar from_i: FRESH / MITIGATED / INVALIDATED."""
    status = "FRESH"
    for i in range(from_i + 1, len(c)):
        if c[i]["low"] <= high and c[i]["high"] >= low:
            status = "MITIGATED"
        if direction == "bull" and c[i]["close"] < low:
            return "INVALIDATED"
        if direction == "bear" and c[i]["close"] > high:
            return "INVALIDATED"
    return status
