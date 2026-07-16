---
name: market-structure
description: >-
  Detect and label market structure on any timeframe. Trigger on 'market
  structure', 'trend state', 'HH HL LH LL', 'analyze structure of <symbol>'.
---

# market-structure

## Purpose
Deterministically classify swing structure (HH/HL/LH/LL) and current trend state (bullish / bearish / ranging) for a symbol+timeframe.

## Inputs
- symbol, timeframe
- N candles via metatrader.get_candles_latest (default 200)
- swing lookback (fractal window, default 2)

## Outputs
- ordered list of swing highs/lows with price+time
- trend state enum: BULLISH | BEARISH | RANGING
- last confirmed swing high and swing low (for BOS/CHoCH reference)

## Workflow
1. Pull candles.
2. Detect fractal swing points (high with `lookback` lower highs each side; symmetric for lows).
3. Sequence swings; label HH/HL/LH/LL vs previous same-type swing.
4. Trend = BULLISH if latest = HH+HL, BEARISH if LH+LL, else RANGING.
5. Emit the last protected high/low for downstream skills.

## Decision rules
- Two consecutive HH/HL = uptrend; two LH/LL = downtrend; mixed = range.
- A single swing does not define trend.

## Validation checklist
- [ ] >= 50 candles available
- [ ] at least 2 swing highs and 2 swing lows detected
- [ ] deterministic: identical candles -> identical labels

## Failure handling
- Insufficient candles -> return NEEDS_MORE_DATA, do not guess.
- Flat/low-volatility data -> RANGING, not a forced trend.

## Examples
H4 EURUSD: swings 1.1377(L)->1.1483(HH)->1.1406(HL) => BULLISH, protected low 1.1406.

## Acceptance criteria
- [ ] Trend state returned with the swing evidence that justifies it
- [ ] Protected high/low emitted for BOS/CHoCH use
