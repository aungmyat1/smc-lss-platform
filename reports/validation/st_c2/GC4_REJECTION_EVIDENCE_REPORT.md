# ST-C2 GC4 Rejection Evidence Report

**Date:** 2026-07-24  
**Lifecycle:** Stage A / A2 / S1-G2  
**Scope:** Research-only reference evidence

## Verdict

GC4 REJECTION EVIDENCE: PARTIAL PASS

S1-G2 REMAINS OPEN

## Evidence

- Added canonical rejection subcodes under R1-R7 in
  `validation/st_c2/evidence_gc4.py`.
- Rejections use stable IDs and include rule ID, timestamp, supporting event
  IDs, causal cutoff, and reason.
- R6 logical trade-plan rejection paths cover stop too small, stop too large,
  missing target, missing FVG chain, and net-R too low.
- Added research-only interface hook:
  `collect_rejection_evidence()`.

## Tests

- `tests/st_c2/test_gc4_evidence.py::test_gc4_rejection_evidence_is_stable_and_canonical`

## Limits

Additional negative golden cases are still required for every subcode before
S1-G2 can be considered completion-audit ready.
