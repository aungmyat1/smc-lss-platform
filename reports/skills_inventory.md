# Skills Inventory — SMC Trading Platform (re-run)
Generated: 2026-07-16 | Verified programmatically: frontmatter + 9 required sections per skill

## Structural validation result
- Total skills: **23** (18 required atomic + 5 orchestrators)
- Required-18 present: **18 / 18** — none missing
- Valid YAML frontmatter: **23 / 23**
- All 9 required sections (Purpose, Inputs, Outputs, Workflow, Decision rules, Validation checklist, Failure handling, Examples, Acceptance criteria): **23 / 23** (0 missing sections)

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
| execution/mt5-trading | PROVEN (dry-run) | live send needs demo | bind demo account |
| journaling | ACTIVE | no persistent store yet | write data/journal.xlsx on close |

## Conflicts
None detected. Orchestrator names differ from atomics; no trigger collisions observed
in live testing (strategy-validator fired cleanly).
