# Changelog

## 2026-07-29

- Added ST-C3 historical data integrity and verified recovery tooling.
- Added candle-level checks for missing timestamps, duplicates, ordering,
  OHLC geometry, volume, optional session/news fields, coverage, and hashes.
- Added guarded MT5 recovery attempts that only merge exact source-returned
  candles and never fabricate or interpolate OHLC.
- Documented current ST-C3 data blocker in generated reports under
  `reports/validation/st_c3/data_integrity/`.

## 2026-07-30

- Added the ST-C3 dataset contract as a governed artifact at
  `contracts/DATASET_CONTRACT.yaml`.
- Added a dataset-source audit and blocked candidate release notes for the
  canonical dataset sprint.
- Added `tools.st_c3_dataset_contract` to verify the contract is honest about
  blocked/approved state and to keep replay prohibited while integrity fails.
- Added strict `--require-approved` mode for dataset release gates.
- Added `DATASET_APPROVAL_SPRINT_REPORT.md` for the current blocked sprint
  handoff.
- Wired the dataset-contract guardrail into CI.
