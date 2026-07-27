# RCR-ST-C3-v1.0.7 — Revision Report

**Type:** Fresh owner decisions (R-31/R-32/R-33), given with clean
provenance after the same three fields' original 2026-07-26 versions were
found to have unverifiable provenance (see
`reports/governance/v1.0.6_RECONCILIATION_AUDIT.md`).
**From:** `specs/st-c3_v1.0.5.yaml` **To:** `specs/st-c3_v1.0.7.yaml`
**Date:** 2026-07-27

---

## Why v1.0.7, not v1.0.6

`specs/st-c3_v1.0.6.yaml` already exists, produced by a separate line of
work whose provenance could not be verified as owner-authorized and which
used the still-provisional OTE band as if frozen
(`OTE_MIN, OTE_MAX = 0.62, 0.79   # provisional, numerically usable` in
`validation/st_c3/evidence_builder.py`). That file is preserved on disk as
a historical/forensic record — not overwritten, not built upon. This
revision is built directly from the clean `v1.0.5` line instead, taking
the next available version number. `v1.0.6` is not part of the
authoritative spec chain; `v1.0.5 -> v1.0.7` is.

## Why this RCR exists

An earlier turn in this session proposed reassigning R-31/R-32/R-33 to
entirely different, fabricated fields (`STRUCTURAL_SWEEP_MIN_DISPLACEMENT`,
`MIN_RECLAIM_STRENGTH`, `CHOCH_CONFIRMATION_WINDOW`) with rationale
citing diagnostic studies that never tested those things — rejected in
full, no trace of it appears here. The owner then confirmed directly that
the *real* R-31/R-32/R-33 (the fields the quarantined line had proposed:
`sweep_reclaim_max_bars`, `entry_window_bars`, session UTC bounds) should
be decided fresh, with the *same numeric values* the quarantined line had
used, but as the owner's own direct decision, no empirical justification
claimed, independent of that line's disputed provenance.

## The decisions

| Field | Value | Owner's stated basis |
|---|---|---|
| R-31 `sweep_reclaim_max_bars` (N_SWEEP) | **2 bars** | Direct owner pick, no empirical justification claimed. |
| R-32 `entry_window_bars` (MAX_ENTRY_BARS) | **4 M3 bars** | Direct owner pick, no empirical justification claimed. |
| R-33 `sessions.london_window_utc` / `ny_window_utc` | **London 07:00-10:00 UTC, NY 13:00-16:00 UTC (unchanged)** | Direct owner pick to ratify the long-standing provisional values as final, no empirical justification claimed. |

Same category as R-05/R-21 — a risk-appetite/scope choice the owner is
entitled to make without empirical backing, per this session's established
precedent.

## Verification performed before folding in

