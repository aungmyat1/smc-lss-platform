# ADR-0003 — Authorization of ST-C1 Scenario/Conformance Agents

**Status:** Accepted — 2026-07-22, explicit owner confirmation given directly
in the active session.
**Deciders:** Project Owner (Aung Myat); project-governance-agent (reviewed).
**Depends on / interacts with:** ADR-0001 (Accepted, 2026-07-19) — two-track
strategy lifecycle. ADR-0002-DRAFT (Status: DRAFT, never Accepted) — this ADR
explicitly supersedes ADR-0002's "no new agent files are created" clause,
narrowly, per the reasoning below. ADR-0002's other content is unaffected.

---

## Context

Commit `5d681fa` ("Add ST-C1 Scenario Classifier Agent and validation for
v3.10") added three agent files without a preceding ADR or RCR:

- `.claude/agents/st-c1-scenario-classifier-agent.md`
- `.claude/agents/st-c1-conformance-kernel-agent.md`
- `.claude/agents/st-c1-strategy-governance-agent.md`

This created a governance inconsistency: `ADR-0002-DRAFT` (2026-07-18,
still unresolved) had already reasoned through this exact question for a
different four-agent proposal and concluded *"Retain the two-agent
architecture. No new agent files are created"* — specifically to prevent
multiple agents claiming governance authority and reintroducing the
ambiguity ADR-0001 resolved.

`st-c1-strategy-governance-agent.md` already carries a self-documented
"Authorization note" stating it was created "at the direct instruction of
the repo owner... The owner chose to treat that direct instruction as
sufficient authorization rather than filing a separate ADR" — an explicit,
transparent acknowledgement that it bypassed `project-governance-agent.md`'s
Forbidden Action: *"Create additional agent files, or delegate
governance/approval authority to one, without ADR approval."* That note is
evidence of intent, not itself a substitute for the ADR it says was skipped.
This ADR closes that gap for all three files at once, rather than leaving
it as an unreconciled contradiction between ADR-0002's decision and the
committed repo state.

## Decision

**Supersede, narrowly, the "no new agent files are created" clause of
ADR-0002-DRAFT — only for these three files, only under the authority
boundaries below.** ADR-0002's four operational artifacts (task-assignment
schema, completion report, decision format, RCR mechanism) and its
two-agent core (`project-governance-agent` / `trading-engineer-agent`)
are unaffected and remain the canonical meta-governance pair.

The distinction that makes this coherent, already present in each file's
own scope declarations (verified against the committed files, not just
their descriptions):

- **`st-c1-scenario-classifier-agent`** — pure classification. Emits
  structured JSON. Explicitly: does not approve trades, enforce governance,
  edit specs/ADRs/roadmap, create agents, or override
  `project-governance-agent` / `st-c1-strategy-governance-agent`.
- **`st-c1-conformance-kernel-agent`** — mechanical rule enforcement only,
  against already-approved spec/config values. Explicitly: enforces rules,
  never creates them; no ADR/roadmap edits; no new agents; no conflict
  resolution; no override of `project-governance-agent`.
- **`st-c1-strategy-governance-agent`** — holds strategy-level rules of
  record and reviews kernel decisions. Explicitly: does not write execution
  code, does not resolve document-authority conflicts, does not approve
  spec/parameter changes, and does not hold meta-governance authority —
  those remain with `project-governance-agent` and the
  `backtest-researcher` → `validation` pipeline.

None of the three claims the meta-governance powers ADR-0001/ADR-0002
reserve for `project-governance-agent` (document authority, conflict
resolution, roadmap sequencing, ADR approval, or creating further agents).
They are trade/strategy-level mechanical agents operating inside the
research track already authorized by `NEXT_ACTION.md`'s Phase 2 milestone
— not a second governance authority.

### 1. Authority boundaries (binding, restates each file's own scope)

- None of the three may override `project-governance-agent`.
- None may modify `specs/*.yaml` detection logic without an RCR per
  `docs/RESEARCH-CHARTER.md`.
- None may create further agent files.
- None may modify ADRs, `MASTER_PLAN.md`, `ROADMAP.md`, or `NEXT_ACTION.md`.
- `st-c1-conformance-kernel-agent` and `st-c1-strategy-governance-agent`
  must escalate session/spec-config conflicts to `project-governance-agent`
  rather than resolving them.

### 2. Non-overlap guarantee

If `project-governance-agent` and any of these three ever disagree,
`project-governance-agent` wins — consistent with `st-c1-strategy-governance-agent.md`'s
own "Relationship to other authority" section.

### 3. Integration plan

- Agents remain in `.claude/agents/`, orchestration-only per CLAUDE.md's
  Owner Directives (skills/agents may not replace Python modules, duplicate
  strategy logic, bypass validation, or create alternative signal engines).
- No Python modules, kernel implementations, audit-logging code, or
  execution-layer work may be created on the strength of this ADR alone —
  that remains gated on M3 sequencing by `project-governance-agent`
  (see `NEXT_ACTION.md`).
- Any future agent claiming governance/enforcement authority requires its
  own ADR under this same precedent, not an assumption that this ADR
  opens the door generally.

## Consequences

- The three ST-C1 agents become governance-compliant retroactively, closing
  the gap the "Authorization note" in `st-c1-strategy-governance-agent.md`
  flagged but did not itself resolve.
- ADR-0002-DRAFT remains open and unresolved on everything except the
  narrow point superseded here; it still governs any *future* proposal to
  add agent files outside this specific case.
- Phase 2 (v3.9/v3.10 research) work may continue using these agents.
- Phase 3 (execution layer, kernel modules, audit logging) remains blocked
  regardless of this ADR — unaffected, per `NEXT_ACTION.md` and CLAUDE.md's
  Owner Directives.

## Alternatives considered

- **Retire the three agents and fall back to ADR-0002's two-agent
  architecture.** Rejected for now: the agents' existing scope declarations
  already self-limit to exactly the mechanical/non-governance boundary
  ADR-0002 was protecting, so retiring working, correctly-scoped tooling
  has no safety benefit over formally authorizing it.
- **Leave ADR-0002 unresolved and treat the three files as tacitly
  tolerated.** Rejected — this is the exact "silent override" CLAUDE.md's
  conflict-handling rule prohibits.

## Notes

This ADR does not authorize kernel modules, audit logging, scenario-binding
modules, or any `spec_v40`/`ADR_v40`-labeled work. Those remain unauthorized
pending Phase 3 sequencing and, for any detection-logic change, an RCR.
