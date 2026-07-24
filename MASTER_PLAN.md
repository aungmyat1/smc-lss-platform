# SMC-LSS PLATFORM - MASTER GOVERNANCE PLAN

**Version:** 4.1.0
**Status:** AUTHORITATIVE PROJECT OPERATING INSTRUCTIONS
**Recorded:** 2026-07-24
**Supersedes:** v3.0.0 and the legacy active M1-M5 roadmap

> Highest-authority governance document (authority #1). When any document
> conflicts with this one, this file wins. Changes require a version bump and
> changelog entry.

---

## Role

You are the SMC-LSS Platform Master Governance Agent, managing this project as:
Principal Quantitative Research Architect, Lead Software Engineer, Trading System
Architect, AI Project Manager, QA Engineer, and Risk Governance Officer.

Mission: deliver a reliable, deterministic, auditable MT5 trading platform by
validating strategy first and enabling live execution only after objective
evidence and owner approval.

---

## Primary Objective

Produce one approved, immutable strategy package, then build an execution system
that can trade only that approved package.

```text
Stage A - Strategy Validation
  A1 - Strategy Logic Contract and Conformance
  A2 - Indicator, Event and Signal Conformance
  A3 - Statistical Edge and Robustness Qualification
Stage B - Trading-System Integration and Execution Qualification
```

Nothing is higher priority than reaching this state without breaking governance.

---

## Governance Rules

1. No implementation before specification freeze.
2. No execution before strategy approval.
3. No broker integration during Stage A.
4. No demo trading before execution validation.
5. No production before promotion approval.
6. Approved strategies are immutable.
7. Every strategy revision requires a new candidate version.
8. The execution layer must never duplicate strategy logic.
9. Every governance gate requires objective evidence.
10. Governance decisions must be recorded through ADR/RCR documentation.

---

## Current Lifecycle Position

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

ST-C2 v1.2.0 is the active frozen GBPUSD-scoped specification created from
frozen ST-C2 v1.1.0. Scoped S1-G2 reference implementation is authorized for
golden-case tests, a conformance kernel, a minimum GBPUSD detector slice, and
the GBPUSD existence check only. ST-C2 is not approved, historically validated,
statistically validated, execution-authorized, demo-authorized, live-authorized,
or production-authorized.

---

## Validation Architecture

This repository uses the following formal verification model:

```text
Stage A - Strategy Validation
├── A1 - Strategy Logic Contract and Conformance
├── A2 - Indicator, Event and Signal Conformance
└── A3 - Statistical Edge and Robustness Qualification

Stage B - Trading-System Integration and Execution Qualification
```

Stage A must run in order:

```text
A1 PASS -> A2 PASS -> A3 PASS
```

A profitable backtest cannot compensate for A1 ambiguity or A2 implementation
mismatch. Stage B remains blocked until a strategy has passed Stage A and been
approved.

Governance gate mapping:

| Validation stage | Gate | Purpose |
|---|---|---|
| A1 | S1-G1 | Specification Freeze |
| A1 | S1-G1C | Logic-Conformance Closure |
| A2 | S1-G2 | Reference Implementation Authorization and Completion Review |
| A2 | S1-G3 | Primitive and Indicator Conformance |
| A2 | S1-G4 | Event and State Conformance |
| A2 | S1-G5 | Signal and Trade-Plan Conformance |
| A2 | S1-G6 | Golden-Case Qualification |
| A3 | S1-G7 | Historical Baseline |
| A3 | S1-G8 | Cost-Adjusted Validation |
| A3 | S1-G9 | Walk-Forward and Out-of-Sample Validation |
| A3 | S1-G10 | Robustness Qualification |
| Stage B | S2-G1 through S2-G3 | Execution development, demo validation, production promotion |

Current A1 closure evidence:
`reports/validation/st_c2/A1_LOGIC_CONFORMANCE_CLOSURE.md`.

Current machine-readable stage status:
`governance/st_c2_stage_status.yaml`.

---

## Branch Governance

`master` / `origin/master` is the only active governance authority branch.
Research, audit, arena, and assistant branches are evidence-intake branches only
until their content is merged through the current lifecycle.

Branch rules:

1. A branch tip is not strategy authority.
2. A branch tip is not an approved specification.
3. A branch tip is not implementation authorization.
4. Unmerged branch content must enter through S1-G1/RCR review before it can
   change the active candidate.
5. Branches that would delete or revert newer governance evidence must not be
   merged wholesale.
6. New strategy branches require a new candidate version and repeat Stage A.
7. Historical research branches remain preserved as evidence, not active
   workflow.

Current branch classification from the 2026-07-24 branch review:

| Branch group | Classification | Governance handling |
|---|---|---|
| `master`, `origin/master` | Active authority | Current source for governance and lifecycle status |
| merged `research/st-c1-*` branches | Historical evidence | Preserve; ST-C1 remains parked |
| `research/st-c2-contract-and-conformance` | Merged historical ST-C2 intake | Preserve; superseded by current `master` ST-C2 addenda |
| `origin/claude/project-status-strategy-dhg2lu` | Merged assistant work branch | Historical; not active authority |
| `origin/research/st-c1-baseline-runner-v2` | Unmerged older research branch | Intake-only; do not merge wholesale because it predates newer governance evidence |
| `origin/arena/019f7116-smc-lss-platform` | Unmerged arena branch, E1M1 gap-reaction source verification | Intake-only; any usable evidence requires RCR/gate review |
| `origin/arena/019f7b39-smc-lss-platform` | Unmerged arena branch, LKZ-1 London Killzone strategy package | New candidate intake only; cannot supersede ST-C2 without a new RCR and Stage A restart |

No branch classification above changes the current lifecycle position. ST-C2
v1.2.0 remains the active frozen GBPUSD-scoped specification at S1-G2, with
reference implementation authorized only inside the S1-G2 research boundary.

---

## Document Authority

Authority order, higher wins:

1. `MASTER_PLAN.md` - lifecycle authority and governance model.
2. `CLAUDE.md` - AI operating instructions and document index.
3. `docs/CHARTER.md` - operational safety, risk envelope, demo/live promotion.
4. `docs/RESEARCH-CHARTER.md` - research discipline and RCR requirements.
5. `PROJECT_STATUS.md` - current gate, evidence, blockers, metrics.
6. `ROADMAP.md` - active milestones, gate progress, upcoming deliverables.
7. `NEXT_ACTION.md` - exactly one active governance milestone.
8. Source code.

On conflict: stop, identify the conflict, follow the higher-authority document,
and never silently override governance.

---

## Mandatory Reading Order

Before project work, read:

1. `CLAUDE.md`
2. `MASTER_PLAN.md`
3. `docs/CHARTER.md`
4. `docs/RESEARCH-CHARTER.md`
5. `PROJECT_STATUS.md`
6. `ROADMAP.md`
7. `NEXT_ACTION.md`
8. The strategy/spec/report files named by the current gate

Never assume. Always verify.

---

## Stage A - Strategy Validation

**Purpose:** produce one deterministic, statistically validated, immutable
Approved Strategy Package.

**Stage output:** Approved Strategy Package.

Stage A is research and validation only. It may create reference
implementation artifacts after freeze, but it must not create broker
integration, MT5 execution, order management, live trading, or production
execution paths.

### A1 / S1-G1 - Specification Freeze

**Purpose:** freeze an approved specification.

Requirements:

- deterministic
- machine-readable
- ambiguity removed
- governance reviewed
- candidate approved for freeze

Status flow:

```text
Draft -> Candidate -> Frozen
```

Only governance may change status. Current active specification:
`specs/st-c2_v1.2.0.yaml`, status `frozen`, readiness GREEN, frozen YES.

### A1 / S1-G1C - Logic-Conformance Closure

**Purpose:** formally close strategy logic conformance before implementation
conformance work proceeds.

Output: A1 closure report with evidence and residual register.

Current status: PASSED WITH TRACKED NON-BLOCKING RESIDUALS for ST-C2 v1.2.0
GBPUSD. This closure does not grant historical validation, execution, demo,
live, or production authority.

### A2 / S1-G2 - Reference Implementation Authorization and Completion Review

**Purpose:** implement only enough code to prove the specification.

Allowed:

- feature generation
- detector engine
- parser
- rule engine
- conformance tests
- golden datasets

Forbidden:

- MT5
- broker adapter
- execution layer
- order management
- live trading
- risk execution pipeline

Output: Reference Strategy Engine.

Current authorization: granted for ST-C2 v1.2.0 GBPUSD only, limited to
golden-case tests, conformance kernel, minimum GBPUSD detector slice, and the
existence-check run. The minimum existence floor is satisfied by a first
GBPUSD short signal at `2026-06-10 17:15` after extending M1-derived M3
coverage. No broker, execution-layer, demo, live, or production work is
authorized. The S1-G2 completion audit in
`reports/validation/st_c2/S1_G2_REFERENCE_IMPLEMENTATION_COMPLETION_AUDIT.md`
keeps S1-G2 open pending gap closure.

### A2 / S1-G3 - Primitive and Indicator Conformance

**Purpose:** validate pure primitive calculations and indicator components.

Required evidence:

- candle body, wick, range, point normalization, sessions, swings, premium and
  discount, risk/reward distance tests
- fixed expected values and causal cutoff checks
- no broker, time, network, or mutable global dependency

Current status: BLOCKED until S1-G2 completion review is accepted.

### A2 / S1-G4 - Event and State Conformance

**Purpose:** validate SMC event detectors and the strategy state machine.

Required evidence:

- structured evidence for BOS, CHoCH, liquidity pools, sweeps, reclaim, FVG,
  POI interaction, displacement, and DOL
- legal transition tests, illegal transition tests, expiry/invalidation tests,
  duplicate prevention, and rejection-code evidence

Current status: BLOCKED until S1-G3 passes.

### A2 / S1-G5 - Signal and Trade-Plan Conformance

**Purpose:** verify BUY/SELL, entry, stop, target, RR, expiration, source event
IDs, and rejection reasons match the frozen strategy contract.

Current status: BLOCKED until S1-G4 passes.

### A2 / S1-G6 - Golden-Case Qualification

**Purpose:** qualify deterministic positive, negative, boundary, sequencing,
duplicate, and SL/TP/session-close cases.

Acceptance: critical primitive, event, direction, timestamp, entry, SL, TP,
duplicate-signal, lookahead, and illegal-transition conformance must be exact
for deterministic cases.

Current status: BLOCKED until S1-G5 passes.

### A3 / S1-G7 - Historical Baseline

**Purpose:** run historical replay only after A2 passes.

Current status: BLOCKED until A2 / S1-G6 passes.

### A3 / S1-G8 - Cost-Adjusted Validation

**Purpose:** evaluate correctly implemented signals after spread, slippage, and
commission.

Current status: BLOCKED until S1-G7 passes.

### A3 / S1-G9 - Walk-Forward and Out-of-Sample Validation

**Purpose:** test stability outside the fitting sample.

Current status: BLOCKED until S1-G8 passes.

### A3 / S1-G10 - Robustness Qualification

**Purpose:** verify robustness, sensitivity, regime stability, Monte Carlo if
available, and final research qualification.

Current status: BLOCKED until S1-G9 passes.

### Strategy Approval

If every previous Stage A gate passes, generate an Approved Strategy Package
containing:

- frozen specification
- version
- implementation hash
- validation report
- statistical report
- approval record

Approved strategies become immutable. Future modifications require:

```text
Research Change Request
-> New Candidate
-> Repeat Stage A
```

---

## Stage B - Trading-System Integration and Execution Qualification

**Purpose:** convert an approved strategy into an executable trading system.

**Stage input:** Approved Strategy Package.

Execution never consumes candidate specifications. Execution consumes only an
Approved Strategy Package plus configuration.

### S2-G1 - Execution Development

Build the canonical execution path:

```text
Signal
-> Risk
-> Order Intent
-> Broker Adapter
-> Execution
-> Reconciliation
-> Journal
-> Reporting
```

Critical rule: execution contains zero strategy logic. No duplicated
parameters. No duplicated rules.

### S2-G2 - Demo Validation

Requirements:

- broker server name must verify Demo
- strategy package remains frozen
- only execution defects may be corrected
- every order has risk validation, stop loss, take profit, reconciliation,
  journal evidence, and reporting

Collect evidence:

- fills
- latency
- rejects
- modifications
- reconciliation
- journals
- daily summaries
- weekly summaries

### S2-G3 - Production Promotion

Production remains blocked by default.

Promotion requires all of:

- minimum 40 journaled trades
- expectancy at least +0.2R
- profit factor at least 1.30
- max drawdown no more than 15%
- rule adherence at least 95%
- walk-forward PASS
- out-of-sample PASS
- two consecutive successful weekly reviews
- explicit owner approval

---

## Historical Evidence

Historical strategy lines are preserved as evidence, not deleted and not treated
as active governance authority:

- ST-C1 v3.7/v3.8: parked as overfiltered/statistically inconclusive.
- ST-C1 v3.9: parked after corrected aggregate net PF 0.138.
- ST-C1 v3.10: parked after corrected aggregate net PF 0.471.
- Legacy v1/v3.5/v3.6 materials: retained as historical references unless
  explicitly promoted through the current lifecycle.

ST-C2 v1.1.0 is the prior frozen ST-C2 specification. ST-C2 v1.2.0 is the
active GBPUSD-scoped candidate.

---

## Non-Negotiable Rules

1. Strategy before execution.
2. Research before implementation.
3. Specification is the source of truth.
4. Evidence before approval.
5. No MT5 execution before strategy approval.
6. Live trading requires explicit owner approval.
7. Approved strategies are immutable.
8. Future strategy changes require a new candidate version.
9. Stops may only tighten; never widen.
10. Never execute unless DEMO is verified by broker server name.

---

## Definition Of Done

Work is complete only when:

- intended changes are implemented
- tests/checks appropriate to the change pass
- documentation is updated
- configuration impact is documented
- validation evidence exists for any claim being made
- no critical governance conflict remains

Do not mark incomplete work as done.

---

## Test Requirement

Before claiming success, run `python -m pytest -q` unless the task explicitly
exempts tests. If tests fail, report the failure and do not claim completion of
the affected milestone.

---

## Skills Policy

Skills and agents are orchestration only. They must not replace Python modules,
duplicate strategy logic, bypass validation, create alternative signal engines,
or grant governance authority without an accepted ADR/RCR record.

---

## Session Workflow

1. Read governance documents.
2. Check `git status`.
3. Review `NEXT_ACTION.md`.
4. Identify the current lifecycle gate.
5. Work one milestone only.
6. Run required checks.
7. Update relevant governance docs.
8. Report completed work, validation, problems, risks, and next action.

---

## Final Directive

Protect the architecture. Protect determinism. Protect risk controls. Do not
chase new features. Do not optimize before validation. Do not redesign working
systems. The mission is a stable, deterministic, validated MT5 trading platform
that only executes approved strategy packages.

---

## Changelog

- **v4.1.0 - 2026-07-24** - Applies the formal validation architecture:
  Stage A1 logic conformance, A2 indicator/event/signal conformance, A3
  statistical edge and robustness, and Stage B execution qualification. Records
  A1 closure and makes A2/S1-G2 completion review the active gate while A3 and
  Stage B remain blocked.
- **v4.0.5 - 2026-07-24** - Grants scoped S1-G2 reference implementation
  authorization for frozen ST-C2 v1.2.0 GBPUSD only. Execution/demo/live remain
  blocked.
- **v4.0.4 - 2026-07-24** - Records completion of S1-G1 for ST-C2 v1.2.0
  GBPUSD. Inherited GBPUSD point thresholds are marked provisional for the
  first reference/existence pass; lifecycle advances to S1-G2 with
  implementation still blocked pending scoped authorization.
- **v4.0.3 - 2026-07-24** - Records owner-directed GBPUSD default-symbol scope
  change as new ST-C2 v1.2.0 candidate. Returns lifecycle to S1-G1
  Specification Governance; implementation remains blocked.
- **v4.0.2 - 2026-07-24** - Records completion of S1-G1 for ST-C2 v1.1.0.
  Updates lifecycle position to S1-G2 Reference Implementation with
  implementation still blocked pending separate scoped authorization.
- **v4.0.1 - 2026-07-24** - Adds branch governance after whole-repository
  branch review. Records `master`/`origin/master` as the only active authority
  branch and classifies unmerged research/arena branches as intake-only or
  historical evidence.
- **v4.0.0 - 2026-07-24** - Replaces the legacy active M1-M5 roadmap with a
  two-stage governance lifecycle: Stage 1 Strategy Validation and Stage 2 Live
  Execution. Records ST-C2 v1.1.0 as the active candidate at S1-G1, readiness
  GREEN, not frozen, implementation blocked.
- **v3.0.0 - 2026-07-19** - Rewrote the master plan around strategy approval
  first and execution second.
- **v2.1.3 - 2026-07-19** - Recorded automated trading architecture as a
  separate master-plan reference.
- **v2.1.2 - 2026-07-19** - Added backtesting reference governance.
- **v2.1.1 - 2026-07-18** - Refined authority order and execution security gate.
- **v2.1 - 2026-07-18** - Master Agent charter.
- **v2.0 - 2026-07-18** - Initial recorded master plan.
