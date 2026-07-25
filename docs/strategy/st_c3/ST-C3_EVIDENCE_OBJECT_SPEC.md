# ST-C3 Evidence Object Specification

**Strategy ID:** ST-C3
**Status:** Pre-freeze draft foundation document

This specification is machine-ready, deterministic, and structured for direct
use by state machines, validator agents, trade-plan generators, governance
logs, and future backtest engines after the required governance gates authorize
those uses.

Every evidence object is atomic, traceable, and non-ambiguous.

---

## Universal Evidence Contract

Each funnel stage produces one or more evidence objects. Every evidence object
must contain:

| Field | Meaning |
|---|---|
| `id` | Unique identifier |
| `tf` | Source timeframe |
| `value` | Structural or numeric data, when the object needs a generic payload |
| `valid` | Boolean validity result |
| `reason` | Explanation when invalid or terminated |
| `timestamp` | Source bar time |
| `provenance` | Module/spec provenance, initially `STC3_v1` |

Object-specific fields below extend this universal contract.

---

## Evidence Objects

### 1. HTF Bias Evidence

`HTFBiasEvidence` represents directional macro structure.

```text
HTFBiasEvidence {
    id: str,
    tf: "H4",
    structure: "HHHL" | "LHLL" | "UNCLEAR",
    bias: "BULLISH" | "BEARISH" | "NONE",
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 2. Sweep Evidence

`SweepEvidence` represents HTF/MF liquidity sweep.

```text
SweepEvidence {
    id: str,
    tf: "H4" | "M15",
    sweep_type: "BUY_SIDE" | "SELL_SIDE",
    wick_penetration: bool,
    level: float,
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 3. Sweep Reclaim Evidence

`SweepReclaimEvidence` represents reclaim within `N_SWEEP` bars.

```text
SweepReclaimEvidence {
    id: str,
    tf: "H4" | "M15",
    reclaim_within_bars: int,
    max_allowed_bars: int,
    reclaimed: bool,
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 4. Displacement Evidence

`DisplacementEvidence` represents impulsive movement after sweep.

```text
DisplacementEvidence {
    id: str,
    tf: "M15",
    impulse_strength: float,
    threshold: float,
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 5. BOS Evidence

`BOSEvidence` represents structural break.

```text
BOSEvidence {
    id: str,
    tf: "M15",
    bos_direction: "UP" | "DOWN",
    body_close_break: bool,
    level: float,
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 6. BOS Extreme Lock Evidence

`BOSExtremeEvidence` locks BOS extreme only after pullback.

```text
BOSExtremeEvidence {
    id: str,
    tf: "M15",
    provisional_extreme: float,
    locked_extreme: float,
    pullback_detected: bool,
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 7. Dealing Range Evidence

`DealingRangeEvidence` defines origin to locked BOS extreme.

```text
DealingRangeEvidence {
    id: str,
    tf: "M15",
    origin: float,
    bos_extreme: float,
    range_size: float,
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 8. OTE Evidence

`OTEEvidence` represents premium/discount OTE zone.

```text
OTEEvidence {
    id: str,
    tf: "M15",
    ote_min: float,
    ote_max: float,
    price_in_ote: bool,
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 9. FVG Evidence

`FVGEvidence` represents fresh fair value gap evidence.

```text
FVGEvidence {
    id: str,
    tf: "H4" | "M15",
    gap_top: float,
    gap_bottom: float,
    fresh: bool,
    inside_ote: bool,
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 10. Order Block Evidence

`OrderBlockEvidence` represents institutional footprint evidence.

```text
OrderBlockEvidence {
    id: str,
    tf: "H4" | "M15",
    ob_high: float,
    ob_low: float,
    fresh: bool,
    inside_ote: bool,
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 11. LTF Confirmation Evidence

`LTFConfirmationEvidence` represents CHoCH/BOS inside the confluence zone.

```text
LTFConfirmationEvidence {
    id: str,
    tf: "M3" | "M1",
    choch_direction: "UP" | "DOWN",
    sweep_local_liquidity: bool,
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 12. Session Window Evidence

`SessionWindowEvidence` represents the allowed trading session.

```text
SessionWindowEvidence {
    id: str,
    tf: "M3" | "M1",
    session: "LONDON" | "NY" | "INVALID",
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 13. Entry Window Evidence

`EntryWindowEvidence` represents the `MAX_ENTRY_BARS` rule.

```text
EntryWindowEvidence {
    id: str,
    tf: "M3" | "M1",
    bars_since_ltf_choch: int,
    max_allowed_bars: int,
    inside_window: bool,
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 14. Invalidation Swing Evidence

`InvalidationSwingEvidence` represents structural invalidation for stop-loss
placement.

```text
InvalidationSwingEvidence {
    id: str,
    tf: "M3" | "M1",
    swing_level: float,
    direction: "LONG" | "SHORT",
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 15. Target Evidence

`TargetEvidence` represents liquidity objectives for TP1/TP2/TP3.

```text
TargetEvidence {
    id: str,
    tf: "H4" | "M15",
    target_type: "TP1_INTERNAL" | "TP2_EXTERNAL" | "TP3_HTF",
    level: float,
    rr: float,
    valid: bool,
    reason: str,
    timestamp,
    provenance: "STC3_v1"
}
```

### 16. Expiry Evidence

`ExpiryEvidence` represents termination conditions.

```text
ExpiryEvidence {
    id: str,
    tf: "M3" | "M1",
    expiry_reason: "BIAS_FLIP" | "ENTRY_WINDOW" | "SL_BREAK" | "SUPERSEDED",
    valid: false,
    timestamp,
    provenance: "STC3_v1"
}
```

---

## Governance Notes

- This document is a pre-freeze foundation document for ST-C3.
- It does not authorize implementation, backtesting, broker integration, demo
  trading, live trading, or production.
- `provenance: "STC3_v1"` is the draft evidence provenance label. S1-G1 may
  ratify or rename it before freeze.
