# ST-C1 v3.10 E1 Tie-Break RCR — Results

Date: 2026-07-22
Status: RCR closed — **outcome: INCONCLUSIVE** on the reversal-capture
thesis, per `reports/audit/ST_C1_V310_E1_TIEBREAK_RCR.md`'s own
pre-declared rollback criteria. Implements the change filed in that RCR;
authorized by `project-governance-agent`.

## What changed

`src/signal_v310.py`'s `detect_e_trigger` now returns E1's result outright
whenever `_e1_trigger_reversal` qualifies, instead of competing against
E2/E3 in a `max(candidates, key=confirm_i)` tie-break. E2/E3 still use the
recency tie-break between each other when E1 does not qualify. Two-line
functional change plus docstring; 3 new tests added
(`tests/test_signal_v310.py`); full suite: 182 passed (179 + 3 new).
Changelog note added to `strategies/candidates/ST-C1_v1.3.0.yaml`; no
version bump (ruled engine-internal, not spec-versioned).

## Result 1 — E1 now fires (success criterion met)

| Symbol | E1 trades |
|---|---|
| EURUSD | 16 |
| GBPUSD | 24 |
| XAUUSD | 16 |
| **Total** | **56** |

All variant `E1M2` (E1 trigger, M2 model) — no `E1M1`/`E1M3` combination
appeared. E1 fires in all three symbols, clearing the RCR's first success
criterion ("at least 2 of 3 symbols").

## Result 2 — E1's behavior is NOT statistically distinguishable from E2/E3 (success criterion NOT met)

| | n | net_r mean | net_r std | net win rate |
|---|---|---|---|---|
| E1 | 56 | -0.339 | 1.042 | 41.1% |
| E2/E3 | 2,157 | -0.398 | 1.978 | 45.8% |

Welch's t-test on net_r: **t = 0.407** (difference 0.059R, pooled SE
0.146). Two-proportion z-test on win rate: **z = -0.704** (difference
-4.7 points, SE 6.7 points). Both are far below the conventional |t|/|z|
>= ~1.96 threshold for 95% confidence — **the observed differences are
consistent with noise at this sample size**, not evidence of a distinct
E1 behavioral signature.

Per the RCR's own pre-declared rollback criteria: *"If E1's resulting
trade population is statistically indistinguishable from E2/E3's... report
as INCONCLUSIVE on the reversal-capture thesis specifically."* That
condition is met. **Verdict: INCONCLUSIVE**, not REJECTED and not
ACCEPTED — 56 trades is a small population, and this result does not rule
out a real difference that a larger population might reveal; it also does
not establish one.

## Result 3 — aggregate PF barely moved, as predicted

| | Aggregate net PF |
|---|---|
| Before (max-confirm_i, all 3 triggers) | 0.469 |
| After (E1-priority) | 0.471 |

The RCR's Expected Improvement section explicitly predicted this: *"NOT
expected to materially change v3.10's aggregate net profit factor."*
Confirmed. Both candidates remain net-losing in every symbol; this RCR
does not change that verdict, and was never intended to (per its own
Notes section and `project-governance-agent`'s authorization).

## What this does and does not establish

- **Does establish:** the tie-break fix works as designed — E1 fires now,
  in all three symbols, for the first time since v3.10 was built.
- **Does not establish:** whether the reversal-capture mechanism has real
  edge. 56 trades is too small a population to distinguish from noise
  against a backdrop of ~2R standard deviation per trade.
- **Does not change:** the separate, larger fact that both v3.9 and v3.10
  are net-losing in every symbol (v3.9 aggregate PF 0.138, v3.10 aggregate
  PF 0.471) — that decision (park vs. continue) remains open and is not
  resolved by this RCR either way, consistent with what was scoped from
  the start.

## Recommended next step

Not started here. Two honest options, neither preferred over the other by
this result:

1. Treat the E1 thesis as inconclusive-and-parked alongside the rest of
   the ST-C1 v3.9/v3.10 line, pending the larger park-or-continue decision.
2. If the line continues, a larger, purpose-built population test (e.g.
   relaxing E1's own gates specifically, which is a separate detection-
   logic change requiring its own RCR) would be needed before this
   specific mechanism could be judged — not merely re-running the same
   engine, which is now bottlenecked by E1's own ~1.86% qualification
   rate, not the tie-break.
