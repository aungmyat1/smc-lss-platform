# ST-C2 GC4 State Machine Report

**Date:** 2026-07-24  
**Lifecycle:** Stage A / A2 / S1-G2  
**Scope:** Research-only reference evidence

## Verdict

GC4 STATE MACHINE: PASS FOR REFERENCE EVIDENCE

S1-G2 REMAINS OPEN

## Evidence

- Added `validation/st_c2/evidence_gc4.py`.
- Added deterministic state sequence:
  `INELIGIBLE -> HTF_BIAS_VALID -> LIQUIDITY_SELECTED -> SWEEP_CONFIRMED -> DEALING_RANGE_VALID -> OTE_VALID -> FVG_CHAIN_VALID -> LTF_CONFIRMATION_VALID -> SIGNAL_READY -> TRADE_PLAN_READY`.
- Every transition includes stable ID, previous state, new state, trigger event,
  rule ID, timestamp, causal cutoff, and reason metadata.
- Added duplicate and illegal-transition checks.
- Added research-only interface hook:
  `collect_state_transition_evidence()`.

## Tests

- `tests/st_c2/test_gc4_evidence.py::test_gc4_builds_complete_state_signal_and_trade_plan`
- `tests/st_c2/test_gc4_evidence.py::test_gc4_detects_illegal_transition_sequence`

## Limits

Runtime execution state, broker state, order state, and post-fill management are
not implemented and remain blocked.
