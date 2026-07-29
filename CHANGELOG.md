# Changelog

## 2026-07-29

- Added ST-C3 historical data integrity and verified recovery tooling.
- Added candle-level checks for missing timestamps, duplicates, ordering,
  OHLC geometry, volume, optional session/news fields, coverage, and hashes.
- Added guarded MT5 recovery attempts that only merge exact source-returned
  candles and never fabricate or interpolate OHLC.
- Documented current ST-C3 data blocker in generated reports under
  `reports/validation/st_c3/data_integrity/`.
