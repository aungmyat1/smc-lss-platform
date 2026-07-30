# ST-C3 Source Integrity Statistical Report

Status: **BLOCKED**

Reason: insufficient cached deterministic sample: 8/100 target days available

Recommendation: **CONTINUE_EVIDENCE_COLLECTION**

Guardrail: Statistical source integrity investigation does not change contracts, validators, approval, replay, or market data.

## Sample

- Coverage: `2021-01-01` through `2025-12-31`
- Target sample days: `100`
- Minimum sample completion rate: `0.95`
- Minimum complete sample days: `95`
- Missing-rate threshold for contract review: `0.001`
- Deterministic sample days cached complete: `8`
- Audited cached day count: `11`
- Statistically sufficient: `False`
- Missing-rate 95% confidence interval: `{'lower': 0.006015492553545249, 'upper': 0.007845455683058679}`
- Decision status: `INSUFFICIENT_EVIDENCE`
- Sample weekday stratification: `{'Friday': 27, 'Monday': 13, 'Thursday': 18, 'Tuesday': 23, 'Wednesday': 19}`
- Sample month stratification: `{'01': 8, '02': 8, '03': 9, '04': 10, '05': 7, '06': 12, '07': 5, '08': 6, '09': 7, '10': 6, '11': 12, '12': 10}`
- Sample condition tags: `{'DST_TRANSITION_WINDOW': 14, 'MONTH_BOUNDARY': 16, 'ORDINARY_TRADING_DAY': 55, 'QUARTER_BOUNDARY': 8, 'QUIET_PERIOD_PROXY': 17}`

## Results

| Symbol | Days | Hours | Expected Minutes | Missing Minutes | Missing Rate | First Missing |
|---|---:|---:|---:|---:|---:|---|
| `EURUSD` | 11 | 262 | 15720 | 128 | 0.00814249 | 2021-01-04T22:45:00Z |
| `GBPUSD` | 11 | 262 | 15720 | 88 | 0.00559796 | 2021-01-04T22:19:00Z |

## Missing Distribution

### EURUSD

- By hour UTC: `{'18': 1, '19': 4, '20': 10, '21': 15, '22': 48, '23': 34, '3': 5, '4': 8, '5': 1, '6': 1, '8': 1}`
- By weekday: `{'Friday': 1, 'Monday': 2, 'Thursday': 4, 'Tuesday': 80, 'Wednesday': 41}`
- By session: `{'LONDON': 1, 'OTHER': 64, 'ROLLOVER': 63}`
- By root-cause category: `{'OFF_SESSION_ZERO_TICK': 64, 'PRIMARY_SESSION_ZERO_TICK': 1, 'ROLLOVER_ZERO_TICK': 63}`
- Samples: `['2021-01-04T22:45:00Z', '2021-01-04T22:46:00Z', '2021-01-05T22:02:00Z', '2021-01-05T22:20:00Z', '2021-01-05T22:23:00Z', '2021-01-05T22:44:00Z', '2021-01-05T22:46:00Z', '2021-01-05T22:49:00Z', '2021-01-05T22:50:00Z', '2021-01-06T22:08:00Z', '2021-01-06T22:09:00Z', '2021-01-06T22:16:00Z', '2021-01-06T22:21:00Z', '2021-01-06T22:23:00Z', '2021-01-06T22:26:00Z', '2021-01-06T22:28:00Z', '2021-01-22T21:38:00Z', '2021-02-10T04:29:00Z', '2021-02-10T21:24:00Z', '2021-02-10T22:07:00Z', '2021-02-10T22:44:00Z', '2021-02-10T22:45:00Z', '2021-02-10T22:46:00Z', '2021-02-10T22:49:00Z', '2021-02-10T22:50:00Z']`

### GBPUSD

- By hour UTC: `{'0': 1, '18': 2, '19': 4, '2': 3, '20': 12, '21': 37, '22': 15, '23': 7, '4': 2, '5': 4, '8': 1}`
- By weekday: `{'Friday': 2, 'Monday': 1, 'Thursday': 3, 'Tuesday': 63, 'Wednesday': 19}`
- By session: `{'LONDON': 1, 'OTHER': 35, 'ROLLOVER': 52}`
- By root-cause category: `{'OFF_SESSION_ZERO_TICK': 35, 'PRIMARY_SESSION_ZERO_TICK': 1, 'ROLLOVER_ZERO_TICK': 52}`
- Samples: `['2021-01-04T22:19:00Z', '2021-01-05T22:18:00Z', '2021-01-05T22:19:00Z', '2021-01-06T22:04:00Z', '2021-01-22T18:24:00Z', '2021-01-22T20:26:00Z', '2021-02-10T04:48:00Z', '2021-02-10T05:11:00Z', '2021-02-10T05:53:00Z', '2021-02-10T21:24:00Z', '2021-02-10T21:32:00Z', '2021-02-10T22:17:00Z', '2021-04-13T00:30:00Z', '2021-04-13T02:12:00Z', '2021-04-13T04:41:00Z', '2021-04-13T08:29:00Z', '2021-04-13T20:18:00Z', '2021-04-13T20:22:00Z', '2021-04-13T20:26:00Z', '2021-04-13T20:27:00Z', '2021-04-13T20:28:00Z', '2021-04-13T21:07:00Z', '2021-04-13T21:08:00Z', '2021-04-13T21:46:00Z', '2021-04-13T22:24:00Z']`

## Cross-Source Comparison

- Observations: `188`
- Checked: `188`
- Reference present: `146`
- Reference absent: `42`

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
