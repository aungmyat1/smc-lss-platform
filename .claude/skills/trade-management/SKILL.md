---
name: trade-management
description: >-
  Manage open trades. Trigger on 'manage trade', 'move to breakeven', 'partial',
  'trail stop'.
---

# trade-management

## Purpose
Rules for partial take-profit, breakeven, and trailing after entry, executed via modify_position.

## Inputs
- open position (get_positions_by_symbol)
- current price, structure
- config: BE trigger (1R), partial (50% at 1R), trail method

## Outputs
- management actions with new SL/TP; modify_position calls (human-confirmed)

## Workflow
1. At +1R: take partial and move stop to breakeven.
2. Trail behind new HL/LH as structure develops.
3. Exit on opposing CHoCH or target.

## Decision rules
- Never move stop away from price (no widening).
- Breakeven only after 1R achieved.

## Validation checklist
- [ ] actions reference current structure
- [ ] stops only tighten

## Failure handling
- Position not found -> stop.
- Modify fails -> instruct manual close rather than run unmanaged.

## Examples
Long +1R at 1.1454: close 50%, SL->1.1436 (BE), trail under new M15 HL.

## Acceptance criteria
- [ ] Deterministic triggers (1R etc.)
- [ ] all actions via modify_position, confirmed
