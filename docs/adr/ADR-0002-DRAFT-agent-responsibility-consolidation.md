# ADR-0002 — Agent Responsibility Consolidation

**Status:** DRAFT — awaiting owner approval. Becomes *Accepted* on approval + git commit.
**Proposed location:** `docs/adr/ADR-0002-agent-responsibility-consolidation.md`
**Date:** 2026-07-18
**Deciders:** Project Owner (Aung); Governance Agent
**Depends on:** ADR-0001 (two-track strategy lifecycle) — must be Accepted first.

---

## Context

A four-agent architecture was proposed (`project-manager.md`, `code-engineer.md`,
`governance-reviewer.md`, `quant-validator.md`). Repository verification (2026-07-18)
established that a functioning two-agent pair already exists:

- `.claude/agents/project-governance-agent.md` — governance / PM authority.
- `.claude/agents/trading-engineer-agent.md` — engineering implementation. Verified to
  already encode: `specs/v1.yaml` as execution authority; v3.5/v3.6 "must not be
  connected to execution without approval"; no direct Signal→Broker path; demo
  verification by broker server name (never `account_type`); mandatory `pytest`; git
  discipline; STOP-and-report on governance conflict.

Adopting the four proposed files would create **six agent files with three claiming
governance authority** — reintroducing the authority ambiguity that ADR-0001 resolved.

However, the proposal contained four operational artifacts the current agents lack:
a task-assignment schema, a completion-report format, a decision format, and a
research-change-request mechanism. These close a real gap: today, task hand-off and
approval are conversational and therefore unauditable, and nothing structurally
prevents an agent from self-approving its own work.

## Decision

**Retain the two-agent architecture.** No new agent files are created. The canonical
pair remains `project-governance-agent.md` (decides WHAT and WHY) and
`trading-engineer-agent.md` (implements HOW), consistent with `AGENT_ALIGNMENT.md`.

**Integrate exactly four artifacts** into the existing two files, and nothing else.

### 1. Engineering Task Assignment Schema — Governance → Engineering

Governance issues work only in this form. Engineering must refuse work that does not
conform.

```
TASK ID:             TASK-<MILESTONE>-<NNN>        e.g. TASK-M2-001
Objective:           one sentence — outcome, not method
Reason:              why now; milestone + ADR reference
Allowed Changes:     explicit file/directory allowlist
Forbidden Changes:   explicit denylist (strategy logic, specs/*, governance docs)
Files Expected:      anticipated files (informational, not binding)
Acceptance Criteria: objectively checkable conditions
Validation Required: exact commands to run + evidence to return
Rollback Plan:       how to revert
Authorized By:       ADR / owner approval reference
```

### 2. Engineering Completion Report — Engineering → Governance

Engineering returns this on task completion. Absent or incomplete → automatic
NEEDS REVISION.

```
Engineering Completion Report
Task:                 TASK-<...>
Files Changed:        path + one-line note each
Implementation:       what was done
Tests:                added / total / pass-fail; exact command + output summary
Validation:           evidence mapped to each acceptance criterion
Git Status:           modified / new / untracked; commit sha if committed
Potential Risks:
Rollback:
Ready for PM Review:  YES / NO
```

### 3. Governance Decision Format — Governance → Owner / Engineering

```
## Project Decision
Task / Milestone:
Status:       APPROVED | REJECTED | NEEDS REVISION
Evidence:     what was verified, and how
Findings:
Conditions:   (required if NEEDS REVISION)
Next Action:
```

**Verify-Before-Approval rule (binding):** no status may be issued on assertion alone.
APPROVED requires verified evidence — diff, test results, validation output, and
documentation update. A claim of "done", "working", or "ready" without evidence is
not approvable.

### 4. Research Change Request (RCR) mechanism

**Trigger:** any proposed change to strategy logic, SMC definitions, `specs/*.yaml`,
indicators, parameters, or optimization. Engineering **must not implement** such a
change; it raises an RCR and stops.

```
RESEARCH CHANGE REQUEST
RCR ID:              RCR-<NNN>
Raised By:
Target Spec:         specs/v3.5.yaml (research) | specs/v1.yaml (execution)
Current Behavior:
Proposed Change:
Hypothesis:
Evidence Required:   backtest / walk-forward / out-of-sample
Expected Improvement:
Success Criteria:    expectancy >= +0.2R, PF >= 1.3, >= 30 trades, OOS, max DD <= 15%
Rollback:
Governance Decision: PENDING | APPROVED | REJECTED
```

RCRs route through `docs/RESEARCH-CHARTER.md`'s six-question template and are logged
to `reports/research_log.md` **before** any backtest. A change targeting the
*execution* spec additionally requires its own ADR and the ADR-0001 promotion path —
research specs are never promoted by number.

### Placement

| Artifact | `project-governance-agent.md` | `trading-engineer-agent.md` |
|---|---|---|
| 1 · Task Schema | **Authoring template** | Reference — refuse non-conforming tasks |
| 2 · Completion Report | Review checklist against it | **Output template** |
| 3 · Decision Format | **Output template** | Reference — never self-approve |
| 4 · RCR | **Owns the gate and decision** | Must raise + STOP; never implement |

## Consequences

**Positive.** Task lifecycle becomes auditable end to end (task → report → decision).
The Verify-Before-Approval rule closes the self-approval loophole structurally.
Acceptance criteria become objectively checkable rather than conversational. The RCR
mechanism gives strategy-contamination a defined refusal path instead of relying on
agent judgment.

**Negative.** Adds process overhead to every task. Two files must stay in sync —
mitigated by both referencing this ADR rather than duplicating its content.

**Neutral.** No change to the authority hierarchy, phase structure, or execution
posture. Execution remains **proposal-only** pending Phase 3 completion (ADR-0001).

## Explicitly out of scope

Not adopted, deferred pending demonstrated need (MASTER_PLAN non-goals forbid gold
plating): `governance-reviewer.md`, `quant-validator.md`, `CHANGELOG.md`,
`GOVERNANCE_LOG.md`.

Not changed: `MASTER_PLAN.md` and `ROADMAP.md` remain at **repository root** (owner
ruling — relocation would break every authority reference). Phase 3 retains the name
**"Risk Engine"**; "Execution Hardening" is noted as an informal alias only.

Not included here: the verified `config/watchlist.yaml` findings (execution config
naming a research spec; `autonomy.demo: auto_on_engine_ready` contradicting
proposal-only). Those belong to the ADR-0001 reconciliation package and are tracked
there, not in this ADR.
