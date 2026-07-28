# S1-G5 Signal and Trade-Plan Conformance — Completion Audit

**Date:** 2026-07-28
**Modeled on:** `reports/validation/st_c3/S1_G4_EVENT_STATE_CONFORMANCE_COMPLETION_AUDIT.md`

## 1. Overview

This audit evaluates whether the evidence gathered in
`reports/validation/st_c3/S1_G5_SIGNAL_TRADE_PLAN_CONFORMANCE_REPORT.md`
satisfies S1-G5's acceptance criteria, as defined in `MASTER_PLAN.md`'s
A2/S1-G5 section. Unlike S1-G3/S1-G4, that section has no "Required
evidence" bullet list — its entire stated requirement is one purpose
line (verified in `S1_G5_READINESS_CHECKLIST.md`, which also rejected a
pasted, fabricated 5-category A-E structure not present in the document):

> verify BUY/SELL, entry, stop, target, RR, expiration, source event IDs,
> and rejection reasons match the frozen strategy contract.

**This audit produces a recommendation only — it does not itself accept
or reject S1-G5.** Acceptance is a separate, explicit owner decision,
exactly as it was for S1-G2, S1-G3, and S1-G4.

## 2. Required Evidence (per MASTER_PLAN.md) and Coverage

| Concept | Coverage | Where |
|---|---|---|
| BUY/SELL (direction) | Covered | `test_bullish_htf_bias_maps_to_long_direction`, `test_bearish_htf_bias_maps_to_short_direction` |
| Entry | Covered | `test_entry_price_and_zone_match_bundle_inputs_exactly` (entry_price, entry_zone_id, entry_window_id, max_entry_bars, bars_since_ltf_choch), `test_entry_uses_order_block_id_when_fvg_invalid` |
| Stop | Covered | `test_stop_price_and_type_match_bundle_for_long` (1.1015), `test_stop_price_and_type_match_bundle_for_short` (1.1985) — both sl_price and sl_type |
| Target | Covered | `test_all_three_targets_match_bundle_inputs_exactly` (parametrized LONG/SHORT, all of target_id/target_type/price/rr), `test_target_types_are_tp1_internal_tp2_external_tp3_htf` |
| RR | Covered | `test_computed_rr_and_min_rr_match_bundle_exactly`, `test_risk_per_trade_pct_matches_bundle`, `test_rr_exactly_at_minimum_still_passes_s12` (boundary), `test_rr_fractionally_below_minimum_rejects_r8` (off-by-epsilon) |
| Expiration | Covered | `test_expiry_rules_and_default_evidence_id_on_valid_trade_plan`, `test_expiry_evidence_id_populated_when_supplied` |
| Source event IDs | Covered | `test_evidence_chain_ids_match_source_evidence_in_declared_order` (all 15, exact order), `test_context_ids_match_source_evidence` (11 context IDs) |
| Rejection reasons | Covered | `test_rejection_reason_text_matches_the_invalidated_evidences_own_reason` (parametrized across 6 representative states/codes, checking `reason` text itself — not just `code`/`state`, which prior tests already covered) |

Every concept in S1-G5's one-line purpose statement has a dedicated,
exact-value test — not an inequality/truthiness check alone, and not an
inference from S1-G3/S1-G4's coverage.

## 3. Test Summary

- `tests/st_c3/test_s1_g5_signal_trade_plan_conformance.py`: 23 passed,
  0 failed.
- Full repository suite: 363 passed, 0 failed (2 pre-existing, unrelated
  `datetime.utcnow()` deprecation warnings in `tests/test_backtest_v35.py`).
- No regressions from the new test file.

## 4. Governance Alignment

- Active spec: `specs/st-c3_v1.0.7.yaml` — unmodified; all new tests read
  `kernel.py`/`trade_plan.py`/`evidence.py` as-is.
- A2/S1-G2, A2/S1-G3, A2/S1-G4: remain `ACCEPTED` (2026-07-27, unaffected).
- A2/S1-G5: evidence gathered, **not yet accepted** — this audit's
  subject.
- A2/S1-G6: not started, blocked behind S1-G5 acceptance.
- A3/execution/demo/live: unaffected, still blocked.
- `NEXT_ACTION.md`, `PROJECT_STATUS.md` synchronized to record
  evidence-gathered-not-accepted status.

## 5. Findings

- Every concept in S1-G5's purpose statement has a corresponding,
  specifically-named test with exact-value assertions, not just
  boolean/inequality checks reused from S1-G3/S1-G4's coverage.
- Two categories previously had only partial or indirect coverage and
  were closed here: the LONG case's stop price (only the SHORT case was
  asserted in `test_golden_cases.py`), and rejection-reason *text*
  (prior negative-case tests asserted `code`/`state` but never `reason`
  itself).
- Source event IDs are now verified ID-by-ID, in declared order, against
  each contributing Evidence object's own `id` — not merely a length/
  truthiness check as `test_golden_cases.py` originally did.
- RR coverage includes both a boundary case (`computed_rr == min_rr`
  exactly passes) and an off-by-epsilon rejection
  (`computed_rr` fractionally below `min_rr` rejects), closing a gap
  the pre-existing `test_rr_below_minimum_rejects_r8` (using a
  far-below value, 1.5 vs. 3.0) did not exercise.
- No lifecycle, execution, A3, or kernel-guard logic was touched; all
  new tests read existing `TradePlan`/`Rejection`/`EvidenceBundle`
  behavior.
- No content from the pasted, fabricated A-E evidence structure was
  used — coverage traces only to `MASTER_PLAN.md`'s actual purpose
  statement and the frozen `trade_plan.schema`.

## 6. Recommendation

**S1-G5 evidence is complete against its actual (single-line)
requirement.** Every concept named in `MASTER_PLAN.md`'s purpose
statement — BUY/SELL, entry, stop, target, RR, expiration, source event
IDs, rejection reasons — has an exact-value test tracing to the frozen
spec, with the two previously-thin spots (LONG-side SL, rejection-reason
text) specifically closed.

This audit's recommendation is that the evidence is **sufficient for
acceptance**, but — consistent with this session's established
discipline — the audit does not accept S1-G5 itself. That remains a
separate, explicit owner decision.

## 7. Next Actions

- Owner decision required: accept S1-G5 on this evidence, or identify
  specific gaps this audit missed.
- If accepted: `governance/st_c3_stage_status.yaml` needs a new
  `s1_g5_gate` block (mirroring `s1_g2_gate`/`s1_g3_gate`/`s1_g4_gate`),
  `NEXT_ACTION.md`/`PROJECT_STATUS.md` updated to ACCEPTED, and
  `MASTER_PLAN.md` version-bumped with a changelog entry — none of that
  is done by this audit on its own.
- If accepted, S1-G6 (Golden-Case Qualification) becomes unblocked per
  `MASTER_PLAN.md`, but starting it remains its own separate,
  not-yet-made owner decision, same pattern as prior gates.
