# CLAUDE.md - SMC-LSS Platform

Institutional Smart Money Concepts (SMC-LSS) trading research and execution
platform.

Goal: a disciplined, config-driven MT5 trading system where strategy validation
comes first and live execution is unlocked only after objective evidence gates
and explicit owner approval. Full authority lives in `MASTER_PLAN.md`; this file
is the AI operating index and hard-rules reminder.

## Document Authority

This file is read first as the entry index, but `MASTER_PLAN.md` is the highest
authority.

1. [`MASTER_PLAN.md`](MASTER_PLAN.md) - AUTHORITATIVE v4.1.0 validation architecture and branch governance model.
2. [`CLAUDE.md`](CLAUDE.md) - AI operating instructions and document index.
3. [`docs/CHARTER.md`](docs/CHARTER.md) - operational safety and promotion gates.
4. [`docs/RESEARCH-CHARTER.md`](docs/RESEARCH-CHARTER.md) - RCR discipline.
5. [`PROJECT_STATUS.md`](PROJECT_STATUS.md) - current gate, evidence, blockers.
6. [`ROADMAP.md`](ROADMAP.md) - gate progress and upcoming deliverables.
7. [`NEXT_ACTION.md`](NEXT_ACTION.md) - exactly one active milestone.
8. Source code.

On conflict: stop, identify it, follow the higher-authority document. Never
silently override governance.

> `docs/MASTER-PLAN.md` is deprecated and superseded by the root
> `MASTER_PLAN.md`.

## Active Lifecycle Model

The active governance model is:

```text
Stage A - Strategy Validation
  A1 - Strategy Logic Contract and Conformance
  A2 - Indicator, Event and Signal Conformance
  A3 - Statistical Edge and Robustness Qualification
Stage B - Trading-System Integration and Execution Qualification
```

Current lifecycle position:

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
| A2 Signal Conformance | IN PROGRESS |
| A3 Statistical Validation | BLOCKED: A2 NOT PASSED |
| Execution | BLOCKED |
| Demo | BLOCKED |
| Production | BLOCKED |

ST-C2 v1.2.0 is the active frozen GBPUSD-scoped specification. Scoped S1-G2
reference implementation is authorized only for golden-case tests, conformance
kernel, minimum GBPUSD detector slice, and the existence check. The first
GBPUSD existence floor is satisfied by a short signal at `2026-06-10 17:15`.
Treat any claim to historical validation, execution, demo, live, or production
authority as a governance conflict until verified in the higher-authority
documents and ADR/RCR records.

## Hard Rules

- Strategy before execution.
- Research before implementation.
- Specification is the source of truth.
- Evidence before approval.
- No implementation before specification freeze.
- No execution before strategy approval.
- No broker integration during Stage A.
- No demo trading before execution validation.
- No production before promotion approval.
- Approved strategies are immutable.
- Every strategy revision requires a new candidate.
- Execution must never duplicate strategy logic.
- Never hardcode strategy values; use approved package plus configuration.
- Stops only tighten. Never widen a stop. Every order carries a stop.
- Never route an order unless the broker server name verifies Demo.
- No live auto-trading until promotion gates and owner approval pass.
- One milestone at a time, as defined by `NEXT_ACTION.md`.
- Nothing is done until required checks pass.

## Stage Responsibilities

Stage A - Strategy Validation:

- freeze candidate specification
- build reference implementation only after freeze and authorization
- close A1 logic conformance
- prove A2 indicator, event, signal, and trade-plan conformance
- run A3 historical replay, statistical, OOS, walk-forward, robustness, and
  sensitivity validation only after A2 passes
- approve or reject the immutable strategy package

SMC-specific implementation skill is required when working inside Stage A
reference implementation, historical validation, backtest diagnosis, and
code/spec conformance because those tasks depend on BOS, CHoCH, liquidity, FVG,
OTE, session, and structural invalidation semantics. It is not required for pure
branch cleanup or governance-document synchronization.

Stage B - Trading-System Integration and Execution Qualification:

- build execution only from an Approved Strategy Package
- keep execution free of duplicated strategy logic
- validate on demo
- promote to production only after evidence gates and explicit owner approval

## Research Discipline

Strategy/spec changes must go through `docs/RESEARCH-CHARTER.md`. No change to
`specs/*.yaml`, detection logic, or tunable strategy behavior is allowed without
the required pre-registered RCR unless it is a pure implementation bug fix
against an already-agreed spec.

## Historical Status

ST-C1 v3.7-v3.10 are parked historical evidence, not active candidates:

- v3.7/v3.8: overfiltered/statistically inconclusive.
- v3.9: corrected aggregate net PF 0.138.
- v3.10: corrected aggregate net PF 0.471.

ST-C2 v1.1.0 is the prior frozen XAUUSD-scoped specification. ST-C2 v1.2.0 is
the active frozen GBPUSD-scoped specification.

## Working Conventions

- Start by reading the governance docs in authority order.
- Check `git status` before work.
- Work only the gate named in `NEXT_ACTION.md`.
- Keep changes scoped to the active milestone.
- For documentation-only governance work, do not modify strategy specs, code,
  YAML parameters, execution state, demo state, or live state.
- For code work, run `python -m pytest -q` before claiming success.
- Skills and agents are orchestration only; they must not replace modules,
  duplicate strategy logic, bypass validation, or grant governance authority.
