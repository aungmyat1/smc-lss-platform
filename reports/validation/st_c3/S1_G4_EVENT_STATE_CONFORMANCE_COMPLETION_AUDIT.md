# S1-G4 Event and State Conformance — Completion Audit

**Date:** 2026-07-27
**Modeled on:** `reports/validation/st_c3/S1_G3_PRIMITIVE_CONFORMANCE_COMPLETION_AUDIT.md`

## 1. Overview

This audit evaluates whether the evidence gathered in
`reports/validation/st_c3/S1_G4_EVENT_STATE_CONFORMANCE_REPORT.md`
satisfies S1-G4's acceptance criteria, as defined in `MASTER_PLAN.md`'s
A2/S1-G4 section ("A2 / S1-G4 - Event and State Conformance"). **This
audit produces a recommendation only — it does not itself accept or
reject S1-G4.** Acceptance is a separate, explicit owner decision, exactly
as it was for S1-G2 and S1-G3.

## 2. Required Evidence (per MASTER_PLAN.md) and Coverage

| Required evidence | Coverage | Where |
|---|---|---|
| Structured evidence for BOS | Covered | `test_concept_maps_to_a_real_spec_registered_evidence_field["BOS"]`, `["BOS_extreme_lock"]` — `BOSEvidence.bos_direction`, `BOSExtremeEvidence.pullback_detected` |
| Structured evidence for CHoCH | Covered | `test_concept_maps_to_a_real_spec_registered_evidence_field["CHoCH"]` — `LTFConfirmationEvidence.choch_direction` |
| Structured evidence for liquidity pools | Covered | `["liquidity_pool_sweep"]` — `SweepEvidence.level`; also `TargetEvidence.target_type` (external pools, see DOL below) |
| Structured evidence for sweeps | Covered | `["sweep_type"]` — `SweepEvidence.sweep_type` |
| Structured evidence for reclaim | Covered | `["reclaim"]` — `SweepReclaimEvidence.reclaimed` |
| Structured evidence for FVG | Covered | `["FVG"]` — `FVGEvidence.gap_top` |
| Structured evidence for POI interaction | Covered | `["POI_interaction"]` — `FVGEvidence.inside_ote` (the S8 confluence guard) |
| Structured evidence for displacement | Covered | `["displacement"]` — `DisplacementEvidence.impulse_strength` |
| Structured evidence for DOL | Covered | `["DOL_target_type"]` plus `test_dol_external_liquidity_targets_are_distinct_from_internal` — `TargetEvidence.target_type` distinguishes TP1_INTERNAL from TP2_EXTERNAL/TP3_HTF (draw-on-liquidity targets) |
| Legal transition tests | Covered (pre-existing `test_golden_cases.py` + new) | `test_golden_case_states_reached_is_a_strict_forward_prefix` — no duplicate/skipped/backward states across both golden fixtures |
| Illegal transition tests | Covered (pre-existing `test_negative_cases.py` + new) | `test_every_rejection_state_stops_before_the_next_state_is_reached` — directly verifies the rejected state and everything downstream is absent from `states_reached` |
| Expiry/invalidation tests | Covered (new, no prior coverage existed) | `test_evaluate_expiry_maps_each_reason_to_the_frozen_err_code` (all 4 reasons), `test_evaluate_expiry_rejects_unknown_reason`, `test_all_frozen_err_codes_are_reachable_via_evaluate_expiry`, `test_trade_plan_exposes_the_same_four_expiry_rules_evaluate_expiry_supports` |
| Duplicate prevention | Covered, honestly scoped (new, no prior coverage existed) | `test_superseded_expiry_is_the_frozen_specs_duplicate_prevention_mechanism`, `test_trade_plan_carries_expiry_evidence_id_for_superseded_tracking` |
| Rejection-code evidence | Covered (pre-existing 14 negative-case tests + new completeness check) | `test_r_codes_used_by_negative_cases_are_a_subset_of_the_frozen_r_codes` — confirms the set of R-codes actually exercised equals the full frozen `R_CODES` set exactly (no gap either direction) |

