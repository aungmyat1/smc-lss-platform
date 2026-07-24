# ROADMAP.md - Gate Progress Under MASTER_PLAN v4.1.1

**Authority:** subordinate to `MASTER_PLAN.md`.
**Purpose:** track active milestones, gate progress, and upcoming deliverables.
**Current lifecycle position:** Stage A - Strategy Validation, A1 / pre-S1-G1 -
ST-C3 Owner Review and Specification Freeze Preparation.

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
| Substage | A1 - Strategy Logic Contract and Conformance |
| Gate | Pre-S1-G1 Owner Review / Specification Freeze Preparation |
| Strategy | ST-C3 v1.0.0 |
| Status | Draft |
| Readiness | YELLOW |
| Frozen | NO |
| Implementation | BLOCKED |
| Backtest | BLOCKED |
| A1 Logic Conformance | NOT STARTED |
| A2 Signal Conformance | BLOCKED: S1-G1 NOT PASSED |
| A3 Statistical Validation | BLOCKED: A2 NOT PASSED |
| Execution | BLOCKED |
| Demo | BLOCKED |
| Production | BLOCKED |

ST-C3 v1.0.0 is the active owner-directed setup track for S1-G1 preparation.
ST-C2 v1.2.0 remains preserved as the frozen GBPUSD-scoped specification with
S1-G2 open, but new ST-C2 S1-G2 work is paused by owner direction.

---

## Active Milestone

Prepare ST-C3 for S1-G1 specification freeze:

- Review and resolve provisional thresholds.
- Keep the four ST-C3 foundation documents aligned with the draft spec:
  strategy architecture, funnel lifecycle, evidence object specification, and
  rejection code specification.
- Keep the ST-C3 parameter sheet aligned with the draft spec.
- Keep the ST-C3 state machine aligned with lifecycle, evidence, rejection,
  termination, and trade-plan contracts.
- Decide instrument scope and session windows.
- Decide portfolio risk controls.
- Confirm `F1`/`F2`/`F3` labels from ADR-0004.
- Decide whether ADR-0005 should formalize the proposed ST-C3 agent roster.
- Prepare the S1-G1 audit package without freezing the spec yet.

---

## Upcoming Gates

| Order | Gate | Requirement |
|---|---|---|
| 1 | ST-C3 S1-G1 | Specification freeze after owner-approved decisions |
| 2 | ST-C3 S1-G1C | Logic-conformance closure |
| 3 | ST-C3 S1-G2 | Scoped reference implementation authorization and completion review |
| 4 | ST-C3 S1-G3-S1-G6 | A2 conformance qualification |
| 5 | ST-C3 S1-G7-S1-G10 | A3 statistical edge and robustness qualification |
| 6 | Stage B | Execution development, demo validation, production promotion |

---

## Guardrails

- ST-C3 remains draft until the S1-G1 freeze act is explicitly approved.
- No ST-C3 code, tests, kernel, scanner, backtest, broker, demo, live, or
  production work is authorized under this milestone.
- Frozen ST-C2 strategy content must not be mutated as part of ST-C3 setup.
