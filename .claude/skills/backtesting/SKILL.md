---
name: backtesting
description: >-
  Deterministic backtest engine spec + runner. Trigger on 'backtest', 'run
  backtest', 'test the strategy'.
---

# backtesting

## Purpose
Replay a deterministic SMC-LSS spec over historical data and produce trade-by-trade results and metrics.

## Inputs
- historical candles (data/ or MT5 export)
- versioned strategy spec
- costs: spread, commission, slippage

## Outputs
- trades list, equity curve, metrics (expectancy R, PF, win%, maxDD, #trades)

## Workflow
1. Load dataset (data/<symbol>_<tf>.csv).
2. Iterate bars; apply atomic skills' rules deterministically.
3. Simulate entries/stops/targets with costs.
4. Output metrics + equity curve to reports/.

## Decision rules
- Same data + same spec => identical results (seedless determinism).
- Include costs always.

## Validation checklist
- [ ] dataset present and validated
- [ ] costs applied
- [ ] >= 30 trades before drawing conclusions

## Failure handling
- No dataset -> NOT IMPLEMENTED, request data (do not fabricate).
- <30 trades -> report low-sample warning.

## Examples
python src/backtest.py --spec specs/v1.yaml --data data/EURUSD_H4.csv -> expectancy, PF, maxDD.

## Acceptance criteria
- [ ] Reproducible metrics file written
- [ ] no look-ahead bias (bar-close only)
