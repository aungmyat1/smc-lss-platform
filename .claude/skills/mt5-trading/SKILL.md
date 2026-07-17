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

## Environment verification (demo-safe gate)
Treat the connector `account_info().account_type` field as UNVERIFIED. It derives
from MT5 `trade_mode` and can report `real` on a broker demo server (confirmed:
VTMarkets demo reports `real`). Never use it to classify an account as demo-safe.

An account is demo-safe only when the **login server name is confirmed to contain
"Demo"** (case-insensitive, e.g. `VTMarkets-Demo`). Resolve it in this order:
1. Match the connected login in `references/attested-environments.md` (authoritative).
2. Else read the server name from the terminal / owner attestation.
3. Else environment is `UNVERIFIED` -> treat as LIVE (fail-safe) and REFUSE test orders.

## Decision rules
- Confirm DEMO_VERIFIED (server name contains "Demo") before any test order; never trust account_type.
- Never place an order without a stop.

## Validation checklist
- [ ] environment is DEMO_VERIFIED via server name / attestation (NOT the account_type field)
- [ ] SL attached via modify after market fill

## Failure handling
- Not DEMO_VERIFIED (LIVE or UNVERIFIED) + test intent -> REFUSE, require verified demo.
- Order rejected -> surface broker error, do not retry blindly.

## Examples
place_market_order(EURUSD, buy, 0.04) -> modify_position(id, sl=1.1418, tp=1.1492).

## Acceptance criteria
- [ ] Documents the two-step SL/TP flow
- [ ] demo guard enforced via server-name verification
