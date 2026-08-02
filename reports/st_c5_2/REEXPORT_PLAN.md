# ST-C5.2 Re-export Plan

Current decision: **INCOMPLETE_EXPORT**

Recommended acquisition actions:

1. In MT5, open EURUSD and GBPUSD charts for M1, M5, M15, H1, H4, and D1.
2. Scroll each chart back to at least 2021-01-01 to force local history synchronization.
3. Increase terminal chart/history bar limits if needed.
4. Rerun `python -m tools.st_c5_3_history_sync_gate`.
5. Only if ST-C5.3 returns `READY_FOR_REEXPORT`, rerun `python -m tools.st_c5_broker_data_qualification --acquire`.
6. Rerun `python -m tools.st_c5_1_vantage_quality_report`.
7. Rerun `python -m tools.st_c5_2_export_completeness_audit`.

No replay or strategy validation may start until a fresh unchanged ST-C3 run approves the dataset.
