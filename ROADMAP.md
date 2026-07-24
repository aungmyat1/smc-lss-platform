# ROADMAP.md - Gate Progress Under MASTER_PLAN v4.1.2

**Authority:** subordinate to `MASTER_PLAN.md`.
**Purpose:** track active milestones, gate progress, and upcoming deliverables.
**Current lifecycle position:** Stage A - Strategy Validation, A1 / S1-G1C -
ST-C3 Logic-Conformance Preparation.

The active governance model is:

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
| Gate | S1-G1C Logic-Conformance Preparation |
| Strategy | ST-C3 v1.0.0 |
| Status | FROZEN -> READY FOR VALIDATION |
| Readiness | GREEN |
| Frozen | YES |
| Implementation | BLOCKED |
| Backtest | BLOCKED |
| A1 Logic Conformance | NOT STARTED: NEXT ACTIVE WORK |
| A2 Signal Conformance | BLOCKED: S1-G1C NOT PASSED |
| A3 Statistical Validation | BLOCKED: A2 NOT PASSED |
| Execution | BLOCKED |
| Demo | BLOCKED |
| Production | BLOCKED |

ST-C3 v1.0.0 is frozen and ready for validation preparation. ST-C2 v1.2.0
remains preserved as the frozen GBPUSD-scoped specification with S1-G2 open,
but new ST-C2 work is paused by owner direction.

---

## Active Milestone

Prepare ST-C3 S1-G1C logic-conformance:

- Verify frozen artifact cross-links.
- Verify YAML structural invariants.
- Prepare the ST-C3 v1.0.0 validation report outline.
- Build logic-conformance checklist against the frozen artifacts.
- Preserve the ST-C3 backtest specification as A3 planning material only.
- Keep proposed execution-agent material blocked until Stage B authorization.

---

## Upcoming Gates

| Order | Gate | Requirement |
|---|---|---|
| 1 | ST-C3 S1-G1C | Logic-conformance closure |
| 2 | ST-C3 S1-G2 | Scoped reference implementation authorization and completion review |
| 3 | ST-C3 S1-G3-S1-G6 | A2 conformance qualification |
| 4 | ST-C3 S1-G7-S1-G10 | A3 statistical edge and robustness qualification |
| 5 | Stage B | Execution development, demo validation, production promotion |

---

## Guardrails

- Frozen ST-C3 strategy logic must not be modified except through a new
  governance-approved revision or candidate lineage.
- No ST-C3 code, tests, kernel, scanner, backtest, broker, demo, live, or
  production work is authorized under this milestone.
- The ST-C3 backtest specification does not authorize backtest execution.
- Frozen ST-C2 strategy content must not be mutated as part of ST-C3 validation
  setup.
