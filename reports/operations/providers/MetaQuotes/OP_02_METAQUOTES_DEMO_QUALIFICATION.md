# OP-02 MetaQuotes Demo Qualification Campaign

Status: **ENVIRONMENT_FAILED**

Objective: determine whether MetaQuotes Demo can provide the historical data
required by ST-C3 using the unchanged frozen ST-C5 pipeline.

## Frozen Evaluation Configuration

| Item | Value |
| --- | --- |
| Provider | MetaQuotes |
| Account type | Demo |
| Server | Pending exact MT5 server |
| Symbols | EURUSD, GBPUSD |
| Evidence timeframes | M1, M3, M15, H4 |
| Candidate export timeframes | H4, M15, M3 |
| Required start | 2021-01-04T00:00:00Z |
| Required end | 2025-12-31 by timeframe |
| Validation | Frozen ST-C5/ST-C3 gates |
| SLA | `reports/operations/PROVIDER_EVALUATION_SLA.md` |
| Connection handoff | `reports/operations/PROVIDER_CONNECTION_HANDOFF_CHECKLIST.md` |
| Provider lock | `reports/operations/provider_lock.json` |
| Environment checklist | `reports/operations/OP_02_ENVIRONMENT_VERIFICATION_CHECKLIST.md` |
| Retry policy | `reports/operations/OP_02_RETRY_POLICY.md` |

## Current Precheck

| Field | Value |
| --- | --- |
| Precheck status | ENVIRONMENT_FAILED |
| Active terminal server | VTMarkets-Demo |
| Evidence | `reports/operations/providers/MetaQuotes/attempt_01/CONNECTION_RECHECK_05.json` |
| Handoff checkpoint | `reports/operations/providers/MetaQuotes/METAQUOTES_CONNECTION_HANDOFF.md` |

## Implementation Status

OP-02 implementation is complete, but the environment failed the retry policy.
The active MT5 server never reached MetaQuotes-Demo; final evidence remains on
VTMarkets-Demo.

Escalation decision: `reports/operations/OP_02_ESCALATION_DECISION.md`

## Execution Sequence

1. Confirm `reports/operations/provider_lock.json` targets MetaQuotes-Demo.
2. Complete `reports/operations/PROVIDER_CONNECTION_HANDOFF_CHECKLIST.md`.
3. Connect MT5 to MetaQuotes Demo.
4. Run `python -m tools.st_c5_3_connection_check`.
5. Record terminal build, server, account type, timestamp, and symbol metadata.
6. Run `python -m tools.st_c5_3_history_sync_gate` only if the connection check returns `READY_FOR_HISTORY_GATE`.
7. If history sync fails, record evidence and update the provider matrix.
8. If history sync passes, run `python -m tools.st_c5_pipeline --acquire`.
9. Continue only through the frozen pipeline sequence.
10. Do not unlock replay unless the dataset is approved by governance evidence.

## Success Criteria

MetaQuotes Demo is ST-C3 eligible only if:

- EURUSD and GBPUSD history satisfies the required window.
- M1/M3/M15/H4 evidence is available.
- Export, normalization, and export audit pass.
- Unchanged ST-C3 validation passes.
- Governance decision is `APPROVE_DATASET`.

## Guardrail

No provider-specific exceptions, manual gap filling, threshold changes, strategy
changes, replay unlock, demo, or live actions are allowed. MetaQuotes history
sync must not be run unless the provider identity check reaches
`READY_FOR_HISTORY_GATE` in a future explicitly reopened evaluation.
