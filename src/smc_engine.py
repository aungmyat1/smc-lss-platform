#!/usr/bin/env python3
"""Deterministic SMC engine — the code behind the atomic skills.

Pure functions, no randomness, no look-ahead beyond what is explicitly gated.
Same input CSV -> identical output, always. Used by backtest.py and dry_run.py.
"""
from __future__ import annotations
import csv
import bisect

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
    A swing at center index i is only *confirmed* after k following bars.

    Plain loops with early-break rather than all(genexpr) — this runs once
    per candle inside the backtest's per-bar analysis loop, and generator
    object creation/teardown dominated profiled runtime at that call volume.
    """
    hi, lo = [], []
    highs = [x["high"] for x in c]
    lows = [x["low"] for x in c]
    for i in range(k, len(c) - k):
        h, l = highs[i], lows[i]
        is_hi = True
        for j in range(i - k, i):
            if not (h > highs[j]):
                is_hi = False
                break
        if is_hi:
            for j in range(i + 1, i + k + 1):
                if not (h >= highs[j]):
                    is_hi = False
                    break
        if is_hi:
            hi.append((i, h))
        is_lo = True
        for j in range(i - k, i):
            if not (l < lows[j]):
                is_lo = False
                break
        if is_lo:
            for j in range(i + 1, i + k + 1):
                if not (l <= lows[j]):
                    is_lo = False
                    break
        if is_lo:
            lo.append((i, l))
    return hi, lo

def confirmed_before(swing_list, idx, k=2):
    """Swings whose center is confirmed by bar `idx` (center + k <= idx).

    swing_list is index-sorted ascending (swings() appends in increasing i
    order), so this is a binary search rather than a full rescan. Called
    inside per-bar loops in order_blocks()/liquidity_sweeps(), a linear scan
    here turns those into O(n^2) over the window.
    """
    pos = bisect.bisect_right(swing_list, idx - k, key=lambda s: s[0])
    return swing_list[:pos]

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

def displacement_move(c, sweep_i, direction, atr_period=14, atr_mult=1.5,
                      body_ratio_min=0.5, start_offset_bars=2, max_run_bars=3):
    """Locate a displacement move per v3.6 spec Sec 5 — replaces qualitative
    "strong displacement" with a numeric test: a maximal run of same-direction
    candles (each body_ratio >= body_ratio_min), starting within
    start_offset_bars of sweep_i, whose cumulative directional range clears
    atr_mult * ATR(atr_period) (measured on the bar immediately before the
    run, so the threshold isn't inflated by the move it's supposed to gate).

    direction: 'bull' or 'bear'. Returns {'start','end','range','origin'} for
    the first (earliest) qualifying start offset, or None if no run in the
    window clears the threshold.
    """
    n = len(c)
    for disp_start in range(sweep_i + 1, sweep_i + start_offset_bars + 1):
        if disp_start >= n:
            break
        ref_atr = atr(c, max(0, disp_start - 1), atr_period)
        if ref_atr <= 0:
            continue
        run_end = None
        for j in range(disp_start, min(disp_start + max_run_bars, n)):
            cndl = c[j]
            is_dir = (cndl["close"] > cndl["open"]) if direction == "bull" else (cndl["close"] < cndl["open"])
            rng = cndl["high"] - cndl["low"]
            body_ratio = (abs(cndl["close"] - cndl["open"]) / rng) if rng > 0 else 0.0
            if not is_dir or body_ratio < body_ratio_min:
                break
            run_end = j
        if run_end is None:
            continue
        origin_open = c[disp_start]["open"]
        end_close = c[run_end]["close"]
        cum_range = (end_close - origin_open) if direction == "bull" else (origin_open - end_close)
        if cum_range >= atr_mult * ref_atr:
            return {"start": disp_start, "end": run_end, "range": cum_range, "origin": origin_open}
    return None


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
    """Order blocks: last opposing candle before a close that breaks a confirmed swing.

    Only the most-recently-confirmed high/low is ever consulted (hi[-1]/lo[-1]),
    so we track it with a monotonic pointer instead of calling confirmed_before()
    (bisect + slice) on every candle — that pattern alone was ~800k calls on an
    80k-bar backtest.
    """
    hi_all, lo_all = swings(c, k)
    obs = []
    hi_ptr, lo_ptr = 0, 0
    n_hi, n_lo = len(hi_all), len(lo_all)
    for i in range(k + 1, len(c)):
        while hi_ptr < n_hi and hi_all[hi_ptr][0] + k <= i:
            hi_ptr += 1
        while lo_ptr < n_lo and lo_all[lo_ptr][0] + k <= i:
            lo_ptr += 1
        hi_last = hi_all[hi_ptr - 1][1] if hi_ptr else None
        lo_last = lo_all[lo_ptr - 1][1] if lo_ptr else None
        if hi_last is not None and c[i]["close"] > hi_last:      # bullish BOS
            j = i - 1
            while j > 0 and c[j]["close"] >= c[j]["open"]:
                j -= 1                                   # walk back to last down candle
            obs.append({"i": j, "dir": "bull", "low": c[j]["low"], "high": c[j]["high"]})
        elif lo_last is not None and c[i]["close"] < lo_last:    # bearish BOS
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
    hi_ptr, lo_ptr = 0, 0
    n_hi, n_lo = len(hi_all), len(lo_all)
    for i in range(k + 1, len(c)):
        rng = c[i]["high"] - c[i]["low"]
        if rng <= 0:
            continue
        body_lo = min(c[i]["open"], c[i]["close"])
        body_hi = max(c[i]["open"], c[i]["close"])
        while lo_ptr < n_lo and lo_all[lo_ptr][0] + k <= i:
            lo_ptr += 1
        while hi_ptr < n_hi and hi_all[hi_ptr][0] + k <= i:
            hi_ptr += 1
        if lo_ptr:
            lvl = lo_all[lo_ptr - 1][1]
            lower_wick = body_lo - c[i]["low"]
            if c[i]["low"] < lvl and c[i]["close"] > lvl and lower_wick >= min_wick_ratio * rng:
                out.append({"i": i, "dir": "bull", "level": round(lvl, 5), "reclaim": round(c[i]["close"], 5)})
        if hi_ptr:
            lvl = hi_all[hi_ptr - 1][1]
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


def resample(c, factor):
    """Aggregate `factor` consecutive candles into one (e.g. factor=4 turns
    H1 candles into H4): open = first bar's open, high/low = max/min over
    the group, close = last bar's close, time = first bar's time (the
    group's own opening timestamp, matching standard OHLC resampling
    convention). Trailing candles that don't complete a full group are
    dropped (a partial, still-forming bar must never be treated as closed).
    Used when a dedicated higher-timeframe file is missing or too short
    (e.g. no native H4 history) — deriving it from an already-available,
    full-history lower timeframe rather than fabricating data."""
    out = []
    for start in range(0, len(c) - factor + 1, factor):
        group = c[start:start + factor]
        out.append({
            "time": group[0]["time"],
            "open": group[0]["open"],
            "high": max(b["high"] for b in group),
            "low": min(b["low"] for b in group),
            "close": group[-1]["close"],
        })
    return out


def mitigation_status(c, from_i, low, high, direction, upto_i=None):
    """Status of a POI zone [low,high] after bar from_i: FRESH / MITIGATED / INVALIDATED,
    evaluated using bars up to and including `upto_i` (default: the end of
    `c`, i.e. the original behavior — callers that already pass a
    window ending "now" don't need to change).

    upto_i matters when `c` is the FULL series and the caller wants status
    "as of bar t" for t << len(c)-1: without it, every call scans to the
    true end of the array regardless of from_i, which is O(len(c)) per call
    and, called once per bar over a full history, reintroduces the O(n^2)
    pattern fixed elsewhere in this module (found via
    tests/test_features.py's linear-scaling guard).
    """
    status = "FRESH"
    end = len(c) - 1 if upto_i is None else upto_i
    for i in range(from_i + 1, end + 1):
        if c[i]["low"] <= high and c[i]["high"] >= low:
            status = "MITIGATED"
        if direction == "bull" and c[i]["close"] < low:
            return "INVALIDATED"
        if direction == "bear" and c[i]["close"] > high:
            return "INVALIDATED"
    return status
