---
name: backtest-researcher
description: >-
  Rule-change research loop. Trigger on 'backtest this', 'did this rule help',
  'compare versions'.
---

# backtest-researcher

## Purpose
Compose backtesting + optimization + validation to accept/reject a rule change objectively.

## Inputs
- versioned spec change
- dataset

## Outputs
- ACCEPT/REJECT with IS/OOS metrics

## Workflow
1. Freeze spec version.
2. backtesting on fixed dataset.
3. optimization if params changed.
4. validation gate (OOS).

## Decision rules
- Accept only on OOS-supported improvement.

## Validation checklist
- [ ] version incremented
- [ ] validation verdict attached

## Failure handling
- No dataset -> NOT IMPLEMENTED.

## Examples
v1.1->v1.2 accepted on +0.22R OOS over 140 trades.

## Acceptance criteria
- [ ] Objective accept/reject with numbers
