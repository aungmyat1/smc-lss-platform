# ST-C1 Research Contract

## Purpose

This document records the deterministic normalization of the SMC-LSS v3.6
strategy source into the candidate contract `ST-C1`.

## Source Alignment

- Source strategy: `docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md`
- Execution authority: `specs/v1.yaml`
- Research authority: `specs/v3.6.yaml`
- Candidate contract: `strategies/candidates/ST-C1_v1.yaml`

## Summary

The v3.6 source has been normalized into a deterministic candidate contract
with explicit:

- strategy identity
- market universe
- structure rules
- liquidity rules
- POI rules
- entry rules
- exit rules
- risk contract
- machine validation checklist

The contract removes discretionary wording from the source by converting the
core trading concepts into boolean rules and explicit trade actions.

## Normalization Notes

- Swing confirmation is fixed at `k=2` bars.
- BOS and CHoCH are defined by candle-close break conditions.
- Liquidity sweeps are defined by wick penetration plus recovery.
- Order blocks are defined as the last opposite-color candle before BOS.
- FVGs are defined by three-candle imbalance conditions.
- Premium and discount are defined relative to the dealing-range midpoint.
- Entry requires a complete boolean sequence and uses next-bar-open execution.
- Risk is explicit and configuration-driven.

## Remaining Ambiguities

None blocking for backtest preparation.

The following items remain intentionally outside M1 scope:

- backtest evidence
- approval decision
- execution-layer implementation
- broker integration
- live promotion

## Normalization Status

READY_FOR_BACKTEST

