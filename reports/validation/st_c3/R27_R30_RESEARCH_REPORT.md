# R-27 / R-28 / R-29 / R-30 Research Report — Detection-Algorithm Distributions

**Status:** empirical-research output — pending owner ratification. Nothing
here is decided; every number below is a descriptive statistic, not a
proposed final value, following `R04_R06_RESEARCH_REPORT.md`'s precedent
exactly.

**Instrument/timeframe:** GBPUSD H4/M15 only.
`data/EURUSD_H4.csv`/`EURUSD_M15.csv` exist but contain only 19/21 rows —
not enough for distribution research. XAUUSD is excluded per R-02's
revision. This matches `R04_R06_RESEARCH_REPORT.md`'s own stated reason for
using GBPUSD.

**Script:** `scripts/research_r27_r30_gbpusd.py` (reproducible; reuses the
existing, cross-candidate `smc_engine.swings()`, `smc_engine.fvgs()`, and
`smc_engine.atr()` primitives already used by ST-C1/ST-C2 research and
`src/features.py` — no ST-C3-specific detection logic was built to produce
this report).

**Dataset:** 5,000 GBPUSD H4 candles, 30,000 GBPUSD M15 candles.

---

## R-27 — HTF Swing/Fractal Lookback (k)

Swing count and spacing on H4, for each candidate fractal lookback `k`
(`smc_engine.swings(c, k)`, unbiased — no filtering applied):

| k | Swing highs | Swing lows | Total swings | Median bars-between-swings | p90 bars-between-swings |
|---|---|---|---|---|---|
| 1 | 1109 | 1234 | 2343 | 2 | 4 |
| 2 | 703 | 676 | 1379 | 3 | 6 |
| 3 | 528 | 513 | 1041 | 5 | 8 |
| 4 | 406 | 395 | 801 | 6 | 12 |
| 5 | 316 | 312 | 628 | 7 | 14 |

**Reading:** larger `k` produces fewer, more widely-spaced (more
"significant") swing points at the cost of a longer confirmation delay
(a swing at `k=5` isn't confirmed until 5 bars after it forms, vs. 1 bar at
`k=1`). `k=2` — the value `scripts/research_r04_r06_gbpusd_m15.py` used as
its own sweep-candidate-generation input, and `smc_engine.swings()`'s
documented default — sits in the middle: 1,379 swings over 5,000 H4 bars
(roughly one every 3.6 bars), a similar swing frequency to what ST-C2 (a
different lineage, cited for scale only) treats as structurally meaningful.
This distribution does not by itself argue for any one value; it is the
tradeoff curve for the owner to pick a point on (responsiveness vs.
confirmation delay), same framing as R-04's wick-ratio tradeoff.

## R-28 — BOS Confirmation-Bar Rule

Using `k=2` swings as the break-level source (10,417 raw body-close BOS
candidates on M15, no confirmation delay applied), the whipsaw rate — how
often a BOS candidate's price re-closes back on the wrong side of the
broken level within N bars of the break:

| Confirmation bars (N) | Whipsaws | Whipsaw rate |
|---|---|---|
| 0 | 0 / 10417 | 0.0% |
| 1 | 1657 / 10417 | 15.9% |
| 2 | 2600 / 10417 | 25.0% |
| 3 | 3267 / 10417 | 31.4% |
| 5 | 4164 / 10417 | 40.0% |

**Reading:** this is an unusual monotonic climb — waiting *longer* after a
body-close break makes the measured "whipsaw rate" go *up*, not down,
because this metric counts any later reversal of the break level, not just
an immediate failed break. It shows that a large fraction of body-close
breaks get revisited/reversed within a few bars regardless of confirmation
window (consistent with GBPUSD M15 being a fairly choppy series at this
raw signal density — 10,417 BOS candidates over 30,000 bars is a very high
hit rate with no other filter applied). This suggests confirmation-bar
count alone is a weak filter here; a "confirmation bars" rule based purely
on holding through N bars would need a different formulation (e.g.
requiring the break to *survive* N bars without closing back, which is a
narrower, more standard definition) than this straightforward "reversed at
any point after N bars" measurement — flagging this as a modeling
ambiguity for the owner/whoever finalizes R-28's exact guard formulation,
not resolving it here.

## R-29 — FVG Minimum Gap-Size

