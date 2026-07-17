#!/usr/bin/env python3
"""Phase 0 research feature database.

Per research-architecture review (2026-07-18): a reusable, queryable
per-candle feature table that strategies read from, rather than each
strategy recomputing swing/FVG/OB/sweep detection inline. This generalizes
the feature/decision separation flagged in reports/quant_research_audit.md
Sec 4 into the platform's actual starting point.

Each primitive is computed ONCE over the full series, then a single O(n)
pass builds one row per bar via monotonic-pointer lookup of "which events
are confirmed as of this bar" — NOT by re-detecting on a per-bar growing
window, which is the exact O(n^2) pattern fixed in backtest_v35.py earlier
this session (re-scanning a growing slice on every bar is quadratic at
tens of thousands of bars).

Honesty note: this does not (yet) materialize IFVG inversion state or the
E1/E2/E3 causal triggers per bar — those require the fuller bar-index
sequencing built into signal_v35.py's M3/E-trigger detectors, which isn't
naturally a per-bar "is this active right now" lookup the way swings/FVG/OB/
sweep/mitigation/premium-discount are. Left for a follow-up rather than
faked with a shortcut version.

Output: data/features_<SYMBOL>_<TF>.csv
Usage:
  python src/features.py --symbol EURUSD --candles data/EURUSD_M5.csv --tf M5
"""
from __future__ import annotations
import argparse, csv, datetime as dt, os
import smc_engine as e

# Session windows match docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md Sec 9
# (half-open UTC hour ranges: [start, end)).
SESSION_WINDOWS = [("LONDON", 6, 10), ("NEWYORK", 11, 15)]
EXTERNAL_LIQUIDITY_LOOKBACK = 40   # bars; matches v3.6 E3_RANGE_LOOKBACK_H1_BARS default


def session_of(ts):
    hh = int(ts[11:13])
    for name, start, end in SESSION_WINDOWS:
        if start <= hh < end:
            return name
    return "OFF"


def day_of_week(ts):
    return dt.datetime.strptime(ts[:10], "%Y-%m-%d").weekday()   # 0=Mon .. 6=Sun


def _nearest_active(zones, ptr, t, lookback=None):
    """Most recent zone confirmed by bar t, given a monotonic pointer `ptr`
    (count of zones with i <= t, already advanced by the caller) — an O(1)
    index, not a scan. zones must be index-ascending.

    An earlier version of this function took a pre-sliced list and looped
    over it looking for the last qualifying entry — O(slice length) per
    call, which grows over the run and reintroduces the exact O(n^2)
    pattern fixed in smc_engine.py/backtest_v35.py earlier this session.
    Caught by test_performance_stays_roughly_linear_on_real_data before
    this module was even used anywhere.
    """
    if ptr == 0:
        return None
    z = zones[ptr - 1]
    if lookback is not None and t - z["i"] > lookback:
        return None
    return z


