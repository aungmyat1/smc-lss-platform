---
name: order-block
description: >-
  Identify order blocks (OB). Trigger on 'order block', 'OB', 'last down/up
  candle before move'.
---

# order-block

## Purpose
Locate the last opposing candle before an impulsive displacement that breaks structure, and define its zone.

## Inputs
- symbol, timeframe, candles
- structure break reference (from choch-bos)
- displacement threshold

## Outputs
- OB zone (open-close or high-low), direction (bullish/bearish), origin time
- mitigation status (untouched / mitigated)

## Workflow
1. Find impulsive move that causes BOS.
2. OB = last opposing-color candle before that move.
3. Define zone; note if it created an FVG (higher quality).
4. Track whether price has returned to mitigate it.

## Decision rules
- Valid OB must precede a structure break with displacement.
- Untouched OB + FVG = A-grade POI.

## Validation checklist
- [ ] OB tied to a real BOS with displacement
- [ ] zone bounds explicit
- [ ] mitigation status tracked

## Failure handling
- No displacement -> not an OB, reject.
- Multiple candidates -> pick the one nearest the origin of the impulse.

## Examples
Bearish OB: last up candle 1.1470-1.1476 before drop that broke 1.1445 low; untouched.

## Acceptance criteria
- [ ] Every OB references its causing BOS
- [ ] FVG-confluence flagged when present
