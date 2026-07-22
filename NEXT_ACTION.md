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

### Outcome (2026-07-22) — dedup bug found and fixed; both prior reads corrected; comparison complete

Per `project-governance-agent`'s ruling (reject "close Phase 2/open Phase
3", reject ADR-0004 for v40, run dedup check + comparison first), the
`duplicate_structure` anomaly was investigated and confirmed to be a real
bug, not a design property: `structure_key`'s `index_offset` was never
wired up in either `validation/historical_replay_engine_v39.py` or
`historical_replay_engine_v310.py`, causing cross-time key collisions that
silently discarded valid trades (`src/backtest_v35.py` already did this
correctly — the newer v3.9/v3.10 engines regressed it). Fixed (two-line
change per engine); full suite re-run, 179 passed, no regressions.

All six affected backtests (v3.9 B1 + v3.10, all three symbols) were
re-run. Trade counts changed substantially (v3.9: 47/37/54 -> 80/78/81;
v3.10: 135/112/120 -> 789/744/684). **Both prior committed analyses are
superseded** — see `reports/audit/ST_C1_DEDUP_BUG_AND_CORRECTED_RESULTS.md`.
Corrected picture is worse for both candidates than originally reported:
XAUUSD is no longer cost-neutral (v3.9) or profitable (v3.10) — both
candidates are now net-losing in **every** symbol, though the
XAUUSD-best/EURUSD-worst ranking survives the fix in both engines.

`reports/audit/ST_C1_V39_VS_V310_COMPARISON.md`: the v3.9-vs-v3.10
comparison (using corrected data) found the symbol-level ranking is
identical across both independently-built engines (evidence of a
structural cost/instrument-scale effect, not an engine-specific flaw), and
a striking scenario-population finding: **v3.10 executed zero E1-triggered
trades in any symbol**, despite E1 (D1 gap-reversal) being the specific new
mechanism the entire v3.10 candidate was built to test. v3.10's realized
population is entirely E2/E3 continuation-family trades — the same
trigger families v3.9 already uses.

**Next step, not started here:** diagnose why v3.10 never executes an E1
trade (prerequisite to judging the reversal-capture thesis at all). If a
symbol-restriction hypothesis is pursued afterward, it must be framed as
"reduces losses, does not yet produce a profitable candidate" (XAUUSD
alone is still net-losing in both corrected reads) — not oversold as a
fix. Drafting `specs/v40.yaml` remains **not authorized**: Phase 2 is not
complete (neither candidate clears `ROADMAP.md`'s promotion bar), and any
detection-logic change requires an RCR per `docs/RESEARCH-CHARTER.md`, not
an ADR.

### Outcome (2026-07-22) — E1 lockout diagnosed (design question, not a bug)

`reports/audit/ST_C1_V310_E1_LOCKOUT_DIAGNOSIS.md`: a read-only diagnostic
scan (EURUSD, full history, no code changed) found E1 qualifies only 1.30%
of the time on its own (86/6,639 checkpoints) and, of those, loses
`detect_e_trigger`'s `max(confirm_i)` "freshest wins" tie-break to E2/E3
**100% of the time** — E1 has never once been selected. Root cause: that
tie-break was authored for v3.9's two-trigger (E2/E3) world and carried
unchanged into v3.10's three-trigger design; neither the code nor the RCR
ever decided what should happen when E1 also qualifies. Per
`project-governance-agent`'s ruling, this is a **design change, not a bug**
(no already-agreed rule is being violated) — fixing it requires a
six-question RCR before any change to the selection logic is backtested.
No code changed. Also newly flagged: the RCR's existence check
(367 trades, reported cleared) never actually validated the
reversal-capture-via-E1 thesis, since zero of those trades were
E1-triggered.

**Next step, not started here:** if the E1 thesis is still worth testing,
file an RCR addressing what the intended E1/E2/E3 selection rule should be,
with a falsifiable hypothesis and expected-improvement number stated
before re-running — explicitly not conflating "does E1 fire" with "does
the candidate become profitable" (both candidates remain net-losing across
all three symbols regardless of this question).

### Outcome (2026-07-22) — E1 diagnostic scan extended to all 3 symbols; tie-break RCR filed

