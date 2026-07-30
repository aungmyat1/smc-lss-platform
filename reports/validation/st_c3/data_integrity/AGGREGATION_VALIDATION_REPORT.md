# ST-C3 Aggregation Validation Report

Status: **BLOCKED**

Reason: EURUSD missing M1 source candle 2021-01-04T22:45:00Z

Guardrail: Aggregation validation does not approve data, open replay, or weaken dataset validation.

| Symbol | M1 Rows | Expected M1 | Missing M1 | First Missing M1 |
|---|---:|---:|---:|---|
| `EURUSD` | 1438 | 1440 | 2 | 2021-01-04T22:45:00Z |
| `GBPUSD` | 1439 | 1440 | 1 | 2021-01-04T22:19:00Z |

## Timeframes

| Symbol | Timeframe | Rows | Expected | Missing | Mismatches | First Missing |
|---|---|---:|---:|---:|---:|---|
| `EURUSD` | `H4` | 5 | 6 | 1 | 0 | 2021-01-04T20:00:00Z |
| `EURUSD` | `M15` | 95 | 96 | 1 | 0 | 2021-01-04T22:45:00Z |
| `EURUSD` | `M3` | 479 | 480 | 1 | 0 | 2021-01-04T22:45:00Z |
| `GBPUSD` | `H4` | 5 | 6 | 1 | 0 | 2021-01-04T20:00:00Z |
| `GBPUSD` | `M15` | 95 | 96 | 1 | 0 | 2021-01-04T22:15:00Z |
| `GBPUSD` | `M3` | 479 | 480 | 1 | 0 | 2021-01-04T22:18:00Z |

## First Sparse Source Hours

- `EURUSD` `2021-01-04T22:00:00Z` status `SPARSE_TICKS` missing minutes: 2021-01-04T22:45:00Z, 2021-01-04T22:46:00Z
- `GBPUSD` `2021-01-04T22:00:00Z` status `SPARSE_TICKS` missing minutes: 2021-01-04T22:19:00Z
