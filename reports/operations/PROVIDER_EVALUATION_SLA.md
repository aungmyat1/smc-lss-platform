# Provider Evaluation SLA

Status: **ACTIVE**

Purpose: prevent provider qualification from consuming unlimited project time.

## SLA

Each provider/account/server combination receives:

| Limit | Value |
| --- | --- |
| Maximum synchronization attempts | 3 |
| Maximum operational duration | 7 operational days |
| Pipeline | Unchanged frozen ST-C5 |
| Acceptance criteria | Unchanged ST-C5/ST-C3 gates |
| Provider-specific exceptions | Not allowed |

## Decision Outcomes

Allowed operational outcomes:

- `CANONICAL_PROVIDER_CANDIDATE`
- `OPERATIONALLY_INSUFFICIENT_FOR_ST_C3_HISTORY`
- `REQUIRES_MANUAL_REVIEW`

## Guardrail

Do not lower historical requirements, change timeframes, relax ST-C3 thresholds,
manually fill data, or optimize strategy to rescue a provider evaluation.
