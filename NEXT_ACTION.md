# NEXT_ACTION.md

**One milestone at a time. This is the next one.**

**Correction (2026-07-22):** this file previously named "PHASE 3 · M3:
Execution Layer Skeleton" as the next milestone. That contradicted
`PROJECT_STATUS.md` §5 and `ROADMAP.md` Phase 2/3, both of which state Phase
3 (execution layer) is explicitly out of scope until a research candidate
clears Phase 2's evidence gates, and neither has cleared them. This file was
simply stale — corrected below, no execution-authority change involved.

## → PHASE 2 (research/validation): ST-C1 v3.9 conformance + population feasibility

*Close the v3.9 "Clean SMC" research-candidate gaps: an E1/E2/E3+M1/M2/M3
conformance audit (not the parked v3.7 G1-G10 pipeline), a conformant
point-in-time engine, and a controlled population-feasibility check. This is
strategy research only — no execution, demo, or live authority changes.*

### Why this now
`specs/v3.9.yaml` / `strategies/candidates/ST-C1_v1.2.0.yaml` were filed
(2026-07-22, `reports/audit/ST_C1_V39_CLEAN_SMC_RCR.md`) as the directed
follow-up to the v3.8 R2.1 population-feasibility rejection, but
`engine_implements_spec: false` and no conformant engine or backtest exists
yet. Population feasibility must be established before any statistical or
profitability read is meaningful.

### Scope (smallest working solution)
1. Audit v3.9 gate-by-gate in its own E1/E2/E3 + M1/M2/M3 + displacement
   terms (see `reports/audit/ST_C1_V39_GOVERNANCE_CONFORMANCE_PRE_EDIT_FINDINGS.md`
   §3c for why the G1-G10 framing does not apply to this spec).
2. Implement the canonical v3.9 point-in-time signal engine, isolated from
   broker/execution imports, only once the conformance audit is complete.
3. Add positive/negative/mirror/cutoff-invariance/determinism tests before
   the broader suite.
4. Run the precommitted population-feasibility ablation (>=30 completed
   sequences overall, >=5 in >=2 symbols) per the RCR's criteria.
5. Keep `engine_implements_spec: false` and all demo/live/promotion flags
   unchanged until the evidence above exists.

### Acceptance criteria
- [ ] v3.9 conformance matrix complete, numeric, and deterministic.
- [ ] Canonical engine implements the full v3.9 contract with gate evidence.
- [ ] `engine_implements_spec` flips to true only after the full conformance
      suite passes; otherwise stays false with partial coverage reported.
- [ ] Population-feasibility gate result reported (pass or fail), funnel
      preserved with explicit rejection codes.
- [ ] `python -m pytest -q` passes after any supporting doc/test updates.
- [ ] No execution, demo, or live autonomy flag changed.

### Estimated complexity / time
Medium to large. The conformance audit and canonical engine are the hard
parts; population feasibility is a gate, not a profitability judgment.

### Outcome (2026-07-22)
Population feasibility **PASSED decisively** (138 completed trades vs. the
30-total/5-per-symbol floor; see `reports/audit/ST_C1_V39_POPULATION_ABLATION_SPEC.md`).
But the same run surfaced deeply negative net expectancy for EURUSD/GBPUSD
and a quality regression on XAUUSD relative to its own v3.6 control — a
real cost/quality concern, not a population problem.

### After this milestone
**Do not** proceed straight to a Phase-7-equivalent profitability read.
Next milestone: a small, pre-registered (per `docs/RESEARCH-CHARTER.md`)
investigation into why so many v3.9 trades carry stop distances tiny
enough that fixed spread/slippage costs dominate R — is the ATR*0.15 stop
buffer convention wrong for this preset, or does E2/E3's zeroed wick-ratio
filter admit zones too tight to trade net of cost? Still research-only;
Phase 3 execution work remains out of scope regardless.

### Update (2026-07-22) — a second, parallel candidate now also queued
Owner directed a new reversal-capture design (v3.10 / ST-C1_v1.3.0,
`reports/audit/ST_C1_V310_REVERSAL_CAPTURE_RCR.md`) alongside v3.9. Its
engine is built and its existence check passed decisively (367 trades
across EURUSD/GBPUSD/XAUUSD combined). It has the **same open next step**
as v3.9: a net-of-cost read via the reused cost model, not yet run.
Both v3.9's cost/quality question and v3.10's net-of-cost read should be
addressed before either candidate is compared to the other or considered
for any further validation stage. Still research-only regardless of order.

### Outcome (2026-07-22) — both open questions now answered

`reports/audit/ST_C1_V39_STOP_DISTANCE_ANALYSIS.md`: v3.9's cost-dominance
is not uniform — concentrated in EURUSD (net win rate 14.9%) and moderate
in GBPUSD, while XAUUSD is cost-neutral (net_r +0.02R). Diagnostic only,
two candidate hypotheses proposed for a future RCR, neither implemented.

`reports/audit/ST_C1_V310_NET_OF_COST_ANALYSIS.md`: v3.10's net-of-cost
read is now computed (367 trades, all three symbols). Same split shape as
v3.9 — XAUUSD net-profitable (PF 1.68, +0.24R expectancy), EURUSD and
GBPUSD both net losers (PF 0.62 and 0.42). One anomaly flagged, not yet
resolved: `duplicate_structure` funnel counts are unusually high relative
to `signal_pass` (~99% deduplicated vs. v3.9's ~77%) — worth checking
before this population feeds any future trial-count/deflated-Sharpe input.

Both reads are diagnostic/statistical only — no code, spec, or promotion
change made. Next step (v3.9-vs-v3.10 comparison, and the dedup-anomaly
check) needs explicit sequencing, not started here.
