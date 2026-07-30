# ST-C3 Market Data Provider Evaluation

Status: **BLOCKED / SOURCE REJECTED AFTER VALIDATION**

Evaluation date: 2026-07-30

## Required Dataset Scope

- Strategy: ST-C3 v1.0.7
- Symbols: `EURUSD`, `GBPUSD`
- Timeframes: `H4`, `M15`, `M3`
- Coverage: `2018-01-01` through `2024-12-31`
- Target timezone: UTC
- Approval rule: zero missing market-open candles, zero duplicates, valid
  OHLCV, reproducible hashes, approved manifest, approved contract

## Evaluated Providers

| Provider | Coverage | Timezone | H4/M15/M3 Support | Automation | Licensing / Access | Result |
|---|---|---|---|---|---|---|
| Local MetaTrader 5 terminal export | Fragmented in current environment | UTC-normalized by export tool | Native H4/M15, M3 unreliable | Existing tool | Broker-terminal dependent | **Rejected**: M15 starts in 2022, M3 one-row 2025 stubs, H4 gaps |
| HistData.com Generic ASCII M1 | 2017-2024 files downloaded for EURUSD/GBPUSD | EST without daylight-saving adjustment; converted to UTC in tooling | Derived from M1 | Implemented in `tools.st_c3_acquire_histdata_dataset` | Free download, owner license review still required before approval | **Rejected after validation**: source gaps/incomplete aggregation windows leave missing H4/M15/M3 candles |
| Dukascopy Historical Data Export / JForex historical data | Long-running FX history; tick-to-monthly exports are advertised | Export tool/API supports historical bars/ticks | Candidate for direct or derived bars | Requires new adapter or JForex/export workflow | Free export advertised; owner license review required | **Next recommended source** |
| TrueFX historical downloads | Tick-by-tick historical FX data advertised | Provider describes institutional tick data; conversion required | Derived from ticks | Requires account/login and new adapter | Registration/access required | Backup source after Dukascopy |
| OANDA v20 candles API | Account/API dependent | API candlestick endpoint | Granularity list supports many bars, but access and history depth must be verified | Requires OANDA account/API token | Account required | Backup source if provider can export full 2018-2024 bars |
| TickData.com / institutional vendors | Commercial institutional intraday FX history | Vendor-defined | Likely derivable | Vendor delivery/API | Paid commercial license | Best fallback if free sources fail strict continuity |

## Selected Candidate Source

HistData.com Generic ASCII M1 was selected for the first automated candidate
attempt because it offers free downloadable forex M1 data for the required
symbols and because H4, M15, and M3 can be deterministically derived from M1
without changing ST-C3 rules.

Provider documentation states that HistData CSV timestamps are Eastern
Standard Time without daylight-saving adjustment, so the acquisition tool
converts source timestamps to UTC by adding five hours.

## Validation Outcome

The HistData acquisition and construction attempt completed, but the candidate
failed the existing ST-C3 validator.

First blockers:

- `EURUSD_H4.csv`: first missing candle `2018-01-02T04:00:00Z`
- `EURUSD_M15.csv`: first missing candle `2018-01-02T05:00:00Z`
- `EURUSD_M3.csv`: first missing candle `2018-01-02T05:06:00Z`
- `GBPUSD_H4.csv`: first missing candle `2018-01-02T20:00:00Z`
- `GBPUSD_M15.csv`: first missing candle `2018-01-02T02:30:00Z`
- `GBPUSD_M3.csv`: first missing candle `2018-01-02T02:33:00Z`

The validator reported:

- `EURUSD_H4.csv`: 2,971 missing timestamps
- `EURUSD_M15.csv`: 8,958 missing timestamps
- `EURUSD_M3.csv`: 25,589 missing timestamps
- `GBPUSD_H4.csv`: 2,737 missing timestamps
- `GBPUSD_M15.csv`: 7,974 missing timestamps
- `GBPUSD_M3.csv`: 24,289 missing timestamps

No candles were fabricated, interpolated, forward-filled, or manually edited.

## Recommendation

Reject HistData.com as the canonical ST-C3 Dataset v1.0 source under the
current no-missing-candles validation contract.

Next recommended source: **Dukascopy Historical Data Export / JForex
historical data**.

Reason:

- It advertises historical data export from tick-by-tick through monthly
  timeframes.
- It has public documentation for historical bars and ticks.
- It is a better next candidate for obtaining dense source data before
  resorting to paid institutional vendors.

If Dukascopy also fails the existing validator, the next practical step is a
paid institutional data source or an owner-approved broker/export that can
provide complete bars matching the repository's strict continuity contract.

## Source References

- HistData data file specification: https://www.histdata.com/f-a-q/data-files-detailed-specification/
- HistData FAQ: https://www.histdata.com/f-a-q/
- HistData free data overview: https://www.histdata.com/
- Dukascopy historical data export: https://www.dukascopy.com/swiss/english/marketwatch/historical/
- Dukascopy historical data API docs: https://www.dukascopy.com/wiki/en/development/strategy-api/historical-data/
- TrueFX historical downloads: https://www.truefx.com/truefx-historical-downloads-2/
- OANDA v20 instruments/candles API: https://developer.oanda.com/rest-live-v20/instrument-df/
