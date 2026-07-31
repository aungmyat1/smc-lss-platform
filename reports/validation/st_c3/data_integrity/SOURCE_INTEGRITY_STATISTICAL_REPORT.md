# ST-C3 Source Integrity Statistical Report

Status: **BLOCKED**

Reason: insufficient cached deterministic sample: 30/100 target days available

Recommendation: **CONTINUE_EVIDENCE_COLLECTION**

Guardrail: Statistical source integrity investigation does not change contracts, validators, approval, replay, or market data.

## Sample

- Coverage: `2021-01-01` through `2025-12-31`
- Target sample days: `100`
- Minimum sample completion rate: `0.95`
- Minimum complete sample days: `95`
- Missing-rate threshold for contract review: `0.001`
- Deterministic sample days cached complete: `30`
- Audited cached day count: `33`
- Provider-calendar excluded source hours: `16`
- Provider-calendar excluded expected minutes: `960`
- Statistically sufficient: `False`
- Missing-rate 95% confidence interval: `{'lower': 0.004663689753505748, 'upper': 0.0055872055391268036}`
- Decision status: `INSUFFICIENT_EVIDENCE`
- Sample weekday stratification: `{'Friday': 27, 'Monday': 13, 'Thursday': 18, 'Tuesday': 23, 'Wednesday': 19}`
- Sample month stratification: `{'01': 8, '02': 8, '03': 9, '04': 10, '05': 7, '06': 12, '07': 5, '08': 6, '09': 7, '10': 6, '11': 12, '12': 10}`
- Sample condition tags: `{'DST_TRANSITION_WINDOW': 14, 'MONTH_BOUNDARY': 16, 'ORDINARY_TRADING_DAY': 55, 'QUARTER_BOUNDARY': 8, 'QUIET_PERIOD_PROXY': 17}`

## Results

| Symbol | Days | Hours | Expected Minutes | Missing Minutes | Missing Rate | First Missing |
|---|---:|---:|---:|---:|---:|---|
| `EURUSD` | 33 | 764 | 45840 | 261 | 0.00569372 | 2021-01-04T22:45:00Z |
| `GBPUSD` | 33 | 764 | 45840 | 207 | 0.00451571 | 2021-01-04T22:19:00Z |

## Missing Distribution

### EURUSD

- By hour UTC: `{'0': 3, '10': 2, '17': 2, '18': 6, '19': 6, '2': 3, '20': 21, '21': 56, '22': 74, '23': 46, '3': 15, '4': 19, '5': 5, '6': 2, '8': 1}`
- By weekday: `{'Friday': 25, 'Monday': 20, 'Thursday': 58, 'Tuesday': 83, 'Wednesday': 75}`
- By session: `{'LONDON': 1, 'OTHER': 130, 'ROLLOVER': 130}`
- By root-cause category: `{'OFF_SESSION_ZERO_TICK': 130, 'PRIMARY_SESSION_ZERO_TICK': 1, 'ROLLOVER_ZERO_TICK': 130}`
- Samples: `['2021-01-04T22:45:00Z', '2021-01-04T22:46:00Z', '2021-01-05T22:02:00Z', '2021-01-05T22:20:00Z', '2021-01-05T22:23:00Z', '2021-01-05T22:44:00Z', '2021-01-05T22:46:00Z', '2021-01-05T22:49:00Z', '2021-01-05T22:50:00Z', '2021-01-06T22:08:00Z', '2021-01-06T22:09:00Z', '2021-01-06T22:16:00Z', '2021-01-06T22:21:00Z', '2021-01-06T22:23:00Z', '2021-01-06T22:26:00Z', '2021-01-06T22:28:00Z', '2021-01-22T21:38:00Z', '2021-02-10T04:29:00Z', '2021-02-10T21:24:00Z', '2021-02-10T22:07:00Z', '2021-02-10T22:44:00Z', '2021-02-10T22:45:00Z', '2021-02-10T22:46:00Z', '2021-02-10T22:49:00Z', '2021-02-10T22:50:00Z']`

### GBPUSD

