# ST-C1 v3.9 Stop-Distance / Cost-Dominance Analysis

Date: 2026-07-22
Status: Diagnostic finding — **analysis only, no code/spec change made**.
Scope: answers the open question filed in `NEXT_ACTION.md`'s "After this
milestone" section and the task list in
`reports/audit/ST_C1_V39_STOP_DISTANCE_INVESTIGATION_PLAN.md`.

## One-sentence verdict

Cost-dominance is **not a uniform v3.9 problem** — it is concentrated almost
entirely in EURUSD (and to a lesser extent GBPUSD), driven by structurally
tight stop distances relative to a near-flat per-symbol transaction-cost
model; XAUUSD is close to cost-neutral across every session.

## Data source

`reports/ablation/st_c1_v39_B1_{EURUSD,GBPUSD,XAUUSD}_raw.json` — the B1
(v3.9-as-specified) cell of the already-run, precommitted population
ablation (`reports/audit/ST_C1_V39_POPULATION_ABLATION_SPEC.md`). 138
completed trades total (47 EURUSD, 37 GBPUSD, 54 XAUUSD). No new backtest
was run for this analysis; all numbers below are computed directly from the
existing trade-level `gross_r` / `cost_r` / `net_r` fields already produced
by `validation/historical_replay_engine_v39.py`.

## Overall (all 138 trades, all symbols/sessions combined)

| Metric | Mean | Median |
|---|---|---|
| `gross_r` | +0.172 | +0.006 |
| `cost_r`  | +0.960 | +0.381 |
| `net_r`   | -0.788 | -0.395 |

- Gross win rate: 50.0% (69/138) — roughly a coin flip before cost.
- Net win rate: 30.4% (42/138) — cost alone accounts for the ~20-point drop.
- Median `cost_r`/`|gross_r|` ratio: **0.79** — for the median trade, cost
  consumes nearly 80% of the gross R move. Mean ratio 1.86 (cost exceeds
  gross move outright for a large share of trades).

This directly confirms the hypothesis in `NEXT_ACTION.md`: v3.9 trades are
cost-dominated at the population level. The question is *why*, and whether
it's uniform.

## Per-symbol breakdown — it is not uniform

| Symbol | n | gross_r mean | cost_r mean | net_r mean | net win% | median cost/|gross| |
|---|---|---|---|---|---|---|
| EURUSD | 47 | +0.288 | **+2.077** | **-1.789** | 14.9% | **1.82** |
| GBPUSD | 37 | -0.096 | +0.600 | -0.696 | 21.6% | 0.97 |
| XAUUSD | 54 | +0.255 | **+0.236** | **+0.019** | 50.0% | **0.21** |

XAUUSD is approximately cost-neutral (net_r mean +0.02, net win rate 50%,
matching its gross win rate almost exactly). EURUSD is the extreme case —
cost_r averages over 2R per trade, more than 7x XAUUSD's cost drag, and net
win rate collapses to 14.9%. GBPUSD sits in between.

## Session breakdown, cross-tabulated against symbol

| Symbol | Session | n | cost_r mean | net_r mean |
|---|---|---|---|---|
| EURUSD | London-only | 23 | **+3.455** | **-2.952** |
| EURUSD | NY-only | 19 | +0.777 | -0.638 |
| EURUSD | Overlap | 5 | +0.677 | -0.810 |
| GBPUSD | London-only | 12 | +0.906 | -1.021 |
| GBPUSD | NY-only | 14 | +0.482 | -0.626 |
| GBPUSD | Overlap | 11 | +0.416 | -0.429 |
| XAUUSD | London-only | 32 | +0.325 | -0.003 |
| XAUUSD | NY-only | 15 | +0.124 | +0.074 |
| XAUUSD | Overlap | 7 | +0.066 | +0.003 |

The raw session-only view (not shown per-symbol) makes London-only look like
the worst session overall (mean cost_r +1.50 vs +0.49 NY-only, +0.37
Overlap) — but the cross-tab shows this is almost entirely an EURUSD effect
(cost_r +3.46 in EURUSD London-only alone), not a session effect in its own
right. XAUUSD's cost_r stays low (0.07-0.33) in every session. **Session is
a confound of symbol here, not an independent driver** — a naive
session-only read would have mis-attributed the problem.

