---
name: validation
description: >-
  Statistical/out-of-sample validation gate. Trigger on 'validate strategy', 'is
  this significant', 'walk forward'.
---

# validation

## Purpose
Decide objectively whether a strategy/version has a real edge (walk-forward, sample size, significance).

## Inputs
- backtest + OOS results
- sample size, expectancy distribution

## Outputs
- verdict ACCEPT/REJECT with the statistics behind it

## Workflow
1. Require adequate sample (>=100 trades ideally).
2. Walk-forward across sub-periods.
3. Check expectancy>0 with acceptable variance.
4. ACCEPT only if edge persists OOS.

## Decision rules
- Positive IS but negative/flat OOS -> REJECT.
- Edge from <30 trades -> not evidence.

## Validation checklist
- [ ] sample size stated
- [ ] OOS persistence shown
- [ ] verdict justified numerically

## Failure handling
- Insufficient data -> INCONCLUSIVE, do not accept.

## Examples
v1.2: IS exp +0.28R, OOS +0.22R over 140 trades, stable => ACCEPT.

## Acceptance criteria
- [ ] Binary verdict with the numbers
- [ ] guards against small-sample/overfit
