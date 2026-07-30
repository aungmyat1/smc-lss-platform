# ST-C3 Dataset Acquisition Report

Status: **BLOCKED / NOT_APPROVED**

Date: 2026-07-30

## Objective

Acquire, normalize, validate, and publish a complete ST-C3 Dataset v1.0
candidate for:

- `EURUSD`, `GBPUSD`
- `H4`, `M15`, `M3`
- `2018-01-01` through `2024-12-31`
- UTC timestamps

No ST-C3 strategy logic, detection logic, replay logic, validation rules, or
approval gates were modified.

## Implemented Acquisition Tool

Added:

`tools/st_c3_acquire_histdata_dataset.py`

The tool:

- downloads HistData yearly Generic ASCII M1 ZIP files
- includes 2017 source data so UTC conversion can cover the beginning of 2018
- converts HistData EST-without-DST timestamps to UTC
- constructs H4, M15, and M3 candles from complete M1 windows only
- writes repository-standard CSV files
- keeps the manifest `NOT_APPROVED`
- invokes the existing integrity and contract validators without modifying
  their rules

## Raw Source Files Downloaded

All expected HistData ZIPs were downloaded:

- `EURUSD` M1: 2017 through 2024
- `GBPUSD` M1: 2017 through 2024

Raw cache path:

`data/market/raw/histdata/st_c3/`

Raw ZIP count: 16

Raw byte total: 53,870,181

## Candidate Files Constructed

Path:

`data/market/approved/st_c3/`

Constructed files:

| File | Status |
|---|---|
| `EURUSD_H4.csv` | constructed from HistData M1 |
| `EURUSD_M15.csv` | constructed from HistData M1 |
| `EURUSD_M3.csv` | constructed from HistData M1 |
| `GBPUSD_H4.csv` | constructed from HistData M1 |
| `GBPUSD_M15.csv` | constructed from HistData M1 |
| `GBPUSD_M3.csv` | constructed from HistData M1 |

The files are candidate data only. They are not approved.

## Validation Result

Existing validation command:

```powershell
python -m tools.st_c3_data_integrity --data data/market/approved/st_c3 --write-reports
```

Result: **BLOCKED**

First blocker:

`EURUSD_H4.csv` missing `2018-01-02T04:00:00Z`

Per-file missing counts:

| File | Missing | Duplicates | Issues |
|---|---:|---:|---:|
| `EURUSD_H4.csv` | 2,971 | 0 | 1 |
| `EURUSD_M15.csv` | 8,958 | 0 | 1 |
| `EURUSD_M3.csv` | 25,589 | 0 | 1 |
| `GBPUSD_H4.csv` | 2,737 | 0 | 1 |
| `GBPUSD_M15.csv` | 7,974 | 0 | 1 |
| `GBPUSD_M3.csv` | 24,289 | 0 | 1 |

Contract validation command:

```powershell
python -m tools.st_c3_dataset_contract --contract contracts/DATASET_CONTRACT.yaml --data data/market/approved/st_c3
```

Result: **BLOCKED**

## Root Cause

HistData M1 source files do not contain every minute required to construct
complete H4, M15, and M3 windows under the repository's strict ST-C3
continuity contract.

The construction tool intentionally drops incomplete aggregation windows
instead of fabricating or interpolating prices. The existing validator then
correctly reports missing timestamps.

## Approval Status

Dataset approval: **NOT_APPROVED**

Manifest status: **NOT_APPROVED**

Contract status: **BLOCKED**

Replay status: **BLOCKED**

A3/statistics/demo/live: **BLOCKED**

## Recommendation

Stop using HistData as the canonical ST-C3 Dataset v1.0 source under the
current validation contract.

Next source to try:

**Dukascopy Historical Data Export / JForex historical data**

If Dukascopy cannot provide data that passes the existing validator without
fabrication or interpolation, escalate to a paid institutional FX intraday
provider or an owner-approved broker export with complete bar continuity.
