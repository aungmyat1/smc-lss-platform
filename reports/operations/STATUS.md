# Operations Status

Updated UTC: `2026-08-03T10:00:35Z`

## OP-01 Provider Matrix

Status: **COMPLETE_FOR_VTMARKETS**

VTMarkets-Demo is closed as
`OPERATIONALLY_INSUFFICIENT_FOR_ST_C3_HISTORY`.

Evidence:

- `reports/operations/OP_01_PROVIDER_CAPABILITY_MATRIX.md`
- `reports/operations/OP_01_ATTEMPT_TRACKER.json`
- `reports/operations/OP_01_ATTEMPT_03_RESULT.md`

## OP-02 MetaQuotes Qualification

Implementation: **COMPLETE**

Environment: **FAILED**

Reason: retry policy exhausted while active MT5 server remained
`VTMarkets-Demo`; required server was `MetaQuotes-Demo`.

Current evidence:

- `reports/operations/provider_lock.json`
- `reports/operations/providers/MetaQuotes/attempt_01/CONNECTION_RECHECK_05.json`
- `reports/operations/OP_02_ENVIRONMENT_VERIFICATION_CHECKLIST.md`
- `reports/operations/OP_02_RETRY_POLICY.md`
- `reports/operations/OP_02_ESCALATION_DECISION.md`

Next action:

Prepare IC Markets Demo evaluation using the same provider connection handoff
and frozen ST-C5/ST-C3 gates.

## OP-03 IC Markets Qualification

Implementation: **READY**

Environment: **PENDING_PROVIDER_CONNECTION**

Latest precheck:

`PENDING_PROVIDER_CONNECTION` because the active MT5 server is still
`VTMarkets-Demo`; expected provider marker is `ICMarkets`.

Current evidence:

- `reports/operations/provider_lock.json`
- `reports/operations/providers/ICMarkets/OP_03_IC_MARKETS_DEMO_QUALIFICATION.md`
- `reports/operations/providers/ICMarkets/IC_MARKETS_CONNECTION_HANDOFF.md`
- `reports/operations/providers/ICMarkets/attempt_01/CONNECTION_PRECHECK_01.json`

Next action:

Connect MT5 to IC Markets Demo and run the provider identity check. Do not run
the history sync gate until the check returns `READY_FOR_HISTORY_GATE`.

## ST-C5

Status: **WAITING_FOR_PROVIDER_CONNECTION**

Reason: IC Markets provider identity has not been proven.

## ST-C3

Status: **NOT_STARTED_FOR_IC_MARKETS**

Reason: no approved IC Markets dataset candidate exists.

## Replay

Status: **BLOCKED**

Reason: dataset is not approved.

## Strategy Validation

Status: **BLOCKED**

Reason: replay is blocked.

## Demo / Live Trading

Status: **BLOCKED**

Reason: strategy validation has not passed.
