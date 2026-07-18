# NEXT_ACTION.md

**One milestone at a time. This is the next one.**

## → PHASE 3 · M1: Configuration Loader (`src/config.py`)

*(Per [`MASTER_PLAN.md`](MASTER_PLAN.md) v2.1.1, Phase 3 is implemented M1→M4:
**M1 config loader** → M2 risk validator → M3 position sizing → M4 approval gate.
M1 is first because Rule 2 forbids hardcoded strategy parameters, so every later
risk component must read config, not constants. Built on the locked v1 engine; the
v3.5 track stays parked.)*

### Why this first
The risk validator, position sizer, and approval gate all consume strategy/risk
parameters. Today those values are hardcoded and duplicated. A single validated
config loader must exist before any of them can be built without baking in more
hardcoded values.

### Scope (smallest working solution)
1. Create `src/config.py` — `load(path) -> Config` reading `config/watchlist.yaml`
   (and `specs/v1.yaml` where relevant to the live path).
2. **Schema validation** — typed accessors; reject invalid/missing values with a clear
   error (fail closed). No silent defaults for risk-relevant fields.
3. Replace hardcoded strategy/risk constants (risk %, min RR, session, window, ATR,
   thresholds) in the live path with config reads.
4. Nothing strategy-related remains hardcoded (Non-Negotiable Rule 2).

### Acceptance criteria
- [ ] `src/config.py` loads + validates config; invalid values are rejected, not defaulted.
- [ ] Changing a value in `config/watchlist.yaml` changes behavior with no code edit.
- [ ] No hardcoded risk/strategy constant remains on the live path.
- [ ] `python -m pytest -q` — all tests pass, plus new tests for the loader/validation. **(Blocked: workspace VM down — restore before claiming done.)**

### Estimated complexity / time
Small. One module + schema validation + tests. One focused session once the VM is up.

### After M1
Proceed to **M2 — Risk Validator** (APPROVED/REJECTED-with-reason for every signal),
then M3 sizing, then M4 the approval gate that fronts Phase 4 execution.
