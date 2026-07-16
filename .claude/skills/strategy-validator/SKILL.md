---
name: strategy-validator
description: >-
  Top-level SMC entry gate that orchestrates the atomic detection skills.
  Trigger on 'validate this setup', 'is this a valid entry', 'check my trade'.
---

# strategy-validator

## Purpose
Binary VALID/INVALID gate that composes market-structure, liquidity-sweep, choch-bos, order-block, fair-value-gap, premium-discount, inducement, mitigation, session-filter, entry-confirmation.

## Inputs
- symbol, proposed direction
- outputs of the atomic skills

## Outputs
- per-check PASS/FAIL with evidence; VERDICT VALID->risk-manager | INVALID

## Workflow
1. Run market-structure + choch-bos (HTF bias).
2. liquidity-sweep (target).
3. premium-discount (zone).
4. order-block/fair-value-gap (POI) + mitigation (fresh).
5. inducement taken + session-filter allowed.
6. entry-confirmation (LTF trigger). All must pass.

## Decision rules
- One FAIL = INVALID. No 'close enough'.

## Validation checklist
- [ ] every atomic gate consulted
- [ ] evidence cited per check

## Failure handling
- Any atomic skill returns NEEDS_MORE_DATA -> INVALID/wait.

## Examples
See prior EURUSD run: HTF bullish but LTF no CHoCH -> INVALID/stand aside.

## Acceptance criteria
- [ ] Aggregates all atomic verdicts
- [ ] hands VALID setups to risk-manager only
