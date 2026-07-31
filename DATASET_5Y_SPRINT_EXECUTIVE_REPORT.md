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

`CONTINUE_EVIDENCE_COLLECTION`

The governance-change path is deferred until the statistical evidence gate is
sufficiently sampled.

Available choices:

- retain strict continuity and select a source that emits complete bars
- govern a deterministic zero-tick candle policy
- qualify a different authoritative M1/bar provider

## Statistical Evidence Gate

Statistical source integrity result: `BLOCKED`

The first statistical audit was run in cache-only mode against the current
pilot cache.

Evidence:

- Target sample: 100 deterministic trading days across 2021-2025
- Deterministic target sample days cached complete: 30 of 100
- Audited cached days: 33
- Total expected audited M1 minutes: 91,680
- Total missing audited M1 minutes: 468
- Missing minute rate: `0.005104712041884817`
- Missing-minute-rate 95% confidence interval:
  `0.004663689753505748..0.0055872055391268036`
- Cross-provider anomalous-timestamp verification: 200 observations checked,
  151 present in HistData M1 and 49 absent in HistData M1
- Evidence acquisition blocked on repeated empty Dukascopy payloads for Friday
  `21:00 UTC` hours on `2021-04-16`, `2021-05-14`, and `2021-07-02`
- Focused Friday `21:00 UTC` investigation classified the repeated failures as
  `DST_FRIDAY_CLOSE_PROVIDER_CALENDAR_MISMATCH`
- Pre-registered exit criteria: at least 95 of 100 deterministic sample days,
  missing-minute rate, confidence interval, distributions by session/weekday/
  symbol/hour, root-cause categories, contextual missing-minute observations,
  and cross-provider verification for anomalous timestamps

The evidence remains statistically insufficient because only 30 of 100
deterministic sample days are complete. The active recommendation is evidence
collection, now accelerated with bounded parallel acquisition and the
evidence-only Dukascopy DST Friday close source-hour exclusion.

## Performance Improvements

Execution has been reordered to profile first, then parallelize only measured
bottlenecks. Source-integrity sample acquisition now supports configurable
bounded parallelism for download/cache operations while preserving deterministic
sample ordering, idempotent cache reuse, and resumable checkpoints.

Latest sequential baseline:

- Command: `python -m tools.st_c3_acquire_source_integrity_sample --max-days 1 --workers 1 --retries 3`
- Progress advanced from 28 of 100 to 29 of 100 deterministic sample days
- Attempted source hours: 48
- Failed source hours: 0
- Elapsed seconds: `111.35310690000188`
- Acquisition seconds: `99.99727680000069`
- `.bi5` decompression/parse seconds: `9.571653900005913`
- M1 reconstruction seconds: `1.7178865000096266`
- Throughput: `25.863669907174828` source hours/minute
- Top measured bottlenecks: download/cache, then `.bi5` decompression/parse

Latest bounded 2-worker download/cache batch:

- Command: `python -m tools.st_c3_acquire_source_integrity_sample --max-days 1 --workers 2 --retries 3`
- Progress advanced from 29 of 100 to 30 of 100 deterministic sample days
- Planned tasks: 48
- Completed tasks: 48
- Duplicate task count: 0
- Failed tasks: 0
- Task order matched deterministic plan: true
- Worker distribution: 24, 24 tasks
- Elapsed seconds: `57.74290550000296`
- Throughput: `49.87625709274107` source hours/minute
- Parallel scope: download/cache only; reconstruction, validation,
  statistical reporting, and cross-provider reporting remain sequential

Latest parallel batch:

- Command: `python -m tools.st_c3_acquire_source_integrity_sample --max-days 4 --workers 4 --retries 3`
- Progress advanced from 24 of 100 to 28 of 100 deterministic sample days
- Planned tasks: 186
- Completed tasks: 186
- Duplicate task count: 0
- Failed tasks: 0
- Worker distribution: 47, 47, 46, 46 tasks
- Elapsed seconds: `102.5809900000022`
- Throughput: `108.79208711087463` source hours/minute
- Parallel efficiency proxy: `0.9382022977648651`
- Parallel scope: download/cache only; reconstruction, validation, statistical
  reporting, and cross-provider reporting remain sequential

Generated:

- `reports/validation/st_c3/data_integrity/PARALLEL_EXECUTION_STATUS.json`
- `reports/validation/st_c3/data_integrity/PERFORMANCE_PROFILE.md`
- `reports/validation/st_c3/data_integrity/PERFORMANCE_PROFILE.json`

Sequential mode remains the compatibility path through `--workers 1`.

## Pipeline Split

Provider Qualification and Canonical Dataset Construction are now documented as
separate workflows in `PROVIDER_QUALIFICATION_PIPELINE.md`.

- Pipeline A, Provider Qualification: active.
- Pipeline B, Canonical Dataset Construction: disabled until provider
  acceptance.
- Allowed provider outcomes remain limited to `ACCEPT_DUKASCOPY`,
  `OPEN_DATA_GOVERNANCE_REVIEW`, and `REJECT_DUKASCOPY`.
- Research dashboard work and aggressive worker scaling are postponed.

