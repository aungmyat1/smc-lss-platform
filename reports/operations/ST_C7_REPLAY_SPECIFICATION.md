# ST-C7 Replay Specification

Status: **PENDING_APPROVED_DATASET**

This replay specification is prepared before results are available. It does not
unlock replay and does not change strategy logic.

## Instruments

- EURUSD
- GBPUSD
- XAUUSD only if an approved dataset supports it

## Replay Environment

| Area | Requirement |
| --- | --- |
| Dataset | Approved canonical dataset only |
| Sessions | Use frozen ST-C3 session/calendar rules |
| Spread model | Use recorded dataset spread when available; otherwise predeclare fixed conservative spread before run |
| Commission model | Predeclare broker/account commission before run |
| Slippage model | Predeclare conservative slippage assumption before run |
| Risk model | Use frozen strategy risk model |
| Execution assumptions | Deterministic replay only; no live/demo execution |

## Guardrails

- No unapproved datasets.
- No strategy optimization before baseline replay.
- No changes to ST-C3 thresholds.
- No replay unlock before dataset approval.
