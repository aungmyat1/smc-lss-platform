---
name: liquidity-sweep
description: >-
  Detect liquidity pools and sweeps (stop runs). Trigger on 'liquidity',
  'liquidity sweep', 'stop run', 'equal highs/lows'.
---

# liquidity-sweep

## Purpose
Identify resting liquidity (equal highs/lows, session/prior-day extremes) and confirm when price sweeps it and rejects.

## Inputs
- symbol, timeframe, candles
- prior session/day high-low
- equal-level tolerance (pips)

## Outputs
- list of liquidity pools with price + type (BSL/SSL)
- sweep events: level, direction, rejection confirmed (bool)

## Workflow
1. Mark equal highs (BSL) / equal lows (SSL) within tolerance.
2. Add prior-day and session extremes as liquidity.
3. A sweep = wick pierces the level then closes back inside.
4. Flag sweep + whether a rejection candle followed.

## Decision rules
- Sweep without close-back-inside = continuation, not a reversal sweep.
- Prefer sweeps into an HTF POI.

## Validation checklist
- [ ] at least one liquidity pool identified
- [ ] sweep requires pierce + close back inside (deterministic)
- [ ] tolerance applied consistently

## Failure handling
- No equal levels -> report 'no clear liquidity', downstream validator fails check 2.
- Ambiguous close -> mark UNCONFIRMED.

## Examples
M15 EURUSD swept equal highs at 1.1476 with a wick to 1.1479 then closed 1.1462 => BSL sweep, rejection confirmed.

## Acceptance criteria
- [ ] Each sweep cites the exact level and the rejection candle
- [ ] BSL/SSL correctly typed
