# ST-C1 Corrected Baseline Report

- Spec: `specs/research/v1_baseline.yaml`
- Git SHA: `c7c415ef179726fe14c135bb6e7e0b3b53e041e2`
- Strategy version: `1.0.0`
- Symbols: `EURUSD`
- Dataset count: `3`
- Funnel records: `0`

## Combined Metrics

| Key | Value |
|---|---|
| total_trades | 105 |
| wins | 31 |
| losses | 74 |
| win_rate_pct | 29.52 |
| profit_factor | 0.2291 |
| expectancy_r | -0.6648 |
| average_r | -0.6648 |
| gross_profit_r | 20.7415 |
| gross_loss_r | 90.5418 |
| net_profit_r | -69.8003 |
| maximum_drawdown_r | -70.8306 |
| drawdown_duration_trades | 104 |
| sharpe_ratio | -0.6253 |
| sortino_ratio | -0.9816 |
| recovery_factor | -0.9855 |
| payoff_ratio | 0.5468 |
| total_R | -69.8003 |
| longest_win_streak | 4 |
| longest_loss_streak | 6 |
| trade_count_adequacy_warning | False |
| mae_distribution |  |
| mfe_distribution |  |
| cost_drag_r |  |

## Funnel Counts

No funnel counts available.

## Symbol Metrics

### EURUSD

| Key | Value |
|---|---|
| total_trades | 105 |
| wins | 31 |
| losses | 74 |
| win_rate_pct | 29.52 |
| profit_factor | 0.2291 |
| expectancy_r | -0.6648 |
| average_r | -0.6648 |
| gross_profit_r | 20.7415 |
| gross_loss_r | 90.5418 |
| net_profit_r | -69.8003 |
| maximum_drawdown_r | -70.8306 |
| drawdown_duration_trades | 104 |
| sharpe_ratio | -0.6253 |
| sortino_ratio | -0.9816 |
| recovery_factor | -0.9855 |
| payoff_ratio | 0.5468 |
| total_R | -69.8003 |
| longest_win_streak | 4 |
| longest_loss_streak | 6 |
| trade_count_adequacy_warning | False |
| mae_distribution |  |
| mfe_distribution |  |
| cost_drag_r |  |

## Notes

- Higher-timeframe context is gated on bar close visibility.
- Slippage is recorded as per-side price movement; USD commission is tracked separately.
- Rejected candidates and stage funnel counts are persisted in dedicated CSV/JSON artifacts.
