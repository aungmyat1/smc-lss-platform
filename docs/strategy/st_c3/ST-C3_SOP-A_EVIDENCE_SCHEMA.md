# ST-C3 SOP-A Evidence Schema

**Strategy ID:** ST-C3  
**Scope:** SOP-A analytical extensions only  
**Status:** Governance draft, documentation-only  
**Authority:** [docs/RESEARCH-CHARTER/SOP_A_RCR.md](../../RESEARCH-CHARTER/SOP_A_RCR.md)

This document defines the proposed SOP-A evidence extensions for a future
ST-C3 revision after the required governance path is completed. It is
analysis-only, introduces no execution semantics, and adds no lifecycle logic.

It is aligned conceptually with the existing ST-C3 evidence model in
`validation/st_c3/evidence.py`, but it does not modify the active kernel,
evidence engine, state machine, or spec.

---

## Purpose

SOP-A extends the evidence model with analytical context that can annotate
pre-execution review without changing trade validity or runtime behavior.

If later approved through a versioned spec revision, these additions would
support richer evidence capture for:

- HTF analytical context
- Qualification gates
- Setup validation extensions
- Confirmation filters
- Deterministic Stage-A summary annotations

---

## Proposed Extension Shape

SOP-A would extend the existing ST-C3 evidence object with five new sections:

```text
{
    "htf_context": { ... },
    "qualification_gates": { ... },
    "setup_validation": { ... },
    "confirmation_filters": { ... },
    "sop_a_summary": { ... }
}
```

Each section is strictly analytical and documentation-only at this stage.

---

## 1. HTF Context Evidence

```text
htf_context: {
    "htf_bias": "bullish | bearish | neutral | undefined",
    "htf_bias_confidence": "high | medium | low",
    "htf_poi_type": "order_block | fvg | breaker | none",
    "htf_poi_location": "price_level or null",
    "draw_on_liquidity": "buy_side | sell_side | none",
    "htf_notes": "string (optional)"
}
```

### Purpose

Captures the frozen analytical HTF state used by SOP-A.

### Governance Notes

- No lifecycle state machine introduced.
- No execution logic introduced.
- Pure analysis only.

---

## 2. Qualification Gates Evidence

```text
qualification_gates: {
    "session_gate": {
        "pass": true | false,
        "session": "london | new_york | asia | none",
        "reason": "string"
    },
    "news_gate": {
        "pass": true | false,
        "impact": "high | medium | low | none",
        "reason": "string"
    },
    "spread_gate": {
        "pass": true | false,
        "spread": "float",
        "threshold": "float",
        "reason": "string"
    },
    "daily_risk_gate": {
        "pass": true | false,
        "current_loss": "float",
        "limit": "float",
        "reason": "string"
    }
}
```

### Purpose

Captures environmental qualification before setup validation.

### Governance Notes

All gates produce PASS/FAIL plus reason; they do not produce execution
decisions.

---

## 3. Setup Validation Evidence

```text
setup_validation: {
    "poi_arrival": {
        "valid": true | false,
        "distance_to_poi": "float",
        "reason": "string"
    },
    "order_block": {
        "valid": true | false,
        "fresh": true | false,
        "mitigated": true | false,
        "reason": "string"
    },
    "fvg": {
        "valid": true | false,
        "gap_size": "float",
        "filled": true | false,
        "reason": "string"
    },
    "liquidity": {
        "valid": true | false,
        "liquidity_type": "internal | external | equal_highs | equal_lows | none",
        "reason": "string"
    }
}
```

### Purpose

Extends existing ST-C3 validators with richer analytical evidence.

### Governance Notes

- No execution logic introduced.
- No lifecycle logic introduced.

---

## 4. Confirmation Filters Evidence

```text
confirmation_filters: {
    "sweep": {
        "detected": true | false,
        "sweep_type": "swing | internal | external | none",
        "reason": "string"
    },
    "choch": {
        "detected": true | false,
        "direction": "bullish | bearish | none",
        "reason": "string"
    },
    "mss": {
        "detected": true | false,
        "impulse_strength": "float",
        "reason": "string"
    },
    "ote": {
        "identified": true | false,
        "retracement_percent": "float",
        "zone": "62-79 | outside | none",
        "reason": "string"
    }
}
```

### Purpose

Captures analytical confirmation signals.

### Governance Notes

OTE is analytical only here. This document does not propose OTE execution
semantics and does not alter the frozen S7 runtime behavior.

---

## 5. SOP-A Summary Block

```text
sop_a_summary: {
    "sop_a_pass": true | false,
    "rejection_reason": "string or null",
    "confidence_score": "float (0.0 - 1.0)",
    "notes": "string (optional)"
}
```

### Purpose

Provides a single deterministic summary of SOP-A analytical conformance.

### Governance Notes

This summary does not block execution. It annotates evidence only.

---

## 6. Analytical Rejection Codes

These codes are proposed as analytical annotations only. They do not affect
execution, trade validity, or lifecycle transitions unless a future approved
spec explicitly says otherwise.

```text
rejection_codes: [
    "SOPA_SESSION_FAIL",
    "SOPA_NEWS_FAIL",
    "SOPA_SPREAD_FAIL",
    "SOPA_RISK_FAIL",
    "SOPA_HTF_BIAS_INVALID",
    "SOPA_POI_INVALID",
    "SOPA_POI_NOT_TOUCHED",
    "SOPA_OB_INVALID",
    "SOPA_FVG_INVALID",
    "SOPA_LIQUIDITY_INVALID",
    "SOPA_SWEEP_MISSING",
    "SOPA_CHOCH_MISSING",
    "SOPA_MSS_MISSING",
    "SOPA_ANALYTICAL_OTE_INVALID"
]
```

---

## Summary

This SOP-A evidence schema:

- Matches the RCR scope in `docs/RESEARCH-CHARTER/SOP_A_RCR.md`
- Introduces no execution logic
- Introduces no lifecycle logic
- Remains Stage-A analytical only
- Is ready to support a future `specs/st-c3_v1.0.8.yaml` draft

## Non-Authorization Notice

This document does not authorize:

- Kernel changes
- Evidence engine changes
- State-machine changes
- Spec promotion
- Backtesting
- Execution logic
- Demo trading
- Live trading

Those remain gated behind explicit owner approval and a future accepted
versioned spec revision.
