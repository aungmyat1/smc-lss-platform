# OP-01 Broker History Acquisition Campaign

Status: **OPEN**

Objective: determine conclusively whether the current MT5 broker environment can
provide the historical data required by ST-C3.

This is an operational campaign, not a new ST-C phase. It does not change
ST-C3, thresholds, strategy logic, provider scoring, governance rules, pipeline
sequence, dataset approval criteria, or research readiness scoring.

## Current Broker Under Test

| Field | Value |
| --- | --- |
| Broker server | VTMarkets-Demo |
| Terminal build | 6063 |
| Current status | OPERATIONALLY_INSUFFICIENT_FOR_ST_C3_HISTORY |
| Dataset status | NOT_APPROVED |
| Replay status | BLOCKED |

## Current Evidence

| Evidence | Location |
| --- | --- |
| Operational attempt 02 | `reports/operations/ST_C6_OPERATIONAL_ATTEMPT_02.md` |
| Operational attempt 03 | `reports/operations/OP_01_ATTEMPT_03_RESULT.md` |
| MT5 synchronization evidence | `reports/operations/MT5_HISTORY_SYNCHRONIZATION_EVIDENCE.md` |
| History gate decision | `reports/st_c5_3/MT5_HISTORY_SYNC_DECISION.json` |
| Pipeline dashboard | `reports/st_c5_pipeline/ST_C5_PIPELINE_DASHBOARD.md` |
| Provider evaluation freeze rule | `reports/operations/OP_01_PROVIDER_EVALUATION_FREEZE_RULE.md` |

## Broker Retention Check

Public documentation reviewed on 2026-08-02 indicates VT Markets MT5 supports
one-minute historical quote data and identifies `VTMarkets-Demo` as the demo
server. I did not find an official VT Markets retention-depth guarantee stating
that EURUSD/GBPUSD M1 and M15 history is available back to 2021 on demo
accounts.

Operational conclusion: **broker-side retention remains undocumented and must
be confirmed by support or by successful terminal synchronization evidence.**

Reference URLs:

- `https://www.vtmarkets.com/metatrader-5/`
- `https://www.vtmarkets.com/en-ca/notification/t2021022202/`
- `https://get.vtmarkets.help/hc/en-us/articles/37317543124249-How-long-does-MT4-5-demo-account-stay-valid`
- `https://www.metatrader5.com/en/terminal/help/algotrading/test_preparation`

## Operational Exit Rule

If three independent synchronization attempts on the same broker, using the
documented runbook, produce materially identical evidence, classify the broker
environment as:

**OPERATIONALLY_INSUFFICIENT_FOR_ST_C3_HISTORY**

This is not a trading-quality rejection. It means the broker environment cannot
currently produce the required historical research dataset.

## Required Next Evidence

1. Close VTMarkets-Demo for ST-C3 historical data after Attempt 03.
2. Evaluate MetaQuotes Demo with the unchanged frozen ST-C5 pipeline.
3. If MetaQuotes Demo is insufficient, proceed to IC Markets Demo.
4. If IC Markets Demo is insufficient, proceed to Pepperstone Demo.

## Decision Tree

```text
VTMarkets Attempt 03
        |
        +-- PASS
        |     |
        |     v
        |  Continue ST-C5 Pipeline
        |
        +-- FAIL / REQUIRES_HISTORY_SYNC
              |
              v
        Operationally Insufficient
              |
              v
        Evaluate Next Broker
```

## Guardrail

No manual gap filling, threshold relaxation, dataset approval, replay unlock,
strategy validation, demo, or live action is permitted from the current state.
