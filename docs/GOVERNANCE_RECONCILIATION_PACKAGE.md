# Governance Reconciliation Package — v1 (FOR REVIEW)

**Status:** DRAFT — awaiting owner approval. **No repository files have been modified.**
**Date:** 2026-07-18 · **Prepared by:** Governance Agent
**Basis:** Governance Alignment Directive + approved revisions 1–6.

## 0. Scope & standing constraints
- **No `specs/` relocation.** Flat paths kept (`specs/v1.yaml`, `specs/v3.5.yaml`, `specs/v3.6.yaml`); track metadata added in place. Restructuring deferred to Engineering (future ADR).
- **ADR-0001 is created first;** governance docs *reference* it rather than embedding history.
- **Minimal edits** — clarify tracks + add ADR reference; no wholesale rewrites unless a factual contradiction requires it.
- **Telegram is out of governance scope** — it belongs to the execution roadmap.
- **Execution posture: PROPOSAL-ONLY** until Phase 3 Risk Engine + validation gates pass. **No automatic MT5 demo execution is authorized.**
- **Blocked prerequisites (verified this session):** workspace VM is down; Git state is **Not Verified**. Nothing in this package can be committed — and therefore cannot become authoritative under the contract — until the VM is restored and `git` is verified.

---

## 1. ADR-0001 — Adoption of the Two-Track Strategy Lifecycle

> Proposed location: `docs/adr/ADR-0001-two-track-strategy-lifecycle.md`

**Status:** Proposed → becomes **Accepted** on owner approval + git commit.
**Date:** 2026-07-18
**Deciders:** Project Owner (Aung); Governance Agent.

**Context.** The repository accumulated conflicting statements about which strategy is authoritative. Verified in the Governance Verification Report (2026-07-18): `docs/CHARTER.md` names `specs/v3.5.yaml` the "version of record" and wires demo auto-execution to its `engine_implements_spec` flag; `MASTER_PLAN.md` names `specs/v1.yaml` the execution authority; `CLAUDE.md` contains both claims. Root cause: no explicit separation between the strategy that *executes* and the strategy under *research*.

**Decision.** Adopt a two-track strategy lifecycle:
- **Execution Track** — `specs/v1.yaml` is the **sole execution authority**; only it may generate executable trading signals. Changes require validation + governance approval + git commit + an ADR.
- **Research Track** — `specs/v3.5.yaml` and `specs/v3.6.yaml` are **research-only** and may never execute trades.
- **No research strategy may be connected directly to execution.**
- **Promotion pipeline:** Research → Backtest → Walk-Forward Validation → Demo Validation → Governance Review → Promotion → **new Execution Release** (`v1.1`, `v1.2`, …). Research version numbers are never deployed directly.
- **Conflict-interpretation rule:** a document saying v3.5 is research while another says v1 is execution is **not** a contradiction. Only disagreements **within the same track** warrant a Governance Conflict Report.
- **Execution posture:** PROPOSAL-ONLY until Phase 3 Risk Engine + validation gates pass; no automatic MT5 demo execution authorized.
- **Spec metadata:** each spec file carries `track`, `status`, `promotion_stage`.
- **Telegram** is execution infrastructure, outside governance scope.

**Consequences.**
- (+) Eliminates the v1/v3.5 ambiguity; one execution authority.
- (+) Research can iterate freely without touching execution.
- (+) Explicit, auditable promotion gates.
- (−) `docs/CHARTER.md` autonomy wording must be clarified (the v3.5 `engine_implements_spec` interlock no longer governs execution).
- (−) Spec relocation is deferred (separate Engineering ADR).
- (!) Until committed and the VM is restored, this ADR is **Proposed**, not Accepted.

---

## 2. Document Change Matrix

| # | Document | Authority | Current issue | Proposed change | Type | Necessary? |
|---|---|---|---|---|---|---|
| 1 | `docs/adr/ADR-0001-*.md` | decision record | absent | Create ADR-0001 (§1) | **NEW** | Yes (prereq) |
| 2 | `MASTER_PLAN.md` | 1 | Self-declares authoritative; no two-track/promotion model | Add ADR-0001 reference; add short Two-Track + Promotion note; soften "AUTHORITATIVE" to "ratified on commit + ADR" | Clarify + ref | Yes |
| 3 | `CLAUDE.md` | 2 | Internal contradiction: "Spec version status" calls v3.5 version-of-record + stale "targets v3.5" line | Add ADR-0001 ref; correct those lines to two-track (exec=v1, research=v3.5) | Necessary edit | Yes |
| 4 | `docs/CHARTER.md` | 3 | Wires demo auto-exec to v3.5 `engine_implements_spec`; calls v3.5 version-of-record | Add ADR-0001 ref; state exec authority=v1; v3.5 research-only (no execution); mark v3.5 autonomy interlock **superseded by ADR-0001**; note proposal-only until Phase 3 | Clarify + ref (no full rewrite) | Yes |
| 5 | `docs/RESEARCH-CHARTER.md` | 4 | Silent on promotion → v1.x | Add ADR-0001 ref; note research promotes to a new v1.x execution release | Ref | Yes |
| 6 | `PROJECT_STATUS.md` | 5 | Describes v3.5 as version-of-record; M0 backtest as next | Add ADR-0001 ref; restate tracks; exec=v1; current = Phase 3/M1 | Clarify + ref | Yes |
| 7 | `ROADMAP.md` | 6 | Execution-only phases; no research/promotion track | Add ADR-0001 ref; append Research Track + promotion pipeline; keep Phase 3/M1 current | Ref + append | Yes |
| 8 | `NEXT_ACTION.md` | 7 | OK (M1) | Add ADR-0001 ref; reaffirm proposal-only posture | Minor ref | Optional |
| 9 | `AGENT_ALIGNMENT.md` | contract | Lists tracks without ADR | Add ADR-0001 ref | Ref | Yes |
| 10 | `specs/v1.yaml` | exec spec | No track metadata | Add `track: execution`, `status: active`, `promotion_stage: deployed` | Metadata | Yes |
| 11 | `specs/v3.5.yaml` | research spec | No track metadata | Add `track: research`, `status: research_candidate`, `promotion_stage: backtest` *(confirm value)* | Metadata | Yes |
| 12 | `specs/v3.6.yaml` | research spec | No track metadata | Add `track: research`, `status: draft`, `promotion_stage: research` | Metadata | Yes |
| 13 | `docs/MASTER-PLAN.md` | deprecated | Banner present | Add ADR-0001 ref to banner | Ref | Optional |

