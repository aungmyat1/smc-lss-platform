# MCP Validation — Functional Tests (re-run 3)
Generated: 2026-07-17 | Real results. Nothing fabricated. Blocked = NOT IMPLEMENTED + reason.

## MetaTrader read path — executed live/demo
| Test | Result | Evidence |
|---|---|---|
| Server responds / auth | **PASS** | get_account_info returned real data |
| Account read | **PASS** | VTMarkets-Demo login 1144985, ~$988, 500x, USD |
| Symbols / price | **PASS** | EURUSD + crosses; bid/ask 1.14426 |
| Candles H1/H4/M15 | **PASS** | 500 H1 + H4/M15 pulled |
| Positions read | **PASS** | 0 open |

## MetaTrader write/execution path — executed once on demo
| Test | Result | Evidence |
|---|---|---|
| Place demo order | **PASS** | EURUSD-VIP 0.01 BUY filled, retcode 10009 |
| Modify SL/TP | **PASS** | SL 1.14164 / TP 1.14764 attached |
| Close position | **PASS** | position closed, account returned flat |
| Journal/deals read | **PASS** | entry+exit deals recorded, round-trip P/L -0.13 |

## Infra tests
| Test | Result | Evidence |
|---|---|---|
| Read file | **PASS** | audit read 22 skill directories |
| Write file | **PASS** | reports + code written (via sandbox heredoc) |
| Execute Python | **PASS** | backtest + smoke tests ran |
| Smoke tests | **PASS** | pytest: 12 passed |
| Backtest run | **PASS (low-sample)** | status LOW_SAMPLE, 1 trade, +2.0R on 92 bars |
| Git status/commit | **PASS** | git history present; `.git/index.lock` absent on 2026-07-17 |
| Redis/Postgres/Docker/WebSocket | **NOT IMPLEMENTED** | servers absent |

## Error / retry / timeout handling
**NOT IMPLEMENTED (untested):** no fault-injection harness. Note: the code sandbox
itself showed intermittent timeouts during this session (infra flakiness, not repo).
