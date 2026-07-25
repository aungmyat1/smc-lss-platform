# ST-C3 Strategy Architecture

**Strategy ID:** ST-C3
**Strategy type:** Next-generation SMC funnel, refined deterministic model
**Execution mode:** Multi-timeframe, rule-based, machine-executable
**Goal:** Improve ST-C2 by hardening edge cases around time, session,
volatility, structural locking, sweep reclaim, BOS extreme locking, entry
expiry, and post-signal termination while keeping full SMC alignment.
**Status:** Pre-freeze draft; ready for full S1-G1 specification review

This document is one of the four mandatory ST-C3 foundation documents. It does
not freeze the strategy, authorize implementation, authorize backtesting, or
grant execution authority.

---

## Identity

| Field | Value |
|---|---|
| Strategy ID | ST-C3 |
| Type | Next-generation SMC funnel |
| Mode | Multi-timeframe, rule-based, machine-executable |
| Lifecycle state | Pre-freeze -> ready for full specification review |
| Authority | Documentation/governance only |

ST-C3 is intentionally separate from ST-C2. ST-C3 does not mutate, supersede,
pause, approve, or reject ST-C2.

---

## Timeframe And Session Stack

| Layer | Role |
|---|---|
| H4 | Bias, macro structure, HTF liquidity, sweep context |
| M15 | Sweep, displacement, BOS, dealing range, OTE, FVG/OB |
| M3/M1 | CHoCH/BOS confirmation, invalidation swing, entry window |

Session layer:

- London window: `07:00-10:00 UTC` provisional.
- NY window: `13:00-16:00 UTC` provisional.
- Optional low-liquidity filters: late Asian and pre-close filters unresolved.

---

## Core Modules

| Module | Responsibility |
|---|---|
| PM/governance agent | Track ST-C3 as a separate candidate from pre-freeze through freeze and validation |
| Validator agent | Enforce funnel stages, session filters, rejection codes, termination codes, evidence IDs, expiry logic, and thresholds |
| Execution agent | Future Stage B consumer of ST-C3 trade plans only after approval |
| Journal/analytics agent | Future logger for enums, sessions, RR, win-rate drift, spread context, and volatility context |
| Funnel state machine | Enforce ordered progression through all funnel stages |
| Evidence layer | Create stable evidence objects consumed by later stages |
| Trade-plan generator | Produce `TRADE_PLAN` for valid setups |

---

## Machine-Ready Components

- State machine.
- ST-C3 rejection codes and termination enums.
- Evidence IDs.
- Numeric thresholds.
- Session filters.
- Sweep reclaim bar limits.
- BOS extreme locking rules.
- Entry window bar limits.
- SL/TP rules.
- Expiry logic.

---

## Authority Boundary

Allowed under the current milestone:

- Documentation and governance setup.
- Owner review of unresolved thresholds and provisional values.
- Preparation of an S1-G1 freeze audit package.

Not allowed under the current milestone:

- ST-C3 implementation code.
- ST-C3 backtests or existence scans.
- Broker, demo, live, or production execution.
- Mutation of frozen ST-C2 strategy content.
