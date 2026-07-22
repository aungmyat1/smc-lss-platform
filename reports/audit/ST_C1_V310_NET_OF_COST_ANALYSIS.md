# ST-C1 v3.10 "Reversal Capture" — Net-of-Cost Read

Date: 2026-07-22
Status: Diagnostic/statistical read — **analysis only, no code/spec change,
no optimization, no promotion**.
Scope: closes the open "next step" recorded in
`reports/audit/ST_C1_V310_REVERSAL_CAPTURE_RCR.md`'s addendum and
`NEXT_ACTION.md`'s "Update (2026-07-22)" — the existence check (367 trades)
had already cleared, but no gross/net R, win rate, or profit factor had
been computed.

## One-sentence verdict

Net of cost, v3.10 loses money in aggregate (profit factor 0.73, expectancy
-0.17R) — but that aggregate hides a split identical in shape to v3.9's:
**XAUUSD is profitable (PF 1.68, +0.24R expectancy), EURUSD and GBPUSD are
both net losers** (PF 0.62 and 0.42 respectively).

## Method

Reused `validation/historical_replay_engine_v310.py` and the same
symbol-aware cost model already validated for v3.9
(`config/research_costs.yaml`) via a new runner,
`validation/run_v310_net_of_cost.py`, mirroring
`validation/run_v39_population_ablation.py`'s pattern exactly (same output
schema: `gross_r`/`cost_r`/`net_r`/`funnel_counts`/`metrics` per trade).
H4 is derived from H1 via `smc_engine.resample(h1, 4)`, per the RCR
addendum's documented fix for missing/too-short native H4 files — not
fabricated data, same mechanism already used for the existence check.

Data: full local history per symbol (M5/H1/D1), same files used throughout
the ST-C1 v3.9/v3.10 research line. **This is development data, already
inspected in prior tasks — not a pristine OOS partition**, same disclosure
as the v3.9 ablation and stop-distance analysis.

Raw output: `reports/ablation/st_c1_v310_net_of_cost_{EURUSD,GBPUSD,XAUUSD}_raw.json`.

## Existence-check cross-check

| Symbol | Trades (this run) | Trades (RCR addendum) |
|---|---|---|
| EURUSD | 135 | 135 |
| GBPUSD | 112 | 112 |
| XAUUSD | 120 | 120 |

Exact match — confirms this run reproduces the same population the RCR's
existence check reported, now with gross/cost/net R computed on top.

## Overall (all 367 trades, all symbols combined)

| Metric | Value |
|---|---|
| gross_r mean / median | +0.512 / +1.000 |
| cost_r mean / median | +0.683 / +0.237 |
| net_r mean / median | -0.172 / +0.277 |
| Gross win rate | 74.7% |
| Net win rate | 58.6% |
| Net profit factor | **0.731** |
| Net expectancy | **-0.172R** |

Cost erodes win rate by ~16 points (74.7% -> 58.6%) and flips a positive
median trade into an aggregate losing system. This is the same directional
effect as v3.9 (cost meaningfully damages the edge), though noticeably less
severe in relative terms than v3.9's overall PF-equivalent picture (v3.9's
overall net_r mean was -0.79R against a smaller gross_r mean of +0.17R).

## Per-symbol breakdown — same split shape as v3.9

| Symbol | n | gross_r mean | cost_r mean | net_r mean | net win% | net PF | median cost/|gross| |
|---|---|---|---|---|---|---|---|
| EURUSD | 135 | +0.628 | +0.867 | **-0.239** | 59.3% | **0.624** | 0.488 |
| GBPUSD | 112 | +0.454 | +0.990 | **-0.537** | 50.9% | **0.425** | 0.406 |
| XAUUSD | 120 | +0.435 | +0.190 | **+0.245** | 65.0% | **1.677** | 0.084 |

XAUUSD is the only net-profitable symbol, with the lowest cost drag by a
wide margin (median cost/|gross| 0.084 vs. 0.41-0.49 for EURUSD/GBPUSD) —
directly consistent with
`reports/audit/ST_C1_V39_STOP_DISTANCE_ANALYSIS.md`'s finding that
EURUSD/GBPUSD's structurally-anchored stops sit much closer to this
platform's near-flat per-symbol transaction-cost floor than XAUUSD's do.
That v3.9 finding was specific to v3.9's engine, but the same symbol-level
pattern reappearing in an independently-built v3.10 engine (different
detection logic, same cost model) is evidence the cost/stop-scale mismatch
is a property of these instruments under this cost model in this data
window, not an artifact of one engine's parameters.

## One anomaly flagged, not resolved here

`duplicate_structure` funnel counts are very high relative to
`signal_pass`/`candidate_ready` — e.g. EURUSD: 13,857 candidate-ready down
to 135 executed trades (~99% deduplicated), versus v3.9's equivalent ratio
of roughly 77% (160 of 207 candidate-ready deduplicated). This is disclosed
as an observation, not diagnosed: it may be expected behavior (a
persistent structure re-evaluated across many consecutive bars before
invalidation, correctly collapsed to one trade) or may indicate the
dedup/structure-key logic is coarser than intended for v3.10's specific
structure representation. **Not verified either way in this pass** — flagged
for a follow-up check before this population count is used as an input to
any deflated-Sharpe/multiple-testing calculation, since an inflated
"candidate" count feeding into a trial-count denominator elsewhere could
matter later even though it doesn't affect the executed-trade R statistics
reported above.

## Rollback-criteria check (per the RCR)

- **Zero qualifying signals across all three symbols** — did not occur;
  N/A.
- **Fail-open/look-ahead defect** — none found in this pass; not
  independently re-audited here (relies on the 14 dedicated tests already
  reported passing in the RCR addendum plus the 178-test full-suite run
  reported there). Re-running the full suite was out of scope for this
  read and was not repeated here.
- **Dynamic R:R violating `min_rr: 3.0` net of cost** — not directly
  checked in this pass. `gross_r` in this engine reflects trade-management-
  adjusted realized R (partial-take/breakeven logic), not the entry-time
  detection RR gate, so it cannot be read off this dataset alone. Flagged
  as **UNKNOWN**, not silently assumed clear.

## What this does NOT establish

- Not a promotion, approval, or "ROBUST" classification. This is
  development-data, in-sample-only evidence, single-pass (no walk-forward,
  no OOS, no CPCV, no deflated Sharpe).
- Not a comparison verdict against v3.9 — both remain open candidates with
  their own unresolved cost/quality questions; `NEXT_ACTION.md` explicitly
  defers any candidate-vs-candidate comparison until both reads exist,
  which is now the case, but the comparison itself is a separate next step.
- Does not authorize any parameter change, symbol-set restriction, or
  further validation-stage advancement — any of those require their own
  RCR per `docs/RESEARCH-CHARTER.md`.

## Recommendation

Two threads now ready for the owner/`project-governance-agent` to sequence,
not started here:

1. **v3.9 vs v3.10 comparison**, now that both have a net-of-cost read —
   both show the same EURUSD/GBPUSD-losing, XAUUSD-winning shape, which
   itself may be the more decision-relevant finding than either candidate
   individually (symbol selection may matter more than which of the two
   detection designs is used).
2. **The `duplicate_structure` anomaly** — worth a quick, cheap check
   before either candidate proceeds further, since a coarse dedup key could
   be silently inflating or deflating the executed-trade population in a
   way that matters for any future statistical-significance read.

Neither is executed in this pass; both require explicit sequencing first.
