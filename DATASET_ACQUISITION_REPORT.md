# ST-C3 Five-Year Dataset Acquisition Report

Status: **IN_PROGRESS**

Date: 2026-07-30

Provider: **Dukascopy tick datafeed**

Dataset version: **Dataset_v1.0_5Y**

## Objective

Acquire, normalize, validate, and publish a complete ST-C3 Dataset v1.0
candidate for:

- `EURUSD`, `GBPUSD`
- `H4`, `M15`, `M3`
- `2021-01-01` through `2025-12-31`
- UTC timestamps

No ST-C3 strategy logic, detection logic, replay logic, validation rules, or
approval gates were modified.

## Implemented Acquisition Tool

Added:

`tools/st_c3_acquire_dukascopy_dataset.py`

The tool:

- downloads hourly Dukascopy `.bi5` tick files into a resumable raw cache
- skips ST-C3-recognized weekend and fixed-holiday closures
- records every attempted hour, byte count, hash, and failure
- reconstructs UTC M1 bid candles from ticks
- aggregates only complete M1 windows into `H4`, `M15`, and `M3`
- writes repository-standard candidate CSV files
- can invoke the existing integrity and contract validators without modifying
  their rules
- keeps dataset approval, replay, A3, demo, and live gates locked

Raw cache path:

`data/market/raw/dukascopy/st_c3/`

Latest status report:

`reports/validation/st_c3/data_integrity/DUKASCOPY_ACQUISITION_STATUS.json`

## Initial Five-Year Sprint Download Batch

Command:

```powershell
python -m tools.st_c3_acquire_dukascopy_dataset --download --start 2021-01-04T00:00:00Z --end 2021-01-04T23:00:00Z --max-hours 48 --retries 2
```

Result: **IN_PROGRESS**

| Metric | Value |
|---|---:|
| Cached open-market hourly files in checkpoint range | 48 |
| Failed downloads | 0 |
| Corrupt cached files remaining | 0 |

The earlier 2018 sample cache remains provider evidence only. The active
canonical sprint is limited to 2021-2025.

The completed checkpoint covered both `EURUSD` and `GBPUSD` together. It did
not modify approval fields.

## Checkpoint Artifacts

The acquisition engine now regenerates:

- `reports/validation/st_c3/data_integrity/ACQUISITION_PROGRESS.json`
- `reports/validation/st_c3/data_integrity/CHECKPOINT_MANIFEST.json`
- `reports/validation/st_c3/data_integrity/DOWNLOAD_RECOVERY_LOG.md`
- `reports/validation/st_c3/data_integrity/NORMALIZATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/AGGREGATION_REPORT.md`

## Candidate Construction

Status: **CHECKPOINT_CONSTRUCTED / FULL_RANGE_INCOMPLETE**

The first checkpoint construction generated 1,158 candles across all six
candidate files for `2021-01-04`.

Construction command:

```powershell
python -m tools.st_c3_acquire_dukascopy_dataset --construct
```

The constructor emits only complete aggregation windows. It does not fabricate,
interpolate, or manually edit prices.

## Validation Status

Status: **BLOCKED**

Checkpoint validation command:

```powershell
python -m tools.st_c3_acquire_dukascopy_dataset --construct --validate --start 2021-01-04T00:00:00Z --end 2021-01-04T23:59:59Z
```

This calls the existing integrity scanner and dataset contract checker. The
validation engine remains unchanged.

Result: **BLOCKED**

Primary blocker:

`EURUSD_H4.csv` checkpoint coverage `2021-01-04T00:00:00Z` through
`2021-01-04T19:59:59Z` does not cover required `2021-01-01` through
`2025-12-31`.

Additional checkpoint risk: lower-timeframe gaps were observed in the one-day
slice, including `EURUSD_M15.csv` missing `2021-01-04T22:45:00Z` and
`GBPUSD_M15.csv` missing `2021-01-04T22:15:00Z`. These remain unresolved and
must not be filled manually.

## Aggregation Validation

Status: **BLOCKED**

Command:

```powershell
python -m tools.st_c3_validate_aggregation --start 2021-01-04T00:00:00Z --end 2021-01-04T23:59:59Z
```

Result:

- `EURUSD` M1 rows: 1,438 of 1,440 expected
- `EURUSD` missing source minutes: `2021-01-04T22:45:00Z`,
  `2021-01-04T22:46:00Z`
- `GBPUSD` M1 rows: 1,439 of 1,440 expected
- `GBPUSD` missing source minute: `2021-01-04T22:19:00Z`
- Aggregation mismatches: 0

Root cause:

The missing M3/M15/H4 windows are explained by sparse source ticks in the
Dukascopy `22h_ticks.bi5` files. The aggregation algorithm did not show an
OHLCV mismatch against the available reconstructed M1 data.

Decision required:

The current constructor emits only minutes that have source ticks. Under the
repository's no-missing-candles contract, sparse zero-tick minutes will keep
the dataset blocked unless an owner-approved, governance-compliant bar policy
is adopted or a provider supplies complete M1/bar data for those minutes.

## Source Integrity Investigation

Status: **BLOCKED**

Command:

```powershell
python -m tools.st_c3_investigate_source_integrity
```

Findings:

- Cached Dukascopy `.bi5` files parse successfully.
- Fresh Dukascopy downloads for the same hourly files match cached SHA-256
  hashes exactly.
- The missing minutes contain zero Dukascopy ticks.
- HistData M1 reference data also lacks the exact probed minutes.

Probe verdicts:

| Symbol | Timestamp | Verdict |
|---|---|---|
| `EURUSD` | `2021-01-04T22:45:00Z` | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `EURUSD` | `2021-01-04T22:46:00Z` | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `GBPUSD` | `2021-01-04T22:19:00Z` | `DUKASCOPY_AND_REFERENCE_ABSENT` |

Conclusion:

The current evidence does not indicate a parser defect, truncated cache, or
stale download. It indicates sparse zero-tick minutes in independently checked
historical data. Dataset production remains blocked pending Dataset Contract
Review.

## Dataset Contract Review

Status: **BLOCKED**

Command:

```powershell
python -m tools.st_c3_dataset_contract_review
```

Findings:

- Current policy: `strict_market_open_candle_continuity`
- Missing timestamp check: `required`
- Allowed gap policy: weekend and fixed holidays only
- Zero-tick probe count: 3
- Aggregation mismatch count: 0

Recommendation:

`OPEN_GOVERNANCE_CHANGE_REQUEST`

Available governance options:

- Retain strict contract and select a provider that supplies complete bars.
- Define a deterministic zero-tick candle policy through a governed contract
  and validator change.
- Select an authoritative M1/bar provider with documented zero-volume or
  carry-forward bar methodology.

## Approval Status

Dataset approval: **NOT_APPROVED**

Manifest status: **NOT_APPROVED**

Contract status: **BLOCKED**

Replay status: **BLOCKED**

A3/statistics/demo/live: **BLOCKED**

## Next Action

Pause large-scale acquisition and open Dataset Contract Review for zero-tick
market-open minutes. Continue full five-year acquisition only after governance
decides whether the contract requires candles for zero-tick minutes or only
minutes with at least one underlying tick.

Recommended next command:

```powershell
python -m tools.st_c3_acquire_dukascopy_dataset --download --max-hours 1000 --retries 3
```

If any market-open source hour fails repeatedly, stop and document the missing
coverage. Do not synthesize candles or weaken validation.
