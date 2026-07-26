#!/usr/bin/env python3
"""Research pass for R-27 (swing/fractal lookback), R-28 (BOS confirmation
bars), R-29 (FVG min gap-size), and R-30 (pullback definition).

Reuses the already-existing, cross-candidate `swings()`, `fvgs()`, and
`atr()` primitives from `src/smc_engine.py` (used by ST-C1/ST-C2 research
and `src/features.py` today). No ST-C3-specific detection logic is built:
every measurement below is descriptive statistics over structural events
these generic functions already produce, with no threshold applied unless
explicitly noted, mirroring `scripts/research_r04_r06_gbpusd_m15.py`'s
discipline exactly.

Runs on GBPUSD only: EURUSD_H4.csv/EURUSD_M15.csv exist but have only
19-21 rows (not enough for distribution research); GBPUSD_H4.csv (5,000
rows) and GBPUSD_M15.csv (30,000 rows) have real depth. XAUUSD is excluded
per R-02's revision.

Usage: python scripts/research_r27_r30_gbpusd.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from smc_engine import atr, fvgs, load_candles, swings  # noqa: E402

H4_PATH = ROOT / "data" / "GBPUSD_H4.csv"
M15_PATH = ROOT / "data" / "GBPUSD_M15.csv"


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


def bars_between(indices):
    return [b - a for a, b in zip(indices, indices[1:])]


# ---------------------------------------------------------------------
# R-27: swing/fractal lookback k
# ---------------------------------------------------------------------
def research_r27(h4):
    print("=" * 70)
    print("R-27 — HTF swing/fractal lookback (k), GBPUSD H4")
    print("=" * 70)
    for k in (1, 2, 3, 4, 5):
        hi, lo = swings(h4, k=k)
        hi_idx = [i for i, _ in hi]
        lo_idx = [i for i, _ in lo]
        all_idx = sorted(hi_idx + lo_idx)
        gaps = bars_between(all_idx)
        print(f"\nk={k}: {len(hi)} swing highs, {len(lo)} swing lows "
              f"({len(all_idx)} total over {len(h4)} bars)")
        if gaps:
            summarize(f"  bars-between-swings (k={k})", gaps)


# ---------------------------------------------------------------------
# Shared: confirmed-swing body-close breaks (BOS candidates), no
# confirmation delay applied — feeds both R-28 and R-30.
# ---------------------------------------------------------------------
def find_bos_candidates(c, k):
    hi_all, lo_all = swings(c, k=k)
    hi_ptr, lo_ptr = 0, 0
    n_hi, n_lo = len(hi_all), len(lo_all)
    out = []
    for i in range(k + 1, len(c)):
        while hi_ptr < n_hi and hi_all[hi_ptr][0] + k <= i:
            hi_ptr += 1
        while lo_ptr < n_lo and lo_all[lo_ptr][0] + k <= i:
            lo_ptr += 1
        hi_last = hi_all[hi_ptr - 1][1] if hi_ptr else None
        lo_last = lo_all[lo_ptr - 1][1] if lo_ptr else None
        close = c[i]["close"]
        if hi_last is not None and close > hi_last:
            out.append({"i": i, "dir": "bull", "level": hi_last})
        elif lo_last is not None and close < lo_last:
            out.append({"i": i, "dir": "bear", "level": lo_last})
    return out


# ---------------------------------------------------------------------
# R-28: BOS confirmation-bar rule
# ---------------------------------------------------------------------
def research_r28(m15, k=2):
    print("\n" + "=" * 70)
    print(f"R-28 — BOS confirmation-bar rule, GBPUSD M15 (swings k={k})")
    print("=" * 70)
    bos = find_bos_candidates(m15, k)
    print(f"\n{len(bos)} raw body-close BOS candidates (no confirmation delay applied)")

    for n in (0, 1, 2, 3, 5):
        invalidated = 0
        for ev in bos:
            i, direction, level = ev["i"], ev["dir"], ev["level"]
            for j in range(i + 1, min(i + 1 + n, len(m15))):
                close = m15[j]["close"]
                if (direction == "bull" and close < level) or (direction == "bear" and close > level):
                    invalidated += 1
                    break
        rate = 100.0 * invalidated / len(bos) if bos else 0.0
        print(f"  confirmation_bars={n}: {invalidated}/{len(bos)} BOS candidates "
              f"re-close on the wrong side within {n} bars ({rate:.1f}% whipsaw rate)")


# ---------------------------------------------------------------------
# R-29: FVG minimum gap-size
# ---------------------------------------------------------------------
def research_r29(h4, m15):
    print("\n" + "=" * 70)
    print("R-29 — FVG minimum gap-size (OB candle-selection already has a")
    print("       reusable deterministic rule via smc_engine.order_blocks(),")
    print("       no threshold needed there beyond R-23/R-24 freshness)")
    print("=" * 70)
    for label, c in (("H4", h4), ("M15", m15)):
        gaps = fvgs(c, min_gap=0.0)
        sizes = [g["upper"] - g["lower"] for g in gaps]
        print(f"\n{label}: {len(gaps)} raw 3-candle FVGs (no min-gap filter)")
        summarize(f"  gap size, absolute price ({label})", sizes)
        atr_relative = []
        for g in gaps:
            i = g["i"]
            a = atr(c, max(0, i - 1), n=1)
            if a > 0:
                atr_relative.append((g["upper"] - g["lower"]) / a)
        summarize(f"  gap size, in MF_ATR(1) units ({label})", atr_relative)
        if atr_relative:
            print(f"  --- {label} pass-rate at candidate ATR(1)-multiple thresholds ---")
            for threshold in (0.0, 0.05, 0.1, 0.2, 0.3, 0.5):
                kept = sum(1 for v in atr_relative if v >= threshold)
                pct = 100.0 * kept / len(atr_relative)
                print(f"    threshold={threshold}: {kept}/{len(atr_relative)} pass ({pct:.1f}%)")


# ---------------------------------------------------------------------
# R-30: pullback definition (bars-until and depth, following a BOS)
# ---------------------------------------------------------------------
def research_r30(m15, k=2):
    print("\n" + "=" * 70)
    print(f"R-30 — Pullback definition following BOS, GBPUSD M15 (swings k={k})")
    print("=" * 70)
    bos = find_bos_candidates(m15, k)
    bars_until = []
    depth_atr = []
    for ev in bos:
        i, direction = ev["i"], ev["dir"]
        bos_close = m15[i]["close"]
        a = atr(m15, i, n=1)
        for j in range(i + 1, min(i + 20, len(m15))):
            close = m15[j]["close"]
            is_pullback = (direction == "bull" and close < m15[j - 1]["close"]) or (
                direction == "bear" and close > m15[j - 1]["close"]
            )
            if is_pullback:
                bars_until.append(j - i)
                if a > 0:
                    depth = (bos_close - close) if direction == "bull" else (close - bos_close)
                    depth_atr.append(depth / a)
                break
    print(f"\n{len(bos)} BOS candidates, {len(bars_until)} with a first-opposite-close "
          f"pullback found within 20 bars")
    summarize("  bars until first pullback close", bars_until)
    summarize("  pullback depth, in ATR(1) units (negative = still favorable)", depth_atr)


# ---------------------------------------------------------------------
# R-30 follow-up: depth-filtered pullback definition. Requires the
# retracement to reach a minimum depth (in ATR(1) units) against the BOS
# direction, not just any single opposite-direction close.
# ---------------------------------------------------------------------
def research_r30_depth_filtered(m15, k=2, window=40):
    print("\n" + "=" * 70)
    print(f"R-30 follow-up — depth-filtered pullback, GBPUSD M15 (swings k={k})")
    print("=" * 70)
    bos = find_bos_candidates(m15, k)
    # exclude degenerate near-zero-ATR bars, flagged as a data-quality issue
    # in the first pass, from skewing this follow-up
    min_atr = 1e-6
    for threshold in (0.1, 0.2, 0.3, 0.5, 0.75, 1.0):
        bars_until = []
        found = 0
        for ev in bos:
            i, direction = ev["i"], ev["dir"]
            bos_close = m15[i]["close"]
            a = atr(m15, i, n=1)
            if a <= min_atr:
                continue
            for j in range(i + 1, min(i + window, len(m15))):
                close = m15[j]["close"]
                depth = (bos_close - close) if direction == "bull" else (close - bos_close)
                if depth / a >= threshold:
                    bars_until.append(j - i)
                    found += 1
                    break
        rate = 100.0 * found / len(bos) if bos else 0.0
        print(f"\ndepth_threshold={threshold} x ATR(1): {found}/{len(bos)} BOS candidates "
              f"reach this depth within {window} bars ({rate:.1f}%)")
        if bars_until:
            summarize(f"  bars until depth={threshold} reached", bars_until)


def main():
    h4 = load_candles(str(H4_PATH))
    m15 = load_candles(str(M15_PATH))
    print(f"Loaded {len(h4)} GBPUSD H4 candles from {H4_PATH}")
    print(f"Loaded {len(m15)} GBPUSD M15 candles from {M15_PATH}")

    research_r27(h4)
    research_r28(m15)
    research_r29(h4, m15)
    research_r30(m15)
    research_r30_depth_filtered(m15)


if __name__ == "__main__":
    main()
