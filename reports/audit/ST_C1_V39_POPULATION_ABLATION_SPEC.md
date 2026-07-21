# ST-C1 v3.9 Population-Feasibility Ablation — Pre-Registered Spec

Written before inspecting any run output (no trade/signal counts have been
viewed at the time this file was created). Acceptance/rejection criteria are
identical to, and inherited from, the already-precommitted criteria in
`reports/audit/ST_C1_V39_CLEAN_SMC_RCR.md` (filed 2026-07-22, before any
v3.9 backtest ran) — this document formalizes the run design against the
newly-built canonical engine (`src/signal_v39.py` +
`validation/historical_replay_engine_v39.py`), it does not introduce new
criteria.

## Purpose

Population feasibility only — is there a large enough completed-sequence
population under v3.9's rules to make a statistical read meaningful at all?
This is explicitly **not** a profitability read (Phase 7 of the source task
is gated on this passing first, and is out of scope for this run regardless
of outcome).

## Cells

Given the owner-directed decision to audit v3.9 in its own E1/E2/E3 terms
(not the parked v3.7 G1-G10 framework), the ablation is structured around
the RCR's own three named relaxations plus one baseline control, not the
source task's A0-A4 G6-population template (which assumed the G1-G10
schema and does not map onto v3.9's actual parameters):

- **B0 (control): v3.6 as specified** — `src/signal_v35.py` unchanged
  (E1 enabled, POI age 60/wick-ratio 0.4/0.5, ATR-gated displacement).
  Establishes the population size the *unrelaxed* schema produces on the
  same data, for direct comparison.
- **B1 (candidate): v3.9 as specified** — `src/signal_v39.py` (E1 disabled,
  E2/E3 wick-ratio zeroed, POI age 120/E3 lookback 60, body-ratio-only
  displacement 0.6/12-bar). This is `ST-C1_v1.2.0.yaml` exactly as filed;
  no parameter is altered for this run.

A full B2/B3/B4 factorial isolating each of the three relaxations
individually was considered but is deferred: given the session's compute
budget, the priority is the single decision-relevant number the RCR
actually gates on (does B1 clear the population floor at all). If B1 passes
and a mechanism breakdown is later needed, that is a well-defined, cheap
follow-up (toggle one v3.9 constant at a time) — noted as next-step scope,
not run here.

## Data

`data/EURUSD_M5.csv` + `data/EURUSD_H1.csv`, `data/GBPUSD_M5.csv` +
`data/GBPUSD_H1.csv`, `data/XAUUSD-VIP_M5.csv` + `data/XAUUSD-VIP_H1.csv` —
the full locally available history for each (M5 ~78-80k bars per symbol,
2025-06 through 2026-07 for EURUSD/GBPUSD, 2025-06 through 2026-07 for
XAUUSD; H1 series extend further back, used only for HTF context windows).

