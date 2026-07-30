# ST-C3 Dataset Release Notes

## Dataset_v1.0_5Y_candidate_dukascopy

Release status: **IN PROGRESS / NOT APPROVED**

Date: 2026-07-30

Source: Dukascopy hourly tick `.bi5` files for 2021-2025, reconstructed into
UTC M1 bid candles, then derived into H4/M15/M3 using complete M1 windows only.

## Dukascopy Acquisition Status

Five-year bounded raw-tick acquisition has started.

Latest batch:

- Checkpoint range: `2021-01-04T00:00:00Z` through `2021-01-04T23:59:59Z`
- Symbols: `EURUSD`, `GBPUSD`
- Cached open-market source hours in checkpoint range: 48
- Reconstructed checkpoint candles: 1,158
- Failed downloads: 0
- Validation status: BLOCKED

Status report:

- `DUKASCOPY_ACQUISITION_STATUS.json`
- `ACQUISITION_PROGRESS.json`
- `CHECKPOINT_MANIFEST.json`
- `DOWNLOAD_RECOVERY_LOG.md`
- `NORMALIZATION_REPORT.md`
- `AGGREGATION_REPORT.md`

Candidate construction and full-range validation have not run yet.

## Dukascopy Approval Status

Not approved.

The manifest remains `approved: false` for `Dataset_v1.0_5Y`. Replay remains
blocked. A3 remains closed. Demo/live remain blocked.

The dataset may become immutable only after complete acquisition, construction,
strict integrity validation, manifest/checksum regeneration, contract
validation, and explicit owner approval.

## Dataset_v1.0_candidate_histdata

Release status: **BLOCKED / NOT APPROVED**

Date: 2026-07-30

Source: HistData.com Generic ASCII M1, converted from EST without daylight
saving adjustment to UTC, then derived into H4/M15/M3.

## Coverage

Required:

- Symbols: `EURUSD`, `GBPUSD`
- Timeframes: `H4`, `M15`, `M3`
- Date range: `2018-01-01` through `2024-12-31`
- Timezone: UTC

Current candidate:

- All required files are present.
- All required files are derived from the same HistData M1 source family.
- All required files still contain missing timestamps under the existing
  ST-C3 continuity validator.

## Integrity Status

FAIL.

See:

- `DATA_INTEGRITY_REPORT.md`
- `VALIDATION_SUMMARY.md`
- `RECOVERY_LOG.md`
- `UPDATED_MANIFEST.json`

## Recovery Status

HistData candidate acquisition and construction completed. Validation failed
because source gaps/incomplete aggregation windows leave missing H4/M15/M3
candles. No rows were fabricated, interpolated, or manually edited.

## Approval Status

Not approved.

The candidate manifest is intentionally marked `approved: false` until all
file-integrity, manifest, and contract gates pass.

Replay remains blocked. A3 remains closed. Demo/live remain blocked.

## Next Version Requirement

`Dataset_v1.0` may be released only after a source provides complete
canonical EURUSD/GBPUSD H4/M15/M3 data for 2018-2024 and all integrity,
manifest, and contract checks pass.
