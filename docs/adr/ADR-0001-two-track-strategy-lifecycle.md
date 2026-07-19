# ADR-0001 — Adoption of the Two-Track Strategy Lifecycle

**Status:** Accepted
**Date:** 2026-07-18 (drafted, in `docs/GOVERNANCE_RECONCILIATION_PACKAGE.md` §1) · **Accepted 2026-07-19** (WO-1)
**Deciders:** Project Owner (Aung); Governance Agent

---

## Context

The repository accumulated conflicting statements about which strategy is
authoritative. Verified in the Governance Verification Report (2026-07-18):
`docs/CHARTER.md` names `specs/v3.5.yaml` the "version of record" and wires demo
auto-execution to its `engine_implements_spec` flag; `MASTER_PLAN.md` names
`specs/v1.yaml` the execution authority; `CLAUDE.md` contains both claims. Root
cause: no explicit separation between the strategy that *executes* and the
strategy under *research*.

## Decision

Adopt a two-track strategy lifecycle:

- **Execution Track** — `specs/v1.yaml` is the **sole execution authority**;
  only it may generate executable trading signals. Changes require validation +
  governance approval + git commit + an ADR.
- **Research Track** — `specs/v3.5.yaml` and `specs/v3.6.yaml` are
  **research-only** and may never execute trades.
- **No research strategy may be connected directly to execution.**
- **Promotion pipeline:** Research → Backtest → Walk-Forward Validation → Demo
  Validation → Governance Review → Promotion → **new Execution Release**
  (`v1.1`, `v1.2`, …). Research version numbers are never deployed directly.
- **Conflict-interpretation rule:** a document saying v3.5 is research while
  another says v1 is execution is **not** a contradiction. Only disagreements
  **within the same track** warrant a Governance Conflict Report.
- **Execution posture:** PROPOSAL-ONLY until Phase 3 Risk Engine + validation
  gates pass; no automatic MT5 demo execution authorized.
- **Spec metadata:** each spec file carries `track`, `status`, `promotion_stage`
  (tracked separately — Batch B, WO-5).
- **Telegram** is execution infrastructure, outside governance scope.

## Consequences

- (+) Eliminates the v1/v3.5 ambiguity; one execution authority.
- (+) Research can iterate freely without touching execution.
- (+) Explicit, auditable promotion gates.
- (−) `docs/CHARTER.md` autonomy wording must be clarified (the v3.5
  `engine_implements_spec` interlock no longer governs execution) — tracked in
  Batch B, WO-6.
- (−) Spec relocation is deferred (separate Engineering ADR, not opened here).

## Related work

- `config/watchlist.yaml` correction to align with this ADR's execution-track
  ruling: WO-2 (Batch A) — see `docs/GOVERNANCE_RECONCILIATION_PACKAGE.md`
  Document Change Matrix row 14.
- Spec metadata (`track` / `status` / `promotion_stage`): WO-5 (Batch B).
- Governance-document references + track clarifications: WO-6 (Batch B).
