# ST-C6 Operational Data Qualification & Replay Readiness

Status: **OPEN**

Current lifecycle state: **PENDING_HISTORY_SYNC**

Current recommendation: **REQUIRES_HISTORY_SYNC**

This milestone is operational. It does not add validation rules, change ST-C3
thresholds, modify strategy logic, approve datasets, or unlock replay.

## Objective

Execute the existing ST-C5 pipeline until it either produces an approved
canonical research dataset or conclusively demonstrates that the current broker
cannot satisfy historical data requirements.

## Evidence Of Current Blocker

| Evidence | Location |
| --- | --- |
| Pipeline dashboard | `reports/st_c5_pipeline/ST_C5_PIPELINE_DASHBOARD.md` |
| Lifecycle manifest | `research_data/metadata/ST_C5_DATASET_LIFECYCLE.json` |
| History sync decision | `reports/st_c5_3/MT5_HISTORY_SYNC_DECISION.json` |
| History sync report | `reports/st_c5_3/MT5_HISTORY_SYNC_REPORT.md` |
| History sync runbook | `reports/st_c5_3/HISTORY_SYNC_RUNBOOK.md` |

## Execution Sequence

1. Execute `reports/st_c5_3/HISTORY_SYNC_RUNBOOK.md` on the authenticated MT5 terminal.
2. Confirm EURUSD and GBPUSD M1/M15/H4 history reaches the required start date.
3. Rerun `python -m tools.st_c5_pipeline`.
4. If the pipeline returns `READY_FOR_REEXPORT`, rerun with `python -m tools.st_c5_pipeline --acquire`.
5. Let the existing pipeline run broker export, normalization, export audit, and ST-C3 handoff without changing code.
6. If the dataset passes unchanged ST-C3 governance, record approval evidence and only then unlock replay.
7. If the history gate still fails after verified terminal synchronization, record that as broker-history limitation evidence and return to provider qualification with the unchanged framework.

## Replay Readiness Checklist

Replay remains blocked until every item is true:

| Item | Required Status | Current Status |
| --- | --- | --- |
| History Sync | PASS | REQUIRES_HISTORY_SYNC |
| Export Complete | PASS | WAITING |
| Normalization | PASS | WAITING |
| ST-C3 Validation | PASS | WAITING |
| Dataset Lifecycle | APPROVED | NOT_APPROVED |
| Dataset Manifest | Frozen | NOT_FROZEN |
| Checksums | Recorded | PENDING_APPROVED_DATASET |
| Governance Decision | Recorded | PENDING_APPROVED_DATASET |

## Allowed Work While Blocked

The following work may proceed because it does not depend on approved historical data:

- MT5 execution adapter hardening
- Order lifecycle management
- Position reconciliation
- Risk-control enforcement
- Logging, monitoring, and recovery
- Deployment and configuration management

Avoid strategy-logic or governance-rule changes until a dataset is approved,
unless a verified defect is found.
