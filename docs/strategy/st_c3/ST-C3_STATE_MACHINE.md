# ST-C3 State Machine

**Strategy ID:** ST-C3
**Status:** Pre-freeze draft foundation document

This deterministic state machine matches the ST-C3 architecture, funnel
lifecycle, evidence objects, rejection codes, and termination logic. It is a
blueprint for future Python/MQL5 implementation after the required governance
gates authorize implementation.

---

## State List

| State | Name |
|---|---|
| `S0` | INIT |
| `S1` | HTF BIAS |
| `S2` | SWEEP |
| `S3` | SWEEP RECLAIM |
| `S4` | DISPLACEMENT + BOS |
| `S5` | BOS EXTREME LOCK |
| `S6` | DEALING RANGE |
| `S7` | OTE |
| `S8` | FVG/OB CONFLUENCE |
| `S9` | LTF CONFIRMATION |
| `S10` | SESSION GATEKEEPER |
| `S11` | ENTRY WINDOW |
| `S12` | RISK & SL/TP BUILD |
| `S13` | TRADE_PLAN EMIT |
| `S14` | EXPIRY / TERMINATION |
| `S15` | TERMINAL |

---

## Transition Table

| State | Description | Guard / Condition | Next | Reject / Terminate |
|---|---|---|---|---|
| `S0` | INIT | Session open and instrument enabled | `S1` | None |
| `S1` | HTF BIAS | `HTFBiasEvidence.valid == true` | `S2` | `R1_HTF_BIAS_UNCLEAR` |
| `S2` | SWEEP | `SweepEvidence.valid == true` | `S3` | `R2_NO_SWEEP` |
| `S3` | SWEEP RECLAIM | `SweepReclaimEvidence.valid == true AND reclaimed == true` | `S4` | `R2_NO_SWEEP` for no reclaim or late reclaim |
| `S4` | DISPLACEMENT + BOS | `DisplacementEvidence.valid == true AND BOSEvidence.valid == true` | `S5` | `R3_NO_DISPLACEMENT_BOS` |
| `S5` | BOS EXTREME LOCK | `BOSExtremeEvidence.valid == true AND pullback_detected == true` | `S6` | `R3_NO_DISPLACEMENT_BOS` for no lock |
| `S6` | DEALING RANGE | `DealingRangeEvidence.valid == true` | `S7` | `R4_NO_OTE_PULLBACK` if range invalid |
| `S7` | OTE | `OTEEvidence.valid == true AND price_in_ote == true` | `S8` | `R4_NO_OTE_PULLBACK` |
| `S8` | FVG/OB CONFLUENCE | `(FVGEvidence.valid == true OR OrderBlockEvidence.valid == true) AND inside_ote == true` | `S9` | `R5_NO_FVG_OB_CONFLUENCE` |
| `S9` | LTF CONFIRMATION | `LTFConfirmationEvidence.valid == true AND sweep_local_liquidity == true` | `S10` | `R6_NO_LTF_CONFIRMATION` |
| `S10` | SESSION GATEKEEPER | `SessionWindowEvidence.valid == true AND session IN {LONDON, NY}` | `S11` | `R6_NO_LTF_CONFIRMATION` for invalid session |
| `S11` | ENTRY WINDOW | `EntryWindowEvidence.valid == true AND inside_window == true` | `S12` | `R7_ENTRY_WINDOW_EXPIRED` |
| `S12` | RISK & SL/TP BUILD | `InvalidationSwingEvidence.valid == true AND TargetEvidence(valid for TP1/TP2/TP3) AND RR >= MIN_RR` | `S13` | Appropriate R-code if any risk or target rule fails |
| `S13` | TRADE_PLAN EMIT | All prior states valid; build `TRADE_PLAN` object | `S14` | Internal error if build fails |
| `S14` | EXPIRY / TERMINATION | Monitor `ExpiryEvidence` plus HTF/LTF updates | `S15` | `ERR_HTF_BIAS_FLIP`, `ERR_ENTRY_WINDOW_EXPIRED`, `ERR_SL_INVALIDATION`, `ERR_SUPERSEDED_SETUP` |
| `S15` | TERMINAL | Trade closed or signal terminated; archive evidence and enums | `S0` | None; reset for next setup |

---

## Priority Rules

- No state can be skipped or revisited.
- Any failed guard triggers exactly one R-code or ERR-code.
- A `TRADE_PLAN` only exists if the machine reaches `S13`.
- After `S13`, only ERR-codes are allowed; R-codes are no longer valid.
