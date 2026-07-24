# ST-C2 S1-G2-GC2 Structural Conformance Report

**Date:** 2026-07-24  
**Strategy:** ST-C2 v1.2.0 GBPUSD  
**Lifecycle:** Stage A / A2 / S1-G2  
**Scope:** Reference implementation only

## Verdict

S1-G2-GC2 STRUCTURAL CONFORMANCE: PASS

S1-G2 REMAINS OPEN

NEXT: S1-G2-GC3 FVG CHAIN AND LTF CONFIRMATION CONFORMANCE

## Implemented Scope

- Added deterministic HTF structural event detection in `validation/st_c2/structure.py`.
- Moved active HTF bias authority to BOS/CHoCH structural evidence only.
- Kept sweep-derived bias and full-window OTE helpers as deprecated compatibility shims only.
- Added liquidity pool selection, sweep/reclaim evidence, structural dealing range selection, and OTE eligibility evidence.
- Added `bias_evidence_timestamp`, `bias_evidence_event_id`, and `bias_evidence_type` coverage through `BiasEvidence`.
- Added CHoCH displacement gating using the frozen `htf_bias_stage.choch.displacement_body_ratio_min`.
- Added structured rule-level provenance in `A2_RULE_COVERAGE_MATRIX.json` for
  all 45 rules using canonical `GC2_structural_module` `v1.0.0` A2 governance
  provenance. The 14 GC2-closed rules are validated by both `traceability_map`
  and `gc2_tests`; the remaining rules are tagged by traceability only until
  direct tests exist.

## Tests

- `tests/st_c2/test_structural_conformance.py`
- `tests/test_st_c2_reference.py`
- `tests/st_c2/test_traceability.py`

Focused result recorded during implementation:

```text
python -m pytest -q tests\st_c2\test_structural_conformance.py tests\test_st_c2_reference.py
14 passed
```

Traceability result:

```text
python -m validation.st_c2.traceability
valid: true
missing_mappings: 28
```

Differential coverage audit:

```text
changed_rule_ids: STC2-BIAS-001, STC2-BIAS-002, STC2-BIAS-003, STC2-BIAS-004,
STC2-BIAS-005, STC2-LIQ-003, STC2-LIQ-004, STC2-LIQ-007, STC2-OTE-001,
STC2-OTE-002, STC2-OTE-003, STC2-STRUCT-001, STC2-STRUCT-004, STC2-STRUCT-005
only_gc2_related: True
```

## Current Blockers

- FVG-chain lifecycle remains partial.
- LTF confirmation evidence remains partial.
- Deterministic state machine is not implemented.
- Full logical trade-plan object is not implemented.
- S1-G2 completion remains blocked by 28 unmapped frozen rules.

## Governance Guardrails

No specs, YAML strategy parameters, broker integration, execution logic, demo trading, live trading, or production authorization were changed by GC2.
