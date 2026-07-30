# ST-C3 Source Integrity Statistical Report

Status: **BLOCKED**

Reason: insufficient cached deterministic sample: 1/100 target days available

Recommendation: **CONTINUE_EVIDENCE_COLLECTION**

Guardrail: Statistical source integrity investigation does not change contracts, validators, approval, replay, or market data.

## Sample

- Coverage: `2021-01-01` through `2025-12-31`
- Target sample days: `100`
- Deterministic sample days cached complete: `1`
- Audited cached day count: `4`
- Statistically sufficient: `False`

## Results

| Symbol | Days | Hours | Expected Minutes | Missing Minutes | Missing Rate | First Missing |
|---|---:|---:|---:|---:|---:|---|
| `EURUSD` | 4 | 94 | 5640 | 17 | 0.00301418 | 2021-01-04T22:45:00Z |
| `GBPUSD` | 4 | 94 | 5640 | 6 | 0.00106383 | 2021-01-04T22:19:00Z |

## Missing Distribution

### EURUSD

- By hour UTC: `{'21': 1, '22': 16}`
- By weekday: `{'Friday': 1, 'Monday': 2, 'Tuesday': 7, 'Wednesday': 7}`
- By session: `{'ROLLOVER': 17}`
- Samples: `['2021-01-04T22:45:00Z', '2021-01-04T22:46:00Z', '2021-01-05T22:02:00Z', '2021-01-05T22:20:00Z', '2021-01-05T22:23:00Z', '2021-01-05T22:44:00Z', '2021-01-05T22:46:00Z', '2021-01-05T22:49:00Z', '2021-01-05T22:50:00Z', '2021-01-06T22:08:00Z', '2021-01-06T22:09:00Z', '2021-01-06T22:16:00Z', '2021-01-06T22:21:00Z', '2021-01-06T22:23:00Z', '2021-01-06T22:26:00Z', '2021-01-06T22:28:00Z', '2021-01-22T21:38:00Z']`

### GBPUSD

- By hour UTC: `{'18': 1, '20': 1, '22': 4}`
- By weekday: `{'Friday': 2, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 1}`
- By session: `{'OTHER': 2, 'ROLLOVER': 4}`
- Samples: `['2021-01-04T22:19:00Z', '2021-01-05T22:18:00Z', '2021-01-05T22:19:00Z', '2021-01-06T22:04:00Z', '2021-01-22T18:24:00Z', '2021-01-22T20:26:00Z']`

## Decision

This report is not statistically sufficient until the deterministic target sample is cached and audited.
No candles were fabricated, interpolated, or manually inserted.
