# ST-C1 Strategy Funnel

The professional framing below applies the attachment: treat SMC as a sequence of measurable evidence gates, not a list of indicators.

## Funnel View

| Stage | Status | EURUSD | XAUUSD | Evidence |
|---|---|---:|---:|---|
| Market Universe | PASS | 80,000 bars | 80,000 bars | Both symbols reached the full replay horizon. |
| Market Regime | PARTIAL | Negative in bull/bear and low/mid/high ATR | Positive in bull/bear and low/mid/high ATR | Post-hoc regime split shows symbol-specific behavior. |
| Session Filter | PASS | 97 trades | 105 trades | Only London/NewYork sessions were traded. |
| Higher Timeframe Bias | PASS | 97 trades | 105 trades | All realized trades obeyed the H1 bias gate. |
| POI | PASS/PARTIAL | 97 trades | 105 trades | All realized trades were the same composite `OB+FVG` path; no separate POI scoring in the replay log. |
| Liquidity Event | PASS | 97 trades | 105 trades | Recent sweep required before entry. |
| MSS / CHoCH | PARTIAL | 97 trades | 105 trades | Implicit via latest swing-break logic, not logged as an auditable state machine. |
| Entry Confirmation | PARTIAL | 97 trades | 105 trades | Entry is next-bar open after signal; no separate candle/volume/momentum telemetry. |
| Risk Validation | FAIL | 97 trades | 105 trades | Validation path uses fixed execution assumptions, not symbol-specific sizing. |
| Trade Execution | FAIL | Cost drag overwhelms EURUSD | Cost drag negligible | Validation path ignores symbol-specific pip metadata. |
| Trade Management | FAIL | None | None | No break-even / partial / trailing logic in replay. |
| Post-Trade Analytics | PASS | Completed | Completed | Trade log and root-cause reports generated from cache. |

## Funnel Statistics

- Realized trades: `202`
- Gross winners: `71`
- Net winners: `40`
- Composite setup coverage: `202/202` trades were `OB+FVG`

## Interpretation

- The funnel does not currently separate independent POI branches in the realized validation path; it collapses into one composite gate.
- EURUSD survives the earlier gates but fails the execution/risk layer.
- XAUUSD survives the entire funnel with positive expectancy, which is evidence for symbol-dependent edge rather than a universal failure.
