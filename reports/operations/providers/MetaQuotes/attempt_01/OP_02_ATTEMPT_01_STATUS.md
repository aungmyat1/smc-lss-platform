# OP-02 MetaQuotes Attempt 01 Status

Status: **PENDING_METAQUOTES_CONNECTION**

Generated UTC: `2026-08-02T09:55:58Z`

## Connection Precheck

| Field | Value |
| --- | --- |
| Expected provider | MetaQuotes Demo |
| Current server | VTMarkets-Demo |
| Account company | VT Markets (Pty) Ltd |
| Terminal connected | true |
| Terminal build | 6063 |

## Decision

OP-02 MetaQuotes qualification was not executed because the active MT5 terminal
session is still connected to `VTMarkets-Demo`.

## Next Action

Connect MT5 to the exact MetaQuotes Demo server, then rerun:

```powershell
python -m tools.st_c5_3_history_sync_gate
```

No history gate, export, ST-C3 validation, approval, replay, demo, or live
action was executed for MetaQuotes in this attempt.
