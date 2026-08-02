# OP-01 Provider Capability Matrix

Status: **OPEN**

This matrix tracks operational broker-history capability only. It does not
replace ST-C4/ST-C4.1 provider qualification or ST-C3 validation.

| Provider | Account Type | Server | Connection Date | Earliest M1 | Earliest M3 | Earliest M15 | Earliest H4 | ST-C3 Result | ST-C3 Eligible | Failure Class | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VTMarkets | Demo | VTMarkets-Demo | 2026-08-02 | None in-window | 2025-10-10 | 2022-07-26 | 2021-01-04 | NOT_RUN | No | History | OPERATIONALLY_INSUFFICIENT_FOR_ST_C3_HISTORY | `reports/operations/OP_01_ATTEMPT_03_RESULT.md` |
| MetaQuotes | Demo | Pending exact server | 2026-08-02 connection check still on VTMarkets-Demo | Pending | Pending | Pending | Pending | NOT_RUN | Pending | Pending | PENDING_METAQUOTES_CONNECTION | `reports/operations/providers/MetaQuotes/attempt_01/CONNECTION_RECHECK_04.json` |
| IC Markets | Demo | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | PLANNED | Pending |
| Pepperstone | Demo | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | Pending | PLANNED | Pending |

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

Provider evaluations are governed by
`reports/operations/OP_01_PROVIDER_EVALUATION_FREEZE_RULE.md`.

VTMarkets-Demo completed its final controlled synchronization attempt under
`reports/operations/OP_01_ATTEMPT_03_PROTOCOL.md` and is classified as
`OPERATIONALLY_INSUFFICIENT_FOR_ST_C3_HISTORY`. Proceed to MetaQuotes Demo with
the unchanged frozen ST-C5 pipeline.
