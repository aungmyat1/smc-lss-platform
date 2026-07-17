# SMC-LSS Skill Architecture (3-layer + master)

Skills stay **flat** at `.claude/skills/<name>/` because Cowork/Claude Code
discovers skills one level deep — nesting under category folders would hide them
from the loader. The 3-layer structure below is therefore a **logical manifest**
(enforced by the `smc-trading-master` orchestrator), not a physical folder tree.

## Master
- `smc-trading-master` -> code: `src/smc_master.py` (ordered pipeline, stop-on-fail)

## Analysis layer (signal generation)
| Skill | Code | MCP/tool |
|---|---|---|
| session-filter | smc_master.session_of | clock |
| market-structure | smc_engine.swings/trend | metatrader candles |
| liquidity-sweep | smc_engine.liquidity_sweeps/pools | metatrader candles |
| choch-bos | smc_engine.swings + backtest.collect | metatrader candles |
| order-block | smc_engine.order_blocks | — |
| fair-value-gap | smc_engine.fvgs | — |
| premium-discount | smc_engine.equilibrium | — |
| inducement | (spec) | — |
| mitigation | (spec) | — |

## Execution layer (order handling)
| Skill | Code | MCP/tool |
|---|---|---|
| entry-confirmation | live_signal.latest_signal | metatrader candles |
| risk-management | live_signal.size | get_account_info/get_symbols |
| mt5-trading | (agent) | place_market_order |
| execution | execution_test.json (verified) | place/modify/close |
| trade-management | (spec) | modify_position |
| journaling | data/journal.csv | filesystem |

## Research layer (offline)
| Skill | Code | MCP/tool |
|---|---|---|
| backtesting | src/backtest.py | python + data/ |
| optimization | backtest --rr sweep (partial) | python |
| validation | src/validate.py | python + reports/ |

## Contract
Each analysis skill consumes candles and emits a typed result that the next
stage consumes (e.g. market-structure -> {trend, swing_high, swing_low}).
The master enforces order and passes outputs downstream.
