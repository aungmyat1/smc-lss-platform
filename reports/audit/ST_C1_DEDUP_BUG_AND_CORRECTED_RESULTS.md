# ST-C1 `structure_key` Dedup Bug — Root Cause, Fix, and Corrected v3.9/v3.10 Results

Date: 2026-07-22
Status: **Bug fix + corrected evidence, superseding prior committed results.**
Classified as a bug fix per `docs/RESEARCH-CHARTER.md`'s carve-out ("the
`before` behavior was never intended and the `after` behavior is just
correcting an implementation error against an already-agreed spec") — not
a detection-logic design change, so no RCR was required for the fix
itself. This closes the "investigate `duplicate_structure` anomaly" item
from `NEXT_ACTION.md`.

## What was found

Both `validation/historical_replay_engine_v39.py` and
`validation/historical_replay_engine_v310.py` build a 300-bar rolling
window (`m5_window = _window(m5, index, 300)`) and pass it to
`signal_v39.analyze()` / `signal_v310.analyze()`, which compute
`structure_key = (symbol, variant, "zone", index_offset + st.zone_creation_i)`.
`zone_creation_i` is an index **within that local 300-bar window** (range
0-299). `index_offset` exists specifically to convert this into a global,
whole-history-unique position — but **neither replay engine ever passed
it**, so it silently defaulted to `0` in both. `src/signal_v35.py`'s own
docstring confirms the intended contract: *"index_offset: the caller's
global bar index that m5[0] corresponds to"* — and `src/backtest_v35.py:113`
already wires this correctly (`index_offset=window_start`). v3.9/v3.10's
replay engines are newer code that dropped this argument, reintroducing a
bug v3.5 had already solved correctly.

**Effect:** any two structurally-unrelated zones detected at completely
different points across the ~80,000-bar (~1 year) history, that happened
to land at the same relative offset within their own 300-bar window,
collided onto an identical `structure_key`. Once the first one executed a
trade, the in-memory `consumed` set treated every later, genuinely
distinct zone at that same relative offset as an already-traded duplicate
— silently discarding real, valid trading opportunities for the rest of
the backtest.

## Empirical confirmation (before the fix)

A read-only diagnostic scan of v3.10/EURUSD (no repo files touched, full
local history) found the single most-repeated `structure_key`,
`('EURUSD', 'E3M1', 'zone', 299)`, hit 1,298 times spanning
**2025-06-25 to 2026-07-21 — the entire dataset.** No real order-block/gap
zone remains valid for a year; this is only explainable by cross-time key
collision. Top 10% of distinct keys accounted for 59% of all candidate
hits.

## Fix

Both replay engines now compute `m5_window_start = max(0, index - 299)`
(matching `_window`'s own `start = max(0, end - size + 1)`) and pass
`index_offset=m5_window_start` into `analyze()`. Two-line change per file
plus one call-site argument each. Full repository test suite re-run after
the change: **179 passed**, no regressions — no test asserted on a
specific computed `structure_key` value from either engine's `analyze()`
output (only hand-constructed fixtures used literal keys like `"k1"`).

## Impact — trade counts changed substantially

| Engine | Symbol | Before | After | Change |
|---|---|---|---|---|
| v3.9 B1 | EURUSD | 47 | 80 | +70% |
| v3.9 B1 | GBPUSD | 37 | 78 | +111% |
| v3.9 B1 | XAUUSD | 54 | 81 | +50% |
| v3.10 | EURUSD | 135 | 789 | +484% |
| v3.10 | GBPUSD | 112 | 744 | +564% |
| v3.10 | XAUUSD | 120 | 684 | +470% |

v3.10's population grew far more (5-6x) than v3.9's (+50-111%), consistent
with v3.10's originally-observed duplicate rate being much higher (~99%
vs. v3.9's ~77%) — the bug's severity scales with how long a design's
structures tend to stay geometrically "fresh" at the same window-relative
offset, and v3.10's D1-gap-anchored E1/E3 structures apparently do this far
more than v3.9's.

## Corrected results — supersedes `ST_C1_V39_STOP_DISTANCE_ANALYSIS.md` and `ST_C1_V310_NET_OF_COST_ANALYSIS.md`

### v3.9 B1 (corrected)

| Symbol | n | gross_r mean | cost_r mean | net_r mean | net win% | net PF |
|---|---|---|---|---|---|---|
| EURUSD | 80 | -0.075 | +1.024 | -1.099 | 10.0% | 0.049 |
| GBPUSD | 78 | -0.036 | +0.714 | -0.750 | 19.2% | 0.125 |
| XAUUSD | 81 | -0.202 | +0.086 | -0.288 | 28.4% | 0.382 |
| **Overall** | **239** | **-0.105** | **+0.605** | **-0.710** | **19.2%** | **0.138** |

**This overturns the prior conclusion.** The previously-reported "XAUUSD is
cost-neutral" finding does not survive the fix: XAUUSD's corrected gross_r
mean is *negative* (-0.202) even before cost, and net PF is 0.382, not
cost-neutral. The bug had been retaining a biased, luckier-than-true subset
of trades at each colliding key (whichever zone happened to execute first
at that offset) — not a representative sample. All three symbols are now
net-losing, and materially worse than previously reported across the
board.

### v3.10 (corrected)

| Symbol | n | gross_r mean | cost_r mean | net_r mean | net win% | net PF |
|---|---|---|---|---|---|---|
| EURUSD | 789 | +0.075 | +0.690 | -0.615 | 40.4% | 0.309 |
| GBPUSD | 744 | +0.138 | +0.566 | -0.428 | 47.2% | 0.460 |
| XAUUSD | 684 | +0.085 | +0.257 | -0.172 | 52.5% | 0.734 |
| **Overall** | **2217** | **+0.099** | **+0.515** | **-0.416** | **46.4%** | **0.469** |

Same story: the previously-reported "XAUUSD is net-profitable" finding
(PF 1.677) does not survive the fix — corrected XAUUSD PF is 0.734, still
the best of the three symbols but net-losing, not profitable. All three
symbols net-losing; aggregate PF worsens from 0.731 (buggy) to 0.469
(corrected).

## What holds and what doesn't, from the original analyses

- **Still holds:** cost meaningfully erodes both candidates' edge, and
  XAUUSD remains relatively the least cost-damaged symbol in both engines
  (lowest cost_r, highest relative PF among the three) — the *qualitative
  ranking* EURUSD/GBPUSD-worse-than-XAUUSD survives the fix in both v3.9
  and v3.10.
- **Does not hold:** the claim that XAUUSD is cost-neutral or profitable in
  either candidate. Both `ST_C1_V39_STOP_DISTANCE_ANALYSIS.md`'s and
  `ST_C1_V310_NET_OF_COST_ANALYSIS.md`'s headline verdicts are corrected by
  this document. A superseding notice has been added to the top of both
  files pointing here; their original content is left intact below the
  notice as historical record, per this repo's practice of preserving
  prior findings (including wrong ones) rather than deleting them.
- **The v3.10 dedup-anomaly question itself is now fully answered:**
  confirmed **bug**, not a real design property and not a data-shape
  artifact, per the task that opened this investigation.

## What this does not establish

- Not a promotion/approval decision. Both candidates are now more clearly
  net-losing in aggregate than previously understood, which if anything
  raises the bar further before any further validation stage.
- Does not itself decide the v3.9-vs-v3.10 comparison or any RCR — those
  remain open, separate next steps, now to be run against corrected data.
- No parameter, spec, or promotion-flag change was made. `engine_implements_spec`
  remains `false` for both `specs/v3.9.yaml` and `specs/v3.10.yaml`.
