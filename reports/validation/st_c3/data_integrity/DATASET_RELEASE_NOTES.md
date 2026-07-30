# ST-C3 Dataset Release Notes

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
