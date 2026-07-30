# ST-C3 Five-Year Dataset Acquisition Plan

Status: **IN PROGRESS**

Date: 2026-07-30

Provider: **Dukascopy**

Dataset version: **Dataset_v1.0_5Y**

## Objective

Acquire the five-year canonical ST-C3 Dataset v1.0 candidate from Dukascopy and
submit it to the unchanged dataset validation and approval gates.

Replay remains blocked until acquisition, validation, manifest generation,
checksum generation, contract approval, and dataset approval all succeed.

## Required Scope

Symbols:

- `EURUSD`
- `GBPUSD`

Coverage:

- `2021-01-01T00:00:00Z` through `2025-12-31T23:59:59Z`

Source granularity:

- Dukascopy hourly tick files

Constructed timeframes:

- `H4`
- `M15`
- `M3`

## Download Order

1. Create raw cache root: `data/market/raw/dukascopy/st_c3/`.
2. Download `EURUSD` hourly tick files from `2021-01-01T00:00:00Z` through
   `2025-12-31T23:00:00Z`.
3. Download `GBPUSD` hourly tick files for the same UTC range.
4. Store raw `.bi5` files by symbol/year/month/day/hour.
5. Record every attempted URL, byte count, checksum, and failure.

Initial seven-year qualification batch was retained as provider evidence only.
The active five-year sprint starts from 2021 onward and does not download
earlier history unless explicitly requested.

Initial five-year sprint batch started on 2026-07-30:

- Range attempted: `2021-01-01T00:00:00Z` through `2021-01-06T23:00:00Z`
- Completed checkpoint range: `2021-01-04T00:00:00Z` through `2021-01-04T23:59:59Z`
- Symbols: `EURUSD`, `GBPUSD`
- Cached open-market source hours in checkpoint range: 48
- Reconstructed checkpoint candles: 1,158
- Validation status: BLOCKED, as expected for a one-day slice against the full
  five-year contract
- Status report: `reports/validation/st_c3/data_integrity/DUKASCOPY_ACQUISITION_STATUS.json`

## Checkpoint Policy

After each bounded batch, regenerate:

- `reports/validation/st_c3/data_integrity/ACQUISITION_PROGRESS.json`
- `reports/validation/st_c3/data_integrity/CHECKPOINT_MANIFEST.json`
- `reports/validation/st_c3/data_integrity/DOWNLOAD_RECOVERY_LOG.md`
- `reports/validation/st_c3/data_integrity/NORMALIZATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/AGGREGATION_REPORT.md`

## Retry Policy

- Retry transient HTTP/network failures up to 3 times.
- Use exponential backoff with deterministic delays.
- Never replace a non-empty cached file unless checksum verification fails
  and the retry is explicitly logged.
- Treat repeated empty/missing files during market-open periods as blockers.
- Do not synthesize missing hours.

## Construction Sequence

1. Parse tick records from `.bi5` files.
2. Reconstruct UTC M1 bid OHLCV bars.
3. Reject incomplete M1 minutes; do not fill them.
4. Aggregate complete M1 windows into M3, M15, and H4.
5. Write candidate CSVs with:
   - `time`
   - `open`
   - `high`
   - `low`
   - `close`
   - `volume`
   - `session`
   - `news_flag`
6. Use deterministic row ordering.
7. Keep manifest `approved: false` until validation passes and owner
   approval is recorded.

## Aggregation Validation Gate

Status: **BLOCKED_PENDING_SOURCE_SPARSE_MINUTE_DECISION**

Before continuing large-scale acquisition, run:

```powershell
python -m tools.st_c3_validate_aggregation --start 2021-01-04T00:00:00Z --end 2021-01-04T23:59:59Z
```

Latest result:

- `EURUSD` missing M1 source candles: `2021-01-04T22:45:00Z`,
  `2021-01-04T22:46:00Z`
- `GBPUSD` missing M1 source candle: `2021-01-04T22:19:00Z`
- H4/M15/M3 aggregation produced no OHLCV mismatches against available M1
  data
- Missing aggregated windows are caused by missing source M1 minutes under the
  current no-fill construction policy

Do not proceed to full five-year acquisition until the sparse-source-minute
policy is resolved without weakening governance.

## Source Integrity Investigation

Status: **BLOCKED_PENDING_DATASET_CONTRACT_REVIEW**

Run:

```powershell
python -m tools.st_c3_investigate_source_integrity
```

Latest result:

- Cached Dukascopy payloads parse successfully.
- Fresh Dukascopy downloads match cached SHA-256 hashes exactly.
- HistData M1 cross-source reference is also absent for all three probed
  minutes.
- Verdict: `DUKASCOPY_AND_REFERENCE_ABSENT` for `EURUSD 22:45`,
  `EURUSD 22:46`, and `GBPUSD 22:19` on `2021-01-04`.

Next gate:

Dataset Contract Review must decide whether ST-C3 requires candles for
market-open zero-tick minutes or only for minutes with at least one underlying
source tick. No validator or contract change is authorized in this sprint.

## Integrity Validation Sequence

Run:

```powershell
python -m tools.st_c3_data_integrity --data data/market/approved/st_c3 --write-reports
```

Required result:

`PASS`

If this fails, stop. Do not modify validator rules.

## Manifest And Checksum Generation

Only after integrity passes:

```powershell
python -m tools.st_c3_prepare_dataset_manifest --data data/market/approved/st_c3 --write
```

The generated manifest must include SHA-256 hashes for all six candidate
files.

## Contract Validation

Run:

```powershell
python -m tools.st_c3_dataset_contract --contract contracts/DATASET_CONTRACT.yaml --data data/market/approved/st_c3
```

Before final approval, strict release validation must use:

```powershell
python -m tools.st_c3_dataset_contract --contract contracts/DATASET_CONTRACT.yaml --data data/market/approved/st_c3 --require-approved
```

## Dataset Versioning

Target release:

`Dataset_v1.0_5Y`

Release contents:

- approved manifest
- file checksums
- provider metadata
- raw acquisition log
- integrity report
- validation summary
- contract approval evidence
- release notes

Once approved, the dataset is immutable. Any repair requires a new dataset
version.

## Expected Runtime

Limited sample verification took under one minute.

Full tick acquisition is expected to be materially larger than HistData M1
downloads. Public tooling references for Dukascopy tick acquisition estimate
roughly minutes per symbol-year depending on concurrency and network speed.

Planning estimate:

- download: several hours for two symbols over 2018-2024 if single-threaded
- parsing/construction: several additional hours
- validation: minutes to tens of minutes depending on file sizes

## Expected Storage

Raw tick `.bi5` files and expanded intermediate data may be significantly
larger than the 53.9 MB HistData raw M1 cache.

Planning estimate:

- raw compressed ticks: multiple GB possible
- constructed CSVs: hundreds of MB possible
- intermediate expanded ticks should be streamed, not retained

## CI Integration

CI should continue to:

- run unit tests
- validate contract honesty
- fail strict release gates when dataset approval is missing

Do not add full dataset download to CI. Full acquisition is an offline
research-infrastructure operation.

## Stop Conditions

Stop immediately if:

- Dukascopy source gaps prevent complete M1 reconstruction
- H4/M15/M3 validation fails
- duplicate timestamps appear
- OHLC validation fails
- manifest hashes mismatch
- licensing/access becomes unacceptable
- existing tests fail

## Approval Handoff

If all gates pass:

- update manifest approval fields only after owner approval
- update `contracts/DATASET_CONTRACT.yaml`
- update release notes
- set replay status to READY only through the approved governance path

Statistical validation, demo, and live trading remain locked until their own
downstream gates pass.
