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
- Corrected the ST-C3 candidate manifest to `approved: false` until all
  integrity, manifest, and contract gates pass.
- Updated the MT5 dataset downloader to build unapproved candidate datasets
  while refusing to replace an already approved immutable dataset.
- Added dataset-governance regression tests for manifest/contract approval
  mismatch handling and candidate download behavior.
- Added the ST-C3 Walk-Forward Validation Engine prompt, blocked until
  dataset approval, replay acceptance, A3 opening, and A3 backtest acceptance.
- Added the ST-C3 Monte-Carlo Robustness Engine prompt, blocked until
  walk-forward acceptance and owner-approved simulation bounds/seeds exist.
- Added the ST-C3 Market Data Acquisition Engine prompt and updated the
  orchestrator stage order to separate acquisition, construction,
  validation, and approval before replay.
- Implemented `tools.st_c3_acquire_histdata_dataset` for HistData M1
  candidate acquisition, UTC normalization, and deterministic H4/M15/M3
  construction.
- Downloaded and staged HistData EURUSD/GBPUSD M1 source ZIPs for 2017-2024,
  constructed six ST-C3 candidate CSVs, and rejected the candidate after the
  unchanged integrity validator reported missing timestamps.
- Added market-data provider evaluation, acquisition, and approval reports
  documenting HistData rejection and Dukascopy as the next recommended source.
- Added Dukascopy provider verification tooling, limited live sample evidence,
  contract audit, timeframe report, qualification matrix, canonical provider
  decision, acquisition plan, and risk review for the provider qualification
  sprint.
- Added source-integrity evidence sample progress reporting, statistical
  observation enrichment, cached HistData anomalous-timestamp comparison, and
  `CROSS_PROVIDER_VERIFICATION_REPORT.md` for the Dukascopy evidence sprint.
- Advanced deterministic source-integrity evidence from 1 to 8 completed
  sample days; kept recommendation at `CONTINUE_EVIDENCE_COLLECTION` after
  repeated Friday `21:00 UTC` empty Dukascopy payloads blocked larger batches.
