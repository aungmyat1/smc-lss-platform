# NEXT_ACTION.md

**One milestone at a time. This is the next one.**

## → PHASE 2 · M2: Strategy Approval and Validation

*Validate the normalized candidate strategy contract with deterministic,
closed-candle evidence and approval gates.*

### Why this now
The strategy contract has been normalized. The next gate is to prove the contract
with deterministic validation evidence before any approval or execution work.

### Scope (smallest working solution)
1. Run deterministic backtesting against the normalized contract.
2. Validate the contract with out-of-sample and walk-forward evidence.
3. Record the approval gates and remaining evidence requirements.
4. Keep the output candidate-only until validation is complete.

### Acceptance criteria
- [ ] The normalized contract has deterministic validation evidence.
- [ ] Versioning and approval status are explicit and immutable per version.
- [ ] The contract is ready for approval review and backtest/validation work.
- [ ] `python -m pytest -q` passes after any supporting doc/test updates.

### Estimated complexity / time
Small to medium. The hard part is making the contract shape clear enough that the
execution layer can consume it later without redesign.

### After M2
Proceed to **M3 execution skeleton**, then M4 demo integration, then M5 live
promotion gate.
