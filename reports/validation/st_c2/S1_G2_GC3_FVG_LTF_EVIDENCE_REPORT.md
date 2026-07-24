# ST-C2 S1-G2-GC3 FVG/LTF Evidence Report

**Date:** 2026-07-24  
**Strategy:** ST-C2 v1.2.0 GBPUSD  
**Lifecycle:** Stage A / A2 / S1-G2  
**Scope:** Reference implementation only

## Verdict

S1-G2-GC3 FVG/LTF EVIDENCE MODULE: PARTIAL PASS

S1-G2 REMAINS OPEN

NEXT: CONTINUE S1-G2 CLOSURES FOR STATE MACHINE, TRADE PLAN, REJECTION COVERAGE, AND REMAINING RULE MAPPINGS

## Implemented Scope

- Added public GC3 evidence module: `validation/st_c2/evidence_gc3.py`.
- Added kernel-facing evidence builder API:
  - `FVGChainEvidence`
  - `LTFConfirmationEvidence`
  - `EvidenceBuilder`
- Kept the ST-C2 reference kernel thin: it consumes GC3 evidence objects rather
  than computing FVG/LTF validity inline.
- Added low-level deterministic FVG/LTF detectors in
  `validation/st_c2/fvg_confirmation.py`.
- Updated the reference kernel to reject at R4/R5 from evidence validity.
- Updated rule-level provenance for GC3-owned rules:
  - `module`: `GC3_evidence_module`
  - `module_version`: `v1.0.0`
  - `source`: `st_c2.evidence_gc3`
  - `validated_by`: `traceability_map`, `gc3_tests`
  - `last_update`: `2026-07-24`

## Rule Closures

- FVG rules mapped: `STC2-FVG-001` through `STC2-FVG-006`.
- LTF rules mapped: `STC2-LTF-001` through `STC2-LTF-004`.
- Traceability missing mappings dropped from 28 to 20.

## Updated Counts

| Metric | Count |
|---|---:|
| Frozen rules in inventory | 45 |
| Implemented or partially implemented rules | 31 |
| Rules with direct tests | 26 |
| Missing rule-test mappings | 20 |

## Classification Distribution

| Classification | Count |
|---|---:|
| `IMPLEMENTED_AND_TESTED` | 19 |
| `IMPLEMENTED_NOT_TESTED` | 3 |
| `PARTIALLY_IMPLEMENTED` | 9 |
| `NOT_IMPLEMENTED` | 14 |

## Tests

```text
python -m pytest -q tests/st_c2/test_evidence_gc3.py
4 passed

python -m pytest -q tests/test_st_c2_reference.py
8 passed
```

Golden-case references:

- `tests/test_st_c2_reference.py::test_positive_golden_case_emits_signal`
- `tests/test_st_c2_reference.py::test_bearish_mirror_emits_short_signal`
- `GC-STC2-GBPUSD-BULL-POS-001`
- `GC-STC2-GBPUSD-BEAR-POS-001`

Differential audit reference:

- `reports/validation/st_c2/DIFFERENTIAL_COVERAGE_AUDIT_GC2.md`

## Remaining Limits

- Some GC3 rules remain `PARTIALLY_IMPLEMENTED` because advanced HTF/MF/LTF
  confluence semantics, mitigation invalidation, and stronger LTF sequencing
  still require additional golden cases.
- State machine, signal candidate, logical trade plan, stop/target/risk, and
  rejection-code completeness remain open.
- S1-G3 is not authorized by this report.

## Governance Guardrails

No strategy YAML parameters, broker integration, execution logic, demo trading,
live trading, or production authorization were changed.
