# ST-C5.3 MT5 History Synchronization Gate

Decision: **REQUIRES_HISTORY_SYNC**

Recommendation: **REQUIRES_HISTORY_SYNC**

Reason: Local MT5 terminal does not yet contain sufficient in-window history for every export source timeframe.

## Required Export Sources

- Required rows checked: `6`
- Required failures: `4`

## Required Failures

- EURUSD M1: NOT_PRESENT_IN_TERMINAL - copy_rates_range returned 261 bars outside requested audit window
- EURUSD M15: START_DATE_MISSING - first available bar is after required start 2021-01-04T00:00:00Z
- GBPUSD M1: NOT_PRESENT_IN_TERMINAL - copy_rates_range returned 261 bars outside requested audit window
- GBPUSD M15: START_DATE_MISSING - first available bar is after required start 2021-01-04T00:00:00Z

## Diagnostic Timeframes

- Diagnostic rows recorded: `6`
- Symbols: `EURUSD, GBPUSD`
- Timeframes queried: `M1, M5, M15, H1, H4, D1`

## Governance

Dataset remains not approved. Replay, strategy validation, demo, and live remain blocked.
