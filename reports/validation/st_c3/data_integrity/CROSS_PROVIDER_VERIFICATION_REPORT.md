# ST-C3 Cross-Provider Verification Report

Status: **BLOCKED**

Reason: source-integrity evidence sample is not complete; cross-provider findings are interim

Recommendation: **CONTINUE_EVIDENCE_COLLECTION**

Guardrail: Cross-provider verification is evidence only; it never replaces Dukascopy data or changes governance gates.

## Summary

- Source report: `reports\validation\st_c3\data_integrity\SOURCE_INTEGRITY_STATISTICAL_REPORT.json`
- Source status: `BLOCKED`
- Observations checked: `188`
- By conclusion: `{'DUKASCOPY_AND_REFERENCE_ABSENT': 42, 'DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT': 146}`
- By symbol: `{'EURUSD': 100, 'GBPUSD': 88}`
- By session: `{'LONDON': 2, 'OTHER': 83, 'ROLLOVER': 103}`
- By root-cause category: `{'OFF_SESSION_ZERO_TICK': 83, 'PRIMARY_SESSION_ZERO_TICK': 2, 'ROLLOVER_ZERO_TICK': 103}`

## Findings

| Timestamp UTC | Symbol | Dukascopy Result | Reference Source Result | Conclusion |
|---|---|---|---|---|
| `2021-01-04T22:19:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-04T22:45:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-04T22:46:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-05T22:02:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-05T22:18:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-05T22:19:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-05T22:20:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-05T22:23:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-05T22:44:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-05T22:46:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-05T22:49:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-05T22:50:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-06T22:04:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-06T22:08:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-06T22:09:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-06T22:16:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-06T22:21:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-06T22:23:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-06T22:26:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-06T22:28:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-22T18:24:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-22T20:26:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-01-22T21:38:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T04:29:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T04:48:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T05:11:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T05:53:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T21:24:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T21:24:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T21:32:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T22:07:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T22:17:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T22:44:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T22:45:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T22:46:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T22:49:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T22:50:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T22:51:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-02-10T22:56:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-04-13T00:30:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T02:12:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T04:41:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T04:42:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T08:29:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T08:29:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T19:25:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T20:18:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T20:19:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T20:22:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T20:26:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T20:27:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T20:28:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T21:07:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T21:08:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T21:17:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T21:22:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T21:38:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T21:44:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T21:46:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T22:24:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T22:26:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T23:43:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-04-13T23:44:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T03:36:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T04:29:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T19:11:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:04:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:05:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:06:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:07:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:08:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:09:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:10:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:11:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:12:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:13:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:14:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:16:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:17:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:18:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:18:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:19:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:23:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:24:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:27:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:29:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:42:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:45:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T21:48:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T22:14:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-07-27T22:16:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-07-27T22:53:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T23:16:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T23:16:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp absent | `DUKASCOPY_AND_REFERENCE_ABSENT` |
| `2021-07-27T23:20:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T23:26:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T23:27:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T23:47:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-07-27T23:57:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T02:46:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T03:41:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T03:55:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T04:16:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T04:24:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T05:09:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T05:35:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T06:13:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T20:18:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T20:22:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T20:36:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T21:02:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T21:06:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T21:07:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T21:08:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T21:09:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T21:09:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T21:10:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T21:23:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T21:40:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T21:41:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T21:44:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T21:50:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T22:04:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T22:24:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T22:26:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T22:26:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T22:42:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T22:50:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T22:56:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T23:07:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T23:13:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T23:14:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T23:27:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T23:28:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-10T23:52:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T02:58:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T03:30:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T03:33:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T04:20:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T04:24:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T04:54:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T05:10:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T18:04:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T18:50:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T19:17:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T19:17:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T19:26:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T19:28:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T19:34:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T19:36:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T20:22:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T20:23:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T20:30:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T20:36:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T20:37:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T20:41:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T20:46:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T21:16:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T22:10:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T22:11:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T22:21:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T22:23:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T22:42:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T22:47:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T22:53:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T23:31:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T23:38:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T23:40:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T23:41:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T23:41:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-08-25T23:42:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-14T20:10:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-14T20:21:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-14T20:25:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-14T20:26:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-14T20:32:00Z` | `EURUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-14T21:13:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-14T21:14:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-14T21:27:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-14T22:26:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-14T22:35:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-14T23:08:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-14T23:27:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-14T23:38:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-14T23:42:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-30T21:26:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-30T22:36:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |
| `2021-09-30T22:37:00Z` | `GBPUSD` | zero ticks in reconstructed M1 source minute | `HistData.com Generic ASCII M1`: timestamp present | `DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT` |

## Decision

This interim report does not accept or reject Dukascopy because the deterministic source-integrity evidence sample is incomplete.
No Dukascopy data was replaced with reference-provider data.
