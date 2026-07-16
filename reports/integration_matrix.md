# Skill-to-MCP Integration Matrix
Generated: 2026-07-16 | ✅ works · 🟡 works but limited · ❌ broken/missing

| Skill | Needs | Bound tool(s) | Status | Note |
|---|---|---|---|---|
| strategy-validator | live candles, price | metatrader: get_candles_latest, get_symbol_price | ✅ | Verified live on EURUSD |
| risk-manager | account, price, symbol specs | metatrader: get_account_info, get_symbol_price, get_symbols | 🟡 | Works; needs per-symbol tick_value for correct sizing on metals/JPY |
| risk-manager (execute) | order placement | metatrader: place_market_order → modify_position | 🟡 | Path exists; NOT tested (real account, no demo) |
| trade-journal-analyst | closed trades, storage | metatrader: get_deals, get_orders + xlsx/CSV | 🟡 | Trade read works; no persistent journal store wired |
| backtest-researcher | historical dataset, compute | data feed + bash(python) | ❌ | No historical data source connected → non-operational |
| trading-coach | overtrading check | metatrader: get_deals | ✅ | Read-only; fine |

## Target pipelines (spec) vs reality
- Market Structure → Data → Python → Results: **🟡** — candles via MCP OK; no dedicated historical store; Python via sandbox OK.
- Risk → Position Calc → MT5 → Execution: **🟡** — calc + MT5 reachable; execution unproven (no demo).
- Backtesting → Python → Dataset → Stats: **❌** — dataset missing.

## Missing integrations to build
1. Historical-data connector for backtest-researcher (highest impact).
2. Persistent journal store (xlsx in outputs, or SQLite in sandbox).
3. Demo-account binding for the execution path so risk-manager can be end-to-end tested.
