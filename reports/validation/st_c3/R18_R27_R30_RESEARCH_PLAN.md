# R-18 / R-27–R-30 Detection-Research Plan

**Status:** Pending — no data collection or analysis has been run yet. This
is a plan stub, committing to nothing. No numeric value in this file is
proposed or decided.

---

## Scope

Empirical distribution analysis to generate **candidate** (not final)
numeric definitions for the four structural-detection gaps found while
attempting to begin real R-18 price-level detection work — see
`R18_DETECTION_GAP_REPORT.md`:

- **R-27** — HTF swing/fractal lookback (`htf_bias_stage.structure_source`)
- **R-28** — BOS confirmation-bar rule (`displacement_bos_stage.bos_confirmation_rule`)
- **R-29** — FVG minimum gap-size / OB candle-selection rule (`fvg_ob_confluence_stage`)
- **R-30** — Pullback definition (`bos_extreme_lock_policy: lock_after_first_pullback`)

Any candidate value this research produces still requires explicit owner
ratification in `OWNER_DECISION_LOG.md` before it may enter a frozen spec —
same process as R-04/R-06 (`R04_R06_RESEARCH_REPORT.md`), which is the
precedent this plan follows.

## Data

**Instruments/timeframes:** GBPUSD H4/M15 — at ST-C3's actual HTF/MF
timeframe stack (`timeframes.htf: H4`, `timeframes.mf: M15` in
`specs/st-c3_v1.0.4.yaml`; H1 does not appear anywhere in ST-C3 and is not
part of this plan). **Correction after checking row counts:**
`data/EURUSD_H4.csv`/`EURUSD_M15.csv` exist but contain only 19/21 rows —
not enough for distribution research. `data/GBPUSD_H4.csv` (5,000 rows) and
`data/GBPUSD_M15.csv` (30,000 rows) have real depth. This pass therefore
runs on GBPUSD only, matching `R04_R06_RESEARCH_REPORT.md`'s own precedent
and stated reason exactly. LTF (M3/M1) data is not needed for R-27–R-30 —
all four gaps live at the HTF/MF level (`HTFBiasEvidence` is H4-only;
`BOSEvidence`/`BOSExtremeEvidence`/`DisplacementEvidence` are M15-only;
`FVGEvidence`/`OrderBlockEvidence` are H4+M15).

## Method (per gap, mirrors R04_R06_RESEARCH_REPORT.md's approach)

- **R-27 (swing/fractal lookback):** for a range of candidate fractal-`k`
  values, measure how many swing points each produces on H4 and how
  stable/non-repainting they are, using the existing cross-candidate
  `src.smc_engine.swings()` primitive — no ST-C3-specific detection logic
  invented, same reuse discipline as R04/R06.
- **R-28 (BOS confirmation bars):** for a range of candidate confirmation-bar
  counts, measure the resulting BOS event rate and false-positive rate
  (BOS events that reverse within N bars) on M15.
  distribution, using confirmed swings as the break-level source.
- **R-29 (FVG/OB definition):** measure the natural size distribution of
  3-candle imbalances (FVGs) and order-block candidate candles on H4/M15,
  with no minimum-gap filter applied, so the resulting distribution isn't
  biased toward any candidate threshold (same "no threshold applied yet"
  discipline R04/R06 used for wick ratio).
- **R-30 (pullback definition):** measure the natural distribution of
  "first opposite-direction close" bar counts following a BOS on M15, to
  characterize what "first pullback" could mean numerically.

## Output

A `R27_R30_RESEARCH_REPORT.md` (naming to follow `R04_R06_RESEARCH_REPORT.md`'s
precedent) presenting each distribution plus pass-rate tables at several
candidate thresholds — not a single recommended number, so the owner's
ratification is an informed choice among real trade-offs, not a rubber
stamp.

## Governance status

Recorded in `OWNER_DECISION_LOG.md`: R-27–R-30 are proceeding via the
empirical-research path; no numeric values are proposed yet; awaiting
data-driven candidate generation, then owner ratification.
