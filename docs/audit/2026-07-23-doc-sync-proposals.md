# Documentation Sync — Authority-Touching Proposals (2026-07-23)

**Status:** DRAFT — proposals only. **No source file has been modified for F1, F2, or F7.**
These three findings touch authority-hierarchy documents (`CLAUDE.md`, `MASTER_PLAN.md`,
`docs/CHARTER.md`) and are therefore left for explicit owner review and approval before
any edit is applied. The routine findings (F3, F4, F5, F6, F8, F9) were applied directly
to their source files in the same pass; this file covers only the draft-only set.

Each item below quotes the EXACT current text as read from the live file, gives a
one-line rationale, and provides the full proposed replacement text.

---

## F1 — `CLAUDE.md` "Spec version status" section

**Rationale:** Section calls `specs/v3.5.yaml` the "version of record," which contradicts
the higher-authority Accepted `ADR-0001` (2026-07-19) and `MASTER_PLAN.md` v3.0.0 —
under ADR-0001 the sole execution authority is `specs/v1.yaml` and v3.5 is research-only.
The section is also stale on the research line (references v3.5/v3.6 only; the research
line has since progressed through ST-C1 v3.7–v3.10, all parked, to ST-C2).

**EXACT current text (verbatim, `CLAUDE.md` lines 68–78):**

```
## Spec version status (resolved 2026-07-18 re-audit)
`specs/v3.5.yaml` is the version of record (per `docs/CHARTER.md`), backed by a
working formula layer + backtest harness (`signal_v35.py`, `backtest_v35.py`,
28 passing tests) but still `RESEARCH_CANDIDATE` — `engine_implements_spec` stays
`false` until the promotion gate in `ROADMAP.md` M1.5 is cleared with logged
evidence, not decided ad hoc. `specs/v1.yaml` is legacy — it's what
`live_signal.py`/`smc_master.py` actually execute today, and stays canonical for
that live path until v3.5 is promoted and those modules are rewired. `specs/v3.6.yaml`
is research-only (IFVG spec), unimplemented, not on the roadmap yet. `ROADMAP.md`
and `NEXT_ACTION.md` were rewritten this audit to target v3.5 going forward — see
`PROJECT_STATUS.md` §1 for the full picture of what changed and why.
```

**Proposed replacement text:**

```
## Spec version status (resolved per ADR-0001; research line updated 2026-07-23)
Execution authority is `specs/v1.yaml` — the legacy spec, and per
`docs/adr/ADR-0001-two-track-strategy-lifecycle.md` (Accepted 2026-07-19) the
**sole execution authority**. It is what `live_signal.py`/`smc_master.py` actually
execute today and stays canonical for that live path until a research candidate is
promoted through the ADR-0001 pipeline into a new versioned execution release
(`v1.1`, `v1.2`, …). Research specs never execute directly.

The research line has progressed `specs/v3.6.yaml` (source strategy under the
approval workflow; `research_spec` in `config/watchlist.yaml`) → ST-C1
(`specs/v3.7`–`v3.10`, all researched to conclusion and **parked** — below the
promotion bar) → **ST-C2 "Hybrid Liquidity-First"** (the active candidate). ST-C2 is
pre-approval: its RCR is filed and a governance/conformance checkpoint is published,
but it is **not yet wired into `config/watchlist.yaml`** (which still names
`research_spec: specs/v3.6.yaml`) and its implementation is not authorized. Note the
earlier `specs/v3.5.yaml` "version of record" framing was superseded by ADR-0001 —
v3.5 is research-only, never the execution authority. See `PROJECT_STATUS.md` §5 for
the current research-track detail.
```

---

## F2 — `MASTER_PLAN.md` "CURRENT PRIORITY" section

**Rationale:** The section pins the project at "PHASE 1 — APPROVED STRATEGY FOUNDATION"
and forbids starting execution-layer work, but `ROADMAP.md` already tracks Phase 1 as
✅ COMPLETE and Phase 2 as 🟡 CURRENT. Aligning this line requires a version-header bump
per this document's own rule ("Changes require a version bump + changelog entry").

**Version convention (read from the file):** header reads `**Version:** 3.0.0`; the
changelog uses semver with third-digit entries (v2.1.1, v2.1.2, v2.1.3) for refinements
and clarifications, second/first digits reserved for larger additions/rewrites (v2.1
charter add, v3.0.0 full rewrite). Aligning a stale priority line to `ROADMAP.md` is a
clarification/correction, not a scope or structure change — so the next logical version
under the file's own pattern is a patch bump: **v3.0.1**. (Owner to confirm; if the
change is judged more than a clarification, v3.1.0 would be the minor-bump alternative.)

