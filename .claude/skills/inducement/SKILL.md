---
name: inducement
description: >-
  Detect inducement (fake liquidity before the real POI). Trigger on
  'inducement', 'IDM', 'trap before POI'.
---

# inducement

## Purpose
Identify minor liquidity that lures early entries ahead of the true point of interest, so entries wait for inducement to be taken first.

## Inputs
- structure + liquidity pools
- POI location (OB/FVG)

## Outputs
- inducement level(s), taken (bool), clean-path-to-POI (bool)

## Workflow
1. Between current price and the POI, find the nearest minor high/low (inducement).
2. Expect price to sweep inducement before reacting at POI.
3. Flag when inducement is taken.

## Decision rules
- Entering before inducement is swept = premature (INVALID).
- POI with unswept inducement in front is lower quality.

## Validation checklist
- [ ] inducement lies between price and POI
- [ ] taken-status tracked

## Failure handling
- No clear inducement -> note it; treat POI with caution.

## Examples
Bearish POI 1.1476; minor high 1.1462 = inducement; taken before tap => entry armed.

## Acceptance criteria
- [ ] Inducement identified relative to a specific POI
- [ ] gate blocks pre-inducement entries
