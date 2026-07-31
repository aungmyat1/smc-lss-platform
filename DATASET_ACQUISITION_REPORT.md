# ST-C3 Five-Year Dataset Acquisition Report

Status: **IN_PROGRESS**

Date: 2026-07-30

Provider: **Dukascopy tick datafeed**

Dataset version: **Dataset_v1.0_5Y**

## Objective

Acquire, normalize, validate, and publish a complete ST-C3 Dataset v1.0
candidate for:

- `EURUSD`, `GBPUSD`
- `H4`, `M15`, `M3`
- `2021-01-01` through `2025-12-31`
- UTC timestamps

No ST-C3 strategy logic, detection logic, replay logic, validation rules, or
approval gates were modified.

## Implemented Acquisition Tool

Added:

`tools/st_c3_acquire_dukascopy_dataset.py`

The tool:

- downloads hourly Dukascopy `.bi5` tick files into a resumable raw cache
- skips ST-C3-recognized weekend and fixed-holiday closures
- records every attempted hour, byte count, hash, and failure
- reconstructs UTC M1 bid candles from ticks
- aggregates only complete M1 windows into `H4`, `M15`, and `M3`
- writes repository-standard candidate CSV files
- can invoke the existing integrity and contract validators without modifying
  their rules
- keeps dataset approval, replay, A3, demo, and live gates locked

Raw cache path:

`data/market/raw/dukascopy/st_c3/`

Latest status report:

`reports/validation/st_c3/data_integrity/DUKASCOPY_ACQUISITION_STATUS.json`

## Initial Five-Year Sprint Download Batch

Command:

```powershell
python -m tools.st_c3_acquire_dukascopy_dataset --download --start 2021-01-04T00:00:00Z --end 2021-01-04T23:00:00Z --max-hours 48 --retries 2
```

Result: **IN_PROGRESS**

| Metric | Value |
|---|---:|
| Cached open-market hourly files in checkpoint range | 48 |
| Failed downloads | 0 |
| Corrupt cached files remaining | 0 |

The earlier 2018 sample cache remains provider evidence only. The active
canonical sprint is limited to 2021-2025.

The completed checkpoint covered both `EURUSD` and `GBPUSD` together. It did
not modify approval fields.

## Checkpoint Artifacts

The acquisition engine now regenerates:

- `reports/validation/st_c3/data_integrity/ACQUISITION_PROGRESS.json`
- `reports/validation/st_c3/data_integrity/CHECKPOINT_MANIFEST.json`
- `reports/validation/st_c3/data_integrity/DOWNLOAD_RECOVERY_LOG.md`
- `reports/validation/st_c3/data_integrity/NORMALIZATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/AGGREGATION_REPORT.md`

## Candidate Construction

Status: **CHECKPOINT_CONSTRUCTED / FULL_RANGE_INCOMPLETE**

The first checkpoint construction generated 1,158 candles across all six
candidate files for `2021-01-04`.

Construction command:

```powershell
python -m tools.st_c3_acquire_dukascopy_dataset --construct
```

The constructor emits only complete aggregation windows. It does not fabricate,
interpolate, or manually edit prices.

## Validation Status

Status: **BLOCKED**

Checkpoint validation command:

```powershell
python -m tools.st_c3_acquire_dukascopy_dataset --construct --validate --start 2021-01-04T00:00:00Z --end 2021-01-04T23:59:59Z
```

This calls the existing integrity scanner and dataset contract checker. The
validation engine remains unchanged.

Result: **BLOCKED**

Primary blocker:

`EURUSD_H4.csv` checkpoint coverage `2021-01-04T00:00:00Z` through
`2021-01-04T19:59:59Z` does not cover required `2021-01-01` through
`2025-12-31`.

Additional checkpoint risk: lower-timeframe gaps were observed in the one-day
slice, including `EURUSD_M15.csv` missing `2021-01-04T22:45:00Z` and
`GBPUSD_M15.csv` missing `2021-01-04T22:15:00Z`. These remain unresolved and
must not be filled manually.

## Aggregation Validation

Status: **BLOCKED**

Command:

```powershell
python -m tools.st_c3_validate_aggregation --start 2021-01-04T00:00:00Z --end 2021-01-04T23:59:59Z
```

Result:

- `EURUSD` M1 rows: 1,438 of 1,440 expected
- `EURUSD` missing source minutes: `2021-01-04T22:45:00Z`,
  `2021-01-04T22:46:00Z`