*Note:* no document's **authority order** changes; this package only clarifies track semantics and adds references.

---

## 3. Migration Sequence *(execute only after approval AND VM restored)*

1. **Baseline** — restore VM; run `git status` + `git log --oneline -5`; capture the current HEAD sha as the rollback anchor. Confirm working tree state (this replaces today's "Not Verified").
2. **ADR** — create `docs/adr/ADR-0001-two-track-strategy-lifecycle.md`; set Status: Accepted. → **Commit A**.
3. **Spec metadata** — add the metadata blocks to `specs/v1.yaml`, `specs/v3.5.yaml`, `specs/v3.6.yaml`; run `pytest`. → **Commit B**.
4. **Governance docs** — apply the reference + clarification edits (matrix rows 2–9, 13). → **Commit C**.
5. **Consistency pass** — re-run the Validation Checklist (§4); confirm no same-track contradictions remain.
6. **Report** — produce the closing Session Report.

---

## 4. Validation Checklist

- [ ] VM restored; `git status` shows a known baseline; HEAD sha recorded.
- [ ] `ADR-0001` exists, Status = Accepted, dated, decision recorded.
- [ ] Every governance document references ADR-0001.
- [ ] No document states v3.5 is the execution / version-of-record strategy (research only).
- [ ] No document connects a research spec to execution (CHARTER interlock marked superseded).
- [ ] "PROPOSAL-ONLY until Phase 3" stated consistently; no demo auto-execution enabled anywhere.
- [ ] `track` / `status` / `promotion_stage` metadata present and valid in all three specs.
- [ ] `python -m pytest -q` passes (metadata did not break YAML parsing/schema).
- [ ] Authority order (8-level) unchanged and identical across `MASTER_PLAN.md`, `CLAUDE.md`, `project-governance-agent.md`.
- [ ] No same-track contradictions remain (per ADR-0001 conflict rule).

---

## 5. Commit Plan *(atomic, ordered — requires VM)*

| Commit | Contents | Message |
|---|---|---|
| **A** | `docs/adr/ADR-0001-*.md` | `docs(adr): ADR-0001 adopt two-track strategy lifecycle` |
| **B** | `specs/v1.yaml`, `specs/v3.5.yaml`, `specs/v3.6.yaml` | `chore(specs): add track/status/promotion_stage metadata (ADR-0001)` |
| **C** | `MASTER_PLAN.md`, `CLAUDE.md`, `docs/CHARTER.md`, `docs/RESEARCH-CHARTER.md`, `PROJECT_STATUS.md`, `ROADMAP.md`, `NEXT_ACTION.md`, `AGENT_ALIGNMENT.md`, `docs/MASTER-PLAN.md` | `docs(governance): reference ADR-0001, clarify execution/research tracks` |

Commit B only after `pytest` is green. Commit C only after the Validation Checklist passes.
Also stages the earlier uncommitted governance files (MASTER_PLAN v2.1.1, governance/engineering agent defs) — confirm they belong in Commit C or a preceding commit once Git state is verified.

---

## 6. Rollback Plan

- **Atomic isolation:** A, B, C are independent commits → revert any one with `git revert <sha>` without disturbing the others.
- **Full rollback:** `git revert C B A` (reverse order), or hard-reset to the baseline sha captured in Migration step 1.
- **Low blast radius:** no spec relocation is performed, so there are **no import/path changes to undo**; governance edits are additive/clarifying, so reverting restores prior text with **zero code impact**.
- **Metadata safety net:** if Commit B's spec metadata breaks parsing/schema (caught by `pytest` before Commit C), revert B alone and hand the schema question to Engineering; governance edits (C) can proceed independently since they don't depend on the metadata.
- **Requires VM** for all `git` operations.

---

## Open confirmations before execution
1. `promotion_stage` value for `specs/v3.5.yaml` — proposed `backtest` (mixed cross-symbol evidence exists; walk-forward not yet passed). Confirm or set.
2. Whether the **earlier uncommitted** governance files (MASTER_PLAN v2.1.1, `project-governance-agent.md`, `AGENT_ALIGNMENT.md`) should be folded into Commit C or committed first — resolvable once Git state is verified.
