# ST-C3 Five-Year Canonical Dataset Sprint Executive Report

Date: 2026-07-30

## Repository Status

The repository remains in strict governed research mode. ST-C3 strategy logic,
detection logic, replay logic, statistical calculations, validation rules, and
approval gates were not modified.

Existing governance remains active:

- Dataset approval: `NOT_APPROVED`
- Replay: `BLOCKED`
- A3/statistical validation: `CLOSED`
- Demo/live: `BLOCKED`

## Dataset Status

Active dataset target:

- Version: `Dataset_v1.0_5Y`
- Provider: Dukascopy tick datafeed
- Coverage: `2021-01-01T00:00:00Z` through `2025-12-31T23:59:59Z`
- Symbols: `EURUSD`, `GBPUSD`
- Timeframes: `H4`, `M15`, `M3`

The manifest and dataset contract now point at the five-year scope but remain
unapproved.

## Acquisition Progress

The Dukascopy acquisition engine supports resumable hourly `.bi5` downloads,
cache reuse, cached-payload parse verification, retry handling, corruption
detection, deterministic M1 reconstruction, and H4/M15/M3 aggregation from
complete windows only.

Completed checkpoint:

- Range: `2021-01-04T00:00:00Z` through `2021-01-04T23:59:59Z`
- Cached open-market source hours: 48
- Failed downloads: 0
- Corrupt cached files remaining: 0

## Validation Status

Checkpoint construction generated 1,158 candles across six candidate files.

Validation result: `BLOCKED`

Primary blocker:

`EURUSD_H4.csv` checkpoint coverage `2021-01-04T00:00:00Z` through
`2021-01-04T19:59:59Z` does not cover the required five-year contract window.

Additional checkpoint risk:

The one-day slice exposed missing lower-timeframe aggregation windows,
including `EURUSD_M15.csv` missing `2021-01-04T22:45:00Z` and
`GBPUSD_M15.csv` missing `2021-01-04T22:15:00Z`. These must be investigated
through source coverage and aggregation evidence only. No interpolation or
manual price editing is allowed.

## Dataset Approval

Dataset approval remains `NOT_APPROVED`.

The dataset contract remains `BLOCKED`.

No manifest approval fields were set.

## Replay Readiness

Replay remains `BLOCKED`.

`REPLAY_READY_REPORT.md` was not generated because dataset approval has not
passed. Statistical validation remains locked.

## Remaining Risks

- Full 2021-2025 Dukascopy acquisition is incomplete.
- Checkpoint validation correctly fails full-range coverage.
- Missing lower-timeframe checkpoint windows must be explained before final
  approval can be considered.
- Full five-year construction may require substantial runtime and storage.

## Files Changed

- `tools/st_c3_acquire_dukascopy_dataset.py`
- `tests/test_st_c3_dukascopy_acquisition.py`
- `contracts/DATASET_CONTRACT.yaml`
- `data/market/approved/st_c3/DATASET_MANIFEST_ST_C3.yaml`
- `DATASET_ACQUISITION_PLAN.md`
- `DATASET_ACQUISITION_REPORT.md`
- `reports/validation/st_c3/data_integrity/DATASET_RELEASE_NOTES.md`
- `reports/validation/st_c3/data_integrity/DUKASCOPY_ACQUISITION_STATUS.json`
- `reports/validation/st_c3/data_integrity/ACQUISITION_PROGRESS.json`
- `reports/validation/st_c3/data_integrity/CHECKPOINT_MANIFEST.json`
- `reports/validation/st_c3/data_integrity/DOWNLOAD_RECOVERY_LOG.md`
- `reports/validation/st_c3/data_integrity/NORMALIZATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/AGGREGATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/DATA_INTEGRITY_REPORT.md`
- `reports/validation/st_c3/data_integrity/VALIDATION_SUMMARY.md`
- `reports/validation/st_c3/data_integrity/RECOVERY_LOG.md`
- `tools/st_c3_data_integrity.py`

## Tests

Focused Dukascopy acquisition/provider/governance tests pass.

Full repository tests pass: `416 passed, 2 warnings`.

## Recommendation

CONTINUE_DATA_ACQUISITION
