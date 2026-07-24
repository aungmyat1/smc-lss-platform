# ST-C2 Golden-Case Library Report

**Date:** 2026-07-24
**Strategy:** ST-C2 v1.2.0
**Symbol:** GBPUSD
**Stage:** A2 / S1-G2-GC1

## Library Structure

```text
validation/st_c2/golden_cases/
├── manifests/
├── positive/
├── negative/
├── boundary/
├── sequencing/
└── identity/
```

Framework module: `validation/st_c2/golden_cases.py`.

## Initial Cases

| Case ID | Category | Source |
|---|---|---|
| `GC-STC2-GBPUSD-CONFIG-001` | identity | frozen GBPUSD-only scope |
| `GC-STC2-GBPUSD-BULL-POS-001` | positive | migrated inline bullish fixture |
| `GC-STC2-GBPUSD-BEAR-POS-001` | positive | migrated inline mirrored bearish fixture |
| `GC-STC2-GBPUSD-LIQ-NEG-001` | negative | migrated inline R1 liquidity rejection |
| `GC-STC2-GBPUSD-CUTOFF-001` | sequencing | migrated cutoff-invariance behavior |
| `GC-STC2-GBPUSD-DETERMINISM-001` | identity | migrated deterministic rerun behavior |
| `GC-STC2-GBPUSD-POINTS-BOUNDARY-001` | boundary | GBPUSD point/pip boundaries |
| `GC-STC2-GBPUSD-ID-STABILITY-001` | identity | stable identifier behavior |

## Result

The manifest validates and all fixture files load. Existing inline tests remain
in place; the migrated fixtures are an initial versioned representation, not a
replacement yet.

Command:

```text
python -m pytest -q tests/st_c2/test_golden_case_framework.py
```

S1-G2 remains open because the full required golden-case library is not yet
complete.
