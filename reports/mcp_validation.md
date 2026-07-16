# MCP Validation — Functional Tests
Generated: 2026-07-16 | Results are REAL. No test was fabricated. Blocked tests marked NOT IMPLEMENTED with reason.

## MetaTrader (read path) — executed live
| Test | Result | Evidence |
|---|---|---|
| Server responds | **PASS** | get_account_info returned data |
| Auth valid | **PASS** | real account fields populated |
| Account read | **PASS** | balance $988.12, 500x, USD |
| Symbols list | **PASS** | get_symbols(*EUR*) returned EURUSD + crosses |
| Live price | **PASS** | EURUSD bid/ask 1.1444 @ 18:37Z |
| Candles (H4/M15) | **PASS** | 30 H4 + 40 M15 bars returned |
| Positions read | **PASS** | 0 open positions |

## MetaTrader (write / execution path) — NOT executed (by policy)
| Test | Result | Reason |
|---|---|---|
| Place demo order | **NOT IMPLEMENTED** | Account is REAL, not demo. Placing test orders on a live account is unsafe and against operating policy. Requires a DEMO account first. |
| Modify position (SL/TP) | **NOT IMPLEMENTED** | Depends on an open test position on a demo account. |
| Cancel order | **NOT IMPLEMENTED** | Same as above. |
| Close position | **NOT IMPLEMENTED** | Same as above. |

## Infra MCP tests
| Test | Result | Reason |
|---|---|---|
| Read file | **PASS** | bash/Read verified against outputs |
| Write file | **PASS** | reports written successfully |
| Execute Python | **PASS (capability)** | bash sandbox has python3 |
| Git status/commit/push | **NOT IMPLEMENTED** | No repo connected; GitHub MCP needs auth |
| Redis / Postgres / Docker / WebSocket | **NOT IMPLEMENTED** | Servers not present |

## Error / retry / timeout handling
**NOT IMPLEMENTED (untestable here):** these require deliberate fault injection
against each server and a repo harness. No evidence exists → not claimed.

## Summary
Read/market-data path across MetaTrader is fully operational and verified. The
execution path is intentionally unproven pending a demo account. Infra beyond the
sandbox is largely absent.
