# ROADMAP.md - Gate Progress Under MASTER_PLAN v4.1.0

**Authority:** subordinate to `MASTER_PLAN.md`.
**Purpose:** track active milestones, gate progress, and upcoming deliverables.
**Current lifecycle position:** Stage A - Strategy Validation, A2 / S1-G2 -
Reference Implementation Completion Review.

The legacy active M1-M5 roadmap is archived. The active governance model is now:

```text
Stage A - Strategy Validation
Stage B - Trading-System Integration and Execution Qualification
```

---

## Current Position

| Field | State |
|---|---|
| Stage | Stage A - Strategy Validation |
| Substage | A2 - Indicator, Event and Signal Conformance |
| Gate | S1-G2 Reference Implementation Completion Review |
| Strategy | ST-C2 v1.2.0 GBPUSD |
| Status | Frozen |
| Readiness | GREEN |
| Frozen | YES |
| Implementation | AUTHORIZED: S1-G2 REFERENCE ONLY |
| A1 Logic Conformance | PASSED WITH TRACKED NON-BLOCKING RESIDUALS |
| A2 Signal Conformance | IN PROGRESS: S1-G2 REMAINS OPEN |
| A3 Statistical Validation | BLOCKED: A2 NOT PASSED |
| Execution | BLOCKED |
| Demo | BLOCKED |
| Production | BLOCKED |

ST-C2 v1.1.0 is frozen as the prior XAUUSD-scoped specification. The active
specification is now ST-C2 v1.2.0, a frozen GBPUSD-scoped specification created
by owner instruction. Scoped S1-G2 reference implementation is authorized;
execution/demo/live remain blocked.

---

## Stage A - Strategy Validation

### A1 / S1-G1 - Specification Freeze - COMPLETE

Goal: freeze one deterministic, machine-readable specification.

Current evidence:

- `specs/st-c2_v1.1.0.yaml` exists as the consolidated candidate.
- `reports/ST-C2_SPEC_AUDIT.md` records all original checklist items closed.
- `reports/ST-C2_IMPLEMENTATION_READINESS.md` records readiness GREEN.
- `reports/research_log.md` records the ST-C2 addendum chain through the
  eleventh addendum.

Completed candidate:

- `specs/st-c2_v1.2.0.yaml`, status `frozen`.
- GBPUSD enabled; XAUUSD and EURUSD disabled.
- Cost profile row changed to GBPUSD.
- XAUUSD-derived point thresholds inherited unchanged as provisional for the
  first GBPUSD reference/existence pass.
- Existence check accepted as `>=1 qualifying GBPUSD signal`.
- Population-feasibility floor deferred beyond the first existence check.

Audit: `reports/ST-C2_V1.2_GBPUSD_SPEC_AUDIT.md` reports READY TO FREEZE.
- MF-to-LTF structural inheritance and liquidity-tagging consistency remain
  unapplied new-scope proposals.
- R1-R7 rejection-code coverage gap and session-close points/pips note remain
  non-blocking implementation-time residuals.

Non-blocking carry-forward items:

- MF-to-LTF structural inheritance and liquidity-tagging consistency remain
  unapplied new-scope proposals.
- R1-R7 rejection-code coverage gap and session-close points/pips note remain
  implementation-time residuals.

### A1 / S1-G1C - Logic-Conformance Closure - COMPLETE

Evidence:

- `reports/validation/st_c2/A1_LOGIC_CONFORMANCE_CLOSURE.md`
- `governance/st_c2_stage_status.yaml`

Verdict: PASS WITH TRACKED NON-BLOCKING RESIDUALS.

This does not authorize A3, Stage B, execution, demo, live, or production.

### A2 / S1-G2 - Reference Implementation - CURRENT, REMAINS OPEN

Authorized scope:

- golden-case tests
- conformance kernel as research code
- minimum GBPUSD detector slice
- existence-check run requiring at least one qualifying GBPUSD signal

Completed:

- `validation/st_c2_reference.py`
- `validation/run_st_c2_gbp_existence.py`
- `tests/test_st_c2_reference.py`
- `reports/ST-C2_V1.2_GBPUSD_REFERENCE_IMPLEMENTATION.md`
- `reports/ST-C2_V1.2_GBPUSD_EXISTENCE_CHECK.md`
- `reports/validation/st_c2/S1_G2_REFERENCE_IMPLEMENTATION_COMPLETION_AUDIT.md`
- `reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json`
- `reports/validation/st_c2/A2_CONFORMANCE_RESULTS.json`
- `reports/validation/st_c2/S1_G2_GC1_CONFORMANCE_FOUNDATIONS_REPORT.md`
- `reports/validation/st_c2/STABLE_IDENTIFIER_CONTRACT.md`
- `reports/validation/st_c2/GOLDEN_CASE_LIBRARY_REPORT.md`
- `reports/validation/st_c2/S1_G2_GC2_STRUCTURAL_CONFORMANCE_REPORT.md`
- `reports/validation/st_c2/HTF_STRUCTURE_AND_BIAS_REPORT.md`
- `reports/validation/st_c2/LIQUIDITY_SWEEP_CONFORMANCE_REPORT.md`
- `reports/validation/st_c2/DEALING_RANGE_OTE_CONFORMANCE_REPORT.md`

