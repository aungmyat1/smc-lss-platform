# ST-C3 Source Integrity Investigation

Status: **BLOCKED**

Reason: Dukascopy is sparse at probed minutes and independent reference also lacks bars

Recommendation: **INVESTIGATE_SOURCE_INTEGRITY**

Guardrail: Source integrity investigation does not approve data, fill candles, open replay, or change validation rules.

## Probe Summary

| Symbol | Timestamp | Cached Parse | Cached Minute | Fresh Dukascopy | HistData M1 | Verdict |
|---|---|---|---|---|---|---|
| `EURUSD` | `2021-01-04T22:45:00Z` | PASS | False | MATCHED_CACHE | False | DUKASCOPY_AND_REFERENCE_ABSENT |
| `EURUSD` | `2021-01-04T22:46:00Z` | PASS | False | MATCHED_CACHE | False | DUKASCOPY_AND_REFERENCE_ABSENT |
| `GBPUSD` | `2021-01-04T22:19:00Z` | PASS | False | MATCHED_CACHE | False | DUKASCOPY_AND_REFERENCE_ABSENT |

## Policy Question

Does the ST-C3 Dataset Contract require candles for zero-tick market-open minutes, or only minutes with at least one source tick?

No candles were fabricated, interpolated, or manually inserted.
