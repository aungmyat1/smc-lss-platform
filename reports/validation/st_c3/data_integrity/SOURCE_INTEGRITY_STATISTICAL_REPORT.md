# ST-C3 Source Integrity Statistical Report

Status: **BLOCKED**

Reason: statistical source integrity sample found 1240 zero-tick market-open minutes

Recommendation: **OPEN_DATA_GOVERNANCE_REVIEW**

Guardrail: Statistical source integrity investigation does not change contracts, validators, approval, replay, or market data.

## Sample

- Coverage: `2021-01-01` through `2025-12-31`
- Target sample days: `100`
- Minimum sample completion rate: `0.95`
- Minimum complete sample days: `95`
- Missing-rate threshold for contract review: `0.001`
- Deterministic sample days cached complete: `100`
- Audited cached day count: `103`
- Provider-calendar excluded source hours: `32`
- Provider-calendar excluded expected minutes: `1920`
- Statistically sufficient: `True`
- Missing-rate 95% confidence interval: `{'lower': 0.004069558281261814, 'upper': 0.004547595328160722}`
- Decision status: `MISSING_RATE_EXCEEDS_THRESHOLD`
- Sample weekday stratification: `{'Friday': 27, 'Monday': 13, 'Thursday': 18, 'Tuesday': 23, 'Wednesday': 19}`
- Sample month stratification: `{'01': 8, '02': 8, '03': 9, '04': 10, '05': 7, '06': 12, '07': 5, '08': 6, '09': 7, '10': 6, '11': 12, '12': 10}`
- Sample condition tags: `{'DST_TRANSITION_WINDOW': 14, 'MONTH_BOUNDARY': 16, 'ORDINARY_TRADING_DAY': 55, 'QUARTER_BOUNDARY': 8, 'QUIET_PERIOD_PROXY': 17}`

## Results

| Symbol | Days | Hours | Expected Minutes | Missing Minutes | Missing Rate | First Missing |
|---|---:|---:|---:|---:|---:|---|
| `EURUSD` | 103 | 2402 | 144120 | 649 | 0.00450319 | 2021-01-04T22:45:00Z |
| `GBPUSD` | 103 | 2402 | 144120 | 591 | 0.00410075 | 2021-01-04T22:19:00Z |

## Missing Distribution

### EURUSD

- By hour UTC: `{'0': 6, '10': 2, '14': 3, '16': 1, '17': 4, '18': 8, '19': 6, '2': 8, '20': 39, '21': 196, '22': 199, '23': 107, '3': 22, '4': 36, '5': 7, '6': 4, '8': 1}`
- By weekday: `{'Friday': 32, 'Monday': 160, 'Thursday': 95, 'Tuesday': 203, 'Wednesday': 159}`
- By session: `{'LONDON': 1, 'NY': 3, 'OTHER': 250, 'ROLLOVER': 395}`
- By root-cause category: `{'OFF_SESSION_ZERO_TICK': 250, 'PRIMARY_SESSION_ZERO_TICK': 4, 'ROLLOVER_ZERO_TICK': 395}`
- Samples: `['2021-01-04T22:45:00Z', '2021-01-04T22:46:00Z', '2021-01-05T22:02:00Z', '2021-01-05T22:20:00Z', '2021-01-05T22:23:00Z', '2021-01-05T22:44:00Z', '2021-01-05T22:46:00Z', '2021-01-05T22:49:00Z', '2021-01-05T22:50:00Z', '2021-01-06T22:08:00Z', '2021-01-06T22:09:00Z', '2021-01-06T22:16:00Z', '2021-01-06T22:21:00Z', '2021-01-06T22:23:00Z', '2021-01-06T22:26:00Z', '2021-01-06T22:28:00Z', '2021-01-22T21:38:00Z', '2021-02-10T04:29:00Z', '2021-02-10T21:24:00Z', '2021-02-10T22:07:00Z', '2021-02-10T22:44:00Z', '2021-02-10T22:45:00Z', '2021-02-10T22:46:00Z', '2021-02-10T22:49:00Z', '2021-02-10T22:50:00Z']`

### GBPUSD

- By hour UTC: `{'0': 7, '1': 2, '10': 2, '14': 3, '17': 3, '18': 5, '19': 7, '2': 7, '20': 55, '21': 179, '22': 199, '23': 74, '3': 11, '4': 23, '5': 11, '6': 1, '7': 1, '8': 1}`
- By weekday: `{'Friday': 19, 'Monday': 117, 'Thursday': 133, 'Tuesday': 196, 'Wednesday': 126}`
- By session: `{'LONDON': 2, 'NY': 3, 'OTHER': 208, 'ROLLOVER': 378}`
- By root-cause category: `{'OFF_SESSION_ZERO_TICK': 208, 'PRIMARY_SESSION_ZERO_TICK': 5, 'ROLLOVER_ZERO_TICK': 378}`
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

- Current decision status: `MISSING_RATE_EXCEEDS_THRESHOLD`
- Recommendation: `OPEN_DATA_GOVERNANCE_REVIEW`
- Next gate: `data governance review board`

## Decision

This report is not statistically sufficient until the deterministic target sample is cached and audited.
No candles were fabricated, interpolated, or manually inserted.
