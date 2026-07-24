# ST-C2 Liquidity Sweep Conformance Report

**Date:** 2026-07-24  
**Gate Slice:** S1-G2-GC2  
**Authority:** `specs/st-c2_v1.2.0.yaml`

## Verdict

LIQUIDITY SWEEP CONFORMANCE: PASS FOR GC2

## Evidence

- Liquidity pools are represented as stable evidence objects.
- Pool selection uses direction, nearest absolute price distance, confirmation timestamp, and stable ID ordering.
- Sweep evidence requires pierce, single-bar reclaim, frozen wick-ratio threshold, and max H4 age.
- Rejected sweep attempts preserve invalidation reason and diagnostic metadata.
- Liquidity evidence is secondary evidence and cannot determine HTF bias.

## Tests

- `tests/st_c2/test_structural_conformance.py::test_liquidity_pool_selection_is_stable_and_directional`
- `tests/st_c2/test_structural_conformance.py::test_sweep_requires_pierce_reclaim_wick_ratio_and_age`
- `tests/test_st_c2_reference.py::test_negative_without_liquidity_rejects_r1`

## Remaining Limits

Equal-high/equal-low aggregation and later FVG/LTF linkage are still governed by later S1-G2 slices.
