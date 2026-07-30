# ST-C3 Data Integrity Report (before)

Status: **BLOCKED**

Reason: EURUSD_H4.csv missing candle 2018-01-02T04:00:00Z

Guardrail: Data recovery does not open A3, run replay, or imply acceptance.

## Root Cause Analysis

The approved-data directory now contains HistData-derived candidate files. Raw HistData M1 source files were downloaded for EURUSD/GBPUSD 2017-2024, converted from EST without daylight-saving adjustment to UTC, and aggregated into H4/M15/M3. The source data contains gaps or incomplete aggregation windows, so the candidate fails the existing no-missing-candles continuity contract. No candles were fabricated, interpolated, or manually edited.

- `EURUSD_H4.csv`: data\market\approved\st_c3\EURUSD_H4.csv: CSV coverage 2018-01-02T00:00:00Z..2024-12-31T19:59:59Z does not cover requested 2018-01-01..2024-12-31
- `EURUSD_M15.csv`: data\market\approved\st_c3\EURUSD_M15.csv: CSV coverage 2018-01-01T22:00:00Z..2024-12-31T21:44:59Z does not cover requested 2018-01-01..2024-12-31
- `EURUSD_M3.csv`: data\market\approved\st_c3\EURUSD_M3.csv: CSV coverage 2018-01-01T22:00:00Z..2024-12-31T21:56:59Z does not cover requested 2018-01-01..2024-12-31
- `GBPUSD_H4.csv`: data\market\approved\st_c3\GBPUSD_H4.csv: CSV coverage 2018-01-02T08:00:00Z..2024-12-31T19:59:59Z does not cover requested 2018-01-01..2024-12-31
- `GBPUSD_M15.csv`: data\market\approved\st_c3\GBPUSD_M15.csv: CSV coverage 2018-01-01T23:00:00Z..2024-12-31T21:44:59Z does not cover requested 2018-01-01..2024-12-31
- `GBPUSD_M3.csv`: data\market\approved\st_c3\GBPUSD_M3.csv: CSV coverage 2018-01-01T22:06:00Z..2024-12-31T21:56:59Z does not cover requested 2018-01-01..2024-12-31

| File | Status | Rows | First | Last | Missing | Duplicates | Issues |
|---|---:|---:|---|---|---:|---:|---:|
| `EURUSD_H4.csv` | BLOCKED | 7930 | 2018-01-02T00:00:00Z | 2024-12-31T16:00:00Z | 2971 | 0 | 1 |
| `EURUSD_M15.csv` | BLOCKED | 164882 | 2018-01-01T22:00:00Z | 2024-12-31T21:30:00Z | 8958 | 0 | 1 |
| `EURUSD_M3.csv` | BLOCKED | 846064 | 2018-01-01T22:00:00Z | 2024-12-31T21:54:00Z | 25589 | 0 | 1 |
| `GBPUSD_H4.csv` | BLOCKED | 8163 | 2018-01-02T08:00:00Z | 2024-12-31T16:00:00Z | 2737 | 0 | 1 |
| `GBPUSD_M15.csv` | BLOCKED | 165883 | 2018-01-01T23:00:00Z | 2024-12-31T21:30:00Z | 7974 | 0 | 1 |
| `GBPUSD_M3.csv` | BLOCKED | 847171 | 2018-01-01T22:06:00Z | 2024-12-31T21:54:00Z | 24289 | 0 | 1 |

## First Blocking Details

- `EURUSD_H4.csv` first missing candle: `2018-01-02T04:00:00Z`
- `EURUSD_H4.csv` CSV_COVERAGE: data\market\approved\st_c3\EURUSD_H4.csv: CSV coverage 2018-01-02T00:00:00Z..2024-12-31T19:59:59Z does not cover requested 2018-01-01..2024-12-31
- `EURUSD_M15.csv` first missing candle: `2018-01-02T05:00:00Z`
- `EURUSD_M15.csv` CSV_COVERAGE: data\market\approved\st_c3\EURUSD_M15.csv: CSV coverage 2018-01-01T22:00:00Z..2024-12-31T21:44:59Z does not cover requested 2018-01-01..2024-12-31
- `EURUSD_M3.csv` first missing candle: `2018-01-02T05:06:00Z`
- `EURUSD_M3.csv` CSV_COVERAGE: data\market\approved\st_c3\EURUSD_M3.csv: CSV coverage 2018-01-01T22:00:00Z..2024-12-31T21:56:59Z does not cover requested 2018-01-01..2024-12-31
- `GBPUSD_H4.csv` first missing candle: `2018-01-02T20:00:00Z`
- `GBPUSD_H4.csv` CSV_COVERAGE: data\market\approved\st_c3\GBPUSD_H4.csv: CSV coverage 2018-01-02T08:00:00Z..2024-12-31T19:59:59Z does not cover requested 2018-01-01..2024-12-31
- `GBPUSD_M15.csv` first missing candle: `2018-01-02T02:30:00Z`
- `GBPUSD_M15.csv` CSV_COVERAGE: data\market\approved\st_c3\GBPUSD_M15.csv: CSV coverage 2018-01-01T23:00:00Z..2024-12-31T21:44:59Z does not cover requested 2018-01-01..2024-12-31
- `GBPUSD_M3.csv` first missing candle: `2018-01-02T02:33:00Z`
- `GBPUSD_M3.csv` CSV_COVERAGE: data\market\approved\st_c3\GBPUSD_M3.csv: CSV coverage 2018-01-01T22:06:00Z..2024-12-31T21:56:59Z does not cover requested 2018-01-01..2024-12-31

## Required Owner Action

Provide a complete approved dataset from an authoritative source for the full manifest coverage window.
Do not manually edit, fabricate, or interpolate candles.
After replacement, rerun `python -m tools.st_c3_data_integrity --data data/market/approved/st_c3 --recover --write-reports`.
