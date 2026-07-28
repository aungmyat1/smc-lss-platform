# S1-G6 Golden-Case Qualification Report

**Date:** 2026-07-28
**Scope:** ST-C3 A2 / S1-G6 mechanical evidence gathering only

## 1. Overview

This report records the current ST-C3 golden-case qualification evidence
produced for A2/S1-G6. It does not accept S1-G6, does not pass A2, and
does not authorize A3. It only documents the deterministic evidence now
available for governance review.

## 2. Artifacts Built

- Golden-case library: `golden/st_c3/`
- Golden runner: `validation/st_c3/golden_runner.py`
- Deterministic funnel tests:
  - `tests/funnel/test_st_c3_golden_bos.py`
  - `tests/funnel/test_st_c3_golden_choch.py`
  - `tests/funnel/test_st_c3_golden_fvg.py`
  - `tests/funnel/test_st_c3_golden_liquidity.py`
- Evidence summary:
  `evidence/conformance/st_c3_s1_g6_golden_summary.json`

## 3. Current Mechanical Results

As of 2026-07-28, the golden runner reports:

- total cases: 6
- passed: 6
- failed: 0

Scenario breakdown:

- `bos`: 1/1 passed
- `choch`: 1/1 passed
- `fvg`: 1/1 passed
- `liquidity`: 1/1 passed
- `displacement`: 1/1 passed
- `invalidations`: 1/1 passed

## 4. Deterministic Coverage

Each case is JSON-backed and verifies:

- exact expected `EvidenceBundle` inputs
- exact expected funnel path
- exact expected rejection payload when the case is negative
- exact expected trade-plan subset when the case is valid

The runner uses the existing ST-C3 kernel. No new strategy logic,
replay logic, execution logic, or optimization logic was introduced.

## 5. Governance Alignment

- S1-G5 remains not accepted.
- S1-G6 is therefore not yet governance-eligible, even though the
  mechanical golden suite currently passes.
- A3 remains blocked.
- Execution/demo/live remain blocked.

## 6. Recommendation

The S1-G6 mechanical evidence is now present and reproducible. This is
enough to support a governance review, but not enough to claim S1-G6 is
accepted. Acceptance remains a separate owner decision after S1-G5 is
resolved.