- By hour UTC: `{'0': 3, '1': 1, '10': 2, '17': 1, '18': 2, '19': 6, '2': 4, '20': 19, '21': 81, '22': 70, '23': 9, '4': 2, '5': 4, '6': 1, '7': 1, '8': 1}`
- By weekday: `{'Friday': 9, 'Monday': 19, 'Thursday': 68, 'Tuesday': 65, 'Wednesday': 46}`
- By session: `{'LONDON': 2, 'OTHER': 54, 'ROLLOVER': 151}`
- By root-cause category: `{'OFF_SESSION_ZERO_TICK': 54, 'PRIMARY_SESSION_ZERO_TICK': 2, 'ROLLOVER_ZERO_TICK': 151}`
- Samples: `['2021-01-04T22:19:00Z', '2021-01-05T22:18:00Z', '2021-01-05T22:19:00Z', '2021-01-06T22:04:00Z', '2021-01-22T18:24:00Z', '2021-01-22T20:26:00Z', '2021-02-10T04:48:00Z', '2021-02-10T05:11:00Z', '2021-02-10T05:53:00Z', '2021-02-10T21:24:00Z', '2021-02-10T21:32:00Z', '2021-02-10T22:17:00Z', '2021-04-13T00:30:00Z', '2021-04-13T02:12:00Z', '2021-04-13T04:41:00Z', '2021-04-13T08:29:00Z', '2021-04-13T20:18:00Z', '2021-04-13T20:22:00Z', '2021-04-13T20:26:00Z', '2021-04-13T20:27:00Z', '2021-04-13T20:28:00Z', '2021-04-13T21:07:00Z', '2021-04-13T21:08:00Z', '2021-04-13T21:46:00Z', '2021-04-13T22:24:00Z']`

## Cross-Source Comparison

- Observations: `200`
- Checked: `200`
- Reference present: `151`
- Reference absent: `49`

## Missing Observation Samples

| Symbol | Timestamp | Session | Weekday | Prev Ticks | Next Ticks | Rollover | Category |
|---|---|---|---|---:|---:|---|---|
| `GBPUSD` | `2021-01-04T22:19:00Z` | `ROLLOVER` | Monday | 18 | 1 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-04T22:45:00Z` | `ROLLOVER` | Monday | 3 | 0 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-04T22:46:00Z` | `ROLLOVER` | Monday | 0 | 4 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-05T22:02:00Z` | `ROLLOVER` | Tuesday | 6 | 1 | True | `ROLLOVER_ZERO_TICK` |
| `GBPUSD` | `2021-01-05T22:18:00Z` | `ROLLOVER` | Tuesday | 7 | 0 | True | `ROLLOVER_ZERO_TICK` |
| `GBPUSD` | `2021-01-05T22:19:00Z` | `ROLLOVER` | Tuesday | 0 | 4 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-05T22:20:00Z` | `ROLLOVER` | Tuesday | 11 | 26 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-05T22:23:00Z` | `ROLLOVER` | Tuesday | 7 | 1 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-05T22:44:00Z` | `ROLLOVER` | Tuesday | 16 | 2 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-05T22:46:00Z` | `ROLLOVER` | Tuesday | 2 | 2 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-05T22:49:00Z` | `ROLLOVER` | Tuesday | 1 | 0 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-05T22:50:00Z` | `ROLLOVER` | Tuesday | 0 | 2 | True | `ROLLOVER_ZERO_TICK` |
| `GBPUSD` | `2021-01-06T22:04:00Z` | `ROLLOVER` | Wednesday | 1 | 2 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-06T22:08:00Z` | `ROLLOVER` | Wednesday | 2 | 0 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-06T22:09:00Z` | `ROLLOVER` | Wednesday | 0 | 3 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-06T22:16:00Z` | `ROLLOVER` | Wednesday | 1 | 5 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-06T22:21:00Z` | `ROLLOVER` | Wednesday | 2 | 1 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-06T22:23:00Z` | `ROLLOVER` | Wednesday | 1 | 3 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-06T22:26:00Z` | `ROLLOVER` | Wednesday | 4 | 6 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-01-06T22:28:00Z` | `ROLLOVER` | Wednesday | 6 | 17 | True | `ROLLOVER_ZERO_TICK` |
| `GBPUSD` | `2021-01-22T18:24:00Z` | `OTHER` | Friday | 13 | 7 | False | `OFF_SESSION_ZERO_TICK` |
| `GBPUSD` | `2021-01-22T20:26:00Z` | `OTHER` | Friday | 3 | 7 | False | `OFF_SESSION_ZERO_TICK` |
| `EURUSD` | `2021-01-22T21:38:00Z` | `ROLLOVER` | Friday | 4 | 17 | True | `ROLLOVER_ZERO_TICK` |
| `EURUSD` | `2021-02-10T04:29:00Z` | `OTHER` | Wednesday | 12 | 15 | False | `OFF_SESSION_ZERO_TICK` |
| `GBPUSD` | `2021-02-10T04:48:00Z` | `OTHER` | Wednesday | 3 | 10 | False | `OFF_SESSION_ZERO_TICK` |

## Pre-Registered Decision Framework

- Current decision status: `INSUFFICIENT_EVIDENCE`
- Recommendation: `CONTINUE_EVIDENCE_COLLECTION`
- Next gate: `complete deterministic source-integrity evidence sample`

## Decision

This report is not statistically sufficient until the deterministic target sample is cached and audited.
No candles were fabricated, interpolated, or manually inserted.
