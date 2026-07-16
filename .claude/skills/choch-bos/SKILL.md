---
name: choch-bos
description: >-
  Classify Change of Character (CHoCH) vs Break of Structure (BOS). Trigger on
  'CHoCH', 'BOS', 'break of structure', 'shift'.
---

# choch-bos

## Purpose
Given labeled structure, classify each break as BOS (trend continuation) or CHoCH (first counter-trend break = potential reversal).

## Inputs
- swing structure + protected high/low (from market-structure)
- candles for close confirmation

## Outputs
- events: type BOS|CHoCH, level, direction, confirmed-by-close (bool)

## Workflow
1. Take last protected high/low.
2. Break in trend direction with body close = BOS.
3. First break against the prevailing trend = CHoCH.
4. Require candle close beyond level (not just wick).

## Decision rules
- CHoCH is the earliest reversal signal; BOS confirms continuation.
- Wick-only break = unconfirmed.

## Validation checklist
- [ ] uses close, not wick
- [ ] references the protected level
- [ ] BOS vs CHoCH correctly typed

## Failure handling
- No prior structure -> defer to market-structure first.
- Ambiguous -> UNCONFIRMED.

## Examples
Uptrend protected low 1.1406; M15 closes 1.1398 below it => bearish CHoCH (possible reversal).

## Acceptance criteria
- [ ] Every event says why it is BOS or CHoCH
- [ ] close-confirmation enforced
