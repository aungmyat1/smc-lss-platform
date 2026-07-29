# ST-C3 Data Integrity Report (after)

Status: **BLOCKED**

Reason: EURUSD_H4.csv missing candle 2018-12-26T00:00:00Z

Guardrail: Data recovery does not open A3, run replay, or imply acceptance.

## Root Cause Analysis

The approved-data directory contains partial or wrong-range files. M15 files begin in 2022 instead of 2018, and M3 files contain one 2025 candle rather than the approved 2018-2024 window. The attempted MT5 recovery did not return exact missing candles, so no repair was applied.

- `EURUSD_M15.csv`: data\market\approved\st_c3\EURUSD_M15.csv: CSV coverage 2022-07-22T01:45:00Z..2024-12-31T23:59:59Z does not cover requested 2018-01-01..2024-12-31
- `EURUSD_M3.csv`: data\market\approved\st_c3\EURUSD_M3.csv: CSV coverage 2025-10-08T06:12:00Z..2025-10-08T06:14:59Z does not cover requested 2018-01-01..2024-12-31
- `GBPUSD_M15.csv`: data\market\approved\st_c3\GBPUSD_M15.csv: CSV coverage 2022-07-22T02:15:00Z..2024-12-31T23:59:59Z does not cover requested 2018-01-01..2024-12-31
- `GBPUSD_M3.csv`: data\market\approved\st_c3\GBPUSD_M3.csv: CSV coverage 2025-10-08T05:15:00Z..2025-10-08T05:17:59Z does not cover requested 2018-01-01..2024-12-31

| File | Status | Rows | First | Last | Missing | Duplicates | Issues |
|---|---:|---:|---|---|---:|---:|---:|
| `EURUSD_H4.csv` | BLOCKED | 10896 | 2018-01-02T00:00:00Z | 2024-12-31T20:00:00Z | 7 | 0 | 0 |
| `EURUSD_M15.csv` | BLOCKED | 60860 | 2022-07-22T01:45:00Z | 2024-12-31T23:45:00Z | 66 | 0 | 1 |
| `EURUSD_M3.csv` | BLOCKED | 1 | 2025-10-08T06:12:00Z | 2025-10-08T06:12:00Z | 0 | 0 | 1 |
| `GBPUSD_H4.csv` | BLOCKED | 10896 | 2018-01-02T00:00:00Z | 2024-12-31T20:00:00Z | 7 | 0 | 0 |
| `GBPUSD_M15.csv` | BLOCKED | 60860 | 2022-07-22T02:15:00Z | 2024-12-31T23:45:00Z | 66 | 0 | 1 |
| `GBPUSD_M3.csv` | BLOCKED | 1 | 2025-10-08T05:15:00Z | 2025-10-08T05:15:00Z | 0 | 0 | 1 |

## First Blocking Details

- `EURUSD_H4.csv` first missing candle: `2018-12-26T00:00:00Z`
- `EURUSD_M15.csv` first missing candle: `2022-12-26T00:00:00Z`
- `EURUSD_M15.csv` CSV_COVERAGE: data\market\approved\st_c3\EURUSD_M15.csv: CSV coverage 2022-07-22T01:45:00Z..2024-12-31T23:59:59Z does not cover requested 2018-01-01..2024-12-31
- `EURUSD_M3.csv` CSV_COVERAGE: data\market\approved\st_c3\EURUSD_M3.csv: CSV coverage 2025-10-08T06:12:00Z..2025-10-08T06:14:59Z does not cover requested 2018-01-01..2024-12-31
- `GBPUSD_H4.csv` first missing candle: `2018-12-26T00:00:00Z`
- `GBPUSD_M15.csv` first missing candle: `2022-12-26T00:00:00Z`
- `GBPUSD_M15.csv` CSV_COVERAGE: data\market\approved\st_c3\GBPUSD_M15.csv: CSV coverage 2022-07-22T02:15:00Z..2024-12-31T23:59:59Z does not cover requested 2018-01-01..2024-12-31
- `GBPUSD_M3.csv` CSV_COVERAGE: data\market\approved\st_c3\GBPUSD_M3.csv: CSV coverage 2025-10-08T05:15:00Z..2025-10-08T05:17:59Z does not cover requested 2018-01-01..2024-12-31

## Required Owner Action

Provide a complete approved dataset from an authoritative source for the full manifest coverage window.
Do not manually edit, fabricate, or interpolate candles.
After replacement, rerun `python -m tools.st_c3_data_integrity --data data/market/approved/st_c3 --recover --write-reports`.
