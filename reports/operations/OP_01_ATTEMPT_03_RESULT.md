# OP-01 Attempt 03 Result

Status: **REQUIRES_HISTORY_SYNC**

Classification: **OPERATIONALLY_INSUFFICIENT_FOR_ST_C3_HISTORY**

Broker server: **VTMarkets-Demo**

Dataset: **NOT_APPROVED**

Replay: **BLOCKED**

## Result

Attempt 03 reproduced the same material blocker as Attempts 01 and 02. The MT5
terminal is connected and the symbols are selectable, but required
lower-timeframe history is unavailable or starts after the ST-C3 required start.

## Required Failures

| Symbol | Timeframe | Status | Reason |
| --- | --- | --- | --- |
| EURUSD | M1 | NOT_PRESENT_IN_TERMINAL | copy_rates_range returned 261 bars outside requested audit window |
| EURUSD | M15 | START_DATE_MISSING | first available bar is after required start 2021-01-04T00:00:00Z |
| GBPUSD | M1 | NOT_PRESENT_IN_TERMINAL | copy_rates_range returned 261 bars outside requested audit window |
| GBPUSD | M15 | START_DATE_MISSING | first available bar is after required start 2021-01-04T00:00:00Z |

## Decision

VTMarkets-Demo is classified as:

**OPERATIONALLY_INSUFFICIENT_FOR_ST_C3_HISTORY**

This is not a trading-quality rejection. It means this broker/account/source
combination cannot currently produce the historical research dataset required
by ST-C3.

## Next Action

Evaluate MetaQuotes Demo using the unchanged frozen ST-C5 history gate and
pipeline.
