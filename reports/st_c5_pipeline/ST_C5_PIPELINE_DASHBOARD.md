# ST-C5 Pipeline Dashboard

Lifecycle State: **PENDING_HISTORY_SYNC**

Recommendation: **REQUIRES_HISTORY_SYNC**

| Stage | Status | Last Run | Blocking Reason | Next Action | Evidence |
| --- | --- | --- | --- | --- | --- |
| History Sync | REQUIRES_HISTORY_SYNC | 2026-08-02T08:58:50Z | Local MT5 terminal does not yet contain sufficient in-window history for every export source timeframe. | Synchronize MT5 terminal history before running any broker re-export. | reports/st_c5_3/MT5_HISTORY_SYNC_REPORT.md |
| Export | WAITING | - | Waiting for history sync | Run broker export only after history sync returns READY_FOR_REEXPORT. | reports/st_c5_3/MT5_HISTORY_SYNC_DECISION.json |
| Normalization | WAITING | - | Export not complete | Wait for a successful broker export. | reports/st_c5/BROKER_DATA_QUALIFICATION_STATUS.json |
| Export Audit | WAITING | - | Export not complete | Run unchanged export completeness audit after export. | reports/st_c5_2/EXPORT_COMPLETENESS_AUDIT.md |
| ST-C3 | WAITING | - | Export not complete | Run unchanged ST-C3 validation only after export audit passes. | reports/st_c5/DATASET_GOVERNANCE_DECISION.json |
| Replay | BLOCKED | - | Dataset not approved | Wait for approved dataset evidence; do not execute replay. | research_data/metadata/ST_C5_DATASET_LIFECYCLE.json |
| Strategy Validation | BLOCKED | - | Replay blocked | Wait for replay unlock after dataset approval. | reports/st_c5_pipeline/ST_C5_PIPELINE_STATUS.json |
| Demo | BLOCKED | - | Strategy validation blocked | Wait for strategy validation approval. | reports/st_c5_pipeline/ST_C5_PIPELINE_STATUS.json |
| Live | BLOCKED | - | Demo blocked | Wait for demo authorization after strategy validation. | reports/st_c5_pipeline/ST_C5_PIPELINE_STATUS.json |

Dataset remains not approved. Replay, strategy validation, demo, and live remain blocked.
