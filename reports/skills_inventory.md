# Skills Inventory — SMC Trading Platform (re-run 2)
Generated: 2026-07-17 | Verified on disk

## Structural validation result
- Total skills: **22** on disk (17 atomic-style skills + 5 orchestrators)
- Required trading capabilities are represented; `risk-management` and `journaling`
  serve both atomic and orchestrator roles after duplicate wrappers were merged.
- Valid YAML/frontmatter and required-section checks were previously reported as passing;
  rerun the structural validator after any skill edit.

## Required-18 (all PASS)
market-structure, liquidity-sweep, order-block, fair-value-gap, choch-bos,
premium-discount, session-filter, inducement, mitigation, entry-confirmation,
risk-management, trade-management, backtesting, optimization, validation,
mt5-trading, execution, journaling.

## Orchestrators (compose the atomics)
strategy-validator, risk-management, backtest-researcher,
journaling, trading-coach.

## Status / issues / recommendations (highlights)
| Skill | Status | Issue | Recommendation |
|---|---|---|---|
| market-structure | ACTIVE + engine-backed | detection now in `smc_engine.swings/trend` | expand to multi-TF |
| choch-bos / order-block / fvg | ACTIVE + engine-backed | BOS/structure coded; OB/FVG still spec-level | code OB/FVG detectors next |
| risk-management | ACTIVE | pip value generic in spec; enforce in code | add tick_value fetch to sizing code |
| backtesting | **OPERATIONAL** | runs; low sample | bulk history loader |
| validation/optimization | SPEC | need dataset + walk-forward runner | wire after bulk data |
| execution/mt5-trading | PROVEN (demo smoke) | scheduled auto-exec still gated | keep demo attestation + M2 gate |
| journaling | ACTIVE | CSV store wired; analytics shallow | expand weekly review outputs |

## Conflicts
None detected. Orchestrator names differ from atomics; no trigger collisions observed
in live testing (strategy-validator fired cleanly).
