# ROADMAP.md — Path to Approved Strategy + MT5 Execution

**Authority:** organized under [`MASTER_PLAN.md`](MASTER_PLAN.md) (v3.0.0).
Phases and priority come from that document; this file holds the per-phase status
and acceptance criteria. **Current priority: Phase 1 — Approved Strategy Foundation.**

**Guiding rule:** strategy first, execution second. Freeze the strategy contract
before building any execution plumbing.

**Revision note (2026-07-19):** re-sequenced around the v3.6 strategy source and
the approved-strategy workflow. The old v3.5-first narrative is historical context
only and no longer defines the upgrade path.

---

## PHASE 1 — Strategy Approval Foundation · ✅ COMPLETE

Deliverables:
- `docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md` as the source strategy
- machine-readable approved strategy contract
- approval gates and validation evidence
- versioning / changelog discipline for the strategy package

*Acceptance:* the strategy source can be normalized into a versioned contract with
deterministic validation outcomes and no ambiguity about fields, rules, or versions.

Completed:
- `strategies/candidates/ST-C1_v1.yaml`
- `research/ST-C1_RESEARCH_CONTRACT.md`
- `reports/ST-C1_NORMALIZATION_REPORT.md`

## PHASE 2 — Validation & Packaging · 🟡 CURRENT

Deliverables:
- closed-candle-only backtest harness
- realistic spread / commission / slippage simulation
- out-of-sample and walk-forward checks
- immutable approved-package output

*Acceptance:* the candidate contract passes evidence gates and produces a signed
or equivalent immutable package for execution.

## PHASE 3 — Execution Layer · ⏳

Deliverables:
- canonical order pipeline
- risk gate
- broker adapter
- reconciliation
- journaling and monitoring

*Acceptance:* every broker action goes through one approved pipeline and can be
reconciled end-to-end.

## PHASE 4 — Demo Automation · ⏳

Deliverables:
- demo integration of the approved contract
- auto-execution on demo only
- trade management and journaling

*Acceptance:* demo trades execute, manage, reconcile, and journal from the approved
contract without manual intervention.

## PHASE 5 — Live Pilot · ⏳

Deliverables:
- owner-approved live promotion gate
- small-size live routing
- monitoring and kill-switch discipline

*Acceptance:* live remains blocked until demo evidence and operational controls pass.

---

## Cross-cutting requirements (every phase)
Deterministic logic only · config-driven limits · unit tests for new logic · update
docs and status files · commit per milestone · never route on an unverified
environment.

## Explicitly out of scope
Rewriting the strategy source without approval · execution shortcuts that bypass the
canonical pipeline · live-account routing before gates pass · AI overlays that alter
execution without approval.
