# ST-C3 Friday 21:00 UTC Source Integrity Investigation

Status: **BLOCKED**

Reason: Dukascopy returns empty payloads for DST Friday 21:00 UTC while adjacent Friday 20:00 UTC and winter Friday 21:00 UTC controls parse.

Recommendation: **CONTINUE_EVIDENCE_COLLECTION**

Guardrail: Friday 21:00 investigation is evidence only; it does not change contracts, validators, calendars, approval, replay, or market data.

## Classification

- Root cause: `DST_FRIDAY_CLOSE_PROVIDER_CALENDAR_MISMATCH`
- Next action: Document DST Friday close behavior and review the evidence-sample market calendar before resuming larger sample batches.

## Summary

- By Dukascopy status: `{'EMPTY_PAYLOAD': 16, 'PARSED': 14}`
- By weekday/hour/status: `{'Friday 20:00 PARSED': 10, 'Friday 21:00 EMPTY_PAYLOAD': 8, 'Friday 21:00 PARSED': 2, 'Friday 22:00 EMPTY_PAYLOAD': 8, 'Monday 21:00 PARSED': 2}`
- HistData reference hours checked: `30`
- HistData hour-row counts by Dukascopy status: `{'EMPTY_PAYLOAD': {'58': 1, '60': 4, '0': 8, '57': 1, '59': 2}, 'PARSED': {'60': 11, '58': 1, '59': 2}}`

## Probes

| Hour UTC | Symbol | Weekday | Dukascopy Status | Bytes | Ticks | HistData M1 Rows |
|---|---|---|---|---:|---:|---:|
| `2021-04-16T20:00:00Z` | `EURUSD` | Friday | `PARSED` | 4658 | 864 | 60 |
| `2021-04-16T20:00:00Z` | `GBPUSD` | Friday | `PARSED` | 5830 | 1290 | 60 |
| `2021-04-16T21:00:00Z` | `EURUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 58 |
| `2021-04-16T21:00:00Z` | `GBPUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 60 |
| `2021-04-16T22:00:00Z` | `EURUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 0 |
| `2021-04-16T22:00:00Z` | `GBPUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 0 |
| `2021-05-14T20:00:00Z` | `EURUSD` | Friday | `PARSED` | 8093 | 1693 | 60 |
| `2021-05-14T20:00:00Z` | `GBPUSD` | Friday | `PARSED` | 7562 | 1769 | 60 |
| `2021-05-14T21:00:00Z` | `EURUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 60 |
| `2021-05-14T21:00:00Z` | `GBPUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 57 |
| `2021-05-14T22:00:00Z` | `EURUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 0 |
| `2021-05-14T22:00:00Z` | `GBPUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 0 |
| `2021-07-02T20:00:00Z` | `EURUSD` | Friday | `PARSED` | 7742 | 1631 | 58 |
| `2021-07-02T20:00:00Z` | `GBPUSD` | Friday | `PARSED` | 7895 | 1818 | 60 |
| `2021-07-02T21:00:00Z` | `EURUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 59 |
| `2021-07-02T21:00:00Z` | `GBPUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 59 |
| `2021-07-02T22:00:00Z` | `EURUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 0 |
| `2021-07-02T22:00:00Z` | `GBPUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 0 |
| `2021-04-23T20:00:00Z` | `EURUSD` | Friday | `PARSED` | 9167 | 1951 | 60 |
| `2021-04-23T20:00:00Z` | `GBPUSD` | Friday | `PARSED` | 9021 | 2065 | 60 |
| `2021-04-23T21:00:00Z` | `EURUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 60 |
| `2021-04-23T21:00:00Z` | `GBPUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 60 |
| `2021-04-19T21:00:00Z` | `EURUSD` | Monday | `PARSED` | 4206 | 1178 | 60 |
| `2021-04-19T21:00:00Z` | `GBPUSD` | Monday | `PARSED` | 2378 | 515 | 60 |
| `2021-01-22T20:00:00Z` | `EURUSD` | Friday | `PARSED` | 9740 | 1762 | 60 |
| `2021-01-22T20:00:00Z` | `GBPUSD` | Friday | `PARSED` | 7044 | 1430 | 59 |
| `2021-01-22T21:00:00Z` | `EURUSD` | Friday | `PARSED` | 8905 | 1779 | 59 |
| `2021-01-22T21:00:00Z` | `GBPUSD` | Friday | `PARSED` | 10956 | 2390 | 60 |
| `2021-01-22T22:00:00Z` | `EURUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 0 |
| `2021-01-22T22:00:00Z` | `GBPUSD` | Friday | `EMPTY_PAYLOAD` | 0 | 0 | 0 |

## Decision

This report is an interim source-integrity investigation. It does not modify the ST-C3 calendar, contract, validator, approval state, replay state, or historical prices.
