# ST-C1 v1.1.0 / spec v3.7 — Final Validation Decision

## The three questions, answered separately (per this task's own framing)

**1. Is the strategy rule completely and objectively specified?**
Mostly yes. `specs/v3.7.yaml` numerically defines all ten gates (G1–G10),
including formulas the prior specs left as prose (`equilibrium = low +
0.5*(high-low)`, `net_available_rr` as an explicit formula, causal-structure
identity for stops). Two disclosed simplifications remain (see
`reports/audit/ST_C1_V37_TRACEABILITY_MATRIX.md` "Known, disclosed
simplifications"): G6's POI-touch search is tractability-bounded rather than
matching the full theoretical staleness window, and G2's reusable/consumed
liquidity lifecycle is only tracked for target selection, not as a fully
general structure state machine.

**2. Does the canonical replay engine enforce the rule point-in-time?**
Yes, for the rules it implements — `HistoricalReplayEngineV37` only ever
operates on already-closed, bounded candle windows (`_bounded_context_window`,
`_window`), computes the actual next-bar-open entry before evaluating G4/G8,
and every gate has passing positive and negative tests
(`tests/test_signal_v37_gates.py`, 30 tests; `reports/audit/ST_C1_V37_CONFORMANCE_MATRIX.md`).
Two real engine defects were found and fixed *during this task* via direct
testing against real EURUSD data before any ablation was run: an
undersized M5 search window for G6, and a cross-timeframe/wrong-direction
bug in G5's causal-displacement check (both documented in the pre-edit
findings and traceability matrix). Fixing these was engineering correctness,
not strategy-parameter optimization, and was done before the locked ablation
ran, consistent with the Research Change Request's own rollback clause.

**3. Does the correctly implemented strategy demonstrate a robust net edge?**
**No evidence either way — zero trades were produced.** All 12 cells of the
locked 2×2×3-symbol ablation (`reports/ablation/ST_C1_V37_ABLATION_REPORT.md`)
produced zero qualifying trades on the full available history for EURUSD,
GBPUSD, and XAUUSD. Because A0 (the loosest cell) also produced zero trades,
this is treated per the pre-committed rollback rule as evidence that a
different gate (G6's M5 sequencing timing bounds) saturates all four cells
identically — the ablation cannot discriminate the location-gate vs.
net-reward-gate hypotheses it was designed to test, and no PF, expectancy,
Sharpe, drawdown, or cost-drag figures exist because there is no trade
population to compute them from.

## Classification

Per this task's classification rules (FAILED / OVERFILTERED / FRAGILE /
PROMISING / ROBUST):

**OVERFILTERED** — "promising metrics but insufficient trades or coverage,"
taken to its limiting case: zero trades, not merely few. This is distinct
from **FAILED** (which requires a demonstrated negative edge or a mandatory
gate failure in the sense of a broken rule) — here every gate is correctly
*implemented* and unit-tested; the gates are simply, collectively, far more
restrictive than the market produces qualifying setups for at the currently
committed parameter values. It is also distinct from **PROMISING** (no
positive evidence exists at all) and far short of **ROBUST** (would require
locked OOS, walk-forward, CPCV, Monte Carlo, deflated Sharpe, and cost stress
— none of which are meaningful to run against zero trades).

## Immediate stop conditions triggered

Per VALIDATION AND STOP RULES: **"rule/code conformance is incomplete"** does
not apply (conformance is complete and tested); but the ablation's own
rollback clause **did** trigger ("A0 does not reproduce the baseline's
qualitative shape... engine-parity defect... fix parity before drawing
conclusions") — this was already acted on twice (the two bug fixes) before
concluding. After both fixes, the zero-trade result persisted, so per this
task's explicit instruction ("Do not optimize a failed baseline," "Do not
optimize parameters during this task"), **work stops here** rather than
tuning `poi_entry_to_sweep_max_m5_bars` or the other G6 timing bounds to
manufacture trades.

## What this does and does not prove about SMC concepts generally

This result says nothing about whether HTF-bias/premium-discount/HTF-POI/
net-reward SMC concepts have edge — it says the *specific, pre-committed
numeric bounds* chosen for this first-draft v3.7 contract (in particular
G6's `poi_entry_to_sweep_max_m5_bars=30`, drawn from v3.6's unrelated
retracement-window convention rather than measured M5 sweep frequency) are
too tight for real M5 sweep timing on the checked data. That is a concrete,
falsifiable, and fixable finding — but fixing it requires a fresh Research
Change Request with its own hypothesis and expected numbers, filed *before*
seeing a new result, per `docs/RESEARCH-CHARTER.md`. It is explicitly not
this task's job to file or execute that follow-up.

## Remaining unknowns

- Whether widening G6's sequencing bounds (via a proper RCR) produces a
  workable trade population, and if so, whether that population has positive
  net expectancy.
- Whether the disclosed G6 POI-touch search bound (`m5_poi_entry_search_bars`)
  is itself still too narrow for D1_GAP-origin POIs specifically (max age 10
  D1 days ≈ up to ~2000-2900 M5 bars depending on session coverage) — it was
  set to 3200 as a tractability compromise, not derived from a full
  theoretical-maximum analysis.
- Whether G2's simplified consumed-liquidity tracking (target-only, not a
  full structure lifecycle) would change results once trades exist to
  observe.

## Exact next safe action

File a new, dated Research Change Request in `reports/research_log.md`
(per `docs/RESEARCH-CHARTER.md`) proposing a specific, falsifiable revision
to G6's sequencing bounds — stating the hypothesis and expected trade-count/
funnel-shift numbers *before* running anything — then invoke
`backtest-researcher` to execute it. Do not adjust these parameters ad hoc.

## Safety confirmation

No broker orders were sent at any point in this task. No demo or live
execution flag was touched (`config/watchlist.yaml`'s `autonomy.demo:
proposal_only`, `autonomy.live: disabled`, `promote_to_live: false` are
untouched). `specs/v3.7.yaml` and `strategies/candidates/ST-C1_v1.1.0.yaml`
both carry `engine_implements_spec: false` / `status: candidate` and are
`RESEARCH_CANDIDATE`/`ablation_only` — nothing in this branch changes what
`live_signal.py`, `daily_runner.py`, or any execution path actually does.
`specs/v1.yaml`, `specs/v3.5.yaml`, `specs/v3.6.yaml`, and
`strategies/candidates/ST-C1_v1.yaml` are all unmodified. No parameters were
optimized based on backtest results — the two code changes made after seeing
real-data behavior were engine-correctness fixes (window sizing, a
cross-timeframe index bug), not strategy-parameter tuning, and both are
disclosed with before/after evidence above and in the traceability matrix.
