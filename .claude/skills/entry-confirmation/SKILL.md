---
name: entry-confirmation
description: >-
  Lower-timeframe entry trigger at a POI. Trigger on 'entry confirmation',
  'entry trigger', 'confirm entry'.
---

# entry-confirmation

## Purpose
After price taps a valid POI (with inducement taken, correct P/D zone), require an LTF confirmation before entry.

## Inputs
- POI + zone/inducement/session gates passed
- LTF candles (e.g. M1/M5)

## Outputs
- confirmation type (LTF CHoCH / FVG / rejection), entry price, invalidation (stop) level

## Workflow
1. Confirm price is at POI and gates pass.
2. Wait for LTF CHoCH or displacement out of the zone.
3. Entry on the confirmation; stop beyond the POI/sweep extreme.

## Decision rules
- No LTF shift = no entry.
- Stop must sit beyond structure, not an arbitrary distance.

## Validation checklist
- [ ] all upstream gates passed first
- [ ] confirmation is objective (close-based)
- [ ] stop tied to structure

## Failure handling
- No confirmation within window -> stand aside.
- Confirmation then immediate invalidation -> abort.

## Examples
At 1.1432 bullish OB, M1 prints CHoCH above 1.1436 => enter 1.1436, stop 1.1418.

## Acceptance criteria
- [ ] Emits entry + structural stop for risk-manager
- [ ] refuses without confirmation
