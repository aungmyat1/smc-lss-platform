# RCR-ST-C3-v1.0.6 — Revision Report

**Type:** Owner decisions (Tier 3 evidence-builder gap fields), decided
directly by the owner in-session — same category as R-05/R-11/R-21 (owner
picks without a prior empirical-research pass), not a research/backtest RCR
under `docs/RESEARCH-CHARTER.md` in its own right.
**From:** `specs/st-c3_v1.0.5.yaml` **To:** `specs/st-c3_v1.0.6.yaml`
**Date:** 2026-07-26

---

## Why

`R18_EVIDENCE_BUILDER_DESIGN.md` (the design proposal for
`build_evidence_bundle()`, R-18's remaining engineering task) found, while
scoping its Tier 3 section, that three fields the builder needs were still
literal placeholder strings in the frozen spec — not missing algorithms
(that was the R-27–R-30 gap, already resolved in v1.0.5), but missing
*numbers* behind an already-defined algorithm, and not tracked under any
existing R-item:

- `liquidity_sweep_stage.sweep_reclaim_max_bars` (N_SWEEP): `"PROVISIONAL_1_TO_3"`
- `entry_window_stage.entry_window_bars` (MAX_ENTRY_BARS): `"PROVISIONAL_3_TO_5_M3_BARS"`
- `sessions.london_window_utc` / `ny_window_utc`: `"PROVISIONAL_07_00_TO_10_00"` / `"PROVISIONAL_13_00_TO_16_00"`

These were surfaced in `R18_EVIDENCE_BUILDER_DESIGN.md` Section 5 and
`R18_OWNER_DECISION_PACKET.md`'s checklist, then answered by the owner
directly.

## The decisions

| Field | Value | Owner's stated basis |
|---|---|---|
| R-31 `sweep_reclaim_max_bars` (N_SWEEP) | **2 bars** | Phase-conditional guidance: 2 for the current A2/S1-G2 research/validation phase, 1 for a future A3+/production-tightening phase, 3 for exploratory robustness testing. A2/S1-G2 is the active phase, so 2 is adopted now. |
| R-32 `entry_window_bars` (MAX_ENTRY_BARS) | **4 M3 bars** | Owner's stated mid-range pick for A2/S1-G2, chosen to avoid biasing the signal-rate study toward either the tight (3-bar) or loose (5-bar) end of the spec's own prior provisional range. |
| R-33 `sessions.london_window_utc` / `ny_window_utc` | **London 07:00-10:00 UTC, NY 13:00-16:00 UTC** | Owner chose to keep the spec's own long-standing provisional times rather than change them. This ratifies status only — the clock values are unchanged from every prior revision. |

None of these three were empirically validated against historical data —
direct owner picks, the same category as R-05's ATR-tolerance decision and
R-21's fixed-lot value.

## Verification performed before folding in

- Confirmed R-31/R-32 are genuinely new fields with no prior R-number
  assigned anywhere in `RESOLUTION_MATRIX.md`/`OWNER_DECISION_LOG.md` —
  distinct from R-27–R-30 (missing algorithms) and from R-06/`max_sweep_age_bars`
  (a different, already-resolved sweep-stage field).
- Confirmed R-33's decision changes ratification status only, not the
  clock values themselves (`07:00-10:00`/`13:00-16:00` already existed as
  spec text in v1.0.1 through v1.0.5, just marked with a `PROVISIONAL_`
  string prefix rather than being a decided value).
- No new spec sections, evidence objects, states, transitions, or
  rejection/termination codes were touched — all three values were written
  into their existing owning fields (`liquidity_sweep_stage`,
  `entry_window_stage`, `sessions`), replacing placeholder strings with
  numbers/ratified strings, not adding new structure.
- Recorded the owner's un-adopted alternatives (R-31's 1-bar/3-bar
  phase-conditional values) in `OWNER_DECISION_LOG.md` rather than silently
  discarding them, so a future phase change has a documented starting point
  instead of requiring re-derivation from scratch.

## What changed in `specs/st-c3_v1.0.6.yaml`

