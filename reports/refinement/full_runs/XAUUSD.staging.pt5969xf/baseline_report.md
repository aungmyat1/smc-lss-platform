# ST-C1 Corrected Baseline Report

- Spec: `specs/research/v1_baseline.yaml`
- Git SHA: `c7c415ef179726fe14c135bb6e7e0b3b53e041e2`
- Strategy version: `1.0.0`
- Symbols: `XAUUSD`
- Dataset count: `3`
- Funnel records: `78528`

## Combined Metrics

| Key | Value |
|---|---|
| total_trades | 103 |
| wins | 49 |
| losses | 54 |
| win_rate_pct | 47.57 |
| profit_factor | 0.8619 |
| expectancy_r | -0.0724 |
| average_r | -0.0724 |
| gross_profit_r | 46.5471 |
| gross_loss_r | 54.0031 |
| net_profit_r | -7.456 |
| maximum_drawdown_r | -19.0043 |
| drawdown_duration_trades | 93 |
| sharpe_ratio | -0.0694 |
| sortino_ratio | -1810.32 |
| recovery_factor | -0.3923 |
| payoff_ratio | 0.9499 |
| total_R | -7.456 |
| longest_win_streak | 4 |
| longest_loss_streak | 6 |
| trade_count_adequacy_warning | False |
| mae_distribution |  |
| mfe_distribution |  |
| cost_drag_r |  |

## Funnel Counts

| Key | Value |
|---|---|
| bias_pass | 311 |
| evaluated | 78669 |
| poi_pass | 141 |
| rejected_bias | 1085 |
| rejected_session | 52925 |
| rejected_signal | 24348 |
| rejected_sweep | 170 |
| session_pass | 25744 |
| signal_pass | 1396 |
| sweep_pass | 141 |
| trade_pass | 141 |

## Symbol Metrics

### XAUUSD

| Key | Value |
|---|---|
| total_trades | 103 |
| wins | 49 |
| losses | 54 |
| win_rate_pct | 47.57 |
| profit_factor | 0.8619 |
| expectancy_r | -0.0724 |
| average_r | -0.0724 |
| gross_profit_r | 46.5471 |
| gross_loss_r | 54.0031 |
| net_profit_r | -7.456 |
| maximum_drawdown_r | -19.0043 |
| drawdown_duration_trades | 93 |
| sharpe_ratio | -0.0694 |
| sortino_ratio | -1810.32 |
| recovery_factor | -0.3923 |
| payoff_ratio | 0.9499 |
| total_R | -7.456 |
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