Blocker:

- Required GBPUSD H4/M15/M3 files are now present.
- The initial short M3-history scan found zero qualifying signals across 3,248
  checked windows, all rejected at R1 liquidity.
- The R1 diagnostic identified insufficient M3 coverage as the cause.
- After extending M1-derived M3 to 16,642 bars, the existence scan found a
  qualifying GBPUSD short signal at `2026-06-10 17:15`.
- S1-G2 completion audit verdict is S1-G2 REMAINS OPEN.
- Missing rule-test mappings: 28.
- Blocking gaps: FVG chain conformance, LTF event evidence, state machine,
  trade plan, rejection subcodes, stable IDs for later evidence objects, and
  golden-case library expansion.
- GC1 foundations PASS: metadata, normalization, schemas, stable IDs,
  golden-case scaffold, traceability validator, and structural interfaces.
- GC2 structural conformance PASS: HTF BOS/CHoCH-only bias, deterministic
  liquidity pool/sweep evidence, structural dealing-range identity, and OTE
  boundary evidence.
- Remaining next slice: S1-G2-GC3 FVG chain and LTF confirmation conformance.

Allowed after authorization: feature generation, detector engine, parser, rule
engine, conformance tests, golden datasets.

Forbidden in this gate: MT5, broker adapter, execution layer, order management,
live trading, risk execution pipeline.

### A2 / S1-G3 - Primitive and Indicator Conformance - BLOCKED

Blocked until S1-G2 completion review is accepted.

Required evidence: primitive exact-match tests, point/pip normalization,
session conversion, swing pivots, premium/discount, risk/reward distance,
causal cutoff checks.

### A2 / S1-G4 - Event and State Conformance - BLOCKED

Blocked until S1-G3 passes.

Required evidence: structured BOS/CHoCH/liquidity/FVG/POI/DOL event evidence,
state transition evidence, illegal-transition rejection, duplicate prevention.

### A2 / S1-G5 - Signal and Trade-Plan Conformance - BLOCKED

Blocked until S1-G4 passes.

Required evidence: direction, timestamp, entry, SL, TP, RR, expiration, source
event IDs, and rejection-reason exact matches.

### A2 / S1-G6 - Golden-Case Qualification - BLOCKED

Blocked until S1-G5 passes.

Required evidence: positive, negative, boundary, sequencing, duplicate, and
SL/TP/session-close golden cases.

### A3 / S1-G7 - Historical Baseline - BLOCKED

Blocked until A2 passes. Profit factor and win rate cannot pass A2.

### A3 / S1-G8 - Cost-Adjusted Validation - BLOCKED

Blocked until S1-G7 passes.

### A3 / S1-G9 - Walk-Forward and Out-of-Sample - BLOCKED

Blocked until S1-G8 passes.

### A3 / S1-G10 - Robustness Qualification - BLOCKED

Blocked until S1-G9 passes.

Output after A3 pass: immutable Approved Strategy Package with frozen spec,
version, implementation hash, validation report, statistical report, robustness
report, and approval record.

---

## Stage B - Trading-System Integration and Execution Qualification

### S2-G1 - Execution Development - BLOCKED

Blocked until an Approved Strategy Package exists.

Build only the canonical path:

```text
Signal -> Risk -> Order Intent -> Broker Adapter -> Execution
-> Reconciliation -> Journal -> Reporting
```

Execution must contain zero strategy logic and consume only the Approved Strategy
Package plus configuration.

### S2-G2 - Demo Validation - BLOCKED

Blocked until S2-G1 passes. Broker server name must verify Demo. Strategy remains
frozen; only execution defects may be corrected.

### S2-G3 - Production Promotion - BLOCKED

Blocked until demo evidence and owner approval pass. Promotion requires at least
40 journaled trades, expectancy at least +0.2R, PF at least 1.30, max drawdown no
more than 15%, rule adherence at least 95%, walk-forward PASS, OOS PASS, two clean
weekly reviews, and explicit owner approval.

---

## Archived Historical Evidence

The following remain preserved as evidence, not active roadmap authority:

- ST-C1 v3.7/v3.8: overfiltered/statistically inconclusive.
- ST-C1 v3.9: parked after corrected aggregate net PF 0.138.
- ST-C1 v3.10: parked after corrected aggregate net PF 0.471.
- Legacy M1-M5 roadmap: superseded as the active governance model by
  `MASTER_PLAN.md` v4.0.0.

---

## Cross-Cutting Requirements

Deterministic logic only. Config-driven limits. Unit tests for new logic. Update
docs and status files. One active milestone at a time. Never route on an
unverified environment. Never treat a candidate spec as executable authority.
