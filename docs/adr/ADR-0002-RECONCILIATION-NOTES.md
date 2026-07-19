# ADR-0002 — Reconciliation Notes

**Status:** DRAFT for review. **No repository files have been modified.**
**Companion to:** `ADR-0002-DRAFT-agent-responsibility-consolidation.md`
**Date:** 2026-07-18 · Prepared by Governance Agent

---

## 1. Owner decisions recorded

| # | Decision | Ruling |
|---|---|---|
| D1 | Four proposed agent files vs existing two | **Amend the existing two.** No new agent files. Defer `governance-reviewer.md`, `quant-validator.md`. |
| D2 | Relocate `MASTER_PLAN.md` / `ROADMAP.md` into `docs/` | **Keep at repository root.** Authority references stay valid. |
| D3 | ADR-0002 scope | Limited to four artifacts: Task Schema, Completion Report, Decision Format, RCR. |

## 2. Insertion points (minimal-change principle)

Both edits are **additive section inserts** — no existing section is rewritten,
renumbered, or deleted.

### `.claude/agents/project-governance-agent.md`
- After *Required Workflow* → insert **“Task Assignment Schema”** (ADR-0002 §1).
- After *Session Ending Requirement* → insert **“Governance Decision Format”** (ADR-0002 §3), including the binding Verify-Before-Approval rule.
- After *Conflict Handling* → insert **“Research Change Request”** (ADR-0002 §4).
- In *Authority Rules* → add one line referencing ADR-0001 and ADR-0002.

### `.claude/agents/trading-engineer-agent.md`
- After *Engineering Rules* → insert **“Task Intake”**: refuse work not issued as a conforming TASK; never self-approve.
- After *Testing Requirement* → insert **“Engineering Completion Report”** (ADR-0002 §2).
- Extend *If Direction Conflict Appears* → add the **RCR** path for strategy/spec change requests.
- In *Authority Rules* → add one line referencing ADR-0001 and ADR-0002.

## 3. Document Change Matrix — additional rows

Continues the numbering in the Governance Reconciliation Package (rows 1–13).

| # | Document | Proposed change | Type | Necessary? |
|---|---|---|---|---|
| 14 | `docs/adr/ADR-0002-*.md` | Create ADR-0002 | **NEW** | Yes |
| 15 | `.claude/agents/project-governance-agent.md` | Insert Task Schema, Decision Format + Verify-Before-Approval, RCR gate; ADR refs | Additive | Yes |
| 16 | `.claude/agents/trading-engineer-agent.md` | Insert Task Intake, Completion Report, RCR path; ADR refs | Additive | Yes |

No changes to authority order, phase structure, spec files, or execution posture.

## 4. Sequencing

ADR-0002 is **dependent on ADR-0001** and must not land first — ADR-0002 references
ADR-0001's two-track model and promotion gates.

```
ADR-0001 accepted + committed   (Commit A)
        ↓
spec metadata                   (Commit B)
        ↓
governance doc references       (Commit C)
        ↓
ADR-0002 + agent amendments     (Commit D)  ← this ADR
```

## 5. Commit plan — addition

| Commit | Contents | Message |
|---|---|---|
| **D** | `docs/adr/ADR-0002-*.md`, `.claude/agents/project-governance-agent.md`, `.claude/agents/trading-engineer-agent.md` | `docs(adr): ADR-0002 consolidate agent responsibilities` |

## 6. Validation checklist

- [ ] ADR-0001 is Accepted and committed before Commit D.
- [ ] Exactly two agent files exist in `.claude/agents/` after the change.
- [ ] Only one file claims governance authority.
- [ ] All four artifacts present and identical in wording across both agent files where shared.
- [ ] Both agent files reference ADR-0001 and ADR-0002.
- [ ] No existing section in either agent file was rewritten or deleted (additive only — confirm by `git diff`).
- [ ] `MASTER_PLAN.md` / `ROADMAP.md` still at repository root; authority references unbroken.
- [ ] No change to strategy logic, `specs/*`, execution posture, or authority order.
- [ ] `python -m pytest -q` still green (agent files are not code, but confirm nothing else moved).

## 7. Rollback

Commit D is independent and additive. `git revert <D>` restores both agent files to
their prior state and removes ADR-0002, with **zero code impact** — no source,
spec, or config file is touched by this change.

## 8. Blockers (verified, unchanged)

- **Workspace VM is down** — re-verified this session. `git` and `pytest` cannot run.
- **Git state: Not Verified** — committed vs uncommitted status of all governance
  files remains unknown until the VM is restored.
- Consequence: ADR-0002 cannot be committed, and therefore cannot become
  authoritative under the contract, until the VM is restored.

## 9. Deferred register

Recorded so these are not silently dropped, and not silently adopted either:
`governance-reviewer.md`, `quant-validator.md`, `CHANGELOG.md`, `GOVERNANCE_LOG.md`,
relocation of governance docs into `docs/`, and renaming Phase 3 to "Execution
Hardening". Each requires its own approval if revived.

## 10. Open item carried from the M1 review

The verified `config/watchlist.yaml` findings — `strategy_spec: specs/v3.5.yaml`
(execution config naming the research spec) and `autonomy.demo: auto_on_engine_ready`
(contradicting the approved proposal-only posture) — are **out of scope for ADR-0002**
and remain tracked under the ADR-0001 package. Flagging here only so they are not lost.
