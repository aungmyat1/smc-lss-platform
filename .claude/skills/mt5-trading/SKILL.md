---
name: mt5-trading
description: >-
  MetaTrader 5 MCP interface conventions. Trigger on 'mt5', 'metatrader',
  'connect broker', 'account/positions'.
---

# mt5-trading

## Purpose
Canonical wrapper for reading MT5 state and placing/modifying orders safely via the metatrader MCP.

## Inputs
- metatrader MCP tools
- symbol, order params

## Outputs
- normalized account/positions/price/candle reads; order results

## Workflow
1. Reads: get_account_info, get_symbol_price, get_candles_latest, get_all_positions, get_deals.
2. Orders: place_market_order THEN modify_position for SL/TP (MCP does not accept SL/TP on market orders).
3. Pending: place_pending_order supports SL/TP directly.

## Decision rules
- Confirm DEMO account before any test order.
- Never place an order without a stop.

## Validation checklist
- [ ] account type checked (demo vs real)
- [ ] SL attached via modify after market fill

## Failure handling
- Real account + test intent -> REFUSE, require demo.
- Order rejected -> surface broker error, do not retry blindly.

## Examples
place_market_order(EURUSD, buy, 0.04) -> modify_position(id, sl=1.1418, tp=1.1492).

## Acceptance criteria
- [ ] Documents the two-step SL/TP flow
- [ ] demo guard enforced
