# Research Log

Append-only, per `docs/RESEARCH-CHARTER.md`. Never overwrite a prior entry, even
a rejected one. Created on first use, 2026-07-21.

---

## Change: 10-gate strategy conformance (spec version: v3.6 -> v3.7, contract ST-C1 v1.0 -> v1.1.0)
Date: 2026-07-21
Author: Claude (research agent), on behalf of the owner-directed audit task

### Why
`reports/audit/st_c1_strategy_conformance_matrix.md` and
`reports/audit/ST_C1_V37_PRE_EDIT_FINDINGS.md` establish that the 363-trade
Phase A baseline (PF 0.4272, expectancy -0.4116R) was produced by
`validation/historical_replay_engine.py` calling `live_signal.py`'s v1 legacy
swing/equilibrium signal wrapped in an ad hoc sweep/POI layer — not by any
implementation of the v3.6 E-trigger/M-model contract, and not by anything
resembling premium/discount location, HTF POI/FVG, causal structural
invalidation, or a net-of-cost reward gate. The baseline result is therefore
evidence about an unintended surrogate, not about ST-C1/v3.6.

### Evidence
`reports/audit/st_c1_strategy_conformance_matrix.md` (E1/E2/E3, displacement,
CHoCH rated MISSING/PARTIAL/MISLABELED); `specs/v3.6.yaml` §26 checklist
unchecked; `historical_replay_engine._determine_target`'s silent gross-fallback
target defect (already fixed in `signal_v35.py` via `REJECT_NO_TARGET` but never
ported); `ST-C1_v1.yaml`'s untested `premium_discount`/`entry_model` location
requirements.

### Hypothesis
The baseline's negative expectancy is confounded by three unmeasured, entangled
defects: (1) wrong signal source entirely (v1 legacy, no HTF causal chain);
(2) no premium/discount location filter; (3) gross 2R gate with silent fallback
target instead of a net-of-cost 3R gate against a preselected external-liquidity
target. The locked 2x2 ablation (location x reward-gate) will separate which
factor(s) drive the sign of expectancy.

### Expected improvement
Correctly gating on G1-G10 is expected to reduce total qualifying trade count
by at least 70% relative to the 363-trade Phase A baseline, and to change the
funnel's dominant rejection reason from signal/sweep (structural) to
location/net_rr (economic) at least 25% of the time each. If neither shift
occurs, reject the hypothesis that location/net-RR gating meaningfully changes
the qualifying trade population, regardless of resulting PF.

### Success criteria
(a) all 10 gates have >=1 positive and >=1 negative passing test; (b) A0
(location-as-today + gross 2R) reproduces the qualitative shape of the existing
Phase A baseline inside the new engine; (c) A1/A2/A3 funnels show the location
and net-RR gates each independently rejecting a nonzero, auditable share of
candidates. Promotion to PROMISING/ROBUST is explicitly out of scope for this
task; classification here can only be FAILED/OVERFILTERED/FRAGILE at best.

### Rollback criteria
Revert/stop before running the ablation if: point-in-time/no-lookahead tests
fail; a clean run and a resumed run of the same cell disagree; any gate
silently defaults to pass on missing inputs; cost reconciliation cannot close
to tolerance. If A0 does not reproduce the existing baseline's qualitative
shape inside the new engine, treat as an engine-parity defect (INCONCLUSIVE),
not a strategy result — fix parity before drawing conclusions from A1-A3.

**Resolution:** see `reports/audit/ST_C1_V37_RESEARCH_CHANGE_REQUEST.md` for
the full filed template and `reports/audit/ST_C1_V37_FINAL_VALIDATION_DECISION.md`
for the outcome once the ablation runs.

---

## Change: G6 poi_entry_to_sweep_max_m5_bars population feasibility (R2.1)
Date: 2026-07-21
Author: Claude (research agent), R2.1 task

### Why
All 12 cells of the locked v3.7 A0-A3 ablation produced zero trades; G6
saturates identically across every cell (0% pass rate against a G5-qualified
population of 372-5022 candidates per cell).

### Evidence
`reports/ablation/st_c1_v37_ablation_raw.json`; a diagnostic example on real
EURUSD data found the nearest matching M5 sweep 127 bars after a genuine POI
touch, ~4x the locked `poi_entry_to_sweep_max_m5_bars=30`.

### Hypothesis
The 30-bar limit is shorter than normal causal sweep latency; a bounded
increase (B1=72, B2=144) can restore a nonzero, statistically usable G6
population without making G6 effectively always-pass. Population
feasibility only — not a profitability claim.

