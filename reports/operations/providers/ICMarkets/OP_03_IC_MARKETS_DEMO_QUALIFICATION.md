# OP-03 IC Markets Demo Qualification

Status: **PENDING_PROVIDER_CONNECTION**

Opened UTC: `2026-08-03T09:59:25Z`

Latest check UTC: `2026-08-03T10:00:35Z`

## Purpose

Evaluate IC Markets Demo as the next MT5 historical data candidate after:

- VTMarkets-Demo closed as `OPERATIONALLY_INSUFFICIENT_FOR_ST_C3_HISTORY`.
- MetaQuotes closed as `METAQUOTES_ENVIRONMENT_UNAVAILABLE`.

This qualification reuses the frozen ST-C5/ST-C3 workflow and does not modify
strategy logic, validation thresholds, dataset approval rules, replay gates,
demo, or live controls.

## Provider Lock

| Field | Value |
| --- | --- |
| Provider | IC Markets |
| Expected server marker | ICMarkets-Demo |
| Account type | Demo |
| Required symbols | EURUSD, GBPUSD |
| Required start | 2021-01-04T00:00:00Z |
| Required end | 2025-12-31 |
| Evidence timeframes | M1, M3, M15, H4 |
| Candidate export timeframes | H4, M15, M3 |

Provider lock: `reports/operations/provider_lock.json`

## Required Sequence

1. Connect MT5 to the IC Markets Demo account.
2. Run:

   ```powershell
   python -m tools.st_c5_3_connection_check --expected-provider ICMarkets --report-dir reports/operations/providers/ICMarkets/attempt_01 --filename-stem CONNECTION_PRECHECK_01
   ```

3. If and only if the connection check returns `READY_FOR_HISTORY_GATE`, run:

   ```powershell
   python -m tools.st_c5_3_history_sync_gate
   ```

4. If the history gate passes, continue with the frozen ST-C5 pipeline.

## Current Decision

Current decision: **PENDING_PROVIDER_CONNECTION**

Attempt 01 connection precheck rejected the active MT5 session because it still
reported `VTMarkets-Demo`, while OP-03 expects IC Markets provider identity.

Latest evidence:

- `reports/operations/providers/ICMarkets/attempt_01/CONNECTION_PRECHECK_01.json`
- `reports/operations/providers/ICMarkets/attempt_01/CONNECTION_PRECHECK_01.md`

No IC Markets history gate, export, ST-C3 validation, replay, demo, or live
action has been executed.
