# ST-C3 Canonical Provider Decision

Date: 2026-07-30

## Decision

**QUALIFIED**

## Selected Canonical Provider

**Dukascopy**

## Decision Scope

This is a provider qualification decision only.

It does not:

- approve a dataset
- update the dataset manifest to approved
- approve the dataset contract
- unblock replay
- open A3
- authorize statistical validation
- authorize demo/live trading

## Rationale

Dukascopy is selected because:

- public documentation advertises historical data export from tick-by-tick
  through monthly timeframes
- public historical-data documentation exists for historical bars and ticks
- deterministic hourly `.bi5` tick URLs are available for automated
  acquisition
- limited repository verification succeeded for both required symbols
- sampled tick data reconstructed complete M1 bars with zero minute gaps
- sampled ticks were monotonic
- sampled reconstructed OHLC values were valid
- M3 can be deterministically derived from complete M1/tick data

## Rejected Providers

HistData:

Rejected because the acquired and constructed candidate failed the unchanged
ST-C3 integrity validator with missing timestamps in every required file.

MT5 Export:

Rejected because the current candidate is fragmented, M15 coverage is
incomplete, M3 is unusable, and exact-candle recovery failed.

Existing Repository Dataset:

Rejected because legacy files are not governed by the ST-C3 manifest and do
not satisfy the required scope.

## Conditions Before Dataset Acquisition

Before full acquisition begins:

- owner must approve the acquisition plan
- storage/runtime expectations must be accepted
- the acquisition script must construct candidate files only
- validation gates must remain unchanged
- replay must remain blocked

## Final Provider Decision

Provider qualification result: **QUALIFIED**

Selected canonical provider for the next sprint: **Dukascopy**

Recommended next step: proceed to Dataset Acquisition Sprint.
