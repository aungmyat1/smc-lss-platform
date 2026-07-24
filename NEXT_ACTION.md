# NEXT_ACTION.md

**One milestone at a time. This is the active milestone.**

## S1-G2 Remaining Rule Closures - State, Trade Plan, and Rejection Evidence

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

Implement the next controlled S1-G2 gap-closure slice: deterministic state
transitions, signal candidate evidence, logical trade-plan evidence, and
remaining rejection-code coverage. S1-G2 remains open; A2/S1-G3 is not
authorized.

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
- GC1 foundations report:
  `reports/validation/st_c2/S1_G2_GC1_CONFORMANCE_FOUNDATIONS_REPORT.md`.
- GC2 structural conformance report:
  `reports/validation/st_c2/S1_G2_GC2_STRUCTURAL_CONFORMANCE_REPORT.md`.
- HTF structure and bias report:
  `reports/validation/st_c2/HTF_STRUCTURE_AND_BIAS_REPORT.md`.
- Liquidity sweep conformance report:
  `reports/validation/st_c2/LIQUIDITY_SWEEP_CONFORMANCE_REPORT.md`.
- Dealing-range OTE conformance report:
  `reports/validation/st_c2/DEALING_RANGE_OTE_CONFORMANCE_REPORT.md`.
- Differential coverage audit:
  `reports/validation/st_c2/DIFFERENTIAL_COVERAGE_AUDIT_GC2.md`.
- GC3 FVG/LTF evidence report:
  `reports/validation/st_c2/S1_G2_GC3_FVG_LTF_EVIDENCE_REPORT.md`.
- Stable identifier contract:
  `reports/validation/st_c2/STABLE_IDENTIFIER_CONTRACT.md`.
- Golden-case library report:
  `reports/validation/st_c2/GOLDEN_CASE_LIBRARY_REPORT.md`.

## Data Finding

The initial `NO_SIGNAL_FOUND` result was caused by insufficient M3 coverage.
After extending M1-derived M3 history to 16,642 bars, the existence floor
(`>=1 qualifying GBPUSD signal`) was satisfied.

## Acceptance Criteria

- Implement or formally close the audit blockers without changing frozen
  strategy parameters.
- Complete the remaining S1-G2 state, signal, trade-plan, and rejection-code
  evidence objects.
- Preserve the reproduced existence signal or explain any change.
- Keep missing mappings honest; do not mark S1-G2 complete.
- Keep A3 historical/statistical validation blocked until A2 passes.
- Execution, demo, live, broker, and production authority remain blocked.

## Blocking Gaps

- FVG/LTF advanced confluence and sequencing remain partial.
- Deterministic state machine is missing.
- Full logical trade-plan object is missing.
- R1-R7 detailed failure coverage is incomplete.
- Stable identifiers are incomplete for FVG, confirmation, signal, and trade-plan
  evidence.
- Versioned golden-case library requires GC3+ expansion.
- Hardcoded symbol precision in the reference kernel was closed by GC1.
