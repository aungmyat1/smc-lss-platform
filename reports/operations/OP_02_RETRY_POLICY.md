# OP-02 Retry Policy

Status: **ACTIVE**

Purpose: prevent endless identical MetaQuotes connection checks.

## Policy

| Limit | Value |
| --- | ---: |
| Maximum connection attempts | 5 |
| Current recorded checks | 5 |
| Remaining checks | 0 |

## Escalation Rule

OP-02 remained blocked after 5 connection attempts. Recorded:

**METAQUOTES_ENVIRONMENT_UNAVAILABLE**

OP-02 is closed as environment failed. Move to the next provider in the
capability matrix.

## Guardrail

Do not run history sync, export, ST-C3 validation, replay, demo, or live actions
unless the provider identity check returns `READY_FOR_HISTORY_GATE`.
