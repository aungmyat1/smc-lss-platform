# Research Change Request (RCR) - SOP-A Analytical Extensions

**RCR-ID:** RCR-2026-07-SOPA  
**Author:** Aung  
**Date:** 2026-07-28  
**Scope:** ST-C3 Strategy Contract (v1.x line)  
**Type:** Analytical Extension (Stage-A)  
**Status:** Draft (Pending Owner Review)

---

## 1. Summary

This RCR proposes adding a set of analytical-only, pre-execution validation
components to the ST-C3 strategy contract. These components correspond to the
Stage-A portion of the SOP (SOP-A) and introduce no execution logic, no
lifecycle semantics, and no Stage-B behavior.

The goal is to strengthen the analytical discipline of ST-C3 without altering
its execution model or violating the 2026-07-27 freeze on S7/S8/S9.

## 2. Motivation

The current ST-C3 kernel implements:

- Sweep
- CHoCH
- MSS
- OB
- FVG
- Liquidity
- Trade-plan conformance
- Evidence generation

However, several analytical components used in discretionary SMC workflows are
not present in ST-C3 and cannot be added without an RCR. These include:

- HTF bias freeze
- HTF POI freeze
- Draw-on-liquidity definition
- Session/news/spread gates
- POI arrival validation extensions
- Analytical OTE context (non-execution)

These additions would improve:

- Signal qualification
- Evidence richness
- Analytical consistency
- Future Stage-B execution agent design

## 3. Proposed Additions (Analytical Only)

### 3.1 HTF Analytical Context

Add analytical functions for:

- HTF bias determination
- HTF bias freeze (non-lifecycle)
- HTF POI selection
- HTF POI freeze (non-lifecycle)
- Draw-on-liquidity identification

These produce frozen analytical context, not runtime state.

### 3.2 Qualification Gates

Add analytical gates for:

- Session qualification
- News qualification
- Spread qualification
- Daily risk qualification (analytical only)

These gates produce PASS/FAIL plus reason, not execution decisions.

### 3.3 Setup Validation Extensions

Add analytical validation for:

- POI arrival
- OB refinement
- FVG refinement
- Liquidity proximity scoring

These extend existing ST-C3 validators.

### 3.4 Confirmation Filters (Analytical Only)

Add analytical detection for:

- Sweep classification
- CHoCH classification
- MSS classification
- OTE zone identification (non-execution)

Important: this RCR does not request OTE execution logic. It requests
analytical identification only, which does not violate the S7 freeze.

### 3.5 Evidence Extensions

Add new evidence fields:

- HTF bias
- HTF POI
- Draw-on-liquidity
- Session/news/spread gate results
- Extended OB/FVG/liquidity validation
- Sweep/CHoCH/MSS classification
- Analytical OTE zone

These fields enrich the evidence dataset without altering execution.

### 3.6 Rejection-Reason Extensions

Add analytical rejection codes for:

- Session fail
- News fail
- Spread fail
- HTF mismatch
- POI mismatch
- Sweep missing
- CHoCH missing
- MSS missing
- Analytical OTE mismatch

These codes do not block execution; they annotate evidence.

## 4. Non-Goals (Explicit Exclusions)

This RCR does not request:

- Position sizing
- Stop-loss logic
- Take-profit logic
- Order placement
- Lifecycle state machine
- Execution agent behavior
- Automation
- Runtime semantics
- Any Stage-B functionality

This keeps the RCR fully within Stage-A scope.

## 5. Impact on ST-C3

### Positive

- Stronger analytical discipline
- Richer evidence
- Better conformance reporting
- Cleaner Stage-B foundation
- No lifecycle or execution changes
- No contradictions with v1.x freeze

### Neutral

- No change to signal validity
- No change to trade-plan validity
- No change to execution behavior

### Negative

- Slight increase in analytical complexity
- Requires spec update (v1.0.8+)
- Requires kernel/evidence schema updates

## 6. Required Spec Changes

If accepted, this RCR will require:

- `specs/st-c3_v1.0.8.yaml`
- `validation/st_c3/kernel.py` (analytical extensions)
- `validation/st_c3/evidence.py` (new fields)
- `validation/st_c3/rejection_codes.py` (analytical codes)
- Updated documentation under `docs/strategy/st_c3/`

No execution agent changes.

## 7. Acceptance Criteria

This RCR is accepted if:

- Owner approves analytical additions
- No execution logic is introduced
- No lifecycle semantics are introduced
- All additions remain pre-execution
- All changes fit within Stage-A scope
- Spec v1.0.8 is drafted and approved

## 8. Owner Decision (Pending)

Options:

- Accept RCR
- Reject RCR
- Request revision
- Defer to Stage-B

Decision will be logged in `OWNER_DECISION_LOG.md`.

## RCR Draft Complete

Possible next deliverables:

- Spec v1.0.8 draft
- SOP-A evidence schema
- SOP-A conformance kernel design
