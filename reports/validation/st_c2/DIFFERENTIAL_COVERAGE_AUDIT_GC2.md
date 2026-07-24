# ST-C2 Differential Coverage Audit - GC2/GC3

**Date:** 2026-07-24  
**Scope:** `reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json`  
**Purpose:** verify rule inventory stability after GC2 structural and GC3
FVG/LTF provenance tagging.

## Verdict

DIFFERENTIAL COVERAGE AUDIT: PASS

S1-G2 traceability remains stable and S1-G2 can continue.

## Four-Axis Audit

| Axis | Result |
|---|---|
| Rule count | PASS: 45 rules |
| Classification distribution | PASS: unchanged in current audit snapshot |
| Test coverage distribution | PASS: 26 rules with direct tests |
| Provenance completeness | PASS: 45 of 45 rules have provenance |
| Provenance version consistency | PASS: 45 of 45 use `v1.0.0` |

## Current Classification Distribution

The repo uses granular classification states rather than a flattened
`IMPLEMENTED` bucket:

| Classification | Count |
|---|---:|
| `IMPLEMENTED_AND_TESTED` | 19 |
| `IMPLEMENTED_NOT_TESTED` | 3 |
| `PARTIALLY_IMPLEMENTED` | 9 |
| `NOT_IMPLEMENTED` | 14 |

## Provenance Distribution

| Provenance Field | Result |
|---|---|
| `module` | `GC2_structural_module` on 14 rules; `GC3_evidence_module` on 10 rules; GC2 A2 governance provenance on the remaining inventory rows until later modules claim them |
| `module_version` | `v1.0.0` on 45 rules |
| `source` | `st_c2.structural`, `st_c2.evidence_gc3`, or traceability-only inventory source |
| `validated_by` with `gc2_tests` | 14 GC2-closed rules |
| `validated_by` with `gc3_tests` | 10 GC3-mapped rules |
| `validated_by` traceability only | 21 remaining rules |

## Acceptance Criteria

- 45 rules exist.
- No rule is missing `classification`.
- No rule is missing `tests`.
- No rule is missing `provenance`.
- All provenance blocks use `module_version: v1.0.0`.
- Direct GC2 test provenance is limited to the GC2-closed rules.

## Next

Continue with remaining S1-G2 closures: state machine, trade-plan,
rejection-code coverage, and remaining rule mappings. S1-G2 remains open;
S1-G3, A3, Stage B, execution, demo, live, and production remain blocked.
