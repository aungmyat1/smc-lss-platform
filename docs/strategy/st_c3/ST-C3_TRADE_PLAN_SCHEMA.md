# ST-C3 Trade-Plan Schema

**Strategy ID:** ST-C3
**Status:** Pre-freeze draft foundation document

This is the canonical ST-C3 trade-plan object emitted at `S13`
(`TRADE_PLAN_EMIT`). It is bound to the ST-C3 evidence objects, state machine,
rejection codes, and expiry logic.

---

## Emission Rule

A `TRADE_PLAN` exists only if the state machine reaches `S13`. Before `S13`,
failures use R-codes. After `S13`, failures use ERR-codes.

---

## YAML Contract

```yaml
trade_plan:
  strategy_id: "ST-C3"

  schema:
    direction:
      type: enum
      values: ["LONG", "SHORT"]
      evidence: HTFBiasEvidence.bias

    context:
      htf_bias_id: HTFBiasEvidence.id
      sweep_id: SweepEvidence.id
      sweep_reclaim_id: SweepReclaimEvidence.id
      bos_id: BOSEvidence.id
      bos_extreme_id: BOSExtremeEvidence.id
      dealing_range_id: DealingRangeEvidence.id
      ote_id: OTEEvidence.id
      fvg_id: FVGEvidence.id
      orderblock_id: OrderBlockEvidence.id
      ltf_confirmation_id: LTFConfirmationEvidence.id
      session_window_id: SessionWindowEvidence.id

    entry:
      entry_zone_type:
        type: enum
        values: ["FVG", "ORDERBLOCK"]
        evidence: [FVGEvidence.valid, OrderBlockEvidence.valid]
      entry_zone_id:
        type: string
        evidence: [FVGEvidence.id, OrderBlockEvidence.id]
      entry_price:
        type: float
      entry_window_id: EntryWindowEvidence.id
      max_entry_bars: EntryWindowEvidence.max_allowed_bars
      bars_since_ltf_choch: EntryWindowEvidence.bars_since_ltf_choch

    risk:
      sl_price:
        type: float
        evidence: InvalidationSwingEvidence.swing_level
      sl_type: "STRUCTURAL_INVALIDATION"
      risk_per_trade_pct:
        type: float
      min_rr_required:
        type: float
      computed_rr:
        type: float

    targets:
      tp1:
        target_id: TargetEvidence.id
        target_type: "TP1_INTERNAL"
        price: TargetEvidence.level
        rr: TargetEvidence.rr
      tp2:
        target_id: TargetEvidence.id
        target_type: "TP2_EXTERNAL"
        price: TargetEvidence.level
        rr: TargetEvidence.rr
      tp3:
        target_id: TargetEvidence.id
        target_type: "TP3_HTF"
        price: TargetEvidence.level
        rr: TargetEvidence.rr

    expiry:
      rules:
        - "BIAS_FLIP"
        - "ENTRY_WINDOW"
        - "SL_BREAK"
        - "SUPERSEDED"
      expiry_evidence_id: ExpiryEvidence.id

    evidence_chain:
      - HTFBiasEvidence.id
      - SweepEvidence.id
      - SweepReclaimEvidence.id
      - DisplacementEvidence.id
      - BOSEvidence.id
      - BOSExtremeEvidence.id
      - DealingRangeEvidence.id
      - OTEEvidence.id
      - FVGEvidence.id
      - OrderBlockEvidence.id
      - LTFConfirmationEvidence.id
      - SessionWindowEvidence.id
      - EntryWindowEvidence.id
      - InvalidationSwingEvidence.id
      - TargetEvidence.id

    status:
      state:
        type: enum
        values: ["VALID", "REJECTED", "TERMINATED"]
      code:
        type: enum
        values:
          - R1_HTF_BIAS_UNCLEAR
          - R2_NO_SWEEP
          - R3_NO_DISPLACEMENT_BOS
          - R4_NO_OTE_PULLBACK
          - R5_NO_FVG_OB_CONFLUENCE
          - R6_NO_LTF_CONFIRMATION
          - R7_ENTRY_WINDOW_EXPIRED
          - ERR_HTF_BIAS_FLIP
          - ERR_ENTRY_WINDOW_EXPIRED
          - ERR_SL_INVALIDATION
          - ERR_SUPERSEDED_SETUP
      reason:
        type: string

    meta:
      created_at:
        type: datetime
      tf_stack:
        type: list
        values: ["H4", "M15", "M3", "M1"]
      session:
        type: enum
        values: ["LONDON", "NY"]
      provenance: "STC3_v1"
```

---

## Correctness Notes

- It matches the 16-state machine because `S13` emits this object.
- Every field is bound to ST-C3 evidence objects.
- Every failure maps to an R-code or ERR-code.
- The object is deterministic and validator-ready, but remains pre-freeze and
  non-executable until governance authorizes implementation.
