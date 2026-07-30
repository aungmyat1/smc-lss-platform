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

## Aggregation Verification

Aggregation validation result: `BLOCKED`

The dedicated aggregation validation gate found no OHLCV mismatches between
aggregated H4/M15/M3 candles and the available reconstructed M1 data.

Root cause evidence:

- `EURUSD` has 1,438 reconstructed M1 rows versus 1,440 expected on
  `2021-01-04`
- `EURUSD` missing source minutes: `2021-01-04T22:45:00Z`,
  `2021-01-04T22:46:00Z`
- `GBPUSD` has 1,439 reconstructed M1 rows versus 1,440 expected on
  `2021-01-04`
- `GBPUSD` missing source minute: `2021-01-04T22:19:00Z`

This points to sparse source ticks in the Dukascopy `22h_ticks.bi5` files
under the current no-fill construction policy, not an observed aggregation
math mismatch.

## Source Integrity Investigation

Source integrity investigation result: `BLOCKED`

Evidence:

- Cached Dukascopy `.bi5` files parse successfully.
- Fresh Dukascopy downloads match cached SHA-256 hashes exactly.
- The affected Dukascopy minutes contain zero ticks.
- HistData M1 reference data is also absent for all three probed minutes.

Probe verdicts:

- `EURUSD` `2021-01-04T22:45:00Z`: `DUKASCOPY_AND_REFERENCE_ABSENT`
- `EURUSD` `2021-01-04T22:46:00Z`: `DUKASCOPY_AND_REFERENCE_ABSENT`
- `GBPUSD` `2021-01-04T22:19:00Z`: `DUKASCOPY_AND_REFERENCE_ABSENT`

The evidence does not support a downloader, cache, parser, or aggregation
defect. The remaining issue is provider/contract suitability for market-open
minutes with zero source ticks.

## Dataset Contract Review

Dataset contract review result: `BLOCKED`

The active contract requires `missing_timestamps: required`, and the effective
loader policy allows only weekend and fixed-holiday gaps. The zero-tick source
minutes are market-open timestamps, so the dataset cannot be approved under
the current contract.

Review recommendation:

`OPEN_GOVERNANCE_CHANGE_REQUEST`

Available choices:

- retain strict continuity and select a source that emits complete bars
- govern a deterministic zero-tick candle policy
- qualify a different authoritative M1/bar provider

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
- Sparse zero-tick source minutes are incompatible with the current
  no-missing-candles contract unless a governance-approved bar policy or a
  more complete source is selected.
- Dataset Contract Review is required before any policy change, provider
  change, or continuation to full five-year production acquisition.
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
- `reports/validation/st_c3/data_integrity/AGGREGATION_VALIDATION_REPORT.json`
- `reports/validation/st_c3/data_integrity/AGGREGATION_VALIDATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_INVESTIGATION.json`
- `reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_INVESTIGATION.md`
- `reports/validation/st_c3/data_integrity/DATASET_CONTRACT_REVIEW.json`
- `reports/validation/st_c3/data_integrity/DATASET_CONTRACT_REVIEW.md`
- `reports/validation/st_c3/data_integrity/DATA_INTEGRITY_REPORT.md`
- `reports/validation/st_c3/data_integrity/VALIDATION_SUMMARY.md`
- `reports/validation/st_c3/data_integrity/RECOVERY_LOG.md`
- `tools/st_c3_data_integrity.py`

## Tests

Focused Dukascopy acquisition/provider/governance tests pass.

Full repository tests pass: `416 passed, 2 warnings`.

## Recommendation

OPEN_GOVERNANCE_CHANGE_REQUEST
