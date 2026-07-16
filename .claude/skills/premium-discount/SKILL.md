---
name: premium-discount
description: >-
  Compute premium/discount equilibrium. Trigger on 'premium discount',
  'equilibrium', 'fib 50', 'OTE'.
---

# premium-discount

## Purpose
Split the relevant dealing range at 50% equilibrium; buy only in discount, sell only in premium (optionally OTE 0.62-0.79).

## Inputs
- range high & low (from swing structure)
- current price

## Outputs
- equilibrium (50%) price
- zone of current price: PREMIUM | DISCOUNT | EQUILIBRIUM
- OTE band bounds

## Workflow
1. Identify the valid dealing range (last impulse leg).
2. equilibrium = (high+low)/2.
3. Classify price vs equilibrium.
4. Compute OTE (0.62-0.79 retracement) for refined entries.

## Decision rules
- Longs require price in discount; shorts require premium.
- Entering premium for a long is INVALID.

## Validation checklist
- [ ] range endpoints justified
- [ ] zone classification matches the math

## Failure handling
- Undefined range -> request market-structure output.
- Price at equilibrium -> no directional edge, wait.

## Examples
Range 1.1377-1.1483: EQ 1.1430; price 1.1444 = PREMIUM => longs discouraged.

## Acceptance criteria
- [ ] Zone + equilibrium returned with the range used
- [ ] OTE band provided
