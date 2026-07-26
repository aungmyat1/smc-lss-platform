# RCR-ST-C3-v1.0.5 — Revision Report

**Type:** Owner decisions (structural-detection algorithm parameters),
each chosen from an empirically-researched tradeoff curve. Not a
research/backtest RCR under `docs/RESEARCH-CHARTER.md` in its own right —
the research itself was already performed and reported in
`R27_R30_RESEARCH_REPORT.md`; this RCR only records the owner's picks from
that report's curves.
**From:** `specs/st-c3_v1.0.4.yaml` **To:** `specs/st-c3_v1.0.5.yaml`
**Date:** 2026-07-26

---

## Why

`R18_DETECTION_GAP_REPORT.md` found that four structural-detection
*algorithm* parameters (distinct from the R-01–R-26 filter thresholds
already frozen) had never been defined anywhere: swing/fractal lookback
(R-27), BOS confirmation bars (R-28), FVG minimum gap-size / OB
candle-selection (R-29), and pullback definition (R-30).
`R27_R30_RESEARCH_REPORT.md` then ran empirical distribution analysis
against real GBPUSD H4/M15 data to produce tradeoff curves/candidate
ranges for each (plus a depth-filtered follow-up for R-30, and a
correction retracting an earlier overclaim that R-28 needed
reformulation). The owner then picked a specific value from each curve.

## The decisions

| Field | Value | Chosen from (R27_R30_RESEARCH_REPORT.md) |
|---|---|---|
| R-27 swing/fractal lookback `k` | **2** | k=1..5 tradeoff curve (responsiveness vs. confirmation delay) |
| R-28 BOS confirmation bars `N` | **2** | N=0..5 tradeoff curve (0%->40% false-BOS rejection rate); rejects ~25% of raw body-close breaks as whipsaws |
| R-29 FVG minimum gap-size (FVG half only) | **0.15x MF_ATR(1)** | 0.1-0.3x candidate range (75.2%/38.5% H4 pass-rate at 0.1x/0.3x) |
| R-30 pullback depth | **0.30x ATR(1)** | depth-filtered 0.1-1.0x ATR(1) tradeoff curve (86.3% reach-rate within 40 bars, median 2 bars) |

R-29's OB (order-block) half required no new number — `smc_engine.
order_blocks()` already implements a deterministic candle-selection rule
("last opposing candle before a confirmed-swing break"), a structural
definition rather than a missing threshold.

## Verification performed before folding in

- Confirmed all four values fall within the empirically-researched ranges
  `R27_R30_RESEARCH_REPORT.md` actually produced — no value outside what
  was measured.
- Confirmed R-27's k=2 is an independently-made owner decision, not an
  inheritance of ST-C2's own swing-detection parameter, even though it
  happens to numerically match `smc_engine.swings()`'s documented default
  (ADR-0004 requires independent decision, not that the number itself must
  differ from any other candidate's).
- No new spec sections, evidence objects, states, transitions, or
  rejection/termination codes were touched — all four values were added as
  new fields within their existing owning pipeline stages
  (`htf_bias_stage`, `displacement_bos_stage`, `fvg_ob_confluence_stage`).

## What changed in `specs/st-c3_v1.0.5.yaml`

- `pipeline.htf_bias_stage.swing_fractal_lookback_k: 2` (new field)
- `pipeline.displacement_bos_stage.bos_confirmation_bars: 2` (new field)
- `pipeline.displacement_bos_stage.pullback_depth_atr_multiplier: 0.30` (new field)
- `pipeline.fvg_ob_confluence_stage.fvg_min_gap_atr_multiplier: 0.15` (new field)

Nothing else changed — no evidence object, state, transition, guard,
rejection/termination code, or other spec field.

## What did NOT happen

- No detection-module code was written. These are spec-text values only;
  `validation/st_c3/kernel.py` still consumes pre-built `Evidence` objects,
  not raw candles.
- No execution, optimization, backtesting, demo, live, or A3 logic added.
- R-18 (`existence_check_floor`) is **not** resolved by this revision — see
  Next Steps.

## Updated governance state

**All R-01 through R-30 tracked fields are now decided except R-18.** R-18
(`existence_check_floor`) needs real detection-module code plus a data
run, not a further spec decision — it is the sole remaining open item on
the entire tracker. No field remains `PENDING`/`DEFERRED` for a spec-value
reason.

## Deliverables

- `specs/st-c3_v1.0.5.yaml`.
- `reports/validation/st_c3/OWNER_DECISION_LOG.md` — R-27–R-30 rows marked
  `APPROVED`, status summary updated.
- `reports/validation/st_c3/RESOLUTION_MATRIX.md` — R-27–R-30 rows and
  priority summary updated to `Resolved`.
- `governance/st_c3_stage_status.yaml` — `spec`/`version` bumped to v1.0.5,
  `v1_0_5_revision` metadata block added, `reference_funnel.
  existence_check_r18` updated to `blocked_on_implementation_only`.
- `docs/strategy/st_c3/ST-C3_CHANGELOG.md` — v1.0.5 entry added.
- `validation/st_c3/evidence.py` — `SPEC_PATH` repointed to
  `specs/st-c3_v1.0.5.yaml`; `tests/st_c3/` re-verified passing (unaffected,
  as expected — these are spec-text values with no kernel consumer yet).
- This report.

## Next steps

R-18 is the only field left on the entire R-01–R-30 tracker, and it now
requires pure engineering, not further governance: build real price-level
detection modules (reusing `smc_engine.swings()`/`fvgs()`/`atr()`/
`order_blocks()` per the research precedent, now parameterized with
k=2/N=2/0.15x/0.30x plus the R-04..R-09 filter thresholds already frozen),
wire them into `validation/st_c3/kernel.py`'s `EvidenceBundle` construction,
and run the result over real GBPUSD/EURUSD candle data via
`tools/existence_check.py` + `tools/power_planning.py` to compute an actual
signal-rate number. This remains within the existing A2/S1-G2 scoped
authorization (`reference_funnel_assembly`, `existence_check_conformance_run`)
— no new authorization is granted or required by this revision, and
execution/optimization/demo/live/A3 remain exactly as blocked as before.
