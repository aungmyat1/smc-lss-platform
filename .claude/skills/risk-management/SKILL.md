---
name: risk-management
description: >-
  Position sizing and risk limits (symbol-generic). Trigger on 'size this
  trade', 'how many lots', 'risk', 'can I take this'.
---

# risk-management

## Purpose
Compute position size from live equity and a structural stop using per-symbol tick value; enforce risk/daily-loss/heat/overtrading limits.

## Inputs
- metatrader.get_account_info (equity)
- entry, structural stop, target
- symbol tick_value/tick_size via get_symbols/get_symbol_price
- config: risk% (1%), daily loss (3%), max positions (3), heat (4%), min R:R (2.0)

## Outputs
- lots (rounded to step), dollar risk, % equity, R:R, decision APPROVED/REFUSED

## Workflow
1. get_account_info -> equity.
2. dollar risk = equity*risk%.
3. stop distance in ticks; pull per-symbol tick_value (NOT hardcoded $10).
4. lots = risk / (stop_ticks*tick_value); round down to step.
5. Check R:R, heat, daily loss, position count, overtrading (get_deals).

## Decision rules
- Any limit breached or lots==0 or R:R<2.0 -> REFUSE.
- Never increase risk after a loss.

## Validation checklist
- [ ] tick_value pulled per symbol
- [ ] all five limits checked
- [ ] place_market_order followed by modify_position for SL/TP

## Failure handling
- Missing tick data -> REFUSE (do not assume).
- Daily loss hit -> block all new trades.

## Examples
Equity 988.12, 1%=9.88, XAUUSD stop 3.0 (300 ticks), tick_value 0.01/... -> size per pulled specs, refuse if R:R<2.

## Acceptance criteria
- [ ] Output has lots, $risk, %equity, R:R, decision
- [ ] symbol-generic (metals/JPY correct)
