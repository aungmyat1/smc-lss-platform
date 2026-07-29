# ST-C3 Dataset Release Notes

## Dataset_v0.1_blocked_candidate

Release status: **BLOCKED / NOT APPROVED**

Date: 2026-07-30

## Coverage

Required:

- Symbols: `EURUSD`, `GBPUSD`
- Timeframes: `H4`, `M15`, `M3`
- Date range: `2018-01-01` through `2024-12-31`
- Timezone: UTC

Current candidate:

- H4 files are present but contain market-open gaps.
- M15 files are present but start in 2022, not 2018.
- M3 files are one-row 2025 stubs, not 2018-2024 datasets.

## Integrity Status

FAIL.

See:

- `DATA_INTEGRITY_REPORT.md`
- `VALIDATION_SUMMARY.md`
- `RECOVERY_LOG.md`
- `UPDATED_MANIFEST.json`

## Recovery Status

Automatic MT5 recovery was attempted for the first 10 detected gaps.
No exact matching candles were returned by the approved source. No rows were
fabricated, interpolated, or manually edited.

## Approval Status

Not approved.

Replay remains blocked. A3 remains closed. Demo/live remain blocked.

## Next Version Requirement

`Dataset_v1.0` may be released only after the owner supplies complete
canonical EURUSD/GBPUSD H4/M15/M3 data for 2018-2024 and all integrity,
manifest, and contract checks pass.