- `pipeline.liquidity_sweep_stage.sweep_reclaim_max_bars`: `"PROVISIONAL_1_TO_3"` -> `2`
- `pipeline.entry_window_stage.entry_window_bars`: `"PROVISIONAL_3_TO_5_M3_BARS"` -> `4`
- `sessions.london_window_utc`: `"PROVISIONAL_07_00_TO_10_00"` -> `"07:00-10:00 UTC"`
- `sessions.ny_window_utc`: `"PROVISIONAL_13_00_TO_16_00"` -> `"13:00-16:00 UTC"`
- `parameters.N_SWEEP.value`/`.status`: `PROVISIONAL_1_TO_3`/`provisional` -> `2`/`decided`
- `parameters.MAX_ENTRY_BARS.value`/`.status`: `PROVISIONAL_3_TO_5`/`provisional` -> `4`/`decided`
- `parameters.SESSION_LONDON.status`/`parameters.SESSION_NY.status`: `provisional` -> `decided`
- `rcr_preregistration.v1_0_6_rcr_entry`: added, pointing at this report

Nothing else changed — no evidence object, state, transition, guard,
rejection/termination code, or other spec field. `OTE_MIN`/`OTE_MAX`/`equilibrium_boundary`
and the R-08 stop-loss guard-direction gap remain exactly as provisional/open
as before this revision — out of scope here.

## What did NOT happen

- No detection-module code was written. `build_evidence_bundle()` remains a
  design artifact (`R18_EVIDENCE_BUILDER_DESIGN.md`), not implemented code.
- `validation/st_c3/kernel.py` is unaffected — it still consumes pre-built
  `Evidence` objects, not raw candles.
- No execution, optimization, backtesting, demo, live, or A3 logic added.
- R-18 (`existence_check_floor`) is **not** resolved by this revision — see
  Next Steps.
- Tier 2 of `R18_EVIDENCE_BUILDER_DESIGN.md` (the new-glue-logic algorithms
  for `SweepReclaimEvidence`, `BOSExtremeEvidence`, `LTFConfirmationEvidence`,
  `TargetEvidence`) is not separately ratified by this revision — this RCR
  only resolves the three Tier 3 numeric gaps that blocked those algorithms
  from being implementable at all.

## Updated governance state

**All R-01 through R-33 tracked fields are now decided except R-18.** R-18
(`existence_check_floor`) needs real detection-module code plus a data run,
not a further spec decision — it remains the sole item open on the entire
tracker.

## Deliverables

- `specs/st-c3_v1.0.6.yaml`.
- `reports/validation/st_c3/OWNER_DECISION_LOG.md` — R-31/R-32/R-33 rows
  added and marked `APPROVED`.
- `reports/validation/st_c3/RESOLUTION_MATRIX.md` — R-31/R-32/R-33 rows
  added, marked `Resolved`.
- `governance/st_c3_stage_status.yaml` — `spec`/`version` bumped to v1.0.6,
  `v1_0_6_revision` metadata block added.
- `docs/strategy/st_c3/ST-C3_CHANGELOG.md` — v1.0.6 entry added.
- `validation/st_c3/evidence.py` — `SPEC_PATH` repointed to
  `specs/st-c3_v1.0.6.yaml`; `tests/st_c3/` re-verified passing (unaffected,
  as expected — these are spec-text values with no kernel consumer yet).
- This report.

## Next steps

R-18 is still the only field open on the entire tracker, and Tier 3's
resolution here removes the last spec-level blocker `R18_EVIDENCE_BUILDER_DESIGN.md`
identified. Before `build_evidence_bundle()` implementation starts, two
things from that design's Section 8 are still outstanding, not answered by
this revision: (1) explicit ratification of the Tier 1/Tier 2 design
approach itself (as opposed to just its Tier 3 numeric inputs), and (2)
whether a partial S1-S9 existence-check run is an acceptable interim R-18
data point, or whether R-18 should wait for a full S1-S13 run. Once those
land, implementation of `validation/st_c3/evidence_builder.py` (or the
owner's preferred name) can begin, wiring it into `signal_fn()` for
`tools/existence_check.py`, and running the result over real GBPUSD/EURUSD
candle data. This remains within the existing A2/S1-G2 scoped authorization
— no new authorization is granted or required by this revision, and
execution/optimization/demo/live/A3 remain exactly as blocked as before.
