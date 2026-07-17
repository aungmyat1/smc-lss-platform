---
name: execution
description: >-
  Pre-execution guardrails. Trigger on 'execute', 'place the trade', 'send
  order'.
---

# execution

## Purpose
Final checklist between an approved+sized setup and order transmission (spread, slippage, session, confirmation, human sign-off).

## Inputs
- approved setup from risk-manager
- live spread (get_symbol_price), session state

## Outputs
- go/no-go + the exact order params to confirm

## Workflow
1. Re-check validator VALID + risk APPROVED + environment DEMO_VERIFIED (per mt5-trading gate; never trust account_type).
2. Spread <= max; session allowed.
3. Present exact params for human confirmation.
4. On confirm, mt5-trading executes; else abort.

## Decision rules
- Any gate stale/failed -> NO-GO.
- Execution is always human-confirmed.

## Validation checklist
- [ ] all upstream verdicts still valid
- [ ] spread/session re-checked at execution time

## Failure handling
- Spread spike -> NO-GO.
- No human confirm -> do not send.

## Examples
Approved long, spread 0.1 pip, killzone active => GO (await user confirm).

## Acceptance criteria
- [ ] Never auto-sends without confirmation
- [ ] re-validates immediately pre-send
