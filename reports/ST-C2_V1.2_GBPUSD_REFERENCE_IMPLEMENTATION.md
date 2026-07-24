# ST-C2 v1.2 GBPUSD Reference Implementation Report

**Date:** 2026-07-24
**Stage:** S1-G2 Reference Implementation
**Scope:** frozen `specs/st-c2_v1.2.0.yaml`

## Verdict

**PARTIAL COMPLETE - EXISTENCE FLOOR SATISFIED**

The authorized reference implementation artifacts were created for the minimum
GBPUSD detector slice:

- `validation/st_c2_reference.py`
- `validation/run_st_c2_gbp_existence.py`
- `tests/test_st_c2_reference.py`

Golden-case and conformance tests pass for the implemented minimum slice.
The real-history existence-check scan ran after GBPUSD H4/M15/M3 availability
was resolved and the minimum existence floor was satisfied.

## Conformance Mapping

| Spec area | Reference artifact | Status |
|---|---|---|
| Enabled symbol | `enabled_symbols()` validates GBPUSD-only scope | Covered |
| G1/G2 liquidity/bias precondition | `_last_sweep()` and `_bias_from_sweep()` | Minimum slice covered |
| G4 OTE/location | `_in_discount_or_premium()` | Minimum slice covered |
| G5 FVG alignment | `_matching_mf_fvg()` | Minimum slice covered |
| G6 LTF confirmation | `_ltf_confirmation()` | Minimum slice covered |
| Rejection codes | `DetectionResult.rejection_code` with R1/R3/R4/R5/R6 | Minimum slice covered |
| Broker isolation | `no_broker_import_guard()` and tests | Covered |

This is not full engine conformance and does not flip
`engine_implements_spec` to true.

## Tests

Focused tests:

- positive GBPUSD golden case
- no-liquidity negative case (`R1`)
- bearish mirror case
- cutoff-invariance
- clean-vs-rerun determinism
- no broker/MT5 import guard
- frozen GBPUSD-only spec metadata

## Existence Check

Report: `reports/ST-C2_V1.2_GBPUSD_EXISTENCE_CHECK.md`

Verdict: **SIGNAL_FOUND**

Scan evidence:

- Checked windows before first signal: `1,365`
- First signal time: `2026-06-10 17:15`
- Direction: `short`

Diagnostic:

- The initial `NO_SIGNAL_FOUND` result came from insufficient M3 coverage.
- `reports/ST-C2_V1.2_GBPUSD_R1_DIAGNOSTIC.md` records
  `DATA_COVERAGE_CAUSE_CONFIRMED`.
- After extending M1-derived M3 to 16,642 bars, the existence floor (`>=1`) was
  satisfied.

Data provenance:

- `data/GBPUSD_H4.csv` and `data/GBPUSD_M15.csv` were exported from the local
  MT5 terminal through `src/load_history.py`.
- `data/GBPUSD_M3.csv` was derived from complete contiguous M1 groups because
  the terminal rejected native `TIMEFRAME_M3` with invalid params.
- No M5-as-M3 substitution was used.

## Authorization Boundary

This report does not authorize historical validation, statistical validation,
execution, demo trading, live trading, broker integration, or production
promotion.
