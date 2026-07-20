# ST-C1 Root Cause Analysis

## 1. Current Strategy Summary

- Name: London SMC Reversal
- Timeframes: H1 bias, M5 execution
- Active sessions: London, NewYork
- Realized funnel: a single composite `OB+FVG` path with sweep and H1 bias gating.

## 2. Statistical Diagnostics

- Combined trades: `202`
- Win rate: `19.802`
- Profit factor: `0.1315`
- Expectancy: `-2.6834R`
- Sharpe ratio: `-0.6973`
- Max drawdown: `-568.1055R`

## 3. Failure Analysis

- EURUSD is the failing symbol: 97 trades, 0 net winners, PF 0.0000.
- XAUUSD is the surviving symbol: 105 trades, 38.1% win rate, PF 1.2622.
- The same composite gate is used on both symbols, so the divergence is not caused by a distinct sub-setup branch.

## 4. Root Cause Ranking

1. **Execution model issue [Critical]**
- The validation path uses a fixed point-size/spread model for both symbols, which is inconsistent with the symbol metadata already present in `config/watchlist.yaml`.
- Evidence: EURUSD gross winners all became net losers; XAUUSD did not.

2. **Market-specific behavior [High]**
- The strategy has demonstrable positive behavior on XAUUSD but not on EURUSD, so the strategy is symbol-dependent.

3. **Trade-management instrumentation gap [Medium]**
- Break-even / partial / trailing mechanics are part of the contract but are not represented in the replay telemetry, limiting diagnostic power.

## 5. Evidence

- `reports/ST-C1_REAL_DATA_STATISTICAL_VALIDATION.md` shows EURUSD PF 0.0000 and XAUUSD PF 1.2622.
- `reports/ST-C1_TRADE_LOG.csv` records every trade with session, regime, and outcome.
- `reports/ST-C1_FAILURE_CLUSTERS.md` shows 31 gross EURUSD winners converted into net losers by cost drag.

## 6. Proposed Hypothesis

- Hypothesis: the current strategy is not universally invalid; it is a symbol-dependent composite funnel whose apparent EURUSD failure is amplified by the replay execution model.

## 7. Single Rule Change

- Do not change multiple rules at once.
- First correction: make execution/risk validation symbol-aware in the validation path so the funnel is measured correctly.
- Second experiment, if measurement still supports it: restrict the strategy to the symbol/regime that survives the funnel, rather than forcing one rule set across all instruments.

## 8. Expected Impact

- Accurate measurement of EURUSD cost drag.
- More realistic XAUUSD PF once symbol metadata is honored.
- Clearer decision on whether the strategy should be split by symbol.

## 9. Risks

- Symbol-filtering too early can become a form of curve fitting if not revalidated out-of-sample.
- Changing execution assumptions may reduce the apparent edge of XAUUSD; that is acceptable if it reflects reality.

## 10. Validation Plan

1. Correct the validation/execution metadata path so each symbol uses its own pip/point/tick assumptions.
2. Rerun EURUSD and XAUUSD through the same cached replay framework.
3. Re-measure the funnel by market regime, session, and symbol.
4. Accept only if the improvement persists out-of-sample and across walk-forward windows.

## 11. Success Criteria

- Metric improvement is real after symbol-aware execution is applied.
- The surviving symbol shows stable PF/Sharpe/expectancy under walk-forward and OOS splits.
- No single month or regime explains the entire edge.

## 12. Rollback Criteria

- If symbol-aware execution removes the edge entirely, do not force the strategy.
- If the edge depends on one exceptional window, reject the refinement.

## 13. Research Priority

- P0: fix measurement fidelity before any strategy change.
- P1: decide whether the strategy should be split by symbol after honest measurement.

## 14. Confidence Score

- High confidence that execution modeling is distorting EURUSD.
- Medium confidence that XAUUSD remains a viable branch after measurement correction.

## 15. Recommendation

- Recommendation: **do not optimize yet**.
- First repair the execution validation path, then decide whether the evidence supports a symbol split.