No trades fall outside the London/NY windows (0 "off-session" trades),
confirming the session gate itself is working as configured.

## Why EURUSD/GBPUSD and not XAUUSD — code-level explanation

Checked `src/signal_v39.py`'s stop logic directly (`_stop_buffer`,
`_stop_sell`/`_stop_buy`, lines 92-118):

- `STOP_BUFFER_ATR_MULT = 0.15` — **unchanged from v3.7's
  `stop_buffer_atr_mult: 0.15`** (confirmed in `src/signal_v37.py:48`). This
  rules out a version-over-version regression in the buffer multiplier
  itself as the cause.
- The stop is anchored to structural levels — `max/min(zone_high/low,
  inducement, swept_level, displacement_origin)` — plus the small ATR*0.15
  buffer on top. The buffer is a minor addition; the dominant term is the
  structural zone/sweep distance itself.
- `config/research_costs.yaml`'s cost model is **near-flat across symbols
  in point terms**: EURUSD/GBPUSD 25 spread + 3 slippage = 28 points;
  XAUUSD 25 spread + 5 slippage = 30 points — almost identical nominal
  cost magnitude.

Combining these: a near-identical fixed transaction cost, applied against
structurally-anchored stops whose typical *price-distance* scale differs by
roughly an order of magnitude between a tight major FX pair (EURUSD) and a
wide-range metal (XAUUSD), mechanically produces a far worse cost/R ratio
on EURUSD. This is consistent with, and sufficient to explain, the observed
pattern without needing to invoke a v3.9-specific detection-logic defect.

## What this analysis does NOT establish (explicitly out of scope here)

Per the evidence-classification convention used elsewhere in this repo
(`reports/SMC_LSS_V39_GOVERNANCE_CONFORMANCE_AGENT_PROMPT.md`'s
VERIFIED/PARTIAL/NOT IMPLEMENTED/UNKNOWN scale):

- **Raw SL distance in price/pips and ATR-at-entry per trade: NOT
  IMPLEMENTED / not directly available.** The current trade record schema
  in `validation/historical_replay_engine_v39.py` stores only
  `gross_r`/`cost_r`/`net_r`, not `entry`/`stop`/`atr_at_entry`. The
  explanation above is inferred from the cost/R ratio pattern plus a direct
  code read of the stop-anchor logic, not from a direct per-trade
  price-distance extraction. Confirming it numerically would require adding
  diagnostic-only output fields to the replay engine (no behavior change)
  and re-running B1 — flagged as a well-defined, cheap follow-up, not done
  in this pass.
- This analysis does not evaluate whether v3.9's *detection* logic
  (structure/liquidity/POI selection) is correct — only that its resulting
  stop distances, combined with the existing cost model, are economically
  survivable on XAUUSD and not on EURUSD/GBPUSD at this population's
  observed distribution.
- v3.10's net-of-cost read (the other open item in `NEXT_ACTION.md`) is not
  addressed here.

## Recommendation

This finding is diagnostic, not a proposed change — per
`docs/RESEARCH-CHARTER.md`, any resulting parameter or spec change (e.g. a
symbol-specific minimum stop-distance floor, a per-symbol/point-adjusted
cost gate at detection time, or dropping EURUSD/GBPUSD from this preset)
requires its own six-question RCR before implementation or backtest. Two
concrete, falsifiable candidate hypotheses this data supports for such an
RCR:

1. Adding a minimum absolute stop-distance gate (in price/points, not R)
   would disproportionately filter EURUSD/GBPUSD candidates and should
   raise EURUSD's net win rate toward its 50% gross rate.
2. Restricting the traded symbol set to instruments where typical
   structural stop distance clears a fixed-cost-to-risk ratio threshold
   (e.g. cost/gross median < 0.3, matching XAUUSD's observed 0.21) would
   produce a population close to XAUUSD's current cost-neutral profile.

Neither is implemented or backtested here — both require an RCR first.
