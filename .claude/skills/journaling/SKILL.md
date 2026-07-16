---
name: journaling
description: >-
  Persistent trade journaling + metrics. Trigger on 'journal', 'log trade',
  'review', 'weekly review'.
---

# journaling

## Purpose
Persist every closed trade to a structured store and compute performance/behaviour metrics.

## Inputs
- closed trades (get_deals/get_orders)
- screenshots (user-attached)
- store: data/journal.xlsx or SQLite

## Outputs
- appended journal row; period metrics (expectancy, PF, win%, maxDD, rule-adherence)

## Workflow
1. On close, append a row (symbol, dir, grade, R, mistakes, reasons, screenshots).
2. Never overwrite history.
3. Periodically compute metrics + recurring patterns.

## Decision rules
- Classify every trade's mistakes.
- Compare rule-followed vs rule-broken expectancy.

## Validation checklist
- [ ] one immutable row per trade
- [ ] metrics recomputed from full history

## Failure handling
- No store -> create data/journal.xlsx first.
- Missing screenshot -> flag incomplete, still log.

## Examples
Row: EURUSD long, A, +1.8R, mistakes=none; period expectancy +0.3R over 40 trades.

## Acceptance criteria
- [ ] Durable store written
- [ ] one concrete improvement per review
