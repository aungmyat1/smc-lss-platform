# NEXT_ACTION.md

**One milestone at a time. This is the next one.**

## → PHASE 3 · M3: Execution Layer Skeleton

*Build the canonical execution pipeline after the strategy approval and statistical
validation gates are in place.*

### Why this now
The approved-strategy path now has mechanical validation, replay, and statistical
validation scaffolding. The next step is to build the execution skeleton without
letting it rewrite strategy logic.

### Scope (smallest working solution)
1. Define the canonical order pipeline.
2. Add the execution risk gate.
3. Add broker adapter boundaries.
4. Add reconciliation and journaling hooks.
5. Keep live trading blocked until approval and execution controls are complete.

### Acceptance criteria
- [ ] Execution consumes approved strategy versions only.
- [ ] Strategy logic remains immutable in the execution layer.
- [ ] Demo/live promotion still requires validation gates.
- [ ] `python -m pytest -q` passes after any supporting doc/test updates.

### Estimated complexity / time
Small to medium. The hard part is preserving the approved-strategy boundary while
adding the order pipeline and safety checks.

### After M3
Proceed to **M4 demo integration**, then M5 live promotion gate.
