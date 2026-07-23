# ROADMAP.md — Path to Approved Strategy + MT5 Execution

**Authority:** organized under [`MASTER_PLAN.md`](MASTER_PLAN.md) (v3.0.0).
Phases and priority come from that document; this file holds the per-phase status
and acceptance criteria. **Current priority: Phase 2 — Strategy Approval & Validation.**

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

## PHASE 2 — Validation & Packaging · 🟡 CURRENT (research/validation, not execution)

**2026-07-22 note:** the ST-C1 10-gate (G1-G10) research line (`specs/v3.7.yaml`,
`strategies/candidates/ST-C1_v1.1.0.yaml`) sits inside this phase, not Phase
3. v3.7's locked ablation result is OVERFILTERED/statistically INCONCLUSIVE
(zero trades in every cell); a follow-up R2.1 population-feasibility
experiment rejected the G6 sweep-timing widening hypothesis within its
tested range (see `PROJECT_STATUS.md` §5). **This v3.7/v3.8 line is now
PARKED** (retained, not deleted) in favor of a new v3.9 "Clean SMC" preset
(`specs/v3.9.yaml`, `strategies/candidates/ST-C1_v1.2.0.yaml`) filed as the
directed follow-up RCR targeting the `REJECTED_NO_DISPLACEMENT` bottleneck —
see `reports/audit/ST_C1_V39_CLEAN_SMC_RCR.md`. No candidate has been
approved; the v3.9 candidate's own population-feasibility backtest has not
yet run. Phase 3 (execution layer) remains explicitly out of scope until a
candidate clears Phase 2's evidence gates — this phase is not yet complete
for this strategy line, regardless of the M1-M2.3 scaffold work described
below.


**2026-07-22 addendum:** a v3.9 governance/conformance/population task is in
progress on local branch `research/st-c1-v39-governance-conformance`. It
audits v3.9 in its own E1/E2/E3+M1/M2/M3 terms (not the parked G1-G10
pipeline — see `reports/audit/ST_C1_V39_GOVERNANCE_CONFORMANCE_PRE_EDIT_FINDINGS.md`
§3c), implements a conformant point-in-time engine only if that audit is
complete, and runs the same population-feasibility floor used in R2.1
before any statistical or profitability claim. Still research/validation
work; Phase 3 remains out of scope regardless of outcome.

**2026-07-22 update — v3.9/v3.10 diagnostic chain complete, line PARKED:**
a dedup bug was found and fixed (corrected both candidates' populations
and results — `reports/audit/ST_C1_DEDUP_BUG_AND_CORRECTED_RESULTS.md`),
the v3.9-vs-v3.10 comparison ran on corrected data, v3.10's E1 lockout was
root-caused and an RCR-authorized fix implemented — result INCONCLUSIVE
(`reports/audit/ST_C1_V310_E1_TIEBREAK_RESULTS.md`). **Final: v3.9
aggregate net PF 0.138, v3.10 aggregate net PF 0.471, both decisive misses
against this phase's PF >= 1.3 / expectancy >= +0.2R bar, in every symbol
of both candidates.** Per `project-governance-agent` ruling, **the ST-C1
v3.9/v3.10 line is PARKED** — same disposition as v3.7/v3.8, retained not
deleted. This phase remains 🟡 CURRENT and open: a parked line closes only
that line, not the phase. A new candidate, ST-C2 ("Hybrid Liquidity-First
Unified SMC Pipeline," `specs/st-c2.yaml`), has been proposed —
architecturally distinct from every ST-C1 variant (conjunctive
all-stages-must-pass pipeline vs. ST-C1's disjunctive E1/E2/E3 branching).
Per governance ruling, an RCR must be filed before any implementation,
population-feasibility, or net-of-cost work on ST-C2 begins — not yet
filed as of this entry.

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