**This is development data, already inspected during the v3.7/v3.8 research
tasks (per `PROJECT_STATUS.md` §5's standing data note) — it is not a
pristine, unseen OOS partition, and this run does not change that status.**
No held-out/locked-OOS split exists in this repository for this strategy
family yet; this is disclosed, not worked around.

## Cost/config freeze

- `HistoricalReplayEngineV39` defaults: `min_rr=3.0` (matches
  `ST-C1_v1.2.0.yaml`'s `min_rr: 3.0` hard floor), cost profile from
  `config/research_costs.yaml` (symbol-aware spread/slippage/commission,
  unchanged from the existing, already-validated cost model — see
  conformance matrix's "Reward / cost model" row).
- `warmup_bars=350` (M5-side detection-window minimum; the H1 side is
  bounded by calendar time independently, not by this value — see
  `HistoricalReplayEngineV39`'s docstring).
- No parameter is tuned between B0 and B1 beyond the three RCR-named
  relaxations baked into `signal_v39.py` vs `signal_v35.py`.

## Acceptance / rejection (precommitted in the RCR, restated here)

- **Population floor:** >=30 completed sequences (signals->trades, i.e.
  `num_trades` in the run output) across EURUSD+GBPUSD+XAUUSD combined,
  AND >=5 in at least 2 of the 3 symbols.
- **REJECTED_NO_DISPLACEMENT share:** not independently measurable with a
  single rejection-code bucket in this engine (the current
  `HistoricalReplayEngineV39.generate_signal` funnel records a coarse
  `rejected_signal` count from `signal_v39.analyze`'s NO-SIGNAL reason
  string, not a per-gate breakdown at replay-engine level) — this is a
  known coverage gap relative to the RCR's second expected-improvement
  number; the *reason strings* inside `rejected_signal` entries are
  inspected qualitatively below instead of a precise percentage.
- **Determinism:** clean vs re-run agreement (already verified in
  `tests/test_historical_replay_v39.py::test_replay_is_deterministic_clean_vs_rerun`
  on synthetic data; not re-run on live data here for time reasons, but the
  engine has no random or wall-clock-dependent state, so this generalizes).
- **Rollback:** if B1 does not clear the population floor, report FAILED
  with the funnel evidence — no parameter tuning, no threshold-shopping, no
  re-running with loosened criteria in this task.
- **If B1 passes:** population feasibility is established; a profitability
  read (Phase 7-equivalent) becomes the next safe action, not something to
  compute inline in this same pass (per the source task's explicit
  sequencing: population first, independently of P&L).

## What happens next in this document

Results are appended to this file's end AFTER both B0 and B1 complete for
all three symbols, with the exact command, elapsed time, and per-symbol
funnel counts — not summarized or cherry-picked.

---

## Results (2026-07-22, exact-head worktree per the final audit report)

Both cells run on the full local history for each symbol: `data/EURUSD_M5.csv`
(2025-06-24 to 2026-07-21, 80,004 M5 bars), `data/GBPUSD_M5.csv` (same range,
80,015 bars), `data/XAUUSD-VIP_M5.csv` (2025-06-03 to 2026-07-21, 80,000
bars); corresponding H1 files (9,000 bars each, extending further back for
HTF context). Engine: `HistoricalReplayEngineV39` (B1) /
`HistoricalReplayEngineV36Control` — a same-machinery subclass wired to
`signal_v35.analyze()` instead of `signal_v39.analyze()` (B0), both with
`warmup_bars=350` (default), same cost profile
(`config/research_costs.yaml`).

### Population (completed sequences = trades)

| Symbol | B0 (v3.6 control) | B1 (v3.9 candidate) |
|---|---|---|
| EURUSD | 2 | 47 |
| GBPUSD | 2 | 37 |
| XAUUSD | 49 | 54 |
| **Total** | **53** | **138** |

### Population-feasibility gate (precommitted: >=30 total AND >=5 in >=2 symbols)

- **B1 (v3.9): PASSES clearly.** 138 total (>>30); all three symbols
  individually clear >=5 (not just two).
- **B0 (v3.6): technically clears the total (53>=30) but FAILS the
  diversification requirement** — only XAUUSD reaches >=5 (49); EURUSD and
  GBPUSD each produce only 2. This is the same shape of failure the v3.7/v3.8
  research line hit (population concentrated in one symbol, or absent).

### Mechanism check (does the population growth trace to the named relaxations, not something else?)

Direct, symbol-by-symbol evidence that the three named relaxations (E1 off,
E2/E3 wick-ratio zeroed, body-ratio-only displacement) are what unlocks
population, not an artifact: EURUSD goes from 2 (B0) to 47 (B1) trades and
GBPUSD from 2 to 37 — both symbols were essentially unpopulated under
unrelaxed v3.6 rules over this ~13-month window and become well-populated
under v3.9. XAUUSD's smaller B0->B1 change (49->54) is consistent with
XAUUSD never having been the population bottleneck (it already cleared the
floor alone under v3.6). This directly supports the RCR's hypothesis: the
FX pairs, not XAUUSD, were where the relaxations were structurally needed.

### Important caveat this gate does NOT resolve — informational net-R only, not a Phase 7 verdict

Population feasibility is a gate on trade *count*, not quality. The engine's
already-existing, reused cost model (gross_r/cost_r/net_r per trade) surfaces
a real quality concern that must not be read past this report's scope:

| Symbol | B1 win rate | B1 profit factor | B1 net R (sum) | B0 win rate | B0 profit factor | B0 net R (sum) |
|---|---|---|---|---|---|---|
| EURUSD | 14.9% | 0.03 | -84.07 | 0% (n=2) | 0.0 | -2.90 |
| GBPUSD | 21.6% | 0.14 | -25.73 | 0% (n=2) | 0.0 | -1.71 |
| XAUUSD | 50.0% | 1.06 | +1.04 | 61.2% | 1.96 | +12.02 |

EURUSD and GBPUSD under B1 show deeply negative net expectancy, and
inspecting individual trades shows several with `cost_r` many multiples of
`gross_r` (e.g. one EURUSD trade: `gross_r=1.0`, `cost_r=31.0`, `net_r=-30.0`)
— the ATR*0.15 stop buffer these trades used produced a very tight risk
distance relative to the fixed spread/slippage cost assumptions, so the
cost model correctly, mechanically penalizes them; this is not a bug in the
cost model, but it is a strong signal that the relaxed E2/E3+displacement
rules are generating some structurally very-tight-stop setups that a
production strategy would need to filter or a cost/risk designer would need
to address — **out of scope to fix in this task** (population feasibility
only, no profitability tuning), but too material to omit.

XAUUSD is directionally healthier under B1 (PF 1.06, marginally net
positive) but noticeably worse than its own B0 control (PF 1.96) — i.e. the
relaxations that were necessary to unlock EURUSD/GBPUSD population appear to
have diluted per-trade quality on XAUUSD, where population was never the
constraint. This is a real quantity/quality tradeoff worth surfacing to the
owner before any Phase-7-equivalent statistical validation is attempted.

### Verdict for this document's precommitted question

**Population feasibility: ACCEPTED for v3.9 as specified** (all three
symbols individually clear the floor; the growth traces to the intended
mechanism). **No profitability classification is made** — Phase 7's
preconditions (locked OOS split, deflated Sharpe, walk-forward) were never
run, this was never in scope for this task, and the raw net-R numbers above
are reported as risk context, not a FAILED/OVERFILTERED/FRAGILE/PROMISING/
ROBUST verdict.

### Determinism / reproducibility of this run

Not independently re-run on this exact live dataset (a second ~21-minute
run per symbol was judged not worth the marginal evidence given
`tests/test_historical_replay_v39.py::test_replay_is_deterministic_clean_vs_rerun`
already establishes clean-vs-resumed equality on synthetic data with the
same engine, and the engine has no random or wall-clock-dependent state).
Flagged as a residual gap, not asserted as verified on live data.

