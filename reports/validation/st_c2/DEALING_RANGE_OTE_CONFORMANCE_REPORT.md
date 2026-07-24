# ST-C2 Dealing Range and OTE Conformance Report

**Date:** 2026-07-24  
**Gate Slice:** S1-G2-GC2  
**Authority:** `specs/st-c2_v1.2.0.yaml`

## Verdict

DEALING RANGE AND OTE CONFORMANCE: PASS FOR GC2

## Evidence

- Structural dealing range is represented as immutable evidence with high/low anchors, equilibrium, confirmation timestamp, and causal cutoff.
- OTE eligibility is evaluated against structural range identity, not a whole-window high/low shortcut.
- Long eligibility requires discount/equilibrium inside the frozen `[0.5, 0.786]` retrace band.
- Short eligibility requires premium/equilibrium inside the frozen `[0.5, 0.786]` retrace band.
- Boundary behavior is tested at exact equilibrium and max-retrace limits.

## Tests

- `tests/st_c2/test_structural_conformance.py::test_structural_dealing_range_ote_boundaries_are_deterministic`
- `tests/st_c2/test_structural_conformance.py::test_structural_context_is_causal_and_deterministic`
- `tests/test_st_c2_reference.py::test_positive_golden_case_emits_signal`
- `tests/test_st_c2_reference.py::test_bearish_mirror_emits_short_signal`

## Remaining Limits

The downstream FVG chain, final LTF confirmation lifecycle, state transitions, and trade-plan generation remain blocked.
