# Research Readiness Index

Status: **INFORMATIONAL**

Overall readiness: **55%**

Current blocker: **PENDING_HISTORY_SYNC**

Recommendation: **REQUIRES_HISTORY_SYNC**

This index is an operational summary only. It does not approve datasets, unlock
replay, modify ST-C3, change strategy logic, or create a new governance gate.

| Area | Weight | Status | Score | Evidence |
| --- | ---: | --- | ---: | --- |
| Strategy | 15% | STABLE | 15% | ST-C1 strategy specification and current freeze policy |
| Rule Engine | 15% | STABLE | 15% | ST-C2 deterministic rule engine and conformance tests |
| Governance | 15% | STABLE | 15% | ST-C3 governance framework and ST-C6 freeze policy |
| Dataset | 25% | BLOCKED_REQUIRES_HISTORY_SYNC | 0% | `reports/st_c5_3/MT5_HISTORY_SYNC_DECISION.json` |
| Replay | 15% | BLOCKED_DATASET_NOT_APPROVED | 0% | `research_data/metadata/ST_C5_DATASET_LIFECYCLE.json` |
| Execution Layer | 10% | PREPARABLE_PARALLEL_TRACK | 7% | Parallel workstream independent of approved historical data |
| Monitoring | 5% | STABLE | 3% | `reports/st_c5_pipeline/ST_C5_PIPELINE_DASHBOARD.md` |

## Interpretation

The project is structurally ready for research validation, but the critical path
is blocked by historical data acquisition. The fastest path forward is to
execute `reports/st_c5_3/HISTORY_SYNC_RUNBOOK.md`, synchronize MT5 history, and
rerun the frozen ST-C5 pipeline unchanged.

## Parallel Track

While the dataset remains blocked, production-engineering work can continue in
areas that do not affect strategy logic or governance:

- MT5 execution reliability
- Order lifecycle management
- Position reconciliation
- Risk-control enforcement
- Logging and monitoring
- Deployment automation
