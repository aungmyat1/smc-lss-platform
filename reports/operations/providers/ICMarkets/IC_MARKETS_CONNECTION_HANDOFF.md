# IC Markets Connection Handoff

Status: **PENDING_PROVIDER_CONNECTION**

Purpose: prevent accidental execution of the history gate, export, or ST-C3
using a non-IC-Markets MT5 server.

## OP-03 Handoff Checklist

| Check | Status | Evidence |
| --- | --- | --- |
| Previous provider closed | Complete | `reports/operations/OP_02_ESCALATION_DECISION.md` |
| Provider lock updated | Complete | `reports/operations/provider_lock.json` |
| MT5 connected | Connected to wrong provider | `reports/operations/providers/ICMarkets/attempt_01/CONNECTION_PRECHECK_01.json` |
| Server matches IC Markets | Pending | `reports/operations/providers/ICMarkets/attempt_01/CONNECTION_PRECHECK_01.json` |
| Provider identity confirmed | Pending | `reports/operations/providers/ICMarkets/attempt_01/CONNECTION_PRECHECK_01.json` |
| EURUSD enabled | Confirmed on active session | `reports/operations/providers/ICMarkets/attempt_01/CONNECTION_PRECHECK_01.json` |
| GBPUSD enabled | Confirmed on active session | `reports/operations/providers/ICMarkets/attempt_01/CONNECTION_PRECHECK_01.json` |
| Timezone recorded | Pending | Connection/history evidence |
| Export permissions verified | Pending | Frozen ST-C5 pipeline evidence |

## Decision

Current decision: **PENDING_PROVIDER_CONNECTION**

Latest check: `reports/operations/providers/ICMarkets/attempt_01/CONNECTION_PRECHECK_01.json`

The next valid state is **READY_FOR_HISTORY_GATE**, and it may only be reached
after the provider identity check confirms the active MT5 server or company
matches IC Markets and required symbols are available.

## Guardrail

Do not run history sync, export, ST-C3 validation, replay, demo, or live actions
while the active MT5 server is not the IC Markets Demo environment.