## Cross-Provider Findings

Cross-provider verification result: `BLOCKED / INTERIM`

Generated:

- `reports/validation/st_c3/data_integrity/CROSS_PROVIDER_VERIFICATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/CROSS_PROVIDER_VERIFICATION_REPORT.json`

Current interim findings:

- `DUKASCOPY_AND_REFERENCE_ABSENT`: 42
- `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT`: 146

This evidence is not a provider decision. It confirms the anomaly set is mixed:
some zero-tick Dukascopy minutes are also absent in the reference source, while
many are present in HistData M1. No reference rows were merged into Dukascopy
data.

## Friday 21:00 UTC Findings

Friday `21:00 UTC` source-integrity investigation result: `BLOCKED / CLASSIFIED`

Generated:

- `reports/validation/st_c3/data_integrity/FRIDAY_2100_INVESTIGATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/FRIDAY_2100_INVESTIGATION_REPORT.json`

Classification:

`DST_FRIDAY_CLOSE_PROVIDER_CALENDAR_MISMATCH`

Evidence summary:

- DST Friday `20:00 UTC` payloads parse for both symbols.
- DST Friday `21:00 UTC` payloads return zero bytes for both symbols.
- Friday `22:00 UTC` payloads return zero bytes, consistent with Friday close.
- Winter Friday `21:00 UTC` controls parse for both symbols.
- Monday DST `21:00 UTC` controls parse for both symbols.
- HistData M1 has rows for many DST Friday `21:00 UTC` reference hours where
  Dukascopy returns zero bytes.

The evidence narrows the repeated sample-acquisition blocker to provider
calendar/policy behavior around DST Friday close. This is not a provider
decision and does not change the ST-C3 calendar, contract, validator, approval
state, or replay state.

## Session Calendar Qualification

Session calendar qualification result: `BLOCKED / IN PROGRESS`

Generated:

- `reports/validation/st_c3/data_integrity/SESSION_CALENDAR_QUALIFICATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/SESSION_CALENDAR_QUALIFICATION_REPORT.json`

Interim comparison:

- ST-C3 Dataset Contract: fixed UTC calendar, Friday close at `22:00 UTC`,
  no DST adjustment encoded.
- Dukascopy: official DST notices and live probes support a `21:00 UTC`
  Friday close/opening behavior during US DST.
- HistData: official FAQ documents EST timestamps without daylight-saving
  adjustments; cached M1 reference rows are present for many DST Friday
  `21:00 UTC` periods, but bar-generation policy remains unqualified.

Provider selection now has two independent decision dimensions:

- data completeness
- session-calendar compatibility with ST-C3 replay assumptions

No provider is accepted or rejected by this report.

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
- Statistical evidence remains insufficient. The deterministic 100-day sample
  must be acquired and audited before rejecting the provider or opening a
  governance change request.
- Repeated Friday `21:00 UTC` empty payloads are now classified as
  `DST_FRIDAY_CLOSE_PROVIDER_CALENDAR_MISMATCH`; a governed calendar/source
  policy review is required before larger evidence batches continue.
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
- `reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_STATISTICAL_REPORT.json`
- `reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_STATISTICAL_REPORT.md`
- `reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_SAMPLE_ACQUISITION.json`
- `reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_SAMPLE_ACQUISITION.md`
- `reports/validation/st_c3/data_integrity/CROSS_PROVIDER_VERIFICATION_REPORT.json`
- `reports/validation/st_c3/data_integrity/CROSS_PROVIDER_VERIFICATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/FRIDAY_2100_INVESTIGATION_REPORT.json`
- `reports/validation/st_c3/data_integrity/FRIDAY_2100_INVESTIGATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/SESSION_CALENDAR_QUALIFICATION_REPORT.json`
- `reports/validation/st_c3/data_integrity/SESSION_CALENDAR_QUALIFICATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/PARALLEL_EXECUTION_STATUS.json`
- `reports/validation/st_c3/data_integrity/PERFORMANCE_PROFILE.json`
- `reports/validation/st_c3/data_integrity/PERFORMANCE_PROFILE.md`
- `tools/st_c3_acquire_source_integrity_sample.py`
- `tools/st_c3_cross_provider_verification.py`
- `tools/st_c3_investigate_friday_2100.py`
- `tools/st_c3_session_calendar_qualification.py`
- `tests/test_st_c3_source_integrity_sample_acquisition.py`
- `tests/test_st_c3_cross_provider_verification.py`
- `tests/test_st_c3_friday_2100_investigation.py`
- `tests/test_st_c3_session_calendar_qualification.py`
- `reports/validation/st_c3/data_integrity/DATA_INTEGRITY_REPORT.md`
- `reports/validation/st_c3/data_integrity/VALIDATION_SUMMARY.md`
- `reports/validation/st_c3/data_integrity/RECOVERY_LOG.md`
- `tools/st_c3_data_integrity.py`

## Tests

Focused Dukascopy acquisition/provider/governance tests pass.

Full repository tests pass: `416 passed, 2 warnings`.

## Recommendation

CONTINUE_EVIDENCE_COLLECTION