- `GBPUSD` M1 rows: 1,439 of 1,440 expected
- `GBPUSD` missing source minute: `2021-01-04T22:19:00Z`
- Aggregation mismatches: 0

Root cause:

The missing M3/M15/H4 windows are explained by sparse source ticks in the
Dukascopy `22h_ticks.bi5` files. The aggregation algorithm did not show an
OHLCV mismatch against the available reconstructed M1 data.

Decision required:

The current constructor emits only minutes that have source ticks. Under the
repository's no-missing-candles contract, sparse zero-tick minutes will keep
the dataset blocked unless an owner-approved, governance-compliant bar policy
is adopted or a provider supplies complete M1/bar data for those minutes.

## Source Integrity Investigation

Status: **BLOCKED**

Command:

```powershell
python -m tools.st_c3_investigate_source_integrity
```

Findings:

- Cached Dukascopy `.bi5` files parse successfully.
- Fresh Dukascopy downloads for the same hourly files match cached SHA-256
  hashes exactly.
- The missing minutes contain zero Dukascopy ticks.
- HistData M1 reference data also lacks the exact probed minutes.

Probe verdicts:

| Symbol | Timestamp | Verdict |
|---|---|---|
| `EURUSD` | `2021-01-04T22:45:00Z` | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `EURUSD` | `2021-01-04T22:46:00Z` | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `GBPUSD` | `2021-01-04T22:19:00Z` | `DUKASCOPY_AND_REFERENCE_ABSENT` |

Conclusion:

The current evidence does not indicate a parser defect, truncated cache, or
stale download. It indicates sparse zero-tick minutes in independently checked
historical data. Dataset production remains blocked pending Dataset Contract
Review.

## Dataset Contract Review

Status: **BLOCKED**

Command:

```powershell
python -m tools.st_c3_dataset_contract_review
```

Findings:

- Current policy: `strict_market_open_candle_continuity`
- Missing timestamp check: `required`
- Allowed gap policy: weekend and fixed holidays only
- Zero-tick probe count: 3
- Aggregation mismatch count: 0

Recommendation:

`CONTINUE_EVIDENCE_COLLECTION`

The earlier governance-change option is deferred until the statistical source
integrity gate is sufficiently sampled.

Available governance options:

- Retain strict contract and select a provider that supplies complete bars.
- Define a deterministic zero-tick candle policy through a governed contract
  and validator change.
- Select an authoritative M1/bar provider with documented zero-volume or
  carry-forward bar methodology.

## Statistical Source Integrity Evidence Gate

Status: **BLOCKED**

Command:

```powershell
python -m tools.st_c3_statistical_source_integrity
```

Findings:

- Target sample: 100 deterministic trading days across `2021-01-01` through
  `2025-12-31`
- Deterministic sample days cached complete: 28 of 100
- Audited cached days: 31
- Total expected audited M1 minutes: 85,920
- Total missing audited M1 minutes: 411
- Missing minute rate: `0.004783519553072626`
- Missing-minute-rate 95% confidence interval:
  `0.004343785742805563..0.0052675333602455`
- Cross-provider comparison for anomalous timestamps:
  200 checked against cached HistData M1 reference rows, with 151 reference
  timestamps present and 49 reference timestamps absent
- Evidence-sample acquisition is blocked on repeated empty Dukascopy payloads
  for Friday `21:00 UTC` hours on `2021-04-16`, `2021-05-14`, and
  `2021-07-02` for both symbols
- Focused Friday `21:00 UTC` investigation classified the repeated empty
  payloads as `DST_FRIDAY_CLOSE_PROVIDER_CALENDAR_MISMATCH`
- Exit criteria are now pre-registered: at least 95% sample completion,
  missing-minute rate, confidence interval, distributions by session/weekday/
  symbol, hour-of-day, root-cause categories, contextual missing-minute
  observations, and cross-provider verification for anomalous timestamps

Recommendation:

`CONTINUE_EVIDENCE_COLLECTION`

Conclusion:

The evidence remains insufficient for provider acceptance or rejection. The
expanded sample shows both confirmed zero-tick minutes across Dukascopy and
HistData and timestamps where HistData has an M1 row while Dukascopy has zero
ticks. The immediate execution path is to continue the deterministic sample
using the evidence-only Dukascopy DST Friday close source-hour exclusion while
preserving the ST-C3 Dataset Contract unchanged.

## Parallel Evidence Collection

Status: **IN_PROGRESS**

Command:

```powershell
python -m tools.st_c3_acquire_source_integrity_sample --max-days 4 --workers 4 --retries 3
```

Outputs:

