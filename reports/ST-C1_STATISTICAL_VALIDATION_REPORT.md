# ST-C1 Statistical Validation Report

- Contract: `D:\ddev\smc-lss-platform\strategies\candidates\ST-C1_v1.yaml`
- Status: `READY_FOR_ROBUSTNESS_VALIDATION`
- Caveat: `Synthetic validation fixture for scaffold verification.`
- Gate reasons: `0`

## Result

READY_FOR_ROBUSTNESS_VALIDATION

## Gate Reasons

- None

## Overall Metrics

- total_trades: `12`
- win_rate_pct: `83.3300`
- profit_factor: `6.0000`
- expectancy_r: `0.8333`
- average_r: `0.8333`
- maximum_drawdown_r: `-1.1000`
- sharpe_ratio: `0.9473`

## Return Distribution

- count: `12`
- min: `-1.1000`
- p10: `-0.7400`
- p25: `0.7750`
- median: `1.0500`
- p75: `1.4250`
- p90: `1.5900`
- max: `1.8000`
- mean: `0.8333`
- stdev: `0.8797`

## Bootstrap Expectancy CI

- Lower: `0.5000`
- Upper: `1.2000`

## Data Split Validation

- Split ratio: `0.5`
- Split time: `2026-06-03T06:15:00Z`

### In-Sample

- Trades: `6`
- PF: `5.3636`
- Sharpe: `0.8963`
- Max DD: `-1.1000`
- Expectancy: `0.8000`

### Out-of-Sample

- Trades: `6`
- PF: `6.7778`
- Sharpe: `1.0015`
- Max DD: `-0.9000`
- Expectancy: `0.8667`

## Walk Forward Validation

| Fold | Train Period | Test Period | Trades | PF | Sharpe | Max DD | Expectancy |
|---|---|---|---:|---:|---:|---:|---:|
| 1 | 2025-12-01T00:00:00Z -> 2025-12-31T23:55:00Z | 2026-06-01T00:00:00Z -> 2026-06-15T23:55:00Z | 2 | inf | 6.5000 | 0.0000 | 1.3000 |
| 2 | 2025-12-01T00:00:00Z -> 2026-06-15T23:55:00Z | 2026-06-16T00:00:00Z -> 2026-07-05T23:55:00Z | 2 | 2.0000 | 0.3333 | -0.9000 | 0.4500 |
| 3 | 2025-12-01T00:00:00Z -> 2026-07-05T23:55:00Z | 2026-07-06T00:00:00Z -> 2026-07-31T23:55:00Z | 2 | inf | 5.6667 | 0.0000 | 0.8500 |

## Stability Tests

### Monthly

| Label | Trades | PF | Sharpe | Max DD | Expectancy |
|---|---:|---:|---:|---:|---:|
| 2025-12 | 3 | 2.0909 | 0.3703 | -1.1000 | 0.4000 |
| 2026-01 | 3 | inf | 3.6742 | 0.0000 | 1.2000 |
| 2026-06 | 3 | 2.8889 | 0.5398 | -0.9000 | 0.5667 |
| 2026-07 | 3 | inf | 2.5129 | 0.0000 | 1.1667 |

### Yearly

| Label | Trades | PF | Sharpe | Max DD | Expectancy |
|---|---:|---:|---:|---:|---:|
| 2025 | 3 | 2.0909 | 0.3703 | -1.1000 | 0.4000 |
| 2026 | 9 | 10.7778 | 1.3072 | -0.9000 | 0.9778 |

### Session

| Label | Trades | PF | Sharpe | Max DD | Expectancy |
|---|---:|---:|---:|---:|---:|
| London | 5 | 1.9500 | 0.3331 | -1.1000 | 0.3800 |
| NewYork | 5 | inf | 2.6976 | 0.0000 | 1.0600 |
| OFF_SESSION | 2 | inf | 7.0000 | 0.0000 | 1.4000 |

### Symbol

| Label | Trades | PF | Sharpe | Max DD | Expectancy |
|---|---:|---:|---:|---:|---:|
| EURUSD | 6 | 5.3636 | 0.8963 | -1.1000 | 0.8000 |
| XAUUSD | 6 | 6.7778 | 1.0015 | -0.9000 | 0.8667 |

### Long/Short

| Label | Trades | PF | Sharpe | Max DD | Expectancy |
|---|---:|---:|---:|---:|---:|
| long | 7 | 3.1500 | 0.5824 | -1.1000 | 0.6143 |
| short | 5 | inf | 3.0643 | 0.0000 | 1.1400 |

## Assumptions

- split_ratio: `0.5`
- note: `Synthetic validation fixture for scaffold verification.`

## Status

READY_FOR_ROBUSTNESS_VALIDATION
