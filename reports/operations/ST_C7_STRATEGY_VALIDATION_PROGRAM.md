# ST-C7 Strategy Validation Program

Status: **PENDING_APPROVED_DATASET**

Purpose: convert the frozen SMC-LSS strategy from rule completeness into
statistical evidence of edge.

ST-C7 cannot begin until a dataset is approved through the unchanged ST-C5/ST-C3
pipeline. This document is preparatory only and does not unlock replay.

## Entry Criteria

| Requirement | Status |
| --- | --- |
| History Sync | Pending approved provider |
| Export Complete | Pending approved provider |
| Normalization | Pending approved provider |
| ST-C3 Validation | Pending approved provider |
| Dataset Lifecycle | NOT_APPROVED |
| Replay | BLOCKED |

## Replay Scope

Required symbols:

- EURUSD
- GBPUSD

Optional symbol if an approved dataset supports it:

- XAUUSD

Replay must use the frozen strategy logic and risk model. No strategy
optimization may occur before baseline replay evidence is produced.

## Statistical Gates

| Metric | Minimum Gate |
| --- | ---: |
| Trades | 200 |
| Profit Factor | > 1.25 |
| Sharpe | > 1.2 |
| Max Drawdown | < 15% |
| Expectancy | Positive |

## Robustness Tests

| Test | Required Shape |
| --- | --- |
| Out-of-sample | Train 2021-2024, test 2025 |
| Walk-forward | 6 months train, 3 months validate, repeat |
| Monte Carlo | Trade sequence randomness, drawdown probability, stability |

## Guardrails

- Do not change strategy logic before baseline replay.
- Do not change ST-C3 thresholds.
- Do not use unapproved datasets.
- Do not proceed to demo without approved replay and statistical evidence.

## Downstream Milestones

```text
Approved Dataset
        |
        v
ST-C7 Strategy Validation
        |
        v
ST-C8 Demo Execution
        |
        v
ST-C9 Controlled Live
```
