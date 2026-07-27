# S1-G4 Event and State Conformance — Evidence Report

**Date:** 2026-07-27
**Strategy:** ST-C3 v1.0.7 (GBPUSD/EURUSD-scoped)
**Status:** EVIDENCE GATHERED — NOT PASSED, NOT ACCEPTED. Whether S1-G4 is
considered complete is a separate, explicit owner decision, mirroring the
S1-G2/S1-G3 acceptance pattern. This report documents what evidence
exists; it does not itself close the gate.

## Scope

Per `MASTER_PLAN.md`, S1-G4 ("Event and State Conformance") is unblocked
once S1-G3 (Primitive and Indicator Conformance) is accepted — which
happened 2026-07-27. Its required evidence categories, and coverage:

| Required evidence | Status | Where |
|---|---|---|
| Structured evidence for BOS, CHoCH, liquidity pools, sweeps, reclaim, FVG, POI interaction, displacement, DOL | Covered | `tests/st_c3/test_s1_g4_event_state_conformance.py::test_concept_maps_to_a_real_spec_registered_evidence_field` (parametrized over all 10 concept mappings) ties each concept to a real field in the frozen spec's evidence registry (`BOSEvidence.bos_direction`, `BOSExtremeEvidence.pullback_detected`, `LTFConfirmationEvidence.choch_direction`, `SweepEvidence.level`/`sweep_type`, `SweepReclaimEvidence.reclaimed`, `FVGEvidence.gap_top`/`inside_ote`, `DisplacementEvidence.impulse_strength`, `TargetEvidence.target_type`); `::test_dol_external_liquidity_targets_are_distinct_from_internal` confirms DOL (draw on liquidity, i.e. external/HTF pools) is TP2_EXTERNAL/TP3_HTF as distinct from TP1_INTERNAL. |
| Legal transition tests | Covered (pre-existing + new) | `tests/st_c3/test_golden_cases.py` (full S0->S13 traversal, LONG and SHORT); new `::test_golden_case_states_reached_is_a_strict_forward_prefix` additionally asserts no duplicate/skipped/backward states. |
| Illegal transition tests | Covered (pre-existing + new) | `tests/st_c3/test_negative_cases.py` (14 tests, one rejection per state); new `::test_every_rejection_state_stops_before_the_next_state_is_reached` directly verifies the rejected state and everything after it is absent from `states_reached` across 5 representative states. |
| Expiry/invalidation tests | Covered (new — no prior coverage) | `::test_evaluate_expiry_maps_each_reason_to_the_frozen_err_code` (all 4 reasons), `::test_evaluate_expiry_rejects_unknown_reason`, `::test_all_frozen_err_codes_are_reachable_via_evaluate_expiry`, `::test_trade_plan_exposes_the_same_four_expiry_rules_evaluate_expiry_supports`. |
| Duplicate prevention | Covered, scoped honestly (new — no prior coverage) | `::test_superseded_expiry_is_the_frozen_specs_duplicate_prevention_mechanism`, `::test_trade_plan_carries_expiry_evidence_id_for_superseded_tracking`. See scope note below. |
| Rejection-code evidence | Covered (pre-existing + new) | `test_negative_cases.py`'s 14 tests exercise R1-R8; new `::test_r_codes_used_by_negative_cases_are_a_subset_of_the_frozen_r_codes` confirms the set of codes actually used equals the full frozen `R_CODES` set (no code untested, no test using a code outside the frozen set). |

## Duplicate-prevention scope note

The frozen ST-C3 spec's *only* duplicate-prevention mechanism is the
`SUPERSEDED` expiry reason -> `ERR_SUPERSEDED_SETUP` (`"newer_higher_priority_setup_exists"`),
which terminates an existing `VALID` trade plan when a newer,
higher-priority setup for the same structure appears. There is no
cross-candidate comparison, ranking, or priority-computation logic
anywhere in the frozen v1.x spec — that would be Stage B / execution-layer
arbitration (candidate selection across concurrent signals), out of scope
for this validator kernel. This report and its tests verify only what the
frozen spec actually defines; no dedup algorithm was invented to fill the
gap.

## Test count

`tests/st_c3/test_s1_g4_event_state_conformance.py`: 23 new tests, all
passing. Combined with pre-existing `tests/st_c3/` suites, the full
`tests/st_c3/` directory now stands at 85 passing tests.

## What this report does NOT claim

- It does not claim S1-G4 is passed or accepted — that remains a separate
  owner decision.
- It does not claim the broader A2 substage (S1-G4 through S1-G6) is
  complete.
- It does not invent duplicate-prevention logic beyond what
  `SUPERSEDED`/`ERR_SUPERSEDED_SETUP` already defines.
- It does not authorize execution, demo, live, or production work.

## Full suite status

`python -m pytest -q` run confirms no regressions from the new test file:
**340 passed, 0 failed** (2 pre-existing deprecation warnings in
`tests/test_backtest_v35.py`, unrelated to this work).
