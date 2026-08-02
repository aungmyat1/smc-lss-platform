# MetaQuotes Connection Handoff

Status: **PENDING_METAQUOTES_CONNECTION**

Purpose: prevent accidental execution of the history gate, export, or ST-C3
using a non-MetaQuotes MT5 server.

## OP-02 Handoff Checklist

| Check | Status | Evidence |
| --- | --- | --- |
| MT5 connected | Pending MetaQuotes connection | `reports/operations/providers/MetaQuotes/attempt_01/CONNECTION_RECHECK_03.json` |
| Server = MetaQuotes-Demo | Pending | `reports/operations/provider_lock.json` |
| Provider identity confirmed | Pending | `python -m tools.st_c5_3_connection_check` |
| EURUSD enabled | Pending MetaQuotes connection | Connection check output |
| GBPUSD enabled | Pending MetaQuotes connection | Connection check output |
| Timezone recorded | Pending | Connection/history evidence |
| Export permissions verified | Pending | Frozen ST-C5 pipeline evidence |

## Decision

Current decision: **PENDING_METAQUOTES_CONNECTION**

The next valid state is **READY_FOR_HISTORY_GATE**, and it may only be reached
after `python -m tools.st_c5_3_connection_check` confirms the active MT5 server
matches the provider lock.

## Guardrail

Do not run history sync, export, ST-C3 validation, replay, demo, or live actions
while the active MT5 server is not MetaQuotes-Demo.