def compute_features(c, k=2, atr_period=14, pd_window=40, poi_max_age=60):
    """c: ascending candle list for ONE symbol/timeframe.
    Returns one feature dict per bar (index 0..len(c)-1). Early bars simply
    have fewer confirmed features available (None/False) — that's an honest
    reflection of "not enough history yet", not padded or backfilled.
    """
    n = len(c)
    hi_all, lo_all = e.swings(c, k)
    fv_all = e.fvgs(c)
    ob_all = e.order_blocks(c, k)
    sw_all = e.liquidity_sweeps(c, k)

    fv_bull = [f for f in fv_all if f["dir"] == "bull"]
    fv_bear = [f for f in fv_all if f["dir"] == "bear"]
    ob_bull = [o for o in ob_all if o["dir"] == "bull"]
    ob_bear = [o for o in ob_all if o["dir"] == "bear"]
    sw_bull = [s for s in sw_all if s["dir"] == "bull"]
    sw_bear = [s for s in sw_all if s["dir"] == "bear"]

    rows = []
    p = dict(hi=0, lo=0, fvb=0, fvr=0, obb=0, obr=0, swb=0, swr=0)
    last_bos_dir = None
    # separate pointer tracking "confirmed swings within the external-
    # liquidity lookback window", advanced independently so it doesn't
    # regrow to the full swing list every bar.
    ext_hi_start = 0
    ext_lo_start = 0

    for t in range(n):
        # swings() returns the CENTER bar of each pivot, not the bar where
        # it becomes knowable — confirming a pivot needs k bars *after* it
        # (that's the whole point of k). smc_engine.confirmed_before() gates
        # on `center + k <= idx`; using `center <= t` here would let a swing
        # become "visible" k bars before it's actually confirmable — a
        # genuine look-ahead bug caught by test_choch_flags_reversal_after_
        # established_bos_direction (a swing low appeared to fire before its
        # own k-bar confirmation window had elapsed).
        while p["hi"] < len(hi_all) and hi_all[p["hi"]][0] + k <= t: p["hi"] += 1
        while p["lo"] < len(lo_all) and lo_all[p["lo"]][0] + k <= t: p["lo"] += 1
        while p["fvb"] < len(fv_bull) and fv_bull[p["fvb"]]["i"] <= t: p["fvb"] += 1
        while p["fvr"] < len(fv_bear) and fv_bear[p["fvr"]]["i"] <= t: p["fvr"] += 1
        while p["obb"] < len(ob_bull) and ob_bull[p["obb"]]["i"] <= t: p["obb"] += 1
        while p["obr"] < len(ob_bear) and ob_bear[p["obr"]]["i"] <= t: p["obr"] += 1
        while p["swb"] < len(sw_bull) and sw_bull[p["swb"]]["i"] <= t: p["swb"] += 1
        while p["swr"] < len(sw_bear) and sw_bear[p["swr"]]["i"] <= t: p["swr"] += 1

        # trend() only ever looks at the last two entries — pass a 2-element
        # view, not the full (growing) confirmed-so-far list. Slicing
        # hi_all[:p["hi"]] every bar copies an ever-larger list on every
        # iteration (same class of bug as _nearest_active's original scan).
        hi_last2, lo_last2 = hi_all[max(0, p["hi"] - 2):p["hi"]], lo_all[max(0, p["lo"] - 2):p["lo"]]
        trend = e.trend(hi_last2, lo_last2)

        hi_last = hi_all[p["hi"] - 1] if p["hi"] else None      # (index, price)
        lo_last = lo_all[p["lo"] - 1] if p["lo"] else None

        # BOS: close beyond the last confirmed swing extreme — the same
        # test order_blocks() uses internally before walking back to the
        # anchor candle, exposed here as its own reusable signal.
        bos_dir = None
        if hi_last and c[t]["close"] > hi_last[1]:
            bos_dir = "bull"
        elif lo_last and c[t]["close"] < lo_last[1]:
            bos_dir = "bear"
        # CHoCH: the first BOS against the prevailing BOS direction is a
        # character change; a same-direction BOS is continuation. Standard
        # definition, not previously a first-class primitive anywhere in
        # this codebase (reports/quant_research_audit.md Sec 6).
        choch = bos_dir is not None and last_bos_dir is not None and bos_dir != last_bos_dir
        if bos_dir is not None:
            last_bos_dir = bos_dir

        # external liquidity: dealing-range extremity within a bounded
        # lookback (mirrors signal_v35._e3_trigger's definition exactly,
        # generalized to any timeframe/window here). ext_*_start advances
        # against hi_all/lo_all directly — never against a copied slice —
        # so the [ext_start:ptr] view stays bounded by the lookback window,
        # not by total history.
        while ext_hi_start < p["hi"] and hi_all[ext_hi_start][0] < t - EXTERNAL_LIQUIDITY_LOOKBACK:
            ext_hi_start += 1
        while ext_lo_start < p["lo"] and lo_all[ext_lo_start][0] < t - EXTERNAL_LIQUIDITY_LOOKBACK:
            ext_lo_start += 1
        external_high = max((p_ for _, p_ in hi_all[ext_hi_start:p["hi"]]), default=None)
        external_low = min((p_ for _, p_ in lo_all[ext_lo_start:p["lo"]]), default=None)
        # internal liquidity (inducement): the most recent confirmed swing,
        # full stop — same proxy as smc_engine.inducement(), computed here
        # from the pointers already advanced instead of a redundant call.
        internal_high = hi_last[1] if hi_last else None
        internal_low = lo_last[1] if lo_last else None

        nearest_fvg_bull = _nearest_active(fv_bull, p["fvb"], t)
        nearest_fvg_bear = _nearest_active(fv_bear, p["fvr"], t)
        nearest_ob_bull = _nearest_active(ob_bull, p["obb"], t, lookback=poi_max_age)
        nearest_ob_bear = _nearest_active(ob_bear, p["obr"], t, lookback=poi_max_age)

        ob_bull_status = (e.mitigation_status(c, nearest_ob_bull["i"], nearest_ob_bull["low"],
                          nearest_ob_bull["high"], "bull", upto_i=t) if nearest_ob_bull else None)
        ob_bear_status = (e.mitigation_status(c, nearest_ob_bear["i"], nearest_ob_bear["low"],
                          nearest_ob_bear["high"], "bear", upto_i=t) if nearest_ob_bear else None)

        atr_v = e.atr(c, t, atr_period)
        eq, pd_hi, pd_lo = e.equilibrium(c, t, pd_window)
        px = c[t]["close"]
        pd_zone = "PREMIUM" if px > eq else ("DISCOUNT" if px < eq else "EQUILIBRIUM")
        rng = c[t]["high"] - c[t]["low"]
        ts = c[t]["time"]

        rows.append({
            "i": t, "time": ts,
            "swing_high": internal_high,
            "swing_low": internal_low,
            "trend": trend,
            "bos_dir": bos_dir, "choch": choch,
            "sweep_bull": bool(p["swb"] and sw_bull[p["swb"] - 1]["i"] == t),
            "sweep_bear": bool(p["swr"] and sw_bear[p["swr"] - 1]["i"] == t),
            "external_liquidity_high": external_high, "external_liquidity_low": external_low,
            "internal_liquidity_high": internal_high, "internal_liquidity_low": internal_low,
            "ob_bull_zone": [nearest_ob_bull["low"], nearest_ob_bull["high"]] if nearest_ob_bull else None,
            "ob_bull_status": ob_bull_status,
            "ob_bear_zone": [nearest_ob_bear["low"], nearest_ob_bear["high"]] if nearest_ob_bear else None,
            "ob_bear_status": ob_bear_status,
            "fvg_bull_zone": [nearest_fvg_bull["lower"], nearest_fvg_bull["upper"]] if nearest_fvg_bull else None,
            "fvg_bear_zone": [nearest_fvg_bear["lower"], nearest_fvg_bear["upper"]] if nearest_fvg_bear else None,
            "premium_discount": pd_zone, "equilibrium": round(eq, 6),
            "atr": round(atr_v, 6), "range": round(rng, 6),
            "session": session_of(ts), "day_of_week": day_of_week(ts), "hour": int(ts[11:13]),
        })
    return rows


FIELDNAMES = ["i", "time", "swing_high", "swing_low", "trend", "bos_dir", "choch",
              "sweep_bull", "sweep_bear", "external_liquidity_high", "external_liquidity_low",
              "internal_liquidity_high", "internal_liquidity_low",
              "ob_bull_zone", "ob_bull_status", "ob_bear_zone", "ob_bear_status",
              "fvg_bull_zone", "fvg_bear_zone", "premium_discount", "equilibrium",
              "atr", "range", "session", "day_of_week", "hour"]


def write_features_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--candles", required=True)
    ap.add_argument("--tf", default="M5")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    c = e.load_candles(a.candles)
    rows = compute_features(c)
    out = a.out or f"data/features_{a.symbol}_{a.tf}.csv"
    write_features_csv(rows, out)
    print(f"wrote {out} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
