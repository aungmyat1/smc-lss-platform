# ST-C3 Rejection Code Specification

**Strategy ID:** ST-C3
**Status:** Pre-freeze draft foundation document

This is the official ST-C3 rejection and termination layer. Every code is
deterministic, machine-readable, and tied directly to a funnel stage.

ST-C3 uses two classes of failure codes:

- `R` codes: pre-entry rejections. These occur before a trade plan is created
  and stop the funnel before entry.
- `ERR` codes: post-signal terminations. These occur after a trade plan is
  created and terminate or invalidate the signal.

Within ST-C3-only prose, `R1`-`R7` and `ERR_*` may be used as shorthand. Machine
records should keep ST-C3 context explicit through `strategy_id: ST-C3` and, in
cross-strategy ledgers, may use canonical namespaced values such as `ST-C3-R1`
and `ST-C3-ERR_HTF_BIAS_FLIP`.

---

## R-Codes: Pre-Entry Rejections

These correspond to funnel stages 1-11.

### R1 - HTF Bias Unclear

Triggered when:

- H4 structure is ambiguous.
- No clear HH/HL or LH/LL exists.
- HTF CHoCH invalidates bias mid-stage.

Reason: Cannot determine directional context.

### R2 - No Valid Sweep

Triggered when:

- No external liquidity sweep exists.
- Sweep wick does not penetrate the level.
- Sweep occurs but reclaim fails because `N_SWEEP` is exceeded.

Reason: No institutional liquidity event.

### R3 - No Displacement or BOS

Triggered when:

- No impulsive move follows the sweep.
- BOS fails to break structure with a body close.
- BOS direction contradicts HTF bias.

Reason: No momentum shift.

### R4 - No OTE Pullback

Triggered when:

- Price does not retrace into the 62-79% zone.
- BOS extreme is not locked, so OTE cannot be computed.
- Retrace occurs but stays outside OTE.

Reason: No optimal entry zone.

### R5 - No FVG/OB Confluence

Triggered when:

- No fresh FVG or OB exists inside OTE.
- Confluence zone is mitigated or invalid.
- Confluence contradicts HTF bias.

Reason: No institutional footprint.

### R6 - No LTF Confirmation

Triggered when:

- No M3/M1 CHoCH/BOS exists inside confluence.
- No local liquidity sweep exists.
- CHoCH occurs outside allowed sessions.

Reason: No valid LTF reversal.

### R7 - Entry Window Expired

Triggered when:

- `MAX_ENTRY_BARS` is exceeded.
- Entry zone is touched too late.
- LTF CHoCH is too old to confirm.

Reason: Timing invalid.

---

## ERR-Codes: Post-Signal Terminations

These correspond to funnel stages 12-14.

### ERR_HTF_BIAS_FLIP

Triggered when:

- H4 bias flips after trade-plan creation.
- HTF CHoCH invalidates directional context.

Reason: Macro structure changed.

### ERR_ENTRY_WINDOW_EXPIRED

Triggered when:

- Entry window closes before execution.
- Price moves away from entry zone.
- LTF confirmation becomes stale.

Reason: Trade timing invalidated.

### ERR_SL_INVALIDATION

Triggered when:

- Price breaks invalidation swing.
- SL level is violated before entry.
- Structure invalidates trade premise.

Reason: Setup structurally broken.

### ERR_SUPERSEDED_SETUP

Triggered when:

- New sweep and BOS appear.
- New dealing range forms.
- New OTE replaces the old one.
- New confluence zone emerges.

Reason: A newer, higher-priority setup exists.

---

## ST-C3 Rejection Code JSON Schema

This schema is used for logging, governance, and machine execution.

```json
{
  "R_CODES": {
    "R1_HTF_BIAS_UNCLEAR": "Rejected: HTF bias not structurally defined.",
    "R2_NO_SWEEP": "Rejected: No valid external liquidity sweep.",
    "R3_NO_DISPLACEMENT_BOS": "Rejected: No valid displacement or BOS.",
    "R4_NO_OTE_PULLBACK": "Rejected: Price did not retrace into OTE zone.",
    "R5_NO_FVG_OB_CONFLUENCE": "Rejected: No valid FVG/OB confluence.",
    "R6_NO_LTF_CONFIRMATION": "Rejected: No valid LTF CHoCH/BOS.",
    "R7_ENTRY_WINDOW_EXPIRED": "Rejected: Entry window exceeded MAX_ENTRY_BARS."
  },
  "ERR_CODES": {
    "ERR_HTF_BIAS_FLIP": "Terminated: HTF structure invalidated.",
    "ERR_ENTRY_WINDOW_EXPIRED": "Terminated: Entry window closed before execution.",
    "ERR_SL_INVALIDATION": "Terminated: Price breached invalidation swing.",
    "ERR_SUPERSEDED_SETUP": "Terminated: Newer sweep/BOS setup detected."
  }
}
```

---

## Failure Record Contract

Every rejection or termination record must include:

- `strategy_id`: `ST-C3`.
- `code`: one ST-C3 rejection or termination code.
- `stage`: failed or terminated funnel stage.
- `reason`: deterministic reason.
- `evidence_ids`: evidence available before failure.
- `timestamp`: source event timestamp.
- `symbol`: instrument under review.
- `timeframe`: source timeframe.

The validator must reject fail-closed when evidence, thresholds, session scope,
or symbol scope is missing.
