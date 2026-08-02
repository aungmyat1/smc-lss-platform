# OP-01 Attempt 03 Protocol

Status: **PENDING_EXECUTION**

Purpose: final controlled VTMarkets-Demo history synchronization attempt.

Attempt 03 must use the documented runbook and the frozen ST-C5 history gate.
No validation thresholds, strategy logic, export code, or governance rules may
be changed.

## Pre-Attempt Evidence To Record

| Item | Required |
| --- | --- |
| MT5 terminal build | Yes |
| Broker server | Yes |
| Account type | Demo or Live |
| Symbol specification | EURUSD and GBPUSD symbol metadata |
| Earliest available M1 before synchronization | Yes |
| Earliest available M3 before synchronization | Yes |
| Earliest available M15 before synchronization | Yes |
| Earliest available H4 before synchronization | Yes |
| Terminal log excerpts | If available |
| Synchronization start time | Yes |
| Synchronization end time | Yes |

## Controlled Execution

1. Execute `reports/st_c5_3/HISTORY_SYNC_RUNBOOK.md`.
2. Do not modify ST-C3.
3. Do not alter export code.
4. Do not change validation thresholds.
5. Do not manually edit or fill data.
6. Rerun `python -m tools.st_c5_3_history_sync_gate`.

## Post-Attempt Evidence To Capture

| Item | Required |
| --- | --- |
| Earliest available EURUSD M1 | Yes |
| Earliest available EURUSD M3 | Yes |
| Earliest available EURUSD M15 | Yes |
| Earliest available EURUSD H4 | Yes |
| Earliest available GBPUSD M1 | Yes |
| Earliest available GBPUSD M3 | Yes |
| Earliest available GBPUSD M15 | Yes |
| Earliest available GBPUSD H4 | Yes |
| History gate result | PASS / REQUIRES_HISTORY_SYNC / FAIL |
| Difference from Attempt 01 | Yes |
| Difference from Attempt 02 | Yes |

## Decision Rule

If Attempt 03 is materially identical to Attempts 01 and 02, classify
VTMarkets-Demo as:

**OPERATIONALLY_INSUFFICIENT_FOR_ST_C3_HISTORY**

Then stop retrying VTMarkets-Demo for ST-C3 historical research data and move to
the next MT5 broker candidate using the unchanged frozen ST-C5 pipeline.

## Branching

```text
VTMarkets Attempt 03
        |
        +-- PASS
        |     |
        |     v
        |  Continue ST-C5 Pipeline
        |
        +-- FAIL / REQUIRES_HISTORY_SYNC
              |
              v
        Operationally Insufficient
              |
              v
        Evaluate Next Broker
```
