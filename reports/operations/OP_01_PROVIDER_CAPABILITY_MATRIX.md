# OP-01 Provider Capability Matrix

Status: **OPEN**

This matrix tracks operational broker-history capability only. It does not
replace ST-C4/ST-C4.1 provider qualification or ST-C3 validation.

| Provider / Server | Account Type | Earliest M1 | Earliest M3 | Earliest M15 | Earliest H4 | ST-C3 Eligible | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VTMarkets-Demo | Demo | None in-window | 2025-10-10 | 2022-07-26 | 2021-01-04 | No | FINAL_ATTEMPT_PENDING | `reports/operations/ST_C6_OPERATIONAL_ATTEMPT_02.md` |
| MetaQuotes Demo | Demo | Pending | Pending | Pending | Pending | Pending | PLANNED | Pending |
| IC Markets Demo | Demo | Pending | Pending | Pending | Pending | Pending | PLANNED | Pending |
| Pepperstone Demo | Demo | Pending | Pending | Pending | Pending | Pending | PLANNED | Pending |

## Interpretation

VTMarkets-Demo currently fails the operational history requirement because:

- EURUSD/GBPUSD M1 returned no in-window bars.
- EURUSD/GBPUSD M3 starts in 2025.
- EURUSD/GBPUSD M15 starts in 2022.
- EURUSD/GBPUSD H4 is available from the required start.

The next meaningful comparison is to run the unchanged ST-C5 history gate
against a second MT5 broker environment.

## Operational Control

This matrix is the primary OP-01 control document. Do not repeat broker-history
evaluations unless this matrix is updated with the attempt status and evidence.

VTMarkets-Demo receives one final controlled synchronization attempt under
`reports/operations/OP_01_ATTEMPT_03_PROTOCOL.md`. If Attempt 03 is materially
identical to Attempts 01 and 02, update the VTMarkets-Demo status to
`OPERATIONALLY_INSUFFICIENT_FOR_ST_C3_HISTORY` and proceed to the next broker.