Every required-evidence category MASTER_PLAN.md lists for S1-G4 has a
covered test, with a traceable link back to the frozen spec's own
evidence registry, rejection-code schema, or termination-code schema —
none of the coverage above required inventing a mechanism the spec does
not define.

## 3. Test Summary

- `tests/st_c3/test_s1_g4_event_state_conformance.py`: 23 passed, 0 failed.
- Full repository suite: 340 passed, 0 failed (2 pre-existing, unrelated
  `datetime.utcnow()` deprecation warnings in `tests/test_backtest_v35.py`).
- No regressions from the new test file.

## 4. Governance Alignment

- Active spec: `specs/st-c3_v1.0.7.yaml` — unmodified; all new tests are
  additive, read `kernel.py`/`evidence.py`/`rejection_codes.py` as-is.
- A2/S1-G2, A2/S1-G3: remain `ACCEPTED` (2026-07-27, unaffected).
- A2/S1-G4: evidence gathered, **not yet accepted** — this audit's
  subject.
- A2/S1-G5, A2/S1-G6: not started, blocked behind S1-G4 acceptance per
  `MASTER_PLAN.md` ("BLOCKED until S1-G4 passes" is the implied
  precondition for S1-G5, mirroring the S1-G3->S1-G4 pattern).
- A3/execution/demo/live: unaffected, still blocked.
- `NEXT_ACTION.md`, `PROJECT_STATUS.md` synchronized to record
  evidence-gathered-not-accepted status.

## 5. Findings

- Every required-evidence category has either a genuinely new test or a
  cross-check against pre-existing coverage; nothing was assumed covered
  without a specific, named test.
- The duplicate-prevention evidence is deliberately narrow: it verifies
  only the `SUPERSEDED` -> `ERR_SUPERSEDED_SETUP` mechanism the frozen
  spec actually defines. It does not claim coverage of a
  candidate-ranking or cross-signal arbitration algorithm, because no
  such algorithm exists in the frozen v1.x spec — that is Stage B /
  execution-layer scope, unaffected by and out of reach of this gate.
- Expiry/invalidation had zero prior test coverage before this session;
  `evaluate_expiry()` existed in `kernel.py` since S1-G2 but was never
  directly exercised until now.
- The structured-evidence-to-spec-field map is the first place in the
  repository that states, in one file, exactly which registered
  Evidence field each MASTER_PLAN.md concept (BOS/CHoCH/liquidity
  pool/sweep/reclaim/FVG/POI/displacement/DOL) corresponds to — prior
  coverage exercised these fields implicitly through golden/negative
  fixtures without ever stating the mapping explicitly.
- No lifecycle, execution, A3, or kernel-guard logic was touched; every
  new test reads existing kernel/evidence/rejection-code behavior, none
  of it writes new production logic.

## 6. Recommendation

**S1-G4 evidence is complete against every category MASTER_PLAN.md
requires**, in the same sense S1-G3's audit found no specification-level
gap: each required category maps to a real, spec-registered mechanism,
and each now has a corresponding test.

This audit's recommendation is that the evidence is **sufficient for
acceptance**, but — consistent with this session's established
discipline — the audit does not accept S1-G4 itself. That remains a
separate, explicit owner decision.

## 7. Next Actions

- Owner decision required: accept S1-G4 on this evidence, or identify
  specific gaps this audit missed.
- If accepted: `governance/st_c3_stage_status.yaml` needs a new
  `s1_g4_gate` block (mirroring the existing `s1_g2_gate`/`s1_g3_gate`
  blocks), `NEXT_ACTION.md`/`PROJECT_STATUS.md` updated to ACCEPTED, and
  `MASTER_PLAN.md` version-bumped with a changelog entry — none of that
  is done by this audit on its own.
- If accepted, S1-G5 (Signal and Trade-Plan Conformance) becomes
  unblocked per `MASTER_PLAN.md`, but starting it remains its own
  separate, not-yet-made owner decision, same pattern as prior gates.
