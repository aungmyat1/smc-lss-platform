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
