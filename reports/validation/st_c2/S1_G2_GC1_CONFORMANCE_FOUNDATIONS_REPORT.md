# ST-C2 S1-G2-GC1 Conformance Foundations Report

**Date:** 2026-07-24
**Strategy:** ST-C2 v1.2.0
**Symbol:** GBPUSD
**Specification:** `specs/st-c2_v1.2.0.yaml`
**Lifecycle:** Stage A / A2 / S1-G2

## Slice Verdict

```text
S1-G2-GC1 CONFORMANCE FOUNDATIONS: PASS
S1-G2 REMAINS OPEN
NEXT: S1-G2-GC2 STRUCTURAL BIAS, LIQUIDITY, AND DEALING-RANGE CONFORMANCE
```

## Scope Completed

- Added explicit GBPUSD research metadata in `specs/st_c2/symbol_metadata.yaml`.
- Added pure price-normalization utilities in `validation/st_c2/symbols.py`.
- Removed hardcoded GBPUSD price multiplier from `validation/st_c2_reference.py`.
- Added immutable evidence schemas in `validation/st_c2/schemas.py`.
- Added stable ID utilities in `validation/st_c2/identifiers.py`.
- Added structural interface contracts in `validation/st_c2/interfaces.py`.
- Added versioned golden-case manifest and initial migrated fixtures.
- Added traceability validator in `validation/st_c2/traceability.py`.
- Added focused deterministic tests under `tests/st_c2/`.

## Symbol Normalization

Approved research metadata:

```yaml
symbol: GBPUSD
digits: 5
point_size: "0.00001"
pip_size: "0.0001"
points_per_pip: 10
price_rounding_digits: 5
timezone_basis: UTC
```

Utilities:

- `points_to_price`
- `price_to_points`
- `pips_to_price`
- `normalize_price`
- `normalize_distance`
- `compare_price_with_tolerance`

No GBPUSD decimal multiplier remains in `validation/st_c2_reference.py`.

## Stable Schemas

Research-only immutable schemas now exist for:

- `StructuralEvent`
- `LiquidityPool`
- `LiquiditySweep`
- `FVGEvent`
- `ConfirmationEvent`
- `StateTransition`
- `SignalCandidate`
- `LogicalTradePlan`
- `RejectionEvidence`

These are serializable and include causal cutoff fields for future exact
golden-case comparison.

## Traceability

Command:

```text
python -m validation.st_c2.traceability
```

Result:

```json
{"valid": true, "errors": [], "missing_mappings": 37}
```

The validator distinguishes valid current mappings from the still-missing
planned mappings. Missing mappings are not hidden.

## Existence Result

Command:

```text
python -m validation.run_st_c2_gbp_existence
```

Result remains unchanged:

- `SIGNAL_FOUND`
- First signal time: `2026-06-10 17:15`
- Direction: `short`

## Boundaries Preserved

- No frozen strategy parameters changed.
- No A3 backtest or profitability experiment was run.
- No MT5 import, broker adapter, order routing, demo/live trading, or execution
  layer was added.
- S1-G2 remains open.
- A3 and Stage B remain blocked.
