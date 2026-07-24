# ST-C3 Evidence Bindings

**Strategy ID:** ST-C3
**Status:** Pre-freeze draft foundation document

This document binds ST-C3 evidence objects into the state machine. It defines
the deterministic relationship between funnel states, evidence consumed,
evidence produced, guard expressions, rejection codes, and post-signal
termination codes.

---

## Core Principle

Every state in the ST-C3 state machine must declare:

- `consumes`: evidence objects it consumes.
- `produces`: evidence objects it produces.
- `guard`: boolean condition referencing evidence fields.
- `reject`: R-code emitted before trade-plan creation.
- `terminate`: ERR-code emitted after `S13_TRADE_PLAN_EMIT`.

This binding layer makes the funnel validator-ready while remaining pre-freeze
and non-executable until governance authorizes implementation.

---

## Evidence Registry

| Evidence | Timeframe | Fields |
|---|---|---|
| `HTFBiasEvidence` | `H4` | `structure`, `bias`, `valid`, `reason` |
| `SweepEvidence` | `H4`, `M15` | `sweep_type`, `wick_penetration`, `level`, `valid` |
| `SweepReclaimEvidence` | `H4`, `M15` | `reclaim_within_bars`, `max_allowed_bars`, `reclaimed`, `valid` |
| `DisplacementEvidence` | `M15` | `impulse_strength`, `threshold`, `valid` |
| `BOSEvidence` | `M15` | `bos_direction`, `body_close_break`, `level`, `valid` |
| `BOSExtremeEvidence` | `M15` | `provisional_extreme`, `locked_extreme`, `pullback_detected`, `valid` |
| `DealingRangeEvidence` | `M15` | `origin`, `bos_extreme`, `range_size`, `valid` |
| `OTEEvidence` | `M15` | `ote_min`, `ote_max`, `price_in_ote`, `valid` |
| `FVGEvidence` | `H4`, `M15` | `gap_top`, `gap_bottom`, `fresh`, `inside_ote`, `valid` |
| `OrderBlockEvidence` | `H4`, `M15` | `ob_high`, `ob_low`, `fresh`, `inside_ote`, `valid` |
| `LTFConfirmationEvidence` | `M3`, `M1` | `choch_direction`, `sweep_local_liquidity`, `valid` |
| `SessionWindowEvidence` | `M3`, `M1` | `session`, `valid` |
| `EntryWindowEvidence` | `M3`, `M1` | `bars_since_ltf_choch`, `max_allowed_bars`, `inside_window`, `valid` |
| `InvalidationSwingEvidence` | `M3`, `M1` | `swing_level`, `direction`, `valid` |
| `TargetEvidence` | `H4`, `M15` | `target_type`, `level`, `rr`, `valid` |
| `ExpiryEvidence` | `M3`, `M1` | `expiry_reason`, `valid` |

---

## State Machine Binding

| State | Consumes | Produces | Guard | Reject / Terminate |
|---|---|---|---|---|
| `S1_HTF_BIAS` | `HTFBiasEvidence` | `HTFBiasEvidence` | `HTFBiasEvidence.valid == true` | `R1_HTF_BIAS_UNCLEAR` |
| `S2_SWEEP` | `SweepEvidence` | `SweepEvidence` | `SweepEvidence.valid == true` | `R2_NO_SWEEP` |
| `S3_SWEEP_RECLAIM` | `SweepReclaimEvidence` | `SweepReclaimEvidence` | `SweepReclaimEvidence.valid == true and SweepReclaimEvidence.reclaimed == true` | `R2_NO_SWEEP` |
| `S4_DISPLACEMENT_BOS` | `DisplacementEvidence`, `BOSEvidence` | `DisplacementEvidence`, `BOSEvidence` | `DisplacementEvidence.valid == true and BOSEvidence.valid == true` | `R3_NO_DISPLACEMENT_BOS` |
| `S5_BOS_EXTREME_LOCK` | `BOSExtremeEvidence` | `BOSExtremeEvidence` | `BOSExtremeEvidence.valid == true and BOSExtremeEvidence.pullback_detected == true` | `R3_NO_DISPLACEMENT_BOS` |
| `S6_DEALING_RANGE` | `DealingRangeEvidence` | `DealingRangeEvidence` | `DealingRangeEvidence.valid == true` | `R4_NO_OTE_PULLBACK` |
| `S7_OTE` | `OTEEvidence` | `OTEEvidence` | `OTEEvidence.valid == true and OTEEvidence.price_in_ote == true` | `R4_NO_OTE_PULLBACK` |
| `S8_FVG_OB_CONFLUENCE` | `FVGEvidence`, `OrderBlockEvidence` | `FVGEvidence`, `OrderBlockEvidence` | `(FVGEvidence.valid == true or OrderBlockEvidence.valid == true) and inside_ote == true` | `R5_NO_FVG_OB_CONFLUENCE` |
| `S9_LTF_CONFIRMATION` | `LTFConfirmationEvidence` | `LTFConfirmationEvidence` | `LTFConfirmationEvidence.valid == true and LTFConfirmationEvidence.sweep_local_liquidity == true` | `R6_NO_LTF_CONFIRMATION` |
| `S10_SESSION_GATEKEEPER` | `SessionWindowEvidence` | `SessionWindowEvidence` | `SessionWindowEvidence.valid == true and SessionWindowEvidence.session in ["LONDON", "NY"]` | `R6_NO_LTF_CONFIRMATION` |
| `S11_ENTRY_WINDOW` | `EntryWindowEvidence` | `EntryWindowEvidence` | `EntryWindowEvidence.valid == true and EntryWindowEvidence.inside_window == true` | `R7_ENTRY_WINDOW_EXPIRED` |
| `S12_RISK_SLTP` | `InvalidationSwingEvidence`, `TargetEvidence` | `InvalidationSwingEvidence`, `TargetEvidence` | `InvalidationSwingEvidence.valid == true and TargetEvidence.valid == true` | `R5_NO_FVG_OB_CONFLUENCE` |
| `S13_TRADE_PLAN_EMIT` | All pre-entry evidence | `TRADE_PLAN` | `all previous states valid` | none |
| `S14_EXPIRY` | `ExpiryEvidence` | `ExpiryEvidence` | monitor expiry evidence | `ERR_HTF_BIAS_FLIP`, `ERR_ENTRY_WINDOW_EXPIRED`, `ERR_SL_INVALIDATION`, `ERR_SUPERSEDED_SETUP` |
