# NEXT_ACTION.md

**One milestone at a time. This is the active milestone.**

## S1-G2 Gap Closure - Reference-Conformance Blockers

Current lifecycle position:

| Field | State |
|---|---|
| Stage | Stage A - Strategy Validation |
| Substage | A2 - Indicator, Event and Signal Conformance |
| Gate | S1-G2 Reference Implementation Completion Review |
| Strategy | ST-C2 v1.2.0 GBPUSD |
| Status | Frozen |
| Readiness | GREEN |
| Frozen | YES |
| Implementation | AUTHORIZED: S1-G2 REFERENCE ONLY |
| A1 Logic Conformance | PASSED WITH TRACKED NON-BLOCKING RESIDUALS |
| A2 Signal Conformance | IN PROGRESS: S1-G2 REMAINS OPEN |
| A3 Statistical Validation | BLOCKED: A2 NOT PASSED |
| Execution | BLOCKED |
| Demo | BLOCKED |
| Production | BLOCKED |

## Objective

Close the blocking gaps found by the S1-G2 completion audit. S1-G2 remains
open; A2/S1-G3 is not authorized.

## Current Evidence

- Minimum reference kernel: `validation/st_c2_reference.py`.
- Golden-case tests: `tests/test_st_c2_reference.py`.
- Existence scan: `reports/ST-C2_V1.2_GBPUSD_EXISTENCE_CHECK.md`.
- R1 diagnostic: `reports/ST-C2_V1.2_GBPUSD_R1_DIAGNOSTIC.md`.
- A1 closure report:
  `reports/validation/st_c2/A1_LOGIC_CONFORMANCE_CLOSURE.md`.
- Stage status: `governance/st_c2_stage_status.yaml`.
- Rule-to-test traceability: `specs/st_c2/rule_to_test_map.yaml`.
- Conformance manifest: `specs/st_c2/conformance_manifest.yaml`.
- Current existence verdict: `SIGNAL_FOUND`.
- First qualifying signal: `2026-06-10 17:15`, direction `short`.
- S1-G2 completion audit:
  `reports/validation/st_c2/S1_G2_REFERENCE_IMPLEMENTATION_COMPLETION_AUDIT.md`.
- A2 coverage matrix:
  `reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json`.
- A2 conformance results:
  `reports/validation/st_c2/A2_CONFORMANCE_RESULTS.json`.

## Data Finding

The initial `NO_SIGNAL_FOUND` result was caused by insufficient M3 coverage.
After extending M1-derived M3 history to 16,642 bars, the existence floor
(`>=1 qualifying GBPUSD signal`) was satisfied.

## Acceptance Criteria

- Implement or formally close the audit blockers without changing frozen
  strategy parameters.
- Rule-to-test missing mappings must be reduced to `0` with direct evidence.
- Critical implementation coverage must reach `100%` for the S1-G2 reference
  contract.
- Full logical trade plan and reproduced existence signal must be deterministic.
- Keep A3 historical/statistical validation blocked until A2 passes.
- Execution, demo, live, broker, and production authority remain blocked.

## Blocking Gaps

- HTF BOS/CHoCH bias is not implemented; current bias is sweep-derived.
- Structural dealing-range identity and OTE lifecycle are missing.
- FVG confluence, freshness, invalidation, tie-break, rounding, and point
  normalization are incomplete.
- LTF confirmation lacks full structured event evidence and lifecycle rules.
- Deterministic state machine is missing.
- Full logical trade-plan object is missing.
- R1-R7 detailed failure coverage is incomplete.
- Stable identifiers are missing.
- Versioned golden-case library is missing.
- Hardcoded symbol precision remains in the reference kernel.
