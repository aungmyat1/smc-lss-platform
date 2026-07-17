# MCP Validation — Functional Tests (re-run)
Generated: 2026-07-16 | Real results. Nothing fabricated. Blocked = NOT IMPLEMENTED + reason.

## MetaTrader read path — executed live
| Test | Result | Evidence |
|---|---|---|
| Server responds / auth | **PASS** | get_account_info returned real data |
| Account read | **PASS** | $988.12, 500x, USD |
| Symbols / price | **PASS** | EURUSD + crosses; bid/ask 1.14426 |
| Candles H1/H4/M15 | **PASS** | 500 H1 + H4/M15 pulled |
| Positions read | **PASS** | 0 open |

## MetaTrader write/execution path — NOT executed (policy)
| Test | Result | Reason |
|---|---|---|
| Place demo order | **NOT IMPLEMENTED** | account is REAL not demo; unsafe. Needs demo binding. |
| Modify/cancel/close | **NOT IMPLEMENTED** | depends on a demo test position |

## Infra tests
| Test | Result | Evidence |
|---|---|---|
| Read file | **PASS** | audit read 23 skills |
| Write file | **PASS** | reports + code written (via sandbox heredoc) |
| Execute Python | **PASS** | backtest + smoke tests ran |
| Smoke tests | **PASS** | pytest: 3 passed |
| Backtest run | **PASS (low-sample)** | status LOW_SAMPLE, 1 trade, +2.0R on 92 bars |
| Git status/commit | **WARNING** | commits exist; a user-side `.git/index.lock` blocked a commit from the sandbox |
| Redis/Postgres/Docker/WebSocket | **NOT IMPLEMENTED** | servers absent |

## Error / retry / timeout handling
**NOT IMPLEMENTED (untested):** no fault-injection harness. Note: the code sandbox
itself showed intermittent timeouts during this session (infra flakiness, not repo).
