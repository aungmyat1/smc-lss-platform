# PROJECT_STATUS.md - SMC-LSS Platform

**Audit date:** 2026-07-24
**Governance model:** `MASTER_PLAN.md` v4.1.1 Stage A/Stage B validation architecture
**Current lifecycle position:** Stage A - Strategy Validation, A1 / pre-S1-G1 -
ST-C3 Owner Review and Specification Freeze Preparation

This file records current gate state, evidence, blockers, and metrics. It is
subordinate to `MASTER_PLAN.md` and should not duplicate the full lifecycle
rules.

---

## Current State

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
S1-G2 open, but new ST-C2 S1-G2 work is paused by owner direction. This does
not approve, reject, mutate, supersede, or execute ST-C2.

---

## Objective

Prepare ST-C3 for its own S1-G1 specification-freeze decision without changing
frozen ST-C2 strategy content, implementing ST-C3, running backtests, or
granting execution authority.

Current path:

```text
ST-C3 v1.0.0 draft candidate
-> owner review of provisional and unresolved fields
-> S1-G1 specification freeze decision
-> S1-G1C logic-conformance closure
-> S1-G2 scoped reference implementation authorization and completion review
-> A2/S1-G3-S1-G6 conformance qualification
-> A3/S1-G7-S1-G10 statistical edge and robustness qualification
-> Stage B execution qualification
```

---

## Evidence On Record

ST-C3 evidence:

- `docs/adr/ADR-0004-st-c3-candidate-intake.md` - accepted intake ADR.
- `reports/research_log.md` - ST-C3 RCR/intake entry.
- `specs/st-c3_v1.0.0.yaml` - draft candidate specification, not frozen.
- `reports/ST-C3_FUNNEL_OVERHAUL_PLAN.md` - S1-G1 preparation plan.
- `docs/strategy/st_c3/ST-C3_STRATEGY_ARCHITECTURE.md` - foundation architecture.
- `docs/strategy/st_c3/ST-C3_FUNNEL_LIFECYCLE.md` - ordered funnel lifecycle.
- `docs/strategy/st_c3/ST-C3_EVIDENCE_OBJECT_SPEC.md` - evidence object contract.
- `docs/strategy/st_c3/ST-C3_REJECTION_CODE_SPEC.md` - rejection and error codes.
- `docs/strategy/st_c3/ST-C3_PARAMETER_SHEET.md` - provisional machine-ready
  parameter sheet.
- `docs/strategy/st_c3/ST-C3_STATE_MACHINE.md` - deterministic state-machine
  blueprint.
- `docs/reference/smc-definitive-guide-dailypriceaction.md` - source reference.
- `docs/reference/smc-8step-entry-model-dailypriceaction.md` - source reference.

Preserved ST-C2 evidence remains on record but is no longer the active
milestone while this ST-C3 setup task is active.

---

## Blockers

ST-C3 S1-G1 blockers:

- Owner review of section 16 provisional thresholds is incomplete.
- Symbol scope and session windows are unresolved.
- Sweep tolerance, wick ratio, sweep age, `BOS_MIN_IMPULSE`, FVG/OB freshness,
  exact `N_SWEEP`, exact `MAX_ENTRY_BARS`, stop buffer, TP2/TP3 RR floors, and
  portfolio risk controls are unresolved or provisional.
- Validation metrics and floors are unresolved.
- Rejection-code coverage and session-close trigger policy need S1-G1 decisions.
- Proposed ST-C3 agent roles are not yet formalized by ADR-0005.

Stage A2 / A3 / Stage B blockers:

- No frozen ST-C3 specification exists.
- No ST-C3 logic-conformance closure exists.
- No ST-C3 reference kernel, golden-case library, existence scanner, backtest,
  broker integration, demo path, live path, or production path exists or is
  authorized.

---

## Next Action

Continue ST-C3 S1-G1 preparation. Resolve owner decisions for provisional and
unresolved fields, then prepare a freeze audit package. Do not freeze the spec
or authorize implementation until the owner explicitly approves the S1-G1 act.
