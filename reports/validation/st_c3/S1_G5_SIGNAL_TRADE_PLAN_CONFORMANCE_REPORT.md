# S1-G5 Signal and Trade-Plan Conformance — Evidence Report

**Date:** 2026-07-28
**Strategy:** ST-C3 v1.0.7 (GBPUSD/EURUSD-scoped)
**Status:** EVIDENCE GATHERED — NOT PASSED, NOT ACCEPTED. Whether S1-G5 is
considered complete is a separate, explicit owner decision, mirroring the
S1-G2/S1-G3/S1-G4 acceptance pattern. This report documents what evidence
exists; it does not itself close the gate.

## Scope

Per `MASTER_PLAN.md`'s A2/S1-G5 section, the gate's entire stated
requirement is one purpose line (there is no separate "Required evidence"
bullet list for this gate, unlike S1-G3/S1-G4 — verified in
`S1_G5_READINESS_CHECKLIST.md` before any evidence work began, after a
pasted message proposed a fabricated 5-category A-E structure that was
rejected):

> verify BUY/SELL, entry, stop, target, RR, expiration, source event IDs,
> and rejection reasons match the frozen strategy contract.

Coverage against each concept in that sentence:

| Concept | Status | Where |
|---|---|---|
| BUY/SELL (direction) | Covered | `test_bullish_htf_bias_maps_to_long_direction`, `test_bearish_htf_bias_maps_to_short_direction` — new exact-value tests; `test_golden_cases.py` already checked this too |
| Entry | Covered (new exact-value tests) | `test_entry_price_and_zone_match_bundle_inputs_exactly` (entry_price, entry_zone_id, entry_window_id, max_entry_bars, bars_since_ltf_choch), `test_entry_uses_order_block_id_when_fvg_invalid` |
| Stop | Covered (new — LONG case had no prior SL-price assertion) | `test_stop_price_and_type_match_bundle_for_long` (1.1015), `test_stop_price_and_type_match_bundle_for_short` (1.1985, pre-existing in golden cases; re-verified here) |
| Target | Covered (new — per-field exact-value checks) | `test_all_three_targets_match_bundle_inputs_exactly` (parametrized LONG/SHORT; target_id/target_type/price/rr for all 3 targets), `test_target_types_are_tp1_internal_tp2_external_tp3_htf` |
| RR | Covered (new — exact-value, boundary, and off-by-epsilon tests) | `test_computed_rr_and_min_rr_match_bundle_exactly`, `test_risk_per_trade_pct_matches_bundle`, `test_rr_exactly_at_minimum_still_passes_s12`, `test_rr_fractionally_below_minimum_rejects_r8` |
| Expiration | Covered (new — no prior coverage before S1-G4/S1-G5 work) | `test_expiry_rules_and_default_evidence_id_on_valid_trade_plan`, `test_expiry_evidence_id_populated_when_supplied` |
| Source event IDs | Covered (new — prior tests only checked length/truthiness, not ID-by-ID correctness) | `test_evidence_chain_ids_match_source_evidence_in_declared_order` (all 15, in order), `test_context_ids_match_source_evidence` (11 context IDs) |
| Rejection reasons | Covered (new — prior negative-case tests checked code/state but never the `reason` text itself) | `test_rejection_reason_text_matches_the_invalidated_evidences_own_reason` (parametrized across 6 representative states/codes) |

## Test count

`tests/st_c3/test_s1_g5_signal_trade_plan_conformance.py`: 23 new tests,
all passing.

## What this report does NOT claim

- It does not claim S1-G5 is passed or accepted — that remains a separate
  owner decision.
- It does not claim the broader A2 substage (S1-G6) is complete.
- It does not invent evidence categories beyond `MASTER_PLAN.md`'s actual
  one-line purpose statement — the pasted A-E structure was explicitly
  rejected as unverifiable against the real document.
- It does not authorize execution, demo, live, or production work.
- No change to `specs/st-c3_v1.0.7.yaml`, `kernel.py`'s guard sequence,
  or any `EvidenceBundle`/`TradePlan` field — this work only adds tests.

## Full suite status

`python -m pytest -q` run confirms no regressions from the new test file:
**363 passed, 0 failed** (2 pre-existing deprecation warnings in
`tests/test_backtest_v35.py`, unrelated to this work).
