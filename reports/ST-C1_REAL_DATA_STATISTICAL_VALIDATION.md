# ST-C1 Real Data Statistical Validation Report

- Contract: `D:\ddev\smc-lss-platform\strategies\candidates\ST-C1_v1.yaml`
- Strategy version: `1.0.0:21f874e75b4864aa`
- Status: `READY_FOR_ROBUSTNESS_VALIDATION`
- Replay jobs completed: `2/2`

## Dataset

- EURUSD M5: `EURUSD`
  - Dataset hash: `696c18e4a98f66be939d53bb576542f928d09af4c773510fdd985f4008fd2054`
  - Cache: `D:\ddev\smc-lss-platform\validation\cache\EURUSD_M5_bce5f5ef7023bc7b18182966.json`
  - Candles processed: `79999`
  - Signals detected: `97`
  - Trades generated: `97`
  - Elapsed: `2891.6s`
- XAUUSD M5: `XAUUSD-VIP`
  - Dataset hash: `86823a48e006f13d5a97f2c1cc3d0c38ae681c28058ad3d170bd608a449eaf1d`
  - Cache: `D:\ddev\smc-lss-platform\validation\cache\XAUUSD_M5_f276504ae0c16e02499624e8.json`
  - Candles processed: `79999`
  - Signals detected: `105`
  - Trades generated: `105`
  - Elapsed: `5421.7s`

## Performance

| Symbol | Timeframe | Trades | Win% | PF | Expectancy | Sharpe | Max DD | Resumed | Cache Hit |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| EURUSD | M5 | 97 | 0.0000 | 0.0000 | -5.7638 | -1.8080 | -559.0915 | True | False |
| XAUUSD | M5 | 105 | 38.1000 | 1.2622 | 0.1624 | 0.1085 | -15.0131 | False | False |

### Combined Metrics

- total_trades: `202`
- win_rate_pct: `19.8000`
- profit_factor: `0.1315`
- expectancy_r: `-2.6834`
- average_r: `-2.6834`
- maximum_drawdown_r: `-568.1055`
- sharpe_ratio: `-0.6973`

## Stability

### Monthly

| Label | Trades | PF | Sharpe | Max DD | Expectancy |
|---|---:|---:|---:|---:|---:|
| 2025-06 | 19 | 0.3107 | -0.4695 | -19.7434 | -0.9339 |
| 2025-07 | 22 | 0.1424 | -0.7964 | -52.1490 | -2.1886 |
| 2025-08 | 13 | 0.0758 | -1.0078 | -49.7716 | -3.7518 |
| 2025-09 | 16 | 0.2966 | -0.4759 | -30.4456 | -1.7779 |
| 2025-10 | 15 | 0.0242 | -1.2443 | -80.6653 | -5.3777 |
| 2025-11 | 18 | 0.0266 | -1.1904 | -73.0918 | -4.0607 |
| 2025-12 | 9 | 0.0000 | -1.4752 | -49.9450 | -5.5494 |
| 2026-01 | 13 | 0.0798 | -0.6258 | -48.1350 | -3.5488 |
| 2026-02 | 11 | 0.0895 | -0.8123 | -20.3497 | -1.8500 |
| 2026-03 | 9 | 0.1855 | -0.7088 | -17.5604 | -1.9512 |
| 2026-04 | 19 | 0.1224 | -0.6650 | -45.0135 | -2.2639 |
| 2026-05 | 16 | 0.3046 | -0.4464 | -37.9506 | -1.9970 |
| 2026-06 | 16 | 0.2024 | -0.5830 | -31.5153 | -1.9697 |
| 2026-07 | 6 | 0.6327 | -0.2001 | -7.2834 | -0.7835 |

### Yearly

| Label | Trades | PF | Sharpe | Max DD | Expectancy |
|---|---:|---:|---:|---:|---:|
| 2025 | 112 | 0.0940 | -0.8321 | -346.8154 | -3.0966 |
| 2026 | 90 | 0.1910 | -0.5505 | -197.8102 | -2.1692 |

### Session

| Label | Trades | PF | Sharpe | Max DD | Expectancy |
|---|---:|---:|---:|---:|---:|
| London | 111 | 0.0992 | -0.8012 | -365.1747 | -3.2718 |
| NewYork | 91 | 0.1905 | -0.5772 | -180.4472 | -1.9656 |

### Symbol

| Label | Trades | PF | Sharpe | Max DD | Expectancy |
|---|---:|---:|---:|---:|---:|
| EURUSD | 97 | 0.0000 | -1.8080 | -559.0915 | -5.7638 |
| XAUUSD | 105 | 1.2622 | 0.1085 | -15.0131 | 0.1624 |

### Long/Short

| Label | Trades | PF | Sharpe | Max DD | Expectancy |
|---|---:|---:|---:|---:|---:|
| long | 93 | 0.1205 | -0.7449 | -248.0786 | -2.6675 |
| short | 109 | 0.1406 | -0.6639 | -302.0631 | -2.6969 |


## Assumptions

- EURUSD: `{"costs":{"commission_r":0.0,"point_size":0.0001,"slippage_points":3.0,"spread_points":25.0,"stop_buffer_atr_mult":0.15,"warmup_bars":40},"dataset_hash":"696c18e4a98f66be939d53bb576542f928d09af4c773510fdd985f4008fd2054","entry":"next candle after signal","exit":"contract-defined SL/TP with stop-first conservative fills","source_symbol":"EURUSD","strategy_version":"1.0.0:21f874e75b4864aa"}`
- XAUUSD: `{"costs":{"commission_r":0.0,"point_size":0.0001,"slippage_points":3.0,"spread_points":25.0,"stop_buffer_atr_mult":0.15,"warmup_bars":40},"dataset_hash":"86823a48e006f13d5a97f2c1cc3d0c38ae681c28058ad3d170bd608a449eaf1d","entry":"next candle after signal","exit":"contract-defined SL/TP with stop-first conservative fills","source_symbol":"XAUUSD-VIP","strategy_version":"1.0.0:21f874e75b4864aa"}`

## Status

READY_FOR_ROBUSTNESS_VALIDATION
