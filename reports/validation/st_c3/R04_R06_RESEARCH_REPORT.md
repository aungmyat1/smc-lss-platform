# R-04 / R-06 Research Report — Wick Ratio & Sweep Age Distributions

**Instrument/timeframe:** GBPUSD M15 (chosen because it's the only one of
the three R-02 instruments with both M15/MF and M3/LTF data available;
EURUSD lacks M3, XAUUSD lacks M15/H4 entirely — see `data/` directory).
**Script:** `scripts/research_r04_r06_gbpusd_m15.py` (reproducible; reuses
the existing, cross-candidate `smc_engine.swings()` primitive already used
by ST-C1/ST-C2 research and `src/features.py` — no ST-C3-specific
detection logic was built to produce this).
**Method:** find every M15 bar that pierces a prior confirmed swing
high/low and reclaims (mirrors `smc_engine.liquidity_sweeps`'s pierce/
reclaim logic exactly), with **no wick-ratio threshold applied**, so the
resulting distribution isn't biased toward any candidate R-04 value.
Dataset: 30,000 M15 candles (~convert to date range: continuous M15 series
supplied in `data/GBPUSD_M15.csv`). 4,062 pierce+reclaim candidates found.

---

## Wick Ratio Distribution (informs R-04)

| Stat | All (n=4062) | Bull (n=2083) | Bear (n=1979) |
|---|---|---|---|
| min | 0.000 | 0.000 | 0.000 |
| p10 | 0.047 | 0.046 | 0.049 |
| p25 | 0.163 | 0.163 | 0.163 |
| p50 (median) | 0.333 | 0.341 | 0.324 |
| p75 | 0.525 | 0.534 | 0.516 |
| p90 | 0.686 | 0.697 | 0.674 |
| max | 0.983 | 0.983 | 0.976 |
| mean | 0.355 | 0.360 | 0.349 |

**Threshold pass-rates** (what fraction of naturally-occurring pierce+
reclaim candidates would still qualify as a "sweep" at each candidate
`wick_ratio_min`):

| Threshold | Candidates passing | % of all candidates |
|---|---|---|
| 0.3 | 2219 / 4062 | 54.6% |
| 0.4 | 1655 / 4062 | 40.7% |
| 0.5 | 1156 / 4062 | 28.5% |
| 0.6 | 711 / 4062 | 17.5% |
| 0.7 | 370 / 4062 | 9.1% |

**Reading:** the median pierce+reclaim candidate has a wick ratio of only
~0.33 — most naturally-occurring sweep-like events have a *smaller* wick
component than 0.5. This matrix's originally proposed 0.5–0.7 range (citing
`specs/st-c2_v1.2.0.yaml:104`'s 0.6 as a reference point) would exclude the
majority of candidates (71.5%–90.9% excluded at 0.5–0.7), consistent with a
deliberately *selective* sweep definition, not an inclusive one — this
matches SMC convention that a "real" sweep should show a decisive wick, not
just any pierce-and-reclaim. Bull/bear distributions are close to
symmetric (no directional bias worth adjusting for).

## Sweep Age Distribution (informs R-06)

| Stat | Value (bars) |
|---|---|
| min | 3 |
| p10 | 3 |
| p25 | 4 |
| p50 (median) | 6 |
| p75 | 8 |
| p90 | 11 |
| max | 26 |
| mean | 6.39 |

**Cap pass-rates:**

| Cap (bars) | Candidates passing | % of all candidates |
|---|---|---|
| 10 | 3638 / 4062 | 89.6% |
| 20 | 4056 / 4062 | 99.9% |
| 30 | 4062 / 4062 | 100.0% |
| 40 | 4062 / 4062 | 100.0% |
| 60 | 4062 / 4062 | 100.0% |
| 100 | 4062 / 4062 | 100.0% |

**Reading:** the observed maximum age in this dataset is only 26 bars.
This matrix's originally proposed 20–60 range is far looser than the data
supports — anything at or above ~30 bars is **non-binding** on this
dataset (100% of candidates already qualify), meaning R-06 would do no
actual filtering work at those values. If a genuinely restrictive
"recency" requirement is wanted, the data suggests something in the
10–15 bar range (89.6% pass at 10 bars — i.e., a ~10% tightening effect),
not 20–60.

---

## What This Report Does NOT Do

- Does not pick a final value for R-04 or R-06 — that remains an owner
  decision, informed by this data, not derived from it automatically (a
  "selective sweep" philosophy and an "inclusive sweep" philosophy are both
  defensible; the data shows what each choice would actually filter, not
  which philosophy is correct).
- Does not touch any other funnel stage — no HTF bias, displacement, OTE,
  FVG/OB confluence, LTF confirmation, or risk/SL/TP logic was built or run.
- Does not constitute an ST-C3 reference implementation. `swings()` is a
  generic primitive already shared across ST-C1/ST-C2 research; nothing
  ST-C3-specific (its own evidence objects, state machine, or rejection
  codes) was implemented.

## Recommendation to Owner

Given the data:
- **R-04:** if the intent is a "decisive wick" sweep definition (matching
  the originally-cited ST-C2 reference point), 0.5 or 0.6 remain reasonable
  choices — 0.5 keeps ~28.5% of naturally-occurring candidates, 0.6 keeps
  ~17.5%. If a more inclusive definition is preferred, 0.3–0.4 would keep
  more (54.6%/40.7%).
- **R-06:** the originally proposed 20–60 range should likely be
  reconsidered — values above ~25-30 do no filtering at all on this data.
  If a real constraint is wanted, 10–15 bars would meaningfully bind
  (89.6% pass at 10 bars); if the intent was just a generous safety cap
  that's not meant to bind often, a smaller number like 20 (99.9% pass,
  effectively a rare-edge-case-only filter) may be exactly what was
  intended — this is a values question this report can't resolve.

## R-03 and R-18 — Not Researched This Pass

- **R-03 (`sessions.low_liquidity_filters`):** no objective "low-liquidity
  signature" has been defined yet — before any scan is meaningful, an
  explicit criterion is needed (e.g. average M15 range below some
  percentile, by session/hour). Not attempted here; this matrix's original
  proposed default (`disabled_by_default`) remains available as a
  zero-research starting point if preferred over building that criterion.
- **R-18 (`existence_check_floor`):** requires a working signal function
  across the entire ST-C3 funnel (HTF bias, sweep, displacement, OTE,
  FVG/OB confluence, LTF confirmation, session, entry window, risk/SL/TP)
  to run `tools/existence_check.py` meaningfully. Assembling that now would
  be building the ST-C3 reference kernel itself — exactly what A2/S1-G2
  gates, which remains not opened. Not attempted; held pending that
  decision.
