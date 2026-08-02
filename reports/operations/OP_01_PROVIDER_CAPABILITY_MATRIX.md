# OP-01 Provider Capability Matrix

Status: **OPEN**

This matrix tracks operational broker-history capability only. It does not
replace ST-C4/ST-C4.1 provider qualification or ST-C3 validation.

| Broker / Server | M1 Since 2021 | M3 Since 2021 | M15 Since 2021 | H4 Since 2021 | ST-C3 Eligible | Status | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VTMarkets-Demo | No | No | Partial | Yes | No | REQUIRES_HISTORY_SYNC | `reports/operations/ST_C6_OPERATIONAL_ATTEMPT_02.md` |
| MetaQuotes Demo | Unknown | Unknown | Unknown | Unknown | Unknown | PENDING_EVALUATION | Pending |
| IC Markets Demo | Unknown | Unknown | Unknown | Unknown | Unknown | PENDING_EVALUATION | Pending |
| Pepperstone Demo | Unknown | Unknown | Unknown | Unknown | Unknown | PENDING_EVALUATION | Pending |

## Interpretation

VTMarkets-Demo currently fails the operational history requirement because:

- EURUSD/GBPUSD M1 returned no in-window bars.
- EURUSD/GBPUSD M3 starts in 2025.
- EURUSD/GBPUSD M15 starts in 2022.
- EURUSD/GBPUSD H4 is available from the required start.

The next meaningful comparison is to run the unchanged ST-C5 history gate
against a second MT5 broker environment.