Raw 3-candle FVGs (`smc_engine.fvgs(c, min_gap=0.0)`, no filter), gap size
measured both in absolute price and in `MF_ATR(1)` units (reusing the same
ATR(1) unit convention R-05/R-07/R-08 already use):

| Timeframe | Raw FVGs | Median gap (ATR(1) units) | p90 (ATR(1) units) |
|---|---|---|---|
| H4 | 1031 | 0.233 | 0.554 |
| M15 | 6571 | 0.250 | 0.595 |

Pass-rate at candidate ATR(1)-multiple thresholds:

| Threshold (x ATR(1)) | H4 pass-rate | M15 pass-rate |
|---|---|---|
| 0.0 (no filter) | 100.0% | 100.0% |
| 0.05 | 88.2% | 91.0% |
| 0.1 | 75.2% | 80.7% |
| 0.2 | 55.2% | 60.1% |
| 0.3 | 38.5% | 42.0% |
| 0.5 | 14.9% | 17.0% |

**Reading:** H4 and M15 gap-size-in-ATR-units distributions are close to
each other (medians 0.233 vs 0.250), suggesting a single ATR(1)-relative
threshold could reasonably apply to both timeframes rather than needing
separate H4/M15 values. **Order-block candle selection does not need a new
threshold** — `smc_engine.order_blocks()` already implements a deterministic
"walk back to the last opposing-direction candle before the break" rule,
which is a structural definition, not a missing number; R-29 for the OB
half is effectively already answered by reusing that existing generic
primitive, leaving only the FVG minimum-gap-size choice for the owner.

## R-30 — Pullback Definition (for `BOS_EXTREME_LOCK`)

Following each of the 10,417 M15 BOS candidates (`k=2`), searching forward
up to 20 bars for the first bar whose close moves opposite the BOS
direction relative to the prior bar's close ("first pullback"):

| Metric | Value |
|---|---|
| BOS candidates with a pullback found within 20 bars | 10,417 / 10,417 (100%) |
| Median bars until first pullback | 1 |
| p90 bars until first pullback | 4 |
| Median pullback depth (ATR(1) units, + = against BOS direction) | 0.178 |
| p90 pullback depth (ATR(1) units) | 0.953 |

**Reading:** under this measurement, a "first pullback" (any single
opposite-direction close) shows up almost immediately (median 1 bar) after
essentially every BOS — consistent with normal bar-to-bar noise, not a
meaningful structural pullback. This is the same modeling-ambiguity issue
flagged in R-28: a literal "first opposite close" definition is too
permissive to be a useful gate (it would lock the BOS extreme on the very
next bar in the median case, regardless of whether any real retracement
happened). A depth-filtered variant (e.g. requiring the opposite move to
reach some ATR(1)-multiple, per the depth distribution above) would be a
more standard "pullback," but picking that threshold is an owner decision
this report doesn't make. One data-quality note: the depth distribution's
minimum (-18.24 ATR units) is an extreme outlier, likely from a bar where
the local ATR(1) was very small (near-zero true range) rather than a real
18-ATR pullback — worth excluding degenerate near-zero-ATR bars in any
follow-up analysis rather than treating that tail literally.

---

## Summary for owner ratification

None of R-27/R-28/R-29/R-30 is resolved by this report — each still needs
an explicit owner decision (or a further-refined research pass, per the
R-28/R-30 modeling-ambiguity notes above, before a clean number/threshold
can even be proposed with confidence). What this report establishes:

- **R-27**: a real tradeoff curve (responsiveness vs. confirmation delay)
  across `k=1..5`; no single value stands out as objectively correct.
- **R-28**: the straightforward "reversed at any point after N bars"
  framing doesn't produce a clean threshold — the guard likely needs a
  different formulation (e.g. "survives N bars without closing back")
  before a bar-count is chosen.
- **R-29**: OB candle-selection needs no new number (already a structural
  rule via `smc_engine.order_blocks()`); FVG minimum gap-size has a
  reasonable candidate range (0.1-0.3x `MF_ATR(1)`, 38-75% pass-rate) for
  the owner to pick from, consistent across H4/M15.
- **R-30**: the naive "first opposite close" pullback definition is too
  permissive to be structurally meaningful; a depth-filtered variant is
  recommended but not decided here.

No spec files were changed by this report. `specs/st-c3_v1.0.4.yaml`
remains frozen and validated as-is.
