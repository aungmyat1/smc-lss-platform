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
| Execution assumptions | Deterministic replay only; next available candle fill assumption unless approved replay engine specifies stricter behavior |

## Frozen Market Model Assumptions

| Area | Frozen Assumption |
| --- | --- |
| Spread | Broker historical spread if present in approved data; otherwise predeclared conservative spread before replay |
| Commission | Realistic commission for the provider/account used by the approved dataset |
| Slippage | Conservative fixed slippage assumption declared before replay |
| Execution timing | Next available candle in deterministic replay |
| Risk | Frozen ST-C strategy risk model; no post-results tuning |

## Guardrails

- No unapproved datasets.
- No strategy optimization before baseline replay.
- No changes to ST-C3 thresholds.
- No replay unlock before dataset approval.
