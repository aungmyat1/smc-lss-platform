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
- `AGGREGATION_VALIDATION_REPORT.md`
- `SOURCE_INTEGRITY_INVESTIGATION.md`

Candidate construction and full-range validation have not run yet.

## Aggregation Validation

Status: **BLOCKED**

The first one-day checkpoint showed sparse Dukascopy source minutes in the
22:00 UTC hour:

- `EURUSD`: missing `2021-01-04T22:45:00Z` and `2021-01-04T22:46:00Z`
- `GBPUSD`: missing `2021-01-04T22:19:00Z`

No H4/M15/M3 OHLCV mismatches were found against the available M1 data. The
release remains blocked because the current no-fill construction policy cannot
produce complete candles when a source minute has no ticks.

## Source Integrity Investigation

Status: **BLOCKED**

Fresh Dukascopy re-downloads matched the cached `.bi5` file hashes exactly,
and the parser successfully decoded the affected hours. HistData M1 reference
data also lacks the exact probed minutes:

- `EURUSD` `2021-01-04T22:45:00Z`
- `EURUSD` `2021-01-04T22:46:00Z`
- `GBPUSD` `2021-01-04T22:19:00Z`

Current evidence points to sparse zero-tick historical minutes rather than a
downloader, cache, or parser defect. Dataset approval remains blocked pending
Dataset Contract Review.

## Dataset Contract Review

Status: **BLOCKED**

The current contract requires missing timestamps to block approval and only
allows weekend/fixed-holiday gaps. The observed zero-tick minutes are
market-open timestamps, so `Dataset_v1.0_5Y` cannot be approved under the
current contract.

Recommendation:

`CONTINUE_EVIDENCE_COLLECTION`

The governance change path remains available only after the statistical
evidence gate is sufficiently sampled.

## Statistical Source Integrity Evidence

Status: **BLOCKED / INSUFFICIENT SAMPLE**

The statistical evidence gate now audits the currently cached deterministic
sample days plus cached pilot evidence:

- Target sample: 100 deterministic trading days
- Deterministic sample days cached complete: 8 of 100
- Audited cached days: 11
- Missing audited M1 minutes: 216 of 31,440
- Missing minute rate: `0.006870229007633588`
- 95% confidence interval:
  `0.006015492553545249..0.007845455683058679`
- Root-cause categories: 115 `ROLLOVER_ZERO_TICK`,
  99 `OFF_SESSION_ZERO_TICK`, 2 `PRIMARY_SESSION_ZERO_TICK`
- Cross-provider anomalous-timestamp checks: 188 checked, 146 present in
  HistData M1, 42 absent in HistData M1
- Evidence-sample acquisition is blocked by repeated empty Dukascopy payloads
  for Friday `21:00 UTC` hours on `2021-04-16`, `2021-05-14`, and
  `2021-07-02`
- Focused Friday `21:00 UTC` investigation classified the repeated empty
  payloads as `DST_FRIDAY_CLOSE_PROVIDER_CALENDAR_MISMATCH`

Generated reports:

- `SOURCE_INTEGRITY_STATISTICAL_REPORT.md`
- `SOURCE_INTEGRITY_SAMPLE_ACQUISITION.md`
- `CROSS_PROVIDER_VERIFICATION_REPORT.md`
- `FRIDAY_2100_INVESTIGATION_REPORT.md`

Recommendation remains:

`CONTINUE_EVIDENCE_COLLECTION`

The release is not approved, and replay remains blocked.

## Friday 21:00 UTC Investigation

Status: **BLOCKED / CLASSIFIED**

The focused probe found that Dukascopy parses DST Friday `20:00 UTC`, winter
Friday `21:00 UTC`, and Monday DST `21:00 UTC` controls, while returning
zero-byte payloads for DST Friday `21:00 UTC` and Friday `22:00 UTC`. HistData
M1 contains rows for many of the DST Friday `21:00 UTC` reference hours.

This supports a provider/calendar-policy divergence around DST Friday close,
not a parser, decompression, or generic downloader defect. No contract,
validator, approval, replay, or historical-price change was made.
- Distribution: mostly rollover, with two observed GBPUSD pilot gaps outside
  rollover on the first deterministic sample day
- Root-cause categories: 21 `ROLLOVER_ZERO_TICK`, 2 `OFF_SESSION_ZERO_TICK`
- Missing-minute-rate 95% confidence interval:
  `0.0013591321291721624..0.003057932662333974`
- Pre-registered exit criteria now require at least 95 of 100 deterministic
  sample days plus missing-rate, confidence-interval, distribution, category,
  and contextual observation outputs

The pilot supports further evidence collection, not an immediate governance
change. Current recommendation:

`CONTINUE_EVIDENCE_COLLECTION`

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
