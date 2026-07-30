# ST-C3 Data Integrity Report (before)

Status: **BLOCKED**

Reason: EURUSD_H4.csv: data\market\approved\st_c3\EURUSD_H4.csv: CSV coverage 2021-01-04T00:00:00Z..2021-01-04T19:59:59Z does not cover requested 2021-01-01..2025-12-31

Guardrail: Data recovery does not open A3, run replay, or imply acceptance.

## Root Cause Analysis

The approved-data directory contains partial or wrong-range files. The files do not cover the manifest's requested window, so manifest hashes and dataset approval remain blocked. No repair was applied.

- `EURUSD_H4.csv`: data\market\approved\st_c3\EURUSD_H4.csv: CSV coverage 2021-01-04T00:00:00Z..2021-01-04T19:59:59Z does not cover requested 2021-01-01..2025-12-31
- `EURUSD_M15.csv`: data\market\approved\st_c3\EURUSD_M15.csv: CSV coverage 2021-01-04T00:00:00Z..2021-01-04T23:59:59Z does not cover requested 2021-01-01..2025-12-31
- `EURUSD_M3.csv`: data\market\approved\st_c3\EURUSD_M3.csv: CSV coverage 2021-01-04T00:00:00Z..2021-01-04T23:59:59Z does not cover requested 2021-01-01..2025-12-31
- `GBPUSD_H4.csv`: data\market\approved\st_c3\GBPUSD_H4.csv: CSV coverage 2021-01-04T00:00:00Z..2021-01-04T19:59:59Z does not cover requested 2021-01-01..2025-12-31
- `GBPUSD_M15.csv`: data\market\approved\st_c3\GBPUSD_M15.csv: CSV coverage 2021-01-04T00:00:00Z..2021-01-04T23:59:59Z does not cover requested 2021-01-01..2025-12-31
- `GBPUSD_M3.csv`: data\market\approved\st_c3\GBPUSD_M3.csv: CSV coverage 2021-01-04T00:00:00Z..2021-01-04T23:59:59Z does not cover requested 2021-01-01..2025-12-31

| File | Status | Rows | First | Last | Missing | Duplicates | Issues |
|---|---:|---:|---|---|---:|---:|---:|
| `EURUSD_H4.csv` | BLOCKED | 5 | 2021-01-04T00:00:00Z | 2021-01-04T16:00:00Z | 0 | 0 | 1 |
| `EURUSD_M15.csv` | BLOCKED | 95 | 2021-01-04T00:00:00Z | 2021-01-04T23:45:00Z | 1 | 0 | 1 |
| `EURUSD_M3.csv` | BLOCKED | 479 | 2021-01-04T00:00:00Z | 2021-01-04T23:57:00Z | 1 | 0 | 1 |
| `GBPUSD_H4.csv` | BLOCKED | 5 | 2021-01-04T00:00:00Z | 2021-01-04T16:00:00Z | 0 | 0 | 1 |
| `GBPUSD_M15.csv` | BLOCKED | 95 | 2021-01-04T00:00:00Z | 2021-01-04T23:45:00Z | 1 | 0 | 1 |
| `GBPUSD_M3.csv` | BLOCKED | 479 | 2021-01-04T00:00:00Z | 2021-01-04T23:57:00Z | 1 | 0 | 1 |

## First Blocking Details

- `EURUSD_H4.csv` CSV_COVERAGE: data\market\approved\st_c3\EURUSD_H4.csv: CSV coverage 2021-01-04T00:00:00Z..2021-01-04T19:59:59Z does not cover requested 2021-01-01..2025-12-31
- `EURUSD_M15.csv` first missing candle: `2021-01-04T22:45:00Z`
- `EURUSD_M15.csv` CSV_COVERAGE: data\market\approved\st_c3\EURUSD_M15.csv: CSV coverage 2021-01-04T00:00:00Z..2021-01-04T23:59:59Z does not cover requested 2021-01-01..2025-12-31
- `EURUSD_M3.csv` first missing candle: `2021-01-04T22:45:00Z`
- `EURUSD_M3.csv` CSV_COVERAGE: data\market\approved\st_c3\EURUSD_M3.csv: CSV coverage 2021-01-04T00:00:00Z..2021-01-04T23:59:59Z does not cover requested 2021-01-01..2025-12-31
- `GBPUSD_H4.csv` CSV_COVERAGE: data\market\approved\st_c3\GBPUSD_H4.csv: CSV coverage 2021-01-04T00:00:00Z..2021-01-04T19:59:59Z does not cover requested 2021-01-01..2025-12-31
- `GBPUSD_M15.csv` first missing candle: `2021-01-04T22:15:00Z`
- `GBPUSD_M15.csv` CSV_COVERAGE: data\market\approved\st_c3\GBPUSD_M15.csv: CSV coverage 2021-01-04T00:00:00Z..2021-01-04T23:59:59Z does not cover requested 2021-01-01..2025-12-31
- `GBPUSD_M3.csv` first missing candle: `2021-01-04T22:18:00Z`
- `GBPUSD_M3.csv` CSV_COVERAGE: data\market\approved\st_c3\GBPUSD_M3.csv: CSV coverage 2021-01-04T00:00:00Z..2021-01-04T23:59:59Z does not cover requested 2021-01-01..2025-12-31

## Required Owner Action

Provide a complete approved dataset from an authoritative source for the full manifest coverage window.
Do not manually edit, fabricate, or interpolate candles.
After replacement, rerun `python -m tools.st_c3_data_integrity --data data/market/approved/st_c3 --recover --write-reports`.
