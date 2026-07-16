---
name: fair-value-gap
description: >-
  Detect fair value gaps / imbalances. Trigger on 'FVG', 'fair value gap',
  'imbalance', 'gap fill'.
---

# fair-value-gap

## Purpose
Detect 3-candle imbalances (FVG) and track their fill state as draw-on-liquidity / entry zones.

## Inputs
- symbol, timeframe, candles
- min gap size (pips)

## Outputs
- FVG zones: upper/lower bound, direction, created time
- fill state: unfilled / partial / filled

## Workflow
1. Scan 3-candle windows.
2. Bullish FVG = candle1.high < candle3.low (gap around candle2). Bearish = mirror.
3. Record gap bounds if >= min size.
4. Update fill state as later candles trade through it.

## Decision rules
- Unfilled FVG in trade direction = valid entry/target zone.
- Filled FVG loses POI value.

## Validation checklist
- [ ] gap satisfies the strict 3-candle inequality
- [ ] min-size filter applied
- [ ] fill state current

## Failure handling
- No qualifying gap -> return none.
- Fully filled -> mark filled, exclude from POIs.

## Examples
Bullish FVG 1.1420-1.1432 (c1.high 1.1420 < c3.low 1.1432), unfilled.

## Acceptance criteria
- [ ] Bounds + direction + fill state on every FVG
- [ ] deterministic detection
