# ST-C1 Normalization Report

## Summary

The SMC-LSS v3.6 strategy source has been normalized into the candidate
strategy contract `strategies/candidates/ST-C1_v1.yaml`.

Converted areas:

- strategy identity and source mapping
- market universe and timeframe constraints
- swing, BOS, and CHoCH structure rules
- liquidity pool and sweep rules
- order block, fair value gap, and premium/discount rules
- entry sequence and invalidation logic
- stop loss, take profit, and management rules
- risk contract and machine validation checklist

The output is candidate-only and remains unapproved.

## Remaining Ambiguities

No blocking ambiguities remain for deterministic implementation.

Items intentionally deferred to later milestones:

- backtesting and validation
- approval gating
- execution-layer buildout
- MT5 connectivity
- live trading eligibility

## Normalization Status

READY_FOR_BACKTEST