`ST_C1_V310_E1_LOCKOUT_DIAGNOSIS.md` extended to GBPUSD/XAUUSD (was
EURUSD-only): E1 qualifies alone in 1.86% of checkpoints combined (371 of
19,922) but loses `detect_e_trigger`'s tie-break to E2/E3 in **0/371**
cases across all three symbols — the lockout is universal, not a EURUSD
artifact. `reports/audit/ST_C1_V310_E1_TIEBREAK_RCR.md` filed (logged to
`reports/research_log.md`) per `project-governance-agent`'s conditional
approval: honestly scoped to "does E1 fire at all," explicitly NOT
claiming this will fix v3.10's profitability (both candidates remain
~10x below `ROADMAP.md`'s promotion bar in every symbol — a separate,
larger go/no-go decision for the owner, unresolved by this RCR either
way). RCR not yet backtested — awaiting owner/governance authorization to
implement and run.

### Outcome (2026-07-22) — E1 tie-break RCR implemented, run, INCONCLUSIVE

Authorized by `project-governance-agent`. `detect_e_trigger` now
prioritizes E1 outright when it qualifies (`src/signal_v310.py`); 3 new
tests added, full suite 182 passed. Re-ran v3.10 for all three symbols:
**E1 fires for the first time — 56 trades (16/24/16 across
EURUSD/GBPUSD/XAUUSD)**, clearing the RCR's existence criterion. But its
behavior is statistically indistinguishable from E2/E3's (Welch's t=0.407
on net_r, z=-0.704 on win rate — both far below the ~1.96 significance
threshold) — per the RCR's own pre-declared rollback criteria, this is
**INCONCLUSIVE** on the reversal-capture thesis, not accept or reject.
Aggregate PF barely moved (0.469 -> 0.471), exactly as the RCR predicted.
See `reports/audit/ST_C1_V310_E1_TIEBREAK_RESULTS.md`.

**This does not change the larger open decision:** both v3.9 (aggregate
PF 0.138) and v3.10 (PF 0.471) remain net-losing in every symbol, roughly
10x below `ROADMAP.md`'s promotion bar. That park-or-continue decision for
the ST-C1 v3.9/v3.10 line remains open, unresolved by this RCR, and is
the largest unaddressed item at this point.

### Outcome (2026-07-22) — ST-C1 v3.9/v3.10 line PARKED; ST-C2 proposed

Per `project-governance-agent` ruling: **the ST-C1 v3.9/v3.10 line is
PARKED** — same disposition as v3.7/v3.8, retained not deleted. No further
open diagnostic plausibly rescues either candidate under the validated
cost model. Recorded in `PROJECT_STATUS.md` §5 and `ROADMAP.md`'s Phase 2
section.

A new candidate, **ST-C2** ("Hybrid Liquidity-First Unified SMC
Pipeline," `specs/st-c2.yaml`), has been proposed — a conjunctive
all-stages-must-pass pipeline at a new H4/M15/M3 timeframe triple,
architecturally distinct from ST-C1's disjunctive E1/E2/E3 branching at
H4/H1/M5.

## → PHASE 2 (research/validation): file the ST-C2 RCR before any implementation

Per `project-governance-agent` ruling: no RCR has been filed for ST-C2
yet. Required before any further work — scenario-classifier design,
conformance-kernel binding, population-feasibility testing, or net-of-cost
validation — per the same precedent `ST_C1_V39_CLEAN_SMC_RCR.md` and
`ST_C1_V310_REVERSAL_CAPTURE_RCR.md` both followed despite being equally
"brand new, owner-supplied, zero prior evidence." `specs/st-c2.yaml` needs
`engine_implements_spec: false` added for consistency with that
precedent. Separately, dedicated ST-C2 agent files (e.g. a
scenario-classifier agent) require their own new ADR before they exist —
that question is separable and does not block the RCR/research path.

### Outcome (2026-07-22) — RCR filed, awaiting authorization

`reports/audit/ST_C2_HYBRID_LIQUIDITY_FIRST_RCR.md` filed (logged to
`reports/research_log.md`) per `docs/RESEARCH-CHARTER.md`'s six-question
template, before any code was written. Scoped to XAUUSD only (matching
`specs/st-c2.yaml` as filed — EURUSD/GBPUSD both `enabled: false`);
existence-check only (>=1 qualifying signal), no population-feasibility
floor precommitted, same disclosed-limitation pattern
`ST_C1_V310_REVERSAL_CAPTURE_RCR.md` used. `specs/st-c2.yaml` already had
`engine_implements_spec: false` set correctly — no change needed there.
Work done on branch `research/st-c2-contract-and-conformance`. No code, no
spec mutation, no execution/demo/live/promotion flag changed.

**Next step, not started here:** `project-governance-agent`/owner
authorization of this RCR, per the same precedent
`ST_C1_V310_E1_TIEBREAK_RCR.md` followed — filed, then explicitly
authorized before implementation. Only after authorization: golden-case
tests, the conformance kernel (as research code, not an agent file), the
minimum XAUUSD detector slice, and the existence-check run — in that
order.
