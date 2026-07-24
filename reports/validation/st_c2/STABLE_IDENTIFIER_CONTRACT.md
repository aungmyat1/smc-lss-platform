# ST-C2 Stable Identifier Contract

**Date:** 2026-07-24
**Strategy:** ST-C2 v1.2.0
**Symbol:** GBPUSD
**Stage:** A2 / S1-G2-GC1

## Purpose

Stable identifiers make conformance outputs byte-comparable across runs without
using Python object hashes, random UUIDs, timestamp-only keys, or mutable
bar-index-only keys.

## Implementation

Implementation module: `validation/st_c2/identifiers.py`.

All IDs use:

- SHA-256
- canonical JSON serialization
- sorted keys
- canonical Decimal formatting
- explicit object type prefix
- exclusion of non-defining diagnostic fields: `metadata`, `diagnostics`,
  `notes`, `debug`

## Object Types

| Object | Function |
|---|---|
| structure | `structure_id()` |
| liquidity pool | `liquidity_pool_id()` |
| sweep | `sweep_id()` |
| FVG | `fvg_id()` |
| confirmation | `confirmation_id()` |
| state transition | `state_transition_id()` |
| signal candidate | `signal_candidate_id()` |
| logical trade plan | `trade_plan_id()` |
| golden case | `golden_case_id()` |

## Defining Attributes

Each object type must include strategy ID, strategy version, symbol, timeframe,
rule ID, event type, direction where applicable, source timestamps, reference
levels, confirmation timestamp, and causal cutoff where applicable.

Diagnostic metadata does not define identity.

## Validation

Tests:

- repeatability
- defining-field mutation changes ID
- non-defining metadata mutation does not change ID
- object-type collision sanity
- schema serialization and immutability

Command:

```text
python -m pytest -q tests/st_c2/test_stable_identifiers.py
```
