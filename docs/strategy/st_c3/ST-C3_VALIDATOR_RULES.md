# ST-C3 Validator Rules

**Strategy ID:** ST-C3
**Status:** Pre-freeze draft foundation document

These rules define how the future ST-C3 validator agent enforces the state
machine, evidence objects, rejection codes, termination codes, and trade-plan
schema. They are implementation-ready for future Python, MQL5, or governance
validator work after implementation is authorized.

---

## Validator Layers

The validator enforces three layers:

- Stage guards: each state must satisfy its evidence conditions.
- Rejection codes: R-codes for pre-entry failures.
- Termination codes: ERR-codes for post-entry failures.

The validator is stateless per tick, but stateful per setup, tracking the active
funnel state.

---

## Global Principles

### Deterministic Evaluation

- Every state has one guard.
- If a guard fails, exactly one R-code is emitted.
- After `S13_TRADE_PLAN_EMIT`, only ERR-codes are allowed.

### Evidence-Driven

- The validator never computes structure.
- The validator only checks `evidence.valid` and evidence fields.
- Evidence is produced by detection modules.

### No Discretion

- No fuzzy logic.
- No probability thresholds.
- No confidence scores.
- Only boolean guards and numeric comparisons.

---

## State-Level Rules

| State | Guard | Reject / Output |
|---|---|---|
| `S1_HTF_BIAS` | `HTFBiasEvidence.valid == true` | `R1_HTF_BIAS_UNCLEAR` |
| `S2_SWEEP` | `SweepEvidence.valid == true` | `R2_NO_SWEEP` |
| `S3_SWEEP_RECLAIM` | `SweepReclaimEvidence.valid == true AND SweepReclaimEvidence.reclaimed == true` | `R2_NO_SWEEP` |
| `S4_DISPLACEMENT_BOS` | `DisplacementEvidence.valid == true AND BOSEvidence.valid == true` | `R3_NO_DISPLACEMENT_BOS` |
| `S5_BOS_EXTREME_LOCK` | `BOSExtremeEvidence.valid == true AND BOSExtremeEvidence.pullback_detected == true` | `R3_NO_DISPLACEMENT_BOS` |
| `S6_DEALING_RANGE` | `DealingRangeEvidence.valid == true` | `R4_NO_OTE_PULLBACK` |
| `S7_OTE` | `OTEEvidence.valid == true AND OTEEvidence.price_in_ote == true` | `R4_NO_OTE_PULLBACK` |
| `S8_FVG_OB_CONFLUENCE` | `(FVGEvidence.valid == true OR OrderBlockEvidence.valid == true) AND inside_ote == true` | `R5_NO_FVG_OB_CONFLUENCE` |
| `S9_LTF_CONFIRMATION` | `LTFConfirmationEvidence.valid == true AND LTFConfirmationEvidence.sweep_local_liquidity == true` | `R6_NO_LTF_CONFIRMATION` |
| `S10_SESSION_GATEKEEPER` | `SessionWindowEvidence.valid == true AND SessionWindowEvidence.session IN ["LONDON", "NY"]` | `R6_NO_LTF_CONFIRMATION` |
| `S11_ENTRY_WINDOW` | `EntryWindowEvidence.valid == true AND EntryWindowEvidence.inside_window == true` | `R7_ENTRY_WINDOW_EXPIRED` |
| `S12_RISK_SLTP` | `InvalidationSwingEvidence.valid == true AND TargetEvidence.valid == true AND computed_rr >= MIN_RR` | `R5_NO_FVG_OB_CONFLUENCE` |
| `S13_TRADE_PLAN_EMIT` | `all previous states valid` | emit `TRADE_PLAN` |

---

## Expiry And Termination

At `S14_EXPIRY`, the validator maps `ExpiryEvidence.expiry_reason` to ERR-code:

| Expiry reason | Termination code |
|---|---|
| `BIAS_FLIP` | `ERR_HTF_BIAS_FLIP` |
| `ENTRY_WINDOW` | `ERR_ENTRY_WINDOW_EXPIRED` |
| `SL_BREAK` | `ERR_SL_INVALIDATION` |
| `SUPERSEDED` | `ERR_SUPERSEDED_SETUP` |

---

## Execution Flow

On every tick:

```text
1. Load current state.
2. Load evidence for that state.
3. Evaluate guard.
4. If guard fails, emit R-code and stop.
5. If guard passes, advance to next state.
6. If state == S13, emit TRADE_PLAN.
7. If state >= S13, check expiry and emit ERR-code if needed.
```

State advancement:

- States advance only forward.
- No backward transitions.
- No skipping states.
- No re-entry into previous states.

---

## Evidence Chain

The validator must attach all evidence IDs to the trade plan:

```text
TRADE_PLAN.evidence_chain = [
  HTFBiasEvidence.id,
  SweepEvidence.id,
  SweepReclaimEvidence.id,
  DisplacementEvidence.id,
  BOSEvidence.id,
  BOSExtremeEvidence.id,
  DealingRangeEvidence.id,
  OTEEvidence.id,
  FVGEvidence.id,
  OrderBlockEvidence.id,
  LTFConfirmationEvidence.id,
  SessionWindowEvidence.id,
  EntryWindowEvidence.id,
  InvalidationSwingEvidence.id,
  TargetEvidence.id
]
```

---

## Validator Output Format

If rejection, pre-entry:

```json
{
  "state": "REJECTED",
  "code": "R#_XXXX",
  "reason": "...",
  "evidence_id": "<evidence.id>"
}
```

If termination, post-entry:

```json
{
  "state": "TERMINATED",
  "code": "ERR_XXXX",
  "reason": "...",
  "trade_plan_id": "<TP.id>"
}
```

If valid, trade plan emitted:

```json
{
  "state": "VALID",
  "trade_plan": {}
}
```
