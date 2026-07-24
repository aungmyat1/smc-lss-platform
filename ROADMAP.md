# ROADMAP.md - Gate Progress Under MASTER_PLAN v4.0.0

**Authority:** subordinate to `MASTER_PLAN.md`.
**Purpose:** track active milestones, gate progress, and upcoming deliverables.
**Current lifecycle position:** Stage 1 - Strategy Validation, S1-G2 -
Reference Implementation.

The legacy active M1-M5 roadmap is archived. The active governance model is now:

```text
Stage 1 - Strategy Validation
Stage 2 - Live Execution
```

---

## Current Position

| Field | State |
|---|---|
| Stage | Strategy Validation |
| Gate | S1-G2 Reference Implementation |
| Strategy | ST-C2 v1.1.0 |
| Status | Frozen |
| Readiness | GREEN |
| Frozen | YES |
| Implementation | BLOCKED |
| Historical Validation | BLOCKED |
| Execution | BLOCKED |
| Demo | BLOCKED |
| Production | BLOCKED |

ST-C2 readiness is green because the original numbered checklist in
`reports/ST-C2_SPEC_AUDIT.md` is closed and
`reports/ST-C2_IMPLEMENTATION_READINESS.md` reports READY FOR IMPLEMENTATION.
The S1-G1 freeze act is now recorded, but implementation authorization remains
blocked.

---

## Stage 1 - Strategy Validation

### S1-G1 - Specification Governance - COMPLETE

Goal: freeze one deterministic, machine-readable specification.

Current evidence:

- `specs/st-c2_v1.1.0.yaml` exists as the consolidated candidate.
- `reports/ST-C2_SPEC_AUDIT.md` records all original checklist items closed.
- `reports/ST-C2_IMPLEMENTATION_READINESS.md` records readiness GREEN.
- `reports/research_log.md` records the ST-C2 addendum chain through the
  eleventh addendum.

Completed:

- `specs/st-c2_v1.1.0.yaml` is promoted to `status: frozen`.
- Freeze is recorded in `reports/audit/ST_C2_HYBRID_LIQUIDITY_FIRST_RCR.md`
  and `reports/research_log.md`.
- MF-to-LTF structural inheritance and liquidity-tagging consistency remain
  unapplied new-scope proposals.
- R1-R7 rejection-code coverage gap and session-close points/pips note remain
  non-blocking implementation-time residuals.

Non-blocking carry-forward items:

- MF-to-LTF structural inheritance and liquidity-tagging consistency remain
  unapplied new-scope proposals.
- R1-R7 rejection-code coverage gap and session-close points/pips note remain
  implementation-time residuals.

### S1-G2 - Reference Implementation - CURRENT, BLOCKED

Blocked until scoped implementation authorization is granted.

Allowed after authorization: feature generation, detector engine, parser, rule
engine, conformance tests, golden datasets.

Forbidden in this gate: MT5, broker adapter, execution layer, order management,
live trading, risk execution pipeline.

### S1-G3 - Historical Validation - BLOCKED

Blocked until a reference implementation exists.

Required evidence: replay, deterministic outputs, trade journal, rejection
codes, conformance audit, rule coverage, and feature coverage.

### S1-G4 - Statistical Validation - BLOCKED

Blocked until S1-G3 evidence exists.

Required evidence: trade count, expectancy, profit factor, drawdown, Sharpe or
equivalent, net after costs, walk-forward, out-of-sample, robustness,
sensitivity, and Monte Carlo if available.

### S1-G5 - Strategy Approval - BLOCKED

Blocked until all previous Stage 1 gates pass.

Output: immutable Approved Strategy Package with frozen spec, version,
implementation hash, validation report, statistical report, and approval record.

---

## Stage 2 - Live Execution

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
