# ST-C3 Parameter Sheet

**Strategy ID:** ST-C3
**Status:** Pre-freeze draft parameter sheet

This sheet records the current machine-ready ST-C3 parameter set. Values marked
provisional or configurable must be ratified during S1-G1 before the strategy
can freeze.

---

## Sweep Parameters

| Parameter | Value | Status |
|---|---|---|
| `N_SWEEP` | `1-3` bars on the sweep timeframe | Provisional |
| `SWEEP_WICK_PENETRATION` | `true` | Owner-defined |
| `SWEEP_CLOSE_RECLAIM` | `required` | Owner-defined |

---

## BOS Parameters

| Parameter | Value | Status |
|---|---|---|
| `BOS_BODY_CLOSE` | `true` | Owner-defined |
| `BOS_EXTREME_LOCK` | `FIRST_PULLBACK` | Owner-defined |
| `BOS_MIN_IMPULSE` | configurable | Unresolved |

---

## OTE Parameters

| Parameter | Value | Status |
|---|---|---|
| `OTE_MIN` | `0.62` | Provisional |
| `OTE_MAX` | `0.79` | Provisional |
| `OTE_REQUIRE_LOCKED_BOS` | `true` | Owner-defined |

---

## Session Parameters

| Parameter | Value | Status |
|---|---|---|
| `SESSION_LONDON` | `07:00-10:00 UTC` | Provisional |
| `SESSION_NY` | `13:00-16:00 UTC` | Provisional |
| `SESSION_REQUIRED_FOR_LTF` | `true` | Owner-defined |

---

## Entry Window Parameters

| Parameter | Value | Status |
|---|---|---|
| `MAX_ENTRY_BARS` | `3-5` M3 bars | Provisional |
| `ENTRY_ZONE` | FVG or OB | Owner-defined |
| `ENTRY_CONFIRMATION` | LTF CHoCH | Owner-defined |

---

## SL/TP Parameters

| Parameter | Value | Status |
|---|---|---|
| `SL` | `INVALIDATION_SWING` | Owner-defined |
| `TP1` | `INTERNAL_LIQUIDITY` | Owner-defined |
| `TP2` | `EXTERNAL_LIQUIDITY` | Owner-defined |
| `TP3` | `HTF_OBJECTIVE` | Owner-defined |
| `MIN_RR` | configurable, example `3R` | Provisional |

---

## Expiry Parameters

| Parameter | Value | Status |
|---|---|---|
| `EXPIRY_ON_BIAS_FLIP` | `true` | Owner-defined |
| `EXPIRY_ON_NEW_SWEEP` | `true` | Owner-defined |
| `EXPIRY_ON_ENTRY_WINDOW_CLOSE` | `true` | Owner-defined |
| `EXPIRY_ON_SL_BREAK` | `true` | Owner-defined |
