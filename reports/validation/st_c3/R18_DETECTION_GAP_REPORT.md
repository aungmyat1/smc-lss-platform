# R-18 Detection Gap Report

**Date:** 2026-07-26
**Trigger:** attempted to begin real price-level SMC detection module work
toward R-18 (`existence_check_floor`), within the A2/S1-G2 scoped
authorization (`reference_funnel_assembly`).
**Outcome:** stopped before writing any detection code. No structural
parameters were invented.

---

## Finding

R-18 cannot proceed to real price-level detection yet, and this is a
different kind of gap from the `PROVISIONAL`/`UNRESOLVED` numeric fields
already tracked in `RESOLUTION_MATRIX.md`. Those fields (e.g.
`sweep_reclaim_max_bars`, `entry_window_bars`, OTE band) are *filter
thresholds* applied after a structural feature has already been identified.

The gap found here is one level lower: **the algorithms that identify the
underlying structural features in raw candle data were never specified with
any number, in the spec or anywhere in `OWNER_DECISION_LOG.md`.**
Specifically, checked against `specs/st-c3_v1.0.4.yaml` and confirmed absent
by grep across the spec and all `reports/validation/st_c3/*.md`:

| Missing parameter | Needed by | What ST-C3's spec actually says |
|---|---|---|
| Swing/fractal lookback (`k`) | `htf_bias_stage` (identifying HH/HL/LH/LL swing points) | `structure_source: hh_hl_lh_ll` — describes *what*, not *how many bars* confirm a swing |
| BOS confirmation-bar count | `displacement_bos_stage` (`bos_confirmation_rule: body_close_required`) | Says a body close breaks structure; no confirmation-bar count given |
| FVG minimum gap size | `fvg_ob_confluence_stage` (FVG detection) | No numeric floor for what counts as a gap |
| Order-block candle-selection rule | `fvg_ob_confluence_stage` (OB detection) | No rule for which candle qualifies as the order block |
| Pullback definition | `displacement_bos_stage.bos_extreme_lock_policy: lock_after_first_pullback` | "First pullback" has no numeric or structural definition |

By contrast, ST-C2's frozen spec (`specs/st-c2_v1.2.0.yaml`) explicitly
carries these same parameters (`htf_swing_fractal_k_h4`, `confirmation_bars`,
etc.) — ST-C3's spec simply never inherited or independently decided
equivalents. Per ADR-0004, ST-C3 is a distinct lineage and must not
silently inherit ST-C2's values; per the hard rules ("No Strategy
Innovation," "Specification is the source of truth"), I cannot invent them
either.

## Why this blocks R-18 specifically

R-18 (`existence_check_floor`) requires a working `signal_fn` that runs the
full funnel over real candle data (`tools/existence_check.py`'s contract).
That `signal_fn` needs real Evidence-producing detection code for at least
`S1_HTF_BIAS` through `S8_FVG_OB_CONFLUENCE`. Every one of those stages
depends on at least one of the five missing parameters above. Even the
stages with fully owner-decided *filter* thresholds (R-04 wick_ratio_min,
R-07 displacement_body_ratio_min) cannot run, because the swing/structure
identification step that feeds them has no defined algorithm.

## Governance disposition

R-18 is reclassified from "needs a research/data run" to **"blocked on a
separate structural-detection specification gap, not yet even tracked as
resolution-matrix rows."** Four new candidate fields are added to
`RESOLUTION_MATRIX.md` to track this gap explicitly (not decided here —
`OWNER_DECISION_LOG.md`'s own convention is that this log records the
owner's decision, not a value the agent proposes on the owner's behalf):

- **R-27** — HTF swing/fractal lookback definition
- **R-28** — BOS confirmation-bar rule
- **R-29** — FVG minimum gap-size definition (and OB candle-selection rule)
- **R-30** — Pullback definition (for `BOS_EXTREME_LOCK`)

All four: status `PENDING`, owner decision required (or research-required,
at the owner's discretion — same category as R-04/R-06, which were
eventually decided via empirical research against real GBPUSD data rather
than an owner pick).

## What did NOT happen

- No detection module code was written.
- No structural-detection parameter was invented, inherited from ST-C2, or
  guessed.
- No spec revision (`specs/st-c3_v1.0.5.yaml` was not created) — this is a
  gap-tracking report, not a decision, so there is nothing to freeze yet.
- `governance/st_c3_stage_status.yaml`'s R-18 tracking is updated to record
  this blocker explicitly (see that file).

## Next steps

R-18 remains open, now explicitly blocked on R-27 through R-30 rather than
being a directly research-runnable field. Per the owner's direction, this is
parked as a future dedicated detection-research task rather than forced now.
The ST-C3 v1.0.4 governance state otherwise stands: 24/26 originally-tracked
fields decided, 275/275 tests passing, no execution/optimization/demo/live/
A3 authorization.
