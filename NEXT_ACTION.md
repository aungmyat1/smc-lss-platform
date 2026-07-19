# NEXT_ACTION.md

**One milestone at a time. This is the next one.**

## → PHASE 1 · M1: Strategy Contract Normalization

*Normalize `docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md` into a machine-readable,
versioned approved-strategy contract.*

### Why this first
The execution layer must trade only an approved contract. Before we can build risk,
broker, or reconciliation plumbing, the source strategy needs a stable contract form
with explicit fields and frozen rules.

### Scope (smallest working solution)
1. Define the approved contract shape for the v3.6 strategy source.
2. Map the source strategy sections into machine-readable fields.
3. Preserve versioning, frozen-rule semantics, and approval status.
4. Keep the output suitable for deterministic validation and later execution.

### Acceptance criteria
- [ ] The source strategy has a machine-readable contract representation.
- [ ] Versioning and approval status are explicit and immutable per version.
- [ ] The contract is suitable for deterministic backtest/validation work.
- [ ] `python -m pytest -q` passes after any supporting doc/test updates.

### Estimated complexity / time
Small to medium. The hard part is making the contract shape clear enough that the
execution layer can consume it later without redesign.

### After M1
Proceed to **M2 — Strategy Approval and Validation**, then M3 execution skeleton,
then M4 demo integration, then M5 live promotion gate.
