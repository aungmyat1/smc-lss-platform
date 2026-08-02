# OP-02 MetaQuotes Connection Recheck 02

Status: **PENDING_METAQUOTES_CONNECTION**

Generated UTC: `2026-08-02T10:10:28Z`

## Connection State

| Field | Value |
| --- | --- |
| Expected provider | MetaQuotes Demo |
| Active server | VTMarkets-Demo |
| Account company | VT Markets (Pty) Ltd |
| Terminal connected | true |
| Terminal build | 6063 |
| EURUSD selected | true |
| GBPUSD selected | true |

## Decision

OP-02 MetaQuotes qualification remains blocked because the active MT5 terminal
session is still connected to `VTMarkets-Demo`.

No history gate, export, ST-C3 validation, approval, replay, demo, or live
action was executed.

## Next Action

Switch MT5 to the exact MetaQuotes Demo server, then rerun the provider
connection handoff checklist before running `python -m tools.st_c5_3_history_sync_gate`.
