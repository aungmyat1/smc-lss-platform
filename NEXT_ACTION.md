# NEXT_ACTION.md

**One milestone at a time. This is the active milestone.**

## ST-C2 A1 Closure and A2 Reference-Conformance Authorization

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
| A2 Signal Conformance | IN PROGRESS |
| A3 Statistical Validation | BLOCKED: A2 NOT PASSED |
| Execution | BLOCKED |
| Demo | BLOCKED |
| Production | BLOCKED |

## Objective

Review whether the current S1-G2 evidence is sufficient to complete the
reference implementation gate and authorize the next A2 correctness gate,
S1-G3 Primitive and Indicator Conformance.

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

## Data Finding

The initial `NO_SIGNAL_FOUND` result was caused by insufficient M3 coverage.
After extending M1-derived M3 history to 16,642 bars, the existence floor
(`>=1 qualifying GBPUSD signal`) was satisfied.

## Acceptance Criteria

- Confirm A1 closure is accepted with tracked non-blocking residuals.
- Confirm reference kernel remains within authorized S1-G2/A2 scope.
- Confirm tests, data provenance, existence report, and diagnostic report are
  recorded as objective evidence.
- Record a governance decision to either complete S1-G2 and move to A2/S1-G3
  Primitive and Indicator Conformance, or keep S1-G2 open with named blockers.
- Keep A3 historical/statistical validation blocked until A2 passes.
- Execution, demo, live, broker, and production authority remain blocked.
