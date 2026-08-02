# ST-C5 Pipeline Dashboard

Lifecycle State: **PENDING_HISTORY_SYNC**

Recommendation: **REQUIRES_HISTORY_SYNC**

| Stage | Status | Last Run | Blocking Reason | Evidence |
| --- | --- | --- | --- | --- |
| History Sync | REQUIRES_HISTORY_SYNC | 2026-08-02T08:36:23Z | Local MT5 terminal does not yet contain sufficient in-window history for every export source timeframe. | reports/st_c5_3/MT5_HISTORY_SYNC_REPORT.md |
| Export | WAITING | - | Waiting for history sync | reports/st_c5_3/MT5_HISTORY_SYNC_DECISION.json |
| Normalization | WAITING | - | Export not complete | reports/st_c5/BROKER_DATA_QUALIFICATION_STATUS.json |
| Export Audit | WAITING | - | Export not complete | reports/st_c5_2/EXPORT_COMPLETENESS_AUDIT.md |
| ST-C3 | WAITING | - | Export not complete | reports/st_c5/DATASET_GOVERNANCE_DECISION.json |
| Replay | BLOCKED | - | Dataset not approved | research_data/metadata/ST_C5_DATASET_LIFECYCLE.json |
| Strategy Validation | BLOCKED | - | Replay blocked | reports/st_c5_pipeline/ST_C5_PIPELINE_STATUS.json |
| Demo | BLOCKED | - | Strategy validation blocked | reports/st_c5_pipeline/ST_C5_PIPELINE_STATUS.json |
| Live | BLOCKED | - | Demo blocked | reports/st_c5_pipeline/ST_C5_PIPELINE_STATUS.json |

Dataset remains not approved. Replay, strategy validation, demo, and live remain blocked.