### Independent variable
`poi_entry_to_sweep_max_m5_bars` only (B0=30 control, B1=72, B2=144). Every
other G1-G10 rule, cost, fill/target/management model, symbol universe,
session, and repaired-candle policy held fixed. G4 disabled in all three
cells (population diagnostics, not strategy-performance results).

### Expected result
B1/B2 show a nonzero, growing completed-G6-sequence count while G6 pass
rate stays <=10% of G5-qualified candidates (still discriminating, not a
no-op). If B2 remains at/near zero, hypothesis rejected within tested range.

### Success criteria
Select the smallest of B0/B1/B2 satisfying ALL: >=30 total completed G6
sequences; >=5 sequences in >=2 symbols; coverage across >=2 calendar years;
G6 pass rate <=10% of G5-qualified; identical clean/resumed results; no
fail-open or look-ahead test failure. B1 wins over B2 if both qualify,
regardless of P&L. PF/expectancy/Sharpe/win-rate/drawdown explicitly
excluded from selection.

### Rollback criteria
Clean/resumed disagreement, any fail-open/look-ahead defect, or B2 failing
to qualify -> REJECTED/INCONCLUSIVE, full stop, no v3.8 files created, no
widening beyond 144 in this task.

**Resolution:** see `reports/audit/ST_C1_V38_G6_POPULATION_RCR.md` for the
full filed template and `reports/audit/ST_C1_V38_FINAL_VALIDATION_DECISION.md`
for the outcome once the B0/B1/B2 experiment runs.

---

## Change: "ST-C1 Clean SMC" preset v1 — displacement-definition relaxation (spec version: v3.6/v3.7/v3.8-line parked -> v3.9, contract v1.1.0 -> v1.2.0)
Date: 2026-07-22
Author: Claude (research agent), on behalf of owner-supplied preset

### Why
`ST_C1_V38_FINAL_VALIDATION_DECISION.md` §15 directed a new, separately
preregistered RCR targeting `REJECTED_NO_DISPLACEMENT` (the bottleneck that
became dominant once the sweep-timing bound was widened in R2.1), not a
further widening of `poi_entry_to_sweep_max_m5_bars`. The owner supplied a
fully specified preset that returns to the v3.6/`ST-C1_v1.yaml` E1/E2/E3
schema with E1 disabled, E2/E3 wick-ratio filters zeroed, and displacement
redefined as body-ratio-only (ATR-magnitude requirement removed,
`body_ratio_min` raised 0.5 -> 0.6).

### Evidence
`reports/ablation/ST_C1_V37_ABLATION_REPORT.md` (12/12 cells, zero trades);
`reports/audit/ST_C1_V38_FINAL_VALIDATION_DECISION.md` §8/§13 (widening
sweep-timing 30->144 raised completed sequences only 8->14, short of the
30-sequence floor, because `REJECTED_NO_DISPLACEMENT` grows to dominate
once sweep-timing is relaxed).

### Hypothesis
Removing the ATR-relative displacement magnitude requirement (body-ratio-
only, threshold raised to keep it discriminating), disabling E1, and
zeroing E2/E3 wick-ratio filters will shrink `REJECTED_NO_DISPLACEMENT`'s
share of the funnel materially and restore a statistically usable
completed-signal population, without collapsing G6 into a no-op (CHoCH
confirmation, structural sweep, and `min_net_rr: 3.0` remain hard gates).

### Expected improvement
(1) `REJECTED_NO_DISPLACEMENT`'s share of the funnel drops >=50% relative to
the v3.8 B2 funnel composition; (2) total completed sequences across
EURUSD/GBPUSD/XAUUSD reach >=30, with >=5 in >=2 symbols (same floor as
R2.1, for direct comparability).

### Success criteria
Both expected-improvement numbers met AND `min_net_rr`/`min_rr` unchanged at
3.0 (population growth must come from the targeted relaxations, not a
loosened reward floor) AND clean/resumed agreement AND no fail-open/look-
ahead defect. Profitability (OOS expectancy > 0, OOS >= 0.5 * IS) is only
evaluated after population feasibility passes.

### Rollback criteria
Population floor not met with all three relaxations applied -> REJECTED, no
promotion, escalate to a design-level question about the G6 causal-chain
model rather than further ad hoc parameter changes. Fail-open/look-ahead
defect -> stop and fix before selection. Clean/resumed disagreement ->
INCONCLUSIVE regardless of population numbers.

**Resolution:** see `reports/audit/ST_C1_V39_CLEAN_SMC_RCR.md` for the full
filed template. `specs/v3.9.yaml` and `strategies/candidates/ST-C1_v1.2.0.yaml`
are created as candidate-only, `engine_implements_spec: false` — pending a
`backtest-researcher` run before any ACCEPT/REJECT verdict.