- `reports/validation/st_c3/data_integrity/PARALLEL_EXECUTION_STATUS.json`
- `reports/validation/st_c3/data_integrity/PERFORMANCE_PROFILE.md`
- `reports/validation/st_c3/data_integrity/PERFORMANCE_PROFILE.json`

Latest parallel batch:

- Completed sample progress: 24 of 100 to 28 of 100
- Planned source tasks: 186
- Completed source tasks: 186
- Duplicate task count: 0
- Failed source tasks: 0
- Workers: 4
- Elapsed seconds: `102.5809900000022`
- Throughput: `108.79208711087463` source hours/minute
- Provider-calendar excluded source hours: 2

Sequential mode remains available by omitting `--workers` or setting
`--workers 1`.

## Cross-Provider Verification

Status: **BLOCKED / INTERIM**

Command:

```powershell
python -m tools.st_c3_cross_provider_verification
```

Output:

- `reports/validation/st_c3/data_integrity/CROSS_PROVIDER_VERIFICATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/CROSS_PROVIDER_VERIFICATION_REPORT.json`

Current interim conclusions:

- `DUKASCOPY_AND_REFERENCE_ABSENT`: 42
- `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT`: 146

The cross-provider report is evidence only. It does not replace Dukascopy data
with HistData rows and does not alter governance.

## Friday 21:00 UTC Investigation

Status: **BLOCKED / CLASSIFIED**

Command:

```powershell
python -m tools.st_c3_investigate_friday_2100
```

Output:

- `reports/validation/st_c3/data_integrity/FRIDAY_2100_INVESTIGATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/FRIDAY_2100_INVESTIGATION_REPORT.json`

Finding:

`DST_FRIDAY_CLOSE_PROVIDER_CALENDAR_MISMATCH`

Evidence:

- DST Friday `20:00 UTC` control hours parsed for both symbols.
- DST Friday `21:00 UTC` hours returned zero-byte Dukascopy payloads for both
  symbols on `2021-04-16`, `2021-04-23`, `2021-05-14`, and `2021-07-02`.
- Friday `22:00 UTC` hours also returned zero-byte payloads, consistent with
  known Friday close behavior.
- Winter Friday `21:00 UTC` controls on `2021-01-22` parsed for both symbols.
- Monday `21:00 UTC` DST controls on `2021-04-19` parsed for both symbols.
- HistData M1 often contains rows for the same DST Friday `21:00 UTC` hours,
  confirming the behavior is provider/reference-policy divergence rather than
  a universal no-data condition.

Conclusion:

The repeated source-hour failures are reproducible and localized. The evidence
supports a provider/calendar mismatch during DST Friday close handling, not a
decompression, parser, or generic downloader defect. No calendar, contract, or
validator change has been made.

## Session Calendar Qualification

Status: **BLOCKED / IN PROGRESS**

Command:

```powershell
python -m tools.st_c3_session_calendar_qualification
```

Output:

- `reports/validation/st_c3/data_integrity/SESSION_CALENDAR_QUALIFICATION_REPORT.md`
- `reports/validation/st_c3/data_integrity/SESSION_CALENDAR_QUALIFICATION_REPORT.json`

Research question:

Which provider's trading calendar matches the assumptions encoded in the
ST-C3 Dataset Contract?

Interim findings:

- ST-C3 currently encodes a fixed UTC calendar with Friday close at
  `22:00 UTC` and no DST adjustment.
- Dukascopy official DST notices and live probes indicate Friday close/opening
  behavior shifts to `21:00 UTC` during US DST.
- HistData documents EST timestamps without daylight-saving adjustments, and
  cached reference rows are present for many DST Friday `21:00 UTC` periods.
- HistData bar-generation methodology remains unqualified for canonical use.

Decision layer:

Provider selection must evaluate both data completeness and session-calendar
compatibility. No provider is accepted or rejected by this report.

## Approval Status

Dataset approval: **NOT_APPROVED**

Manifest status: **NOT_APPROVED**

Contract status: **BLOCKED**

Replay status: **BLOCKED**

A3/statistics/demo/live: **BLOCKED**

## Next Action

Pause large-scale production acquisition. Acquire only the deterministic
100-day evidence sample, then rerun source-integrity statistics before any
provider rejection or governance change request.

Recommended next command:

```powershell
python -m tools.st_c3_acquire_source_integrity_sample --max-days 1 --retries 3
```

Before running larger batches, review the evidence-sample market calendar in a
separate governed decision. Do not synthesize candles, weaken validation,
approve data, or unlock replay.
