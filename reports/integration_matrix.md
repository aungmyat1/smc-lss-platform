# Skill-to-MCP Integration Matrix (re-run 2)
Generated: 2026-07-17 | ✅ works · 🟡 limited · ❌ broken

| Skill | Needs | Binding | Status | Note |
|---|---|---|---|---|
| market-structure / choch-bos | candles | smc_engine + metatrader.get_candles_latest | ✅ | engine computes swings/BOS deterministically |
| strategy-validator | multi-check | atomics + MCP reads | ✅ | live-fired; INVALID/stand-aside verdict verified |
| risk-management | account, symbol specs | metatrader.get_account_info/get_symbols | 🟡 | sizing works; per-symbol tick_value to add in code |
| execution / mt5-trading | order placement | place_market_order→modify_position | 🟡 | one demo round trip verified; scheduled auto-exec still gated |
| backtesting | historical data + python | smc_engine + data/*.csv + bash python | ✅ | operational; low sample |
| optimization / validation | dataset, splits | backtest engine | 🟡 | runner pending bulk data |
| journaling | closed trades + store | get_deals + csv | 🟡 | CSV store wired; analytics/review loop still shallow |
| trading-coach | overtrading check | get_deals | ✅ | read-only |

## Target pipelines
- Market Structure → Data → Python → Results: **✅** (engine + backtest run).
- Risk → Position Calc → MT5 → Execution: **🟡** (calc+reads ✅; one demo round trip ✅; scheduled auto-exec gated).
- Backtesting → Python → Dataset → Statistics: **✅ (low-sample)**.

## Missing integrations
1. Bulk historical loader (unblocks conclusive backtest).
2. Journal analytics/review workflow.
3. Coded OB/FVG/liquidity detectors (currently spec-level).
