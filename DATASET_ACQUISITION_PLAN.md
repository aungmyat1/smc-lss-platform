# ST-C3 Dataset Acquisition Plan

Status: **READY FOR OWNER APPROVAL**

Date: 2026-07-30

Provider: **Dukascopy**

## Objective

Acquire the full canonical ST-C3 Dataset v1.0 candidate from Dukascopy and
submit it to the unchanged dataset validation and approval gates.

Replay remains blocked until acquisition, validation, manifest generation,
checksum generation, contract approval, and dataset approval all succeed.

## Required Scope

Symbols:

- `EURUSD`
- `GBPUSD`

Coverage:

- `2018-01-01T00:00:00Z` through `2024-12-31T23:59:59Z`

Source granularity:

- Dukascopy hourly tick files

Constructed timeframes:

- `H4`
- `M15`
- `M3`

## Download Order

1. Create raw cache root: `data/market/raw/dukascopy/st_c3/`.
2. Download `EURUSD` hourly tick files from `2017-12-31T19:00:00Z` through
   `2024-12-31T23:00:00Z` to ensure aggregation coverage at the contract
   boundaries.
3. Download `GBPUSD` hourly tick files for the same UTC range.
4. Store raw `.bi5` files by symbol/year/month/day/hour.
5. Record every attempted URL, byte count, checksum, and failure.

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

`Dataset_v1.0`

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
