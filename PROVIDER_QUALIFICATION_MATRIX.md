# ST-C3 Provider Qualification Matrix

Status: **COMPLETE**

Date: 2026-07-30

Scoring:

- `PASS`: documented and/or verified evidence satisfies criterion for
  provider qualification
- `FAIL`: evidence shows criterion is not satisfied
- `BLOCKED`: access or evidence is insufficient for qualification
- `PARTIAL`: usable only with additional constraints or after full
  acquisition validation

## Matrix

| Provider | Coverage | UTC Compatibility | DST Consistency | H4 Accuracy | M15 Accuracy | M3 Availability | Reproducibility | Automation | Licensing / Access | Integrity Evidence | Result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Dukascopy | PASS | PASS | PASS | PARTIAL | PARTIAL | PARTIAL | PASS | PASS | PARTIAL | PASS on limited sample | **QUALIFIED** |
| HistData | PASS | PARTIAL | PASS after EST-no-DST conversion | FAIL | FAIL | FAIL | PASS | PASS | PARTIAL | FAIL on constructed candidate | **NOT QUALIFIED** |
| MT5 Export | FAIL | PASS after export normalization | PARTIAL | FAIL | FAIL | FAIL | PARTIAL | PARTIAL | Broker/account dependent | FAIL on current candidate | **NOT QUALIFIED** |
| Existing Repository Dataset | FAIL | MIXED | MIXED | FAIL | FAIL | FAIL | PARTIAL | N/A | Repository-local only | Not governed for ST-C3 | **NOT QUALIFIED** |
| TrueFX | PASS by public docs | PASS by docs / requires verification | BLOCKED | PARTIAL | PARTIAL | PARTIAL | PARTIAL | PARTIAL | Login/registration required | Not verified in repo | Backup candidate |
| OANDA v20 | BLOCKED | PASS by API design | BLOCKED | PARTIAL | PARTIAL | PARTIAL | PASS if account/API available | PASS | Account/token required | Not verified in repo | Backup candidate |
| Paid institutional vendor | PASS expected | PASS expected | PASS expected | PASS expected | PASS expected | PASS expected | PASS expected | Vendor-specific | Paid contract required | Not verified in repo | Escalation path |

## Evidence Notes

### Dukascopy

Public evidence:

- Dukascopy Historical Data Export advertises CSV export in timeframes from
  tick-by-tick to monthly.
- Dukascopy historical data docs cover historical bars, ticks, feed history,
  and historical data service APIs.
- Public datafeed hourly `.bi5` tick URLs are deterministic by symbol, UTC
  year, zero-indexed month, day, and hour.

Repository verification:

`python -m tools.st_c3_verify_dukascopy_provider`

Result: `PASS`

Verified samples:

- `EURUSD` 2024-01-02 00:00 UTC: 1,432 ticks, 60 minute bars, 0 minute gaps
- `EURUSD` 2024-01-02 01:00 UTC: 2,570 ticks, 60 minute bars, 0 minute gaps
- `GBPUSD` 2024-01-02 00:00 UTC: 1,789 ticks, 60 minute bars, 0 minute gaps
- `GBPUSD` 2024-01-02 01:00 UTC: 4,163 ticks, 60 minute bars, 0 minute gaps

All samples had monotonic tick timestamps and valid OHLC reconstruction.

Qualification caveat:

Dukascopy is qualified for the Dataset Acquisition Sprint, not for dataset
approval. Full 2018-2024 acquisition must still pass the unchanged ST-C3
validator.

### HistData

Public evidence:

- HistData provides free M1 forex files.
- HistData states timestamps are Eastern Standard Time without daylight
  saving adjustment.

Repository evidence:

- HistData raw source files were downloaded for EURUSD/GBPUSD 2017-2024.
- Candidate H4/M15/M3 files were constructed.
- Existing validator rejected the candidate with missing timestamps in every
  required file.

Result: not qualified under the current ST-C3 no-missing-candles contract.

### MT5 Export

Repository evidence:

- Current MT5 candidate was fragmented.
- M15 coverage began in 2022 rather than 2018.
- M3 files were one-row 2025 stubs.
- H4/M15 gaps remained.
- MT5 recovery did not return exact missing candles.

Result: not qualified.

### Existing Repository Dataset

Repository evidence:

- Legacy `data/*.csv` files are outside the governed ST-C3 manifest.
- Scope, timezone, timeframes, and hashes are not sufficient for ST-C3
  approval.

Result: not qualified.

## Qualification Result

Selected provider: **Dukascopy**

Decision: **QUALIFIED**

Dukascopy is the only evaluated provider with both public historical-data
support and a passing repository verification sample for the required
symbols.

Replay remains blocked until full dataset acquisition, validation, approval,
manifest generation, and contract approval are complete.

## Source References

- Dukascopy Historical Data Export: https://www.dukascopy.com/swiss/english/marketwatch/historical/
- Dukascopy Historical Data docs: https://www.dukascopy.com/wiki/en/development/strategy-api/historical-data/
- Dukascopy Historical Data Service docs: https://www.dukascopy.com/wiki/en/development/strategy-api/historical-data/historical-data-service/
- HistData specification: https://www.histdata.com/f-a-q/data-files-detailed-specification/
- HistData FAQ: https://www.histdata.com/f-a-q/
- TrueFX historical downloads: https://www.truefx.com/truefx-historical-downloads-2/
- OANDA candles API: https://developer.oanda.com/rest-live-v20/instrument-df/
