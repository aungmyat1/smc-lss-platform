# ST-C2 GC4 Signal Candidate Report

**Date:** 2026-07-24  
**Lifecycle:** Stage A / A2 / S1-G2  
**Scope:** Research-only reference evidence

## Verdict

GC4 SIGNAL CANDIDATE: PASS FOR REFERENCE EVIDENCE

S1-G2 REMAINS OPEN

## Evidence

- Signal candidates are built with `SignalCandidate`.
- Stable IDs include symbol, direction, signal timestamp, causal cutoff, source
  event IDs, and rule IDs.
- Source event IDs include HTF bias, liquidity pool, sweep, dealing range, OTE,
  FVG chain, LTF confirmation, and component event IDs where present.
- No execution fields are included.
- Added research-only interface hook:
  `collect_signal_candidate_evidence()`.

## Tests

- `tests/st_c2/test_gc4_evidence.py::test_gc4_builds_complete_state_signal_and_trade_plan`
- `tests/test_st_c2_reference.py::test_deterministic_clean_vs_rerun`

## Limits

Duplicate rejection is represented by stable signal identity, but broader
multi-window replay duplicate suppression remains a later completion-audit
concern.
