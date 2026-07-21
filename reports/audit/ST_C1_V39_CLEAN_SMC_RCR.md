# Research Change Request — "Clean SMC" Preset v1 (displacement-definition relaxation)

Filed per `docs/RESEARCH-CHARTER.md` before any new backtest runs. This is the
follow-up Research Change Request that `PROJECT_STATUS.md` §5 and
`reports/audit/ST_C1_V38_FINAL_VALIDATION_DECISION.md` §15 called for:
targeting the `REJECTED_NO_DISPLACEMENT` bottleneck specifically, not a
further uncontrolled widening of `poi_entry_to_sweep_max_m5_bars` (already
tested and rejected up to its 144-bar ceiling in R2.1).

## Change: "ST-C1 Clean SMC" parameter preset (spec version: v3.6/v3.7/v3.8-line parked -> v3.9, contract v1.1.0 -> v1.2.0)
Date: 2026-07-22
Author: Claude (research agent), on behalf of owner-supplied preset

### Why
Owner supplied a fully specified parameter preset ("ST-C1 Clean SMC v1")
that returns to the v3.6/`ST-C1_v1.yaml` E1/E2/E3 + displacement schema
(rather than v3.7's G1-G10 gate pipeline) with three specific, targeted
relaxations aimed at the diagnosed bottleneck chain:
1. **E1 (D1 gap reaction) disabled entirely** (`e1_gap_max_age_d1_bars: 0`,
   etc.) — removes the rarest, most restrictive HTF trigger from the
   funnel's entry point.
2. **E2/E3 wick-ratio reaction/sweep filters zeroed** (`e2_reaction_wick_ratio_min: 0.0`,
   `e3_sweep_wick_ratio_min: 0.0`, `e3_reclaim_window_h1_bars: 0`) — relies
   on CHoCH/structure confirmation instead of wick geometry to qualify a
   reaction, removing a pre-G6 filter that was never itself under test in
   v3.7/v3.8.
3. **Displacement redefined as body-ratio-only** (`displacement_atr_period: 0`,
   `displacement_atr_mult: 0.0` i.e. ATR-relative magnitude requirement
   OFF; `displacement_body_ratio_min: 0.6`, stricter than v3.7's 0.5, but
   the ONLY displacement qualifier) — this is the direct, targeted change
   `ST_C1_V38_FINAL_VALIDATION_DECISION.md` §15 asked for: the v3.8 funnel
   showed `REJECTED_NO_DISPLACEMENT` becoming the dominant rejection reason
   once the sweep-timing bound was widened, and that ATR-relative threshold
   was never itself varied in v3.7 or v3.8.

### Evidence
- `reports/ablation/ST_C1_V37_ABLATION_REPORT.md`: 12/12 locked cells, zero
  trades — G6 saturates before location/net-RR gates are ever exercised.
- `reports/audit/ST_C1_V38_FINAL_VALIDATION_DECISION.md` §8, §13: widening
  `poi_entry_to_sweep_max_m5_bars` 30->144 raised completed sequences only
  8->14 (still short of the 30-sequence floor), because survivors past the
  sweep-timing gate were then caught by `REJECTED_NO_DISPLACEMENT`, "a
  fixed, untested parameter [that] grows to dominate."
- `reports/audit/ST_C1_V38_FINAL_VALIDATION_DECISION.md` §15 ("Exact next
  safe action"): explicitly directs a new, separately preregistered RCR
  against `REJECTED_NO_DISPLACEMENT`, not further sweep-timing widening.

### Hypothesis
The dominant remaining bottleneck is the joint effect of (a) the ATR-relative
displacement magnitude requirement (`atr_mult=1.5` in v3.7/v1.1.0) rejecting
genuine directional moves that have a strong body ratio but do not reach
1.5x ATR14 outside high-volatility windows, compounded by (b) E1's rare D1
gap requirement and (c) E2/E3's wick-ratio filters rejecting POI touches
before displacement is ever evaluated. Removing the ATR-magnitude
displacement requirement (body-ratio-only, threshold raised to 0.6 to keep
it discriminating), disabling E1, and zeroing E2/E3 wick-ratio filters will
shrink `REJECTED_NO_DISPLACEMENT`'s share of the funnel materially and,
combined, restore a statistically usable completed-signal population —
without collapsing G6 into a no-op, since CHoCH confirmation, structural
sweep detection, and `min_net_rr: 3.0` remain hard gates.

### Expected improvement
Two falsifiable numbers, stated before running anything:
1. `REJECTED_NO_DISPLACEMENT`'s share of the G6 rejection funnel drops by
   at least 50% (relative) versus the v3.8 B2 funnel composition reported
   in `reports/diagnostics/ST_C1_V38_G6_LATENCY_REPORT.md`.
2. Total completed signal sequences across EURUSD/GBPUSD/XAUUSD full
   history reach **>=30**, with **>=5 in >=2 of the 3 symbols** — the same
   population floor used in R2.1 (`ST_C1_V38_G6_POPULATION_RCR.md`), so
   the two experiments are directly comparable.
If neither number is met, the hypothesis that displacement-definition
relaxation (rather than the sweep-timing bound already rejected) is the
controlling bottleneck is REJECTED within this preset.

### Success criteria
Tied to `backtest-researcher`'s ACCEPT/REJECT gate: (a) both expected-
improvement numbers above are met; (b) `min_net_rr: 3.0` and `min_rr: 3.0`
remain enforced unchanged (population growth must come from the targeted
relaxations, not from also loosening the reward floor); (c) clean vs.
resumed runs agree; (d) no fail-open or look-ahead defect in the new
body-ratio-only displacement logic or the E1-disabled/E2/E3-wick-zeroed
paths. Only once population criteria (a)-(d) pass does a profitability
read (OOS expectancy > 0 AND OOS >= 0.5 * IS expectancy) become relevant —
population feasibility is decided first and independently of P&L, exactly
as in R2.1.

### Rollback criteria
- Population floor (>=30 total, >=5 in >=2 symbols) not met even with all
  three relaxations applied together -> REJECTED, no promotion, revert to
  documenting the E1/E2/E3+ATR-displacement schema as still infeasible
  within this strategy family's structural definition, and escalate to a
  design-level conversation (is the G6-style strict causal chain itself
  the wrong model) rather than a further ad hoc parameter change.
- Any fail-open or look-ahead defect found in the new displacement/CHoCH
  logic -> stop, fix, re-run before any selection is made.
- Clean vs. resumed disagreement on any symbol -> INCONCLUSIVE, do not
  select this preset even if the population floor is otherwise met.
- If the population floor IS met but `REJECTED_NO_DISPLACEMENT`'s relative
  share does NOT drop as hypothesized (i.e., population grew for a
  different reason, e.g. E1 removal alone) -> population result may still
  be usable, but the *mechanism* hypothesis is falsified and must be
  reported as such, not silently reattributed to the displacement change.

---
Logged to `reports/research_log.md` in date order alongside this entry, per
`docs/RESEARCH-CHARTER.md`. No backtest was run before this template was
filed. `specs/v3.9.yaml` and `strategies/candidates/ST-C1_v1.2.0.yaml` are
created as RESEARCH_CANDIDATE / candidate-only artifacts with
`engine_implements_spec: false` — this RCR does not itself constitute a
backtest run or an ACCEPT verdict.

---

## Addendum (2026-07-22) — disclosing a fourth, previously unnamed relaxation

Found during the v3.9 governance/conformance audit
(`reports/audit/ST_C1_V39_CONFORMANCE_MATRIX.md`, E3 row): `specs/v3.9.yaml`
sets `e3_reclaim_window_h1_bars: 0` (disabled), which removes the v3.6/v3.8
bound requiring an E3 sweep's reclaim to occur same-bar or the next H1 bar
only. This numeric value was already present in the committed spec (no code
or spec value is changed by this addendum) but was **not named** among the
three relaxations this RCR's "Why" section states above (E1 disabled, E2/E3
wick filters zeroed, displacement body-ratio-only). An unbounded reclaim
window is a fourth, materially relevant relaxation: it can grow the E3
population independently of the displacement-definition hypothesis this RCR
is testing.

**Disclosure, not a new proposal:** this addendum does not change
`specs/v3.9.yaml`, `ST-C1_v1.2.0.yaml`, or any numeric value — it corrects
the RCR's own account of what is being tested, so that Phase 6 population
results are attributed correctly. If the population-feasibility floor is met,
the Phase 6/7 report must state whether population growth depended on the
unbounded reclaim window specifically (e.g. via a controlled cell that
restores a 1-bar window), not attribute the result solely to the three
originally-named relaxations. No rollback/success criteria above are
changed; this only sharpens what "the hypothesis" being tested actually
covers.

## Correction (2026-07-22) — the above addendum was wrong; retracted

Built during `src/signal_v39.py` test development
(`tests/test_signal_v39.py`): `E3_RECLAIM_WINDOW_H1_BARS` has **no
observable effect on outcomes at any value** (verified directly — running
`signal_v35._e3_trigger` on an identical fixture with the module constant
set to 0, 1, and 50 produces the identical result every time). Root cause:
`smc_engine.liquidity_sweeps()` already requires the reclaim close to occur
on the *same* bar as the sweep wick, by definition (its own docstring:
"body closes back ABOVE it" describes one candle, not a window) — so the
downstream "reclaim window" loop in `_e3_trigger` always matches on its
very first iteration (`k == sweep_i`) regardless of the configured window
size. There is no code path today that can produce a "delayed reclaim N
bars later" signal at all.

**This means the addendum above is retracted: `e3_reclaim_window_h1_bars:
0` in `specs/v3.9.yaml` is not a fourth relaxation** — it is a no-op
parameter change with no behavioral consequence, inherited unchanged from
v3.6/v3.7/v3.8. The RCR's original account (three relaxations: E1 disabled,
E2/E3 wick filters zeroed, displacement body-ratio-only) was correct as
originally written; no amendment to the funnel-attribution requirement is
needed. Left in place (not deleted) per research-log discipline — a wrong
finding, corrected once tested, is itself part of the audit trail.