**EXACT current text (verbatim, `MASTER_PLAN.md` header lines 4–5):**

```
**Version:** 3.0.0
**Status:** AUTHORITATIVE PROJECT OPERATING INSTRUCTIONS
**Recorded:** 2026-07-19 · Supersedes v2.1.3
```

**EXACT current text (verbatim, `MASTER_PLAN.md` "CURRENT PRIORITY" lines 58–62):**

```
## CURRENT PRIORITY

**PHASE 1 — APPROVED STRATEGY FOUNDATION.** Do not start execution-layer work
until the strategy source is normalized, validated, and approved. Frozen —
do not redesign execution plumbing before the approved strategy contract exists.
```

**Proposed replacement — header block:**

```
**Version:** 3.0.1
**Status:** AUTHORITATIVE PROJECT OPERATING INSTRUCTIONS
**Recorded:** 2026-07-23 · Supersedes v3.0.0
```

**Proposed replacement — "CURRENT PRIORITY" section:**

```
## CURRENT PRIORITY

**PHASE 2 — STRATEGY APPROVAL & VALIDATION.** Phase 1 (Approved Strategy
Foundation) is complete; the strategy contract exists and the current work is
proving a candidate through backtest, out-of-sample, and walk-forward evidence
gates (`ROADMAP.md` Phase 2 🟡 CURRENT). Execution-layer work (Phase 3) remains
out of scope until a candidate clears the Phase 2 gates — do not redesign or build
execution plumbing before an approved strategy contract passes validation.
```

**Proposed changelog entry to prepend (verbatim, follows the file's existing format):**

```
- **v3.0.1 — 2026-07-23** — Aligns "CURRENT PRIORITY" with `ROADMAP.md`'s tracked
  Phase 1 ✅ COMPLETE / Phase 2 🟡 CURRENT state (moves the stale Phase 1 pin to
  Phase 2 — Strategy Approval & Validation). Clarification only; scope, sequencing,
  authority order, and non-negotiable rules unchanged.
```

---

## F7 — `docs/CHARTER.md` + `MASTER_PLAN.md` "historical references only"

**Rationale:** Both documents call `specs/v1.yaml` (and v3.5) "historical references
only," which conflicts with ADR-0001 and `config/watchlist.yaml` naming `specs/v1.yaml`
the "sole execution authority." Both statements are true on different axes: v1 is the
current live execution-authority spec AND legacy/superseded relative to the research
line. One reconciling sentence, usable verbatim in both places, resolves the apparent
contradiction without picking a side.

**EXACT current text (verbatim, `docs/CHARTER.md` lines 118–120):**

```
_Strategy source of record: **`docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md`**.
The approved execution contract does not exist yet; it is the next deliverable.
`specs/v1.yaml` and `specs/v3.5.yaml` remain historical references only._
```

**EXACT current text (verbatim, `MASTER_PLAN.md` lines 88–98, "CURRENT SYSTEM TRUTH");
the target sentence is the "Legacy artifacts" bullet, lines 94–95):**

```
- **Legacy artifacts:** v3.5/v1 materials remain historical references only.
  They do not define the new architecture.
```

**Proposed ONE reconciling sentence (drop-in for both places):**

```
Per ADR-0001, `specs/v1.yaml` is simultaneously the current live execution-authority
spec (the sole spec permitted to generate executable signals) AND legacy relative to
the research line (v3.5/v3.6/ST-C1/ST-C2) — both hold on different axes (execution vs.
research), so v1 is "legacy" only in the research sense, never a non-executing
historical artifact.
```

**Suggested application (for owner reference; not applied here):**

- In `docs/CHARTER.md`, replace the sentence
  "``specs/v1.yaml` and `specs/v3.5.yaml` remain historical references only.`"
  with the reconciling sentence above (keeping v3.5 as research-only, v1 as the
  execution-authority-yet-research-legacy spec).
- In `MASTER_PLAN.md`, replace the "Legacy artifacts" bullet's
  "`v3.5/v1 materials remain historical references only.`" clause with the same
  reconciling sentence, keeping "They do not define the new architecture" applicable to
  the v3.5 research materials.
```
