# ST-C3 Ultra-Fast Validation Funnel

**Date:** 2026-07-28
**Status:** Governance planning material; not an acceptance decision
**Strategy:** ST-C3 v1.0.7
**Current gate state:** S1-G5 and S1-G6 evidence gathered, neither accepted

## Purpose

This document adopts the ST-C3 continuous validation funnel as the next
governance-ready planning standard after the S1-G5/S1-G6 evidence review.
It preserves the v1.x freeze, keeps A3 blocked until explicitly opened,
and does not authorize execution, optimization, broker integration, demo,
live trading, or production.

## Fast-Track Flow

1. Review S1-G5 and S1-G6 in one consolidated evidence session.
2. Record two independent owner outcomes: one for S1-G5 and one for S1-G6.
3. If both gates are accepted, prepare the A3 opening decision packet.
4. Once A3 is explicitly opened, build one deterministic replay ledger.
5. Run baseline statistics directly from that replay ledger.
6. Run robustness from the same immutable ledger in parallel with statistics.
7. Run walk-forward / out-of-sample validation only after statistics and
   robustness both pass.
8. Keep execution-stage work blocked until A3 passes and a separate execution
   decision is made.

## Replay Ledger Standard

The replay ledger is the single source of truth for A3 validation. Each
trade record must include:

- entry
- exit
- R
- MAE
- MFE
- session
- news flag
- rationale
- win/loss

The ledger must be deterministic, complete, reproducible, and stable across
repeated runs from the same inputs.

## Replay Hashing Standard

- Compute a SHA-256 hash of the full replay ledger.
- Store the hash in the consolidated evidence packet header.
- Store the standalone hash at `evidence/st_c3/replay_hash.txt` when the A3
  replay ledger exists.
- Require statistics, robustness, and walk-forward outputs to reference the
  same replay hash.

## A3 Validation Rules

Baseline statistics must be computed directly from the replay ledger without
manual export or reformatting. The required metrics are expectancy, profit
factor, win rate, average R, maximum drawdown, recovery factor, Sharpe,
Sortino, and stability.

Robustness validation must use a threshold table at
`validation/st_c3/robustness_thresholds.yaml` before robustness results become
pass/fail authoritative. The table must cover spread, commission, slippage,
delayed fills, random trade removal, Monte Carlo reshuffles, yearly splits,
volatility regimes, and session slices.

Walk-forward / out-of-sample validation must use fixed-year slices unless an
owner decision records a different window method. It runs only after baseline
statistics and robustness both pass. The default pass criteria are non-negative
expectancy across windows and profit factor above 1.2 in the majority of
windows.

Stats and robustness engines must report their own version identifiers in all
A3 evidence outputs to prevent silent drift.

## Owner Decision Packet

The consolidated owner packet must include:

- S1-G5 gate evidence and recommended outcome
- S1-G6 gate evidence and recommended outcome
- replay hash, once an A3 replay ledger exists
- stats summary, once A3 statistics exist
- robustness matrix, once A3 robustness exists
- walk-forward / OOS results, if applicable
- explicit recommendation: accept, reject, or defer

The S1-G5/S1-G6 review should use a fixed 48-hour decision window. Outcomes:

- Accept: open the next permitted gate only if all preconditions are satisfied.
- Reject: revise strategy or evidence.
- Defer: freeze progression until a later owner decision.

## Governance Guardrails

- S7, S9, and S12 remain permanently excluded from v1.x.
- S1-G5 and S1-G6 remain separate governance decisions even when reviewed
  together.
- Evidence gathering does not imply acceptance.
- A3 remains blocked until explicitly opened.
- Execution, optimization, broker integration, demo, live trading, and
  production remain blocked until their own future owner decisions.
