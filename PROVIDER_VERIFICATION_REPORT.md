# ST-C3 Provider Verification Report

Status: **PASS / LIMITED SAMPLE**

Date: 2026-07-30

Provider verified: **Dukascopy**

## Verification Objective

Verify the highest-ranked provider with a limited sample only.

This report does not approve a dataset and does not authorize replay. It
verifies that Dukascopy is technically suitable for the next Dataset
Acquisition Sprint.

## Verification Tool

`tools/st_c3_verify_dukascopy_provider.py`

The tool:

- downloads hourly Dukascopy `.bi5` tick files from deterministic datafeed
  URLs
- decompresses LZMA payloads
- parses 20-byte tick records
- reconstructs bid-based M1 OHLC bars for each UTC hour
- verifies tick monotonicity
- verifies minute continuity
- verifies OHLC geometry

## Command

```powershell
python -m tools.st_c3_verify_dukascopy_provider
```

## Sample Scope

Symbols:

- `EURUSD`
- `GBPUSD`

UTC hours:

- `2024-01-02T00:00:00Z`
- `2024-01-02T01:00:00Z`

## Results

| Symbol | Hour UTC | Ticks | Minute Bars | Minute Gaps | Monotonic Ticks | OHLC Valid |
|---|---|---:|---:|---:|---|---|
| `EURUSD` | `2024-01-02T00:00:00Z` | 1,432 | 60 | 0 | true | true |
| `EURUSD` | `2024-01-02T01:00:00Z` | 2,570 | 60 | 0 | true | true |
| `GBPUSD` | `2024-01-02T00:00:00Z` | 1,789 | 60 | 0 | true | true |
| `GBPUSD` | `2024-01-02T01:00:00Z` | 4,163 | 60 | 0 | true | true |

## Checks

Timestamp continuity:

PASS. Each sampled hour reconstructed 60 M1 bars with zero minute gaps.

OHLC validity:

PASS. Reconstructed bars satisfied high >= open/close, low <= open/close,
and high >= low.

Weekend handling:

Not fully tested in this limited weekday sample. Full acquisition must
validate weekend closure behavior through the existing ST-C3 validator.

DST handling:

Dukascopy URL addressing and sample timestamps are UTC-hour based. Full
acquisition must continue using UTC hour paths.

Session boundaries:

Not fully tested in this limited sample. Because source ticks are UTC-hour
addressed, session assignment can use the existing repository UTC session
logic during construction.

Aggregation correctness:

PASS for M1 reconstruction from ticks in the limited sample. M3, M15, and H4
aggregation must be verified during full acquisition by constructing from
complete M1 windows and running the unchanged validator.

Manifest compatibility:

PARTIAL. Dukascopy can provide source data suitable for generating governed
CSV files, but manifest compatibility can only pass after full dataset
construction and checksum generation.

## Verification Decision

Dukascopy passes limited provider verification.

Decision: **QUALIFIED FOR DATASET ACQUISITION**

Replay remains **BLOCKED**.
