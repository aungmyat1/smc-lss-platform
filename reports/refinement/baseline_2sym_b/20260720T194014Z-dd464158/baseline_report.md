# ST-C1 Corrected Baseline Report

- Strategy: `ST-C1`
- Version: `1.0.0`
- Git SHA: `a6eb3105de3b7bfc8af82a77079a1601257bbe3a`
- Runner fingerprint: `81a168439601ee32c96ff64ef8a7e17eb9dd70d0ff6a81499dc8f278228de4ae`
- Dataset count: `6`
- Funnel records: `156877`

## Combined Metrics

| Metric | Value |
|---|---|
| total_trades | 243 |
| win_rate_pct | 39.92 |
| profit_factor | 0.4493 |
| expectancy_r | -0.3895 |
| maximum_drawdown_r | -105.4671 |
| sharpe_ratio | -0.3451 |

## R Breakdown

| Metric | Value |
|---|---|
| trade_count | 243 |
| gross_r | -1.881703 |
| net_r | -94.657647 |
| spread_r | 74.010183 |
| slippage_r | 18.765759 |
| commission_r | 0.0 |
| swap_r | 0.0 |
| total_cost_drag_r | 92.775946 |

## Funnel Counts

| Metric | Value |
|---|---|
| bias_pass | 609 |
| candidate_ready | 243 |
| censored_end_of_data | 0 |
| duplicate_structure | 0 |
| evaluated | 157120 |
| executed_trade | 243 |
| poi_pass | 243 |
| rejected_bias | 1945 |
| rejected_poi | 0 |
| rejected_risk | 0 |
| rejected_session | 107078 |
| rejected_signal | 47488 |
| rejected_sweep | 366 |
| rejected_target | 0 |
| session_pass | 50042 |
| signal_pass | 2554 |
| skipped_open_trade | 0 |
| sweep_pass | 243 |

## By Symbol

### EURUSD
| Metric | Value |
|---|---|
| total_trades | 119 |
| win_rate_pct | 32.77 |
| profit_factor | 0.2328 |
| expectancy_r | -0.6507 |
| maximum_drawdown_r | -78.4588 |
| sharpe_ratio | -0.5749 |

### XAUUSD
| Metric | Value |
|---|---|
| total_trades | 124 |
| win_rate_pct | 46.77 |
| profit_factor | 0.7572 |
| expectancy_r | -0.1389 |
| maximum_drawdown_r | -28.708 |
| sharpe_ratio | -0.1302 |

## Notes

- Higher-timeframe context is gated on bar-close visibility.
- Cost drag is split into spread, slippage, commission, and swap components.
- Rejected candidates and management events are persisted as dedicated artifacts.
