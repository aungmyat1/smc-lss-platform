# ST-C1 Failure Clusters

| Cluster | Evidence | Impact |
|---|---|---|
| EURUSD cost-overwhelm | `31/31` gross winners converted to net losers; avg gross `-0.0420R`, avg cost `5.7218R`, net `-5.7638R`. | Costs dominate outcomes; profitable gross trades cannot survive the execution assumptions. |
| EURUSD stop streaks | Longest consecutive stop-loss streak: `10`. | The edge does not recover in streaky adverse conditions. |
| EURUSD regime weakness | Bullish H1 `-5.5789R`, bearish H1 `-5.9238R`; low ATR `-7.5283R`. | Failure is broad, not localized to one trend state. |
| XAUUSD viable cluster | Bullish H1 `0.0619R`, bearish H1 `0.2469R`; high ATR `0.2085R`. | Same funnel can work on gold under this replay. |
| XAUUSD stop streaks | Longest consecutive stop-loss streak: `9`. | Even the profitable symbol still experiences runs of losses, but they do not destroy expectancy. |
| Composite setup collapse | All `202` realized trades were `OB+FVG`. | The realized funnel lacks independent scoring of OB-only, FVG-only, CHoCH-only, or MSS-only branches. |

## Notes

- News periods were not joined into the replay cache, so there is no evidence-based news cluster classification in this pass.
- The current validation path does not expose per-trade management events, so break-even/partial/trailing clusters cannot be measured directly.
