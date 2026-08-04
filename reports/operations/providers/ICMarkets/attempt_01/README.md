# IC Markets Attempt 01

Status: **PENDING_PROVIDER_CONNECTION**

This directory is reserved for OP-03 IC Markets Demo connection evidence.

First command after MT5 is connected to the IC Markets Demo environment:

```powershell
python -m tools.st_c5_3_connection_check --expected-provider ICMarkets --report-dir reports/operations/providers/ICMarkets/attempt_01 --filename-stem CONNECTION_PRECHECK_01
```

Do not run the history gate unless the connection check returns
`READY_FOR_HISTORY_GATE`.
