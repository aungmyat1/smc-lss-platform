# OP-02 Escalation Decision

Status: **ENVIRONMENT_FAILED**

Decision: **METAQUOTES_ENVIRONMENT_UNAVAILABLE**

Generated UTC: `2026-08-02T14:10:04Z`

## Why OP-02 Cannot Continue

OP-02 requires the active MT5 server to be `MetaQuotes-Demo` before any history
sync, export, ST-C3 validation, replay, demo, or live action may run.

The final permitted connection check still reports:

| Field | Value |
| --- | --- |
| Expected provider | MetaQuotes |
| Required server | MetaQuotes-Demo |
| Active server | VTMarkets-Demo |
| Terminal connected | true |
| Terminal build | 6063 |
| EURUSD selected | true |
| GBPUSD selected | true |

## Blocker Classification

Blocker type: **Environment**

This is not a software failure. The provider identity guard is behaving
correctly by preventing MetaQuotes qualification from running against
VTMarkets-Demo.

## Retry Policy Result

The OP-02 retry policy allowed 5 connection attempts. The final attempt did not
reach `READY_FOR_HISTORY_GATE`.

Outcome:

**ENVIRONMENT_FAILED**

## Next Provider

Proceed to IC Markets Demo using the same unchanged provider connection handoff,
provider lock, ST-C5 history gate, and ST-C3 validation criteria.

## Guardrail

No history gate, export, ST-C3 validation, replay, strategy validation, demo, or
live action was executed for MetaQuotes.
