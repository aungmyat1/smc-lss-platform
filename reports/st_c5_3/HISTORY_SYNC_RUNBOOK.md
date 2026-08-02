# ST-C5.3 MT5 History Synchronization Runbook

Current decision: **REQUIRES_HISTORY_SYNC**

Required before re-export:

1. Open the authenticated Vantage MT5 terminal.
2. Select EURUSD and GBPUSD in Market Watch.
3. Open charts for M1, M15, and H4 for each symbol.
4. Force each chart to load history back to `2021-01-04T00:00:00Z`.
5. Confirm the terminal has in-window M1 history because M3 may need to be derived from M1.
6. Rerun `python -m tools.st_c5_3_history_sync_gate`.
7. Only if the gate returns `READY_FOR_REEXPORT`, run `python -m tools.st_c5_broker_data_qualification --acquire`.
8. Rerun `python -m tools.st_c5_2_export_completeness_audit`.
9. Rerun unchanged ST-C3 validation.

No dataset approval, replay, strategy validation, demo, or live path may be unlocked by this gate.
