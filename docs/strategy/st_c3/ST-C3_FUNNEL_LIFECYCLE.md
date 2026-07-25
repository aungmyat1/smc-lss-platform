# ST-C3 Funnel Lifecycle

**Strategy ID:** ST-C3
**Status:** Pre-freeze draft foundation document

This document defines the ordered ST-C3 funnel lifecycle. It is the behavioral
skeleton that the state machine, validator, evidence layer, and future
trade-plan generator must follow after S1-G1 freeze and later implementation
authorization.

---

## Ordered Lifecycle

| Order | Stage | Required output |
|---|---|---|
| 1 | HTF Bias (H4) | Detect HH/HL or LH/LL structure; lock bias until HTF CHoCH; no counter-bias trades | `HTF_BIAS_ID` |
| 2 | External Liquidity Sweep (H4/M15) | Wick must penetrate HTF liquidity and violate the level | `SWEEP_ID` |
| 3 | Sweep Reclaim | Price must close back inside range within `N_SWEEP` bars | `SWEEP_RECLAIM_ID` |
| 4 | Displacement and Provisional BOS (M15) | Strong displacement; BOS requires body-close break; BOS extreme remains provisional | `DISPLACEMENT_ID`, `BOS_ID` |
| 5 | BOS Extreme Locking | BOS extreme locks only after first structural pullback | `BOS_EXTREME_ID` |
| 6 | Dealing Range Definition | Range equals origin to locked BOS extreme | `DEALING_RANGE_ID` |
| 7 | OTE Zone | 62-79%; shorts only in premium OTE; longs only in discount OTE | `OTE_ZONE_ID` |
| 8 | FVG / Order Block Confluence (H4/M15) | Fresh, unmitigated, inside OTE, aligned with HTF bias | `FVG_ID`, `ORDERBLOCK_ID` |
| 9 | LTF CHoCH/BOS Confirmation (M3/M1) | Shorts sweep local highs then CHoCH/BOS down; longs sweep local lows then CHoCH/BOS up | `LTF_CHOCH_ID` |
| 10 | Session Gatekeeper | LTF confirmation valid only in London or NY windows; otherwise reject with `ST-C3-R6` | `SESSION_WINDOW_ID` |
| 11 | Entry Window Activation | Entry must occur within `MAX_ENTRY_BARS` after LTF CHoCH; zone is MF/LTF FVG or refined OB | `ENTRY_WINDOW_ID`, `ENTRY_ZONE_ID` |
| 12 | Structural Invalidation Stop | SL is the invalidation swing that formed CHoCH | `INVALIDATION_SWING_ID` |
| 13 | Liquidity-Based Targets | TP1 internal liquidity at or above configured minimum RR; TP2 external liquidity; TP3 HTF objective | `TP1_ID`, `TP2_ID`, `TP3_ID` |
| 14 | Expiry Logic and ERR Codes | Terminate on bias flip, entry-window expiry, SL invalidation, or superseded setup | `EXPIRY_ID` |

---

## Determinism Rules

- Each transition is binary: pass advances to the next stage, fail emits a
  rejection or termination enum.
- A later stage cannot create valid evidence unless every required prior stage
  is valid.
- BOS is provisional until the first pullback locks the BOS extreme.
- OTE is computed from the swing origin to the locked BOS extreme.
- Session validation must pass before entry activation.
- A valid funnel must emit exactly one `TRADE_PLAN` object.
- Expiry can terminate a setup before or after signal creation.

---

## Open S1-G1 Decisions

- Exact `N_sweep` reclaim limit.
- Symbol scope.
- Final London and NY session windows.
- Low-liquidity filter policy.
- Entry window `MAX_BARS`.
- FVG/OB freshness.
- SL buffer.
- TP2 and TP3 minimum RR rules.
- Volatility and spread context rules.

---

## Termination Codes

| Trigger | Canonical code |
|---|---|
| HTF bias flips | `ST-C3-ERR_HTF_BIAS_FLIP` |
| Entry window expires | `ST-C3-ERR_ENTRY_WINDOW_EXPIRED` |
| SL invalidation breaks | `ST-C3-ERR_SL_INVALIDATION` |
| Newer sweep/BOS appears | `ST-C3-ERR_SUPERSEDED_SETUP` |
