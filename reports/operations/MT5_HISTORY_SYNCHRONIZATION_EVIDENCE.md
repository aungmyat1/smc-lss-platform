# ST-C6 MT5 History Synchronization Evidence

Decision: **REQUIRES_HISTORY_SYNC**

Generated UTC: `2026-08-02T08:57:29Z`

History source: `MetaTrader5.copy_rates_range from local authenticated MT5 terminal`

## Terminal Metadata

- Terminal build: `6063`
- Broker server: `VTMarkets-Demo`

## Required History

| Symbol | Timeframe | Status | Earliest Bar | Latest Bar | Bar Count | Reason | Precise Reason |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| EURUSD | M1 | FAIL | - | - | 0 | Unknown | MT5 returned 261 bars outside requested audit window only |
| EURUSD | M3 | REQUIRES_HISTORY_SYNC | 2025-10-10T13:03:00Z | 2025-12-31T23:57:00Z | 27680 | Unknown | earliest in-window bar 2025-10-10T13:03:00Z is after required start 2021-01-04T00:00:00Z |
| EURUSD | M15 | REQUIRES_HISTORY_SYNC | 2022-07-26T08:45:00Z | 2025-12-31T23:45:00Z | 85513 | Unknown | earliest in-window bar 2022-07-26T08:45:00Z is after required start 2021-01-04T00:00:00Z |
| EURUSD | H4 | PASS | 2021-01-04T00:00:00Z | 2025-12-31T20:00:00Z | 7786 | - | - |
| GBPUSD | M1 | FAIL | - | - | 0 | Unknown | MT5 returned 261 bars outside requested audit window only |
| GBPUSD | M3 | REQUIRES_HISTORY_SYNC | 2025-10-10T12:06:00Z | 2025-12-31T23:57:00Z | 27680 | Unknown | earliest in-window bar 2025-10-10T12:06:00Z is after required start 2021-01-04T00:00:00Z |
| GBPUSD | M15 | REQUIRES_HISTORY_SYNC | 2022-07-26T09:15:00Z | 2025-12-31T23:45:00Z | 85513 | Unknown | earliest in-window bar 2022-07-26T09:15:00Z is after required start 2021-01-04T00:00:00Z |
| GBPUSD | H4 | PASS | 2021-01-04T00:00:00Z | 2025-12-31T20:00:00Z | 7786 | - | - |

Dataset remains not approved. Replay, strategy validation, demo, and live remain blocked.
