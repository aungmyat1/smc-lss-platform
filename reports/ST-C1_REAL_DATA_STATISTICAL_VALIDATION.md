# ST-C1 Real Data Statistical Validation Report

- Contract: `D:\ddev\smc-lss-platform\strategies\candidates\ST-C1_v1.yaml`
- Status: `BLOCKED`
- Caveat: `The real-data replay pass over the available historical CSVs did not complete within this session, so no completed ST-C1 real-data performance evidence was captured.`

## Dataset

- Source: local repository historical CSV exports under `data/`
- Symbols available for the run:
  - `EURUSD`
  - `XAUUSD-VIP`
- Timeframes:
  - `M5`
  - `H1`
  - `D1`
- Date range:
  - `EURUSD_M5.csv`: `2025-06-20 22:55` to `2026-07-17 17:50`
  - `EURUSD_H1.csv`: `2025-02-05 18:00` to `2026-07-17 17:00`
  - `EURUSD_D1.csv`: `2024-08-13 00:00` to `2026-07-17 00:00`
  - `XAUUSD-VIP_M5.csv`: `2025-06-02 07:25` to `2026-07-17 17:50`
  - `XAUUSD-VIP_H1.csv`: `2025-01-08 19:00` to `2026-07-17 17:00`
  - `XAUUSD-VIP_D1.csv`: `2024-08-09 00:00` to `2026-07-17 00:00`
- Candle count:
  - `EURUSD_M5.csv`: `80000`
  - `EURUSD_H1.csv`: `9000`
  - `EURUSD_D1.csv`: `500`
  - `XAUUSD-VIP_M5.csv`: `80000`
  - `XAUUSD-VIP_H1.csv`: `9000`
  - `XAUUSD-VIP_D1.csv`: `500`

## Pipeline

- Historical dataset: available and verified on disk
- M2.2 replay engine: invoked against the real CSVs
- ST-C1 trade results: not fully captured before the run timed out
- M2.3 statistical validation: not reached with completed real-data trade output

## Performance

- Total trades: `not available`
- Win rate: `not available`
- Profit factor: `not available`
- Sharpe ratio: `not available`
- Maximum drawdown: `not available`
- Expectancy: `not available`
- Average R: `not available`

## Stability

- Monthly: `not available`
- Yearly: `not available`
- Session: `not available`
- Symbol: `not available`
- Long/short: `not available`

## Gate

- Required pass thresholds:
  - trades `>= 200`
  - PF `> 1.25`
  - Sharpe `> 1.2`
  - DD `< 15%`
- Outcome: `BLOCKED`
- Reason: the real-data replay did not complete, so the gate could not be evaluated on finished ST-C1 trade evidence.

