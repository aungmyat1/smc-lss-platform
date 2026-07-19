# ADR-0002 — Governance Review Report

**Reviewer:** Project Governance Agent
**Date:** 2026-07-18
**Review target:** ADR-0002 — Agent Responsibility Consolidation (+ Reconciliation Notes)
**Repository files modified:** NONE

---

## 0. Review-target verification (read first)

| Path named in task | Verified state |
|---|---|
| `docs/adr/ADR-0002-agent-responsibility-consolidation.md` | **DOES NOT EXIST** |
| `docs/adr/ADR-0002-Reconciliation-Notes.md` | **DOES NOT EXIST** |
| `docs/adr/` directory | **DOES NOT EXIST** — no ADR files anywhere in repo |

Verified 2026-07-18 by exhaustive `**/*.md` enumeration of the repository (a targeted
`**/ADR*` glob returned a false negative; the exhaustive pattern is authoritative).

**Consequence:** this review is performed against the **drafts held in the governance
working folder**, not against repository artifacts. No ADR has entered the repository.
This is correct and expected under the standing "do not modify repository files" hold —
recorded here so the review is not mistaken for a review of committed state.

---

## 1. DECISION

# APPROVE WITH CONDITIONS

ADR-0002 is architecturally and structurally sound and is consistent with the
two-system model, the single-authority chain, and research/execution separation.
It **cannot** be granted unconditional APPROVED status, for five reasons:

1. **Principle 4 cannot be satisfied.** The workspace VM is down (re-verified this
   session), so `git diff`, `git status`, and `pytest` cannot be executed. The evidence
   rule forbids issuing APPROVED without them. Issuing APPROVED here would itself
   violate the principle being applied.
2. Five required amendments are outstanding (§3).
3. ADR-0002 depends on ADR-0001, which is not yet Accepted or committed.
4. The review targets do not exist in the repository (§0).
5. An **unauthorized third agent file** has appeared and must be dispositioned by the
   Owner before agent-scope consolidation can be finalized (§2.2, Finding A-1).

---

## 2. FINDINGS

### 2.1 Architecture assessment — **PASS**

ADR-0002 preserves the two-agent architecture and adds no new agents. Its four
artifacts map cleanly onto the two-system model:

- **System 1 (Research / SVOS / validation)** and **System 2 (Production execution)**
  are separated at the agent layer by the **Research Change Request** mechanism, which
  is the correct control point for a System 1 → System 2 transition. RCR + ADR-0001's
  promotion pipeline together form the only sanctioned path from research into execution.
- The Task Schema / Completion Report / Decision Format triad closes the audit loop
  (assignment → evidence → adjudication) that was previously conversational and therefore
  unauditable.

No architectural objection.

### 2.2 Authority assessment — **CONDITIONAL FAIL**

**Finding A-1 — Unauthorized agent expansion. Severity: HIGH. BLOCKING.**

A third agent file now exists that was **not present** at earlier verification in this
same session:

```
.claude/agents/m1-governance-review-agent.md
```

Earlier enumeration returned exactly two agent files (`project-governance-agent.md`,
`trading-engineer-agent.md`). This file appeared afterwards. It is materially the
`governance-reviewer` role that ADR-0002 **explicitly deferred** in its out-of-scope
register — created without ADR approval.

It self-describes as *"Senior Quant Platform Governance Reviewer"*, operates as a
*"governance gate"*, and issues `APPROVED / PROVISIONALLY APPROVED / REJECTED`
decisions plus M2 authorization. **Two files now claim governance approval authority**,
which is precisely the authority conflict for which the four-agent proposal was
rejected. This violates **Principle 3 (No autonomous agent expansion)** and invalidates
the task's stated premise that the repository contains only two agents.

*In fairness to the content:* the file is high quality and independently corroborates
this reviewer's findings — it predicts the `strategy_spec` authority conflict (its
Step 6), forbids `auto_on_engine_ready` (Step 7), and mandates PROVISIONALLY APPROVED
rather than DONE when tests cannot run (Step 8). The objection is **structural, not
substantive**: correct content introduced through an unapproved channel is still an
uncontrolled governance change.

**Disposition required from Owner** (Governance will not decide unilaterally):
either (a) retire/archive it and fold any needed content into the two canonical agents
under ADR-0002, or (b) formally authorize it via ADR with an explicit precedence rule
resolving which file holds approval authority.

**Finding A-2 — `AGENT_ALIGNMENT.md` contradicts Principle 1. Severity: MEDIUM.**