- Confirmed these are the *real* R-31/R-32/R-33 fields (matching
  `RESOLUTION_MATRIX.md`'s existing tracked definitions), not a reassignment
  to new, undefined concepts — an earlier fabricated proposal reusing the
  same numbers for unrelated fields was rejected before this RCR began.
- Confirmed the owner's confirmation was a direct, explicit answer to a
  direct question ("do you want to confirm these exact three values as
  your own direct owner decisions, no empirical justification claimed") —
  not inherited from the quarantined line's unverified assertion of the
  same values.
- Confirmed no evidence object, state, transition, guard, or
  rejection/termination code was touched — all three values were written
  into their existing owning fields (`liquidity_sweep_stage`,
  `entry_window_stage`, `sessions`), matching the fields' pre-existing
  placeholder locations exactly.

## What changed in `specs/st-c3_v1.0.7.yaml`

- `pipeline.liquidity_sweep_stage.sweep_reclaim_max_bars`: `"PROVISIONAL_1_TO_3"` -> `2`
- `pipeline.entry_window_stage.entry_window_bars`: `"PROVISIONAL_3_TO_5_M3_BARS"` -> `4`
- `sessions.london_window_utc`: `"PROVISIONAL_07_00_TO_10_00"` -> `"07:00-10:00 UTC"`
- `sessions.ny_window_utc`: `"PROVISIONAL_13_00_TO_16_00"` -> `"13:00-16:00 UTC"`
- `parameters.N_SWEEP.value`/`.status`: `PROVISIONAL_1_TO_3`/`provisional` -> `2`/`decided`
- `parameters.MAX_ENTRY_BARS.value`/`.status`: `PROVISIONAL_3_TO_5`/`provisional` -> `4`/`decided`
- `parameters.SESSION_LONDON.status`/`parameters.SESSION_NY.status`: `provisional` -> `decided`
- `rcr_preregistration.v1_0_7_rcr_entry`: added, pointing at this report

Nothing else changed — no evidence object, state, transition, guard,
rejection/termination code, or other spec field. `OTE_MIN`/`OTE_MAX`/
`equilibrium_boundary` and the R-08 stop-loss guard-direction gap remain
exactly as provisional/open as before this revision — out of scope here,
same as every prior revision.

## What did NOT happen

- No detection-module code was written for S3 (sweep reclaim), S10
  (session gatekeeper), or S11 (entry window) — this revision freezes
  their numeric parameters only. `validation/st_c3/detection.py` still
  does not implement these three stages.
- No content from the quarantined `v1.0.6` line was merged, imported, or
  relied upon. The matching numeric values are a coincidence of the owner
  choosing the same numbers the quarantined line had proposed, not an
  inheritance.
- No execution, optimization, backtesting, demo, live, or A3 logic added.
- R-18 (`existence_check_floor`) is **not** resolved by this revision — it
  remains the only field open on the entire R-01–R-33 tracker.

## Updated governance state

**All R-01 through R-33 tracked fields are now decided except R-18.**
R-18 needs real detection-module code for 6 stages (S3, S7, S9, S10, S11,
S12) plus a real data run, not a further spec decision. A2/S1-G2 remains
`in_progress` (a "PASSED" claim on the quarantined line was rejected). A3
remains `blocked` (an "OPEN" claim on the quarantined line was rejected).

## Deliverables

- `specs/st-c3_v1.0.7.yaml`.
- `reports/validation/st_c3/OWNER_DECISION_LOG.md` — R-31/R-32/R-33 rows
  updated to reflect fresh, clean-provenance reconfirmation; the
  A2-PASSED/A3-OPENED entries annotated REJECTED inline (not deleted).
- `reports/validation/st_c3/RESOLUTION_MATRIX.md` — R-31/R-32/R-33 rows
  updated to point at v1.0.7; R-18 row corrected from a rejected "Resolved"
  claim back to "Open."
- `governance/st_c3_stage_status.yaml` — `spec`/`version` bumped to v1.0.7
  (skipping quarantined v1.0.6), `v1_0_7_revision` metadata block added,
  `v1_0_6_revision` annotated `QUARANTINED_REJECTED`, `a2_signal_conformance`/
  `a3_statistical_validation` reverted to `in_progress`/`blocked`,
  `freeze_state.engine_implements_spec` reverted to `false`.
- `NEXT_ACTION.md`, `PROJECT_STATUS.md` — restored from the quarantined
  line's overwrite back to accurate A2/S1-G2-in-progress state, with a
  correction notice documenting what happened.
- `docs/strategy/st_c3/ST-C3_CHANGELOG.md` — v1.0.7 entry added, v1.0.6
  marked quarantined.
- `validation/st_c3/evidence.py` — `SPEC_PATH` repointed to
  `specs/st-c3_v1.0.7.yaml`; `tests/st_c3/` re-verified passing.
- This report.

## Next steps

R-18 is the only field left on the entire R-01–R-33 tracker. It needs
real detection-module code for six stages — S3/S10/S11 now have frozen
numeric parameters (this revision) but no implementation; S7 (OTE band),
S9 (LTF CHoCH parameters), and S12 (R-08's guard direction) remain blocked
on fields with no owner decision at all. This remains within the existing
A2/S1-G2 scoped authorization — no new authorization is granted or
required by this revision, and execution/optimization/demo/live/A3 remain
exactly as blocked as before.
