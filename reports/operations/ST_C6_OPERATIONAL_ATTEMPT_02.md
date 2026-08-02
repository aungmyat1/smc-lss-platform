# ST-C6 Operational Attempt 02

Status: **STOPPED_AT_HISTORY_GATE**

Decision: **REQUIRES_HISTORY_SYNC**

Generated UTC: `2026-08-02T09:06:23Z`

## Terminal Re-check

| Item | Value |
| --- | --- |
| Terminal connected | true |
| Terminal build | 6063 |
| Terminal max bars | 100000 |
| Broker server | VTMarkets-Demo |
| EURUSD selected | true |
| GBPUSD selected | true |

## Gate Result

The frozen ST-C5.3 history synchronization gate still returns
`REQUIRES_HISTORY_SYNC`.

| Symbol | Timeframe | Status | Reason |
| --- | --- | --- | --- |
| EURUSD | M1 | NOT_PRESENT_IN_TERMINAL | copy_rates_range returned 261 bars outside requested audit window |
| EURUSD | M15 | START_DATE_MISSING | first available bar is after required start 2021-01-04T00:00:00Z |
| GBPUSD | M1 | NOT_PRESENT_IN_TERMINAL | copy_rates_range returned 261 bars outside requested audit window |
| GBPUSD | M15 | START_DATE_MISSING | first available bar is after required start 2021-01-04T00:00:00Z |

## Stop Decision

Broker export, normalization, export audit, ST-C3 validation, governance
approval, replay, demo, and live paths were not executed.

## Next Action

Execute `reports/st_c5_3/HISTORY_SYNC_RUNBOOK.md` on the MT5 terminal, then
rerun `python -m tools.st_c5_3_history_sync_gate`.