`AGENT_ALIGNMENT.md` states *"Neither agent overrides the other."* Principle 1 mandates
a strict chain: Owner → Governance Agent → Engineering Agent → Code, in which Governance
**does** outrank Engineering. This is a same-track (governance) contradiction and must be
amended, not interpreted.

**Finding A-3 — Phase 3 naming divergence. Severity: LOW.**

`m1-governance-review-agent.md` names the phase *"Execution Hardening"*; approved
`MASTER_PLAN.md` names it *"Risk Engine"*. Milestone content (M1–M4) is identical across
both. Cosmetic, but should converge on the approved name.

### 2.3 Risk assessment

| ID | Risk | Severity | Category |
|---|---|---|---|
| R-1 | Two files claim governance approval authority (A-1) | **HIGH** | A — introduced now |
| R-2 | Evidence rule unsatisfiable — VM down, no `git diff`/`pytest` | **HIGH** | C — blocking |
| R-3 | `config/watchlist.yaml` declares `strategy_spec: specs/v3.5.yaml` (research spec) in the execution config while `config.load()` defaults to `specs/v1.yaml` — a live Principle 2 exposure | MEDIUM | B — pre-existing debt |
| R-4 | `autonomy.demo: auto_on_engine_ready` contradicts approved proposal-only posture ("engine ready" ≠ "execution authorized") | MEDIUM | B — pre-existing debt |
| R-5 | Git state Not Verified — committed vs uncommitted status of all governance files unknown | MEDIUM | B |
| R-6 | ADR-0002 depends on unapproved ADR-0001 | LOW | sequencing |
| R-7 | `docs/adr/` vs `docs/ADR/` casing unresolved — breaks on case-sensitive CI | LOW | D — future |

R-3 and R-4 are **pre-existing governance debt, non-blocking for ADR-0002**, and remain
tracked under the ADR-0001 package. Neither is authorized for silent repair.

---

## 3. REQUIRED AMENDMENTS

ADR-0002 must incorporate the following five clauses before it may be Accepted.

| # | Clause | Current state in draft | Required action |
|---|---|---|---|
| 1 | **Owner Override Rule** | **ABSENT** | Add: the Owner may override any agent decision at any time. All agent decisions are advisory to the Owner and binding only on agents. |
| 2 | **Authority Precedence Rule** | **PARTIAL** — hierarchy referenced, agent-level precedence unstated; contradicted by `AGENT_ALIGNMENT.md` | Add explicit chain: **Owner > Governance Agent > Engineering Agent > Code.** Governance outranks Engineering on all WHAT/WHY questions. Amend `AGENT_ALIGNMENT.md`'s "neither overrides the other" accordingly (Finding A-2). |
| 3 | **No Autonomous Scope Expansion** | **ABSENT as binding clause** | Add: no agent may create agents, workflows, strategies, execution paths, or governance documents without ADR approval. Finding A-1 demonstrates this gap is already being exercised. |
| 4 | **Diff Evidence Requirement** | **PRESENT but generic** | Strengthen: `git diff` output is a **mandatory returned artifact**, not a generic "diff". APPROVED requires `git diff` + `pytest` result + validation evidence + documentation confirmation. Absent any one → NEEDS REVISION. |
| 5 | **ADR as single source of truth** | **PARTIAL** — stated as rationale, not normative | Elevate to binding: agent files and governance documents **reference** ADRs and must not restate or fork their content. On divergence, the ADR governs. |

---

## 4. FINAL MERGE SEQUENCE

```
ADR-0001  (two-track strategy lifecycle)
    ↓
Owner disposition of m1-governance-review-agent.md   ← gate, Finding A-1
    ↓
ADR-0002  (amended with the five clauses in §3)
    ↓
Agent amendments  (project-governance-agent.md + trading-engineer-agent.md)
    ↓
Phase implementation  (Phase 3 · M2 Risk Validator)
```

**Preconditions for progressing past ADR-0002:**
- Workspace VM restored; `git status` / `git diff` / `pytest -q` executable.
- M1 closed at its verified status: **PROVISIONALLY APPROVED**, not DONE (no test evidence).
- Execution posture unchanged: **proposal-only**. No demo or live execution authorized.

---

## 5. Scope compliance statement

This review recommends **no new agents**, **no relocation of `MASTER_PLAN.md`**, **no
strategy changes**, and **no execution activation**. Finding A-1 concerns disposition of
an agent file that already exists; the decision is reserved to the Owner.
