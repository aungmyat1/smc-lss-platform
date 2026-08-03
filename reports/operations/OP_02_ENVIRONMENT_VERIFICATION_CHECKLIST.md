# OP-02 Environment Verification Checklist

Status: **BLOCKED**

Purpose: distinguish OP-02 software readiness from the external MT5 provider
connection issue.

## Checklist

| Check | Status | Evidence |
| --- | --- | --- |
| MT5 installed | PASS | `reports/operations/providers/MetaQuotes/attempt_01/CONNECTION_RECHECK_04.json` |
| Internet connection / terminal connected | PASS | `reports/operations/providers/MetaQuotes/attempt_01/CONNECTION_RECHECK_04.json` |
| MetaQuotes-Demo listed | UNKNOWN | Manual terminal verification required |
| MetaQuotes demo account created | UNKNOWN | Manual terminal verification required |
| Login successful | FAIL | Active server remains VTMarkets-Demo |
| Server visible in terminal | FAIL | Active server remains VTMarkets-Demo |
| EURUSD available | PASS_ON_CURRENT_SERVER | Current server is VTMarkets-Demo |
| GBPUSD available | PASS_ON_CURRENT_SERVER | Current server is VTMarkets-Demo |

## Decision

Current decision: **BLOCKED**

Reason: MT5 is installed and connected, but not connected to MetaQuotes-Demo.

## Next Action

Manually verify whether MetaQuotes-Demo is available in the installed MT5
terminal. If unavailable after the retry policy is exhausted, classify OP-02 as
`METAQUOTES_ENVIRONMENT_UNAVAILABLE` and move to the next provider.
