# ST-C7 Validation Gates

Status: **FROZEN_BEFORE_RESULTS**

These gates are predeclared before replay results are available.

| Metric | Gate |
| --- | ---: |
| Minimum trades | 200 |
| Profit Factor | > 1.25 |
| Sharpe | > 1.2 |
| Maximum Drawdown | < 15% |
| Expectancy | Positive |

## Robustness Requirements

| Test | Requirement |
| --- | --- |
| Out-of-sample | Train 2021-2024, test 2025 |
| Walk-forward | 6 months train, 3 months validate, repeat |
| Monte Carlo | Trade sequence randomness, drawdown probability, stability |
| Parameter sensitivity | Verify edge is not isolated to one exact setting |

## Guardrail

Do not change these gates after seeing replay results.
