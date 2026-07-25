#!/usr/bin/env python3
"""Research pass for R-04 (wick_ratio_min) and R-06 (max_sweep_age_bars).

Reuses the already-existing, cross-candidate `swings()` primitive from
`src/smc_engine.py` (used by ST-C1/ST-C2 research and `src/features.py`
today) to find sweep *candidates* — bars that pierce a prior confirmed
swing high/low and reclaim — with NO wick-ratio threshold applied, so the
resulting distribution is unbiased by any particular R-04 candidate value.

This is descriptive-statistics research to inform a spec-parameter
decision, not an ST-C3 reference implementation: it does not touch HTF
bias, displacement, OTE, FVG/OB confluence, LTF confirmation, or any other
ST-C3-specific funnel stage. It only answers "what does the wick-ratio and
sweep-age distribution look like for swing-piercing-and-reclaiming bars on
GBPUSD M15," independent of ST-C3's own detection logic.

Usage: python scripts/research_r04_r06_gbpusd_m15.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from smc_engine import load_candles, swings  # noqa: E402

CANDLES_PATH = ROOT / "data" / "GBPUSD_M15.csv"
K = 2  # swing confirmation lookback, matches smc_engine.swings default elsewhere


def find_sweep_candidates(c, k=K):
    """Bars that pierce a prior confirmed swing low/high and reclaim,
    regardless of wick ratio. Mirrors smc_engine.liquidity_sweeps' pierce/
    reclaim logic exactly, but with no min_wick_ratio filter, and also
    records `age` (bars between the swing's formation and the sweep).
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
            swing_idx, lvl = lo_all[lo_ptr - 1]
            lower_wick = body_lo - c[i]["low"]
            if c[i]["low"] < lvl and c[i]["close"] > lvl:
                out.append({
                    "i": i, "dir": "bull", "level": lvl,
                    "wick_ratio": lower_wick / rng,
                    "age_bars": i - swing_idx,
                })
        if hi_ptr:
            swing_idx, lvl = hi_all[hi_ptr - 1]
            upper_wick = c[i]["high"] - body_hi
            if c[i]["high"] > lvl and c[i]["close"] < lvl:
                out.append({
                    "i": i, "dir": "bear", "level": lvl,
                    "wick_ratio": upper_wick / rng,
                    "age_bars": i - swing_idx,
                })
    return out


def percentile(values, p):
    if not values:
        return None
    s = sorted(values)
    idx = int(round((p / 100.0) * (len(s) - 1)))
    return s[idx]


def summarize(label, values):
    if not values:
        print(f"{label}: no data")
        return
    values = sorted(values)
    print(f"{label} (n={len(values)}):")
    print(f"  min={values[0]:.4f}  p10={percentile(values,10):.4f}  "
          f"p25={percentile(values,25):.4f}  p50={percentile(values,50):.4f}  "
          f"p75={percentile(values,75):.4f}  p90={percentile(values,90):.4f}  "
          f"max={values[-1]:.4f}  mean={sum(values)/len(values):.4f}")


def main():
    c = load_candles(str(CANDLES_PATH))
    print(f"Loaded {len(c)} GBPUSD M15 candles from {CANDLES_PATH}")
    candidates = find_sweep_candidates(c)
    print(f"Found {len(candidates)} pierce+reclaim sweep candidates (no wick-ratio filter)\n")

    wick_ratios = [x["wick_ratio"] for x in candidates]
    ages = [x["age_bars"] for x in candidates]
    bull_wick = [x["wick_ratio"] for x in candidates if x["dir"] == "bull"]
    bear_wick = [x["wick_ratio"] for x in candidates if x["dir"] == "bear"]

    summarize("Wick ratio (all)", wick_ratios)
    summarize("Wick ratio (bull sweeps)", bull_wick)
    summarize("Wick ratio (bear sweeps)", bear_wick)
    print()
    summarize("Sweep age in bars (all)", ages)

    print("\n--- R-04 (wick_ratio_min) framing ---")
    for threshold in (0.3, 0.4, 0.5, 0.6, 0.7):
        kept = sum(1 for w in wick_ratios if w >= threshold)
        pct = 100.0 * kept / len(wick_ratios) if wick_ratios else 0.0
        print(f"  threshold={threshold}: {kept}/{len(wick_ratios)} candidates pass ({pct:.1f}%)")

    print("\n--- R-06 (max_sweep_age_bars) framing ---")
    for cap in (10, 20, 30, 40, 60, 100):
        kept = sum(1 for a in ages if a <= cap)
        pct = 100.0 * kept / len(ages) if ages else 0.0
        print(f"  cap={cap} bars: {kept}/{len(ages)} candidates pass ({pct:.1f}%)")


if __name__ == "__main__":
    main()
