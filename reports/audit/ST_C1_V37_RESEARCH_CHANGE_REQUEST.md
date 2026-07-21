# Research Change Request — ST-C1 v1.0 → v1.1.0 (spec v3.6 → v3.7)

Filed per `docs/RESEARCH-CHARTER.md` before any backtest is run on the new candidate.
This is a genuine research/design change, not a bug fix against an already-agreed
spec — v3.6/ST-C1 v1.0 never had premium/discount, HTF-FVG, or net-reward gates
implemented at all (see `ST_C1_V37_PRE_EDIT_FINDINGS.md` §5), so there is no prior
"intended" behavior being restored.

## Change: 10-gate strategy conformance (spec version: v3.6 -> v3.7, contract ST-C1 v1.0 -> v1.1.0)
Date: 2026-07-21
Author: Claude (research agent), on behalf of the owner-directed audit task

### Why
`reports/audit/st_c1_strategy_conformance_matrix.md` and this task's own pre-edit
findings establish that the 363-trade Phase A baseline (PF 0.4272, expectancy
-0.4116R) was produced by `validation/historical_replay_engine.py` calling
`live_signal.py`'s v1 legacy swing/equilibrium signal wrapped in an ad hoc
sweep/POI layer — not by any implementation of the v3.6 E-trigger/M-model
contract, and not by anything resembling premium/discount location, HTF POI/FVG,
causal structural invalidation, or a net-of-cost reward gate. The baseline result
is therefore evidence about an unintended surrogate, not about ST-C1/v3.6. There
is currently zero evidence — positive or negative — about the strategy this
project's documents (`docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md`,
`strategies/candidates/ST-C1_v1.yaml`) actually describe.

### Evidence
- `reports/audit/st_c1_strategy_conformance_matrix.md`: E1/E2/E3, displacement,
  and CHoCH classification rated MISSING/PARTIAL/MISLABELED against the actual
  replay path.
- `specs/v3.6.yaml` §26 (`docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md` "What v3.6
  changes vs. current code") lists its own implementation checklist as unchecked.
- `validation/historical_replay_engine.py::_determine_target` falls back silently
  to `entry ± min_rr*risk` when no swing extremum exists — the exact "no-DOL
  silently passes" defect `src/signal_v35.py` already fixed with
  `REJECT_NO_TARGET`, but never ported into the engine that produced the baseline.
- `strategies/candidates/ST-C1_v1.yaml`'s own `poi.premium_discount` and
  `entry_model.long/short` sections require discount/premium location before
  entry; no test in the repo verifies this, and the replay engine does not
  implement it as a persisted, ID-anchored range gate.

### Hypothesis
The baseline's negative expectancy is confounded by three unmeasured, entangled
defects rather than being attributable to "SMC concepts don't have edge on this
data": (1) the signal source itself is not the E/M contract at all (v1 legacy
signal, no HTF causal chain); (2) there is no premium/discount location filter,
so counter-trend-into-premium/discount-against-them longs/shorts are admitted;
(3) the reward gate is gross 2R with a silent fallback target, not a
net-of-cost 3R gate against a preselected external-liquidity target — so trades
that are mechanically unprofitable after real spread/slippage/commission are
still counted as qualifying. Implementing G1–G10 correctly, and running the
locked 2×2 ablation (location × reward-gate) specified in this task, will
separate which of these three factors (if any) drives the sign of expectancy,
rather than continuing to read one conflated number.

### Expected improvement
No specific expectancy number is asserted in advance — per this task's own
constraint ("closer alignment with the article is not proof of edge") and
`docs/RESEARCH-CHARTER.md`'s ban on vague directional claims, a number is
still required, so it is stated as a falsifiable trade-count/structure
expectation instead: correctly gating on G1–G10 (HTF bias + external structure +
premium/discount + HTF POI + net 3R) is expected to reduce total qualifying
trade count by at least 70% relative to the 363-trade Phase A baseline (fewer,
more selective setups), and is expected to change the funnel's dominant
rejection reason from "signal"/"sweep" (structural, as today) to "location"
and/or "net_rr" (economic) rejections at least 25% of the time each. If neither
shift occurs, the hypothesis that location/net-RR gating meaningfully changes
the qualifying trade population is rejected regardless of the resulting PF.

### Success criteria
This is a locked ablation (A0–A3), not a single accept/reject backtest. Success
for the *research change* (implementing G1–G10 correctly) is: (a) all 10 gates
have at least one positive and one negative test passing; (b) `A0`
(location-as-today + gross 2R) reproduces the qualitative shape of the existing
Phase A baseline within the same engine (sanity check that nothing else moved);
(c) `A1`/`A2`/`A3` funnels show the location and net-RR gates each independently
rejecting a nonzero, auditable share of candidates (evidence the gates are live,
not dead code). Promotion to a `PROMISING`/`ROBUST` classification is explicitly
**out of scope for this task** per the owner's ablation-not-optimization
instruction; classification here can only be `FAILED`/`OVERFILTERED`/`FRAGILE`
at best, per the VALIDATION AND STOP RULES section of this task.

### Rollback criteria
Revert to treating v3.6/ST-C1 v1.0 + the existing conformance matrix as the
last word, and stop before running any ablation, if: point-in-time / no-lookahead
tests fail for the new canonical module; a clean run and a resumed run of the
same ablation cell disagree; any gate silently defaults to pass when its inputs
are missing (violates the required gate-trace contract); or cost reconciliation
between gross/net R cannot be closed to tolerance. If A0 does **not** reproduce
the existing baseline's qualitative shape (roughly: extremely high trade count,
negative net expectancy) inside the new engine, that is treated as an engine
defect (an apples-to-oranges swap, not a strategy result) and is INCONCLUSIVE —
fix the engine parity issue before drawing any conclusion from A1–A3.

---
Logged to `reports/research_log.md` in date order alongside this entry, per
`docs/RESEARCH-CHARTER.md`. No backtest was run before this template was filled.
