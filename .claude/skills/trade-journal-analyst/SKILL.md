---
name: trade-journal-analyst
description: >-
  Post-trade review wrapper over journaling. Trigger on 'journal my trade',
  'weekly review'.
---

# trade-journal-analyst

## Purpose
Delegates persistence/metrics to journaling and produces the human-facing review + one fix.

## Inputs
- closed trades
- journal store

## Outputs
- review summary + single next fix

## Workflow
1. Call journaling to append + compute.
2. Surface top recurring mistake + one action.

## Decision rules
- Always end with exactly one concrete fix.

## Validation checklist
- [ ] uses durable store
- [ ] one fix per review

## Failure handling
- No store -> create it first.

## Examples
40-trade review: top mistake early-entry; fix = wait for LTF CHoCH.

## Acceptance criteria
- [ ] Actionable single-fix output
