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
- **Correction (WO-1, 2026-07-19):** the earlier "workspace VM is down / Git state Not Verified / cannot be committed" language in this package was factually wrong — `git` and `pytest` run directly against this repository; the Cowork sandbox referenced elsewhere is separate, external infrastructure with no bearing on committing to this repo. Struck throughout (§3 step 1, §4, §5, §6). See D-3 below.

---

## 0.1 Owner ruling D-3 — `config/watchlist.yaml` execution-config correction

**Ruling:** `strategy_spec` must name the execution-track spec (`specs/v1.yaml`),
never a research spec — declaring `specs/v3.5.yaml` in an execution config
contradicts ADR-0001's track separation regardless of any runtime interlock
that happens to keep it non-executing today. `autonomy.demo` must read a
proposal-only value; `auto_on_engine_ready` is not a valid pre-promotion state
under ADR-0001 — engine-ready is not execution-authorized.

**Rationale:** this is alignment, not new judgment. It matches the M1
Governance Review's Finding R-3 (spec-authority exposure) and R-4 (autonomy
posture contradiction), both already logged as pre-existing debt, and follows
directly from the execution-track decision in ADR-0001 §Decision.

**Executed under:** WO-1 (this ADR + Change Matrix row 14, below); the config
edit itself is WO-2.

---

## 1. ADR-0001 — Adoption of the Two-Track Strategy Lifecycle

> **Extracted and Accepted (WO-1, 2026-07-19):** see
> `docs/adr/ADR-0001-two-track-strategy-lifecycle.md`, the canonical record.
> This section is retained as drafting history only — the file above governs.

**Status:** ~~Proposed~~ **Accepted** — see `docs/adr/ADR-0001-*.md`.
**Date:** 2026-07-18 (drafted) · Accepted 2026-07-19
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
- (!) ~~Until committed and the VM is restored, this ADR is Proposed, not Accepted.~~ Superseded — Accepted 2026-07-19 (WO-1); see `docs/adr/ADR-0001-*.md`.

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
| 14 | `config/watchlist.yaml` | execution config | `strategy_spec: specs/v3.5.yaml` names a research spec from an execution config; `autonomy.demo: auto_on_engine_ready` permits an unauthorized pre-promotion execution state | Set `strategy_spec: specs/v1.yaml`; set `autonomy.demo` to a proposal-only value; keep `autonomy.live` disabled and `promote_to_live: false` | Correction (D-3) | Yes |

*Note:* no document's **authority order** changes; this package only clarifies track semantics and adds references.

---

## 3. Migration Sequence *(execute only after approval)*

1. **Baseline** — run `git status` + `git log --oneline -5`; capture the current HEAD sha as the rollback anchor. Confirm working tree state.
2. **ADR** — create `docs/adr/ADR-0001-two-track-strategy-lifecycle.md`; set Status: Accepted. → **Commit A**.
3. **Spec metadata** — add the metadata blocks to `specs/v1.yaml`, `specs/v3.5.yaml`, `specs/v3.6.yaml`; run `pytest`. → **Commit B**.
4. **Governance docs** — apply the reference + clarification edits (matrix rows 2–9, 13). → **Commit C**.
5. **Consistency pass** — re-run the Validation Checklist (§4); confirm no same-track contradictions remain.
6. **Report** — produce the closing Session Report.

---

## 4. Validation Checklist

- [x] `git status` shows a known baseline; HEAD sha recorded (WO-1).
- [x] `ADR-0001` exists, Status = Accepted, dated, decision recorded (WO-1 — `docs/adr/ADR-0001-two-track-strategy-lifecycle.md`).
- [ ] Every governance document references ADR-0001.
- [ ] No document states v3.5 is the execution / version-of-record strategy (research only).
- [ ] No document connects a research spec to execution (CHARTER interlock marked superseded).
- [ ] "PROPOSAL-ONLY until Phase 3" stated consistently; no demo auto-execution enabled anywhere.
- [ ] `track` / `status` / `promotion_stage` metadata present and valid in all three specs.
- [ ] `python -m pytest -q` passes (metadata did not break YAML parsing/schema).
- [ ] Authority order (8-level) unchanged and identical across `MASTER_PLAN.md`, `CLAUDE.md`, `project-governance-agent.md`.
- [ ] No same-track contradictions remain (per ADR-0001 conflict rule).

---

## 5. Commit Plan *(atomic, ordered)*

| Commit | Contents | Message |
|---|---|---|
| **A** | `docs/adr/ADR-0001-*.md` | `docs(adr): ADR-0001 adopt two-track strategy lifecycle` |
| **B** | `specs/v1.yaml`, `specs/v3.5.yaml`, `specs/v3.6.yaml` | `chore(specs): add track/status/promotion_stage metadata (ADR-0001)` |
| **C** | `MASTER_PLAN.md`, `CLAUDE.md`, `docs/CHARTER.md`, `docs/RESEARCH-CHARTER.md`, `PROJECT_STATUS.md`, `ROADMAP.md`, `NEXT_ACTION.md`, `AGENT_ALIGNMENT.md`, `docs/MASTER-PLAN.md` | `docs(governance): reference ADR-0001, clarify execution/research tracks` |

Commit B only after `pytest` is green. Commit C only after the Validation Checklist passes.
The earlier governance files (MASTER_PLAN v2.1.1, governance/engineering agent defs) referenced in
the original drafting of this plan are already committed (see `git log` — commit `7512629` and
subsequent); no separate staging decision remains for them.

---

## 6. Rollback Plan

- **Atomic isolation:** A, B, C are independent commits → revert any one with `git revert <sha>` without disturbing the others.
- **Full rollback:** `git revert C B A` (reverse order), or hard-reset to the baseline sha captured in Migration step 1.
- **Low blast radius:** no spec relocation is performed, so there are **no import/path changes to undo**; governance edits are additive/clarifying, so reverting restores prior text with **zero code impact**.
- **Metadata safety net:** if Commit B's spec metadata breaks parsing/schema (caught by `pytest` before Commit C), revert B alone and hand the schema question to Engineering; governance edits (C) can proceed independently since they don't depend on the metadata.

---

## Open confirmations before execution
1. `promotion_stage` value for `specs/v3.5.yaml` — proposed `backtest` (mixed cross-symbol evidence exists; walk-forward not yet passed). Confirm or set. (Batch B, WO-5.)
2. ~~Whether the earlier uncommitted governance files... should be folded into Commit C~~ — moot: those files are already committed (see §5 Commit Plan note).
