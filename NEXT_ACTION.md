# NEXT_ACTION.md

**One milestone at a time. This is the next one.**

## → M1: Config loader (`src/config.py`)

### Why this first
The charter has a hard rule: *"Never hardcode strategy values. Everything must come from configuration."* Right now `specs/v1.yaml` exists but **no code reads it** — `risk_pct`, `min_rr`, `k`, `window`, and `sessions` are hardcoded in `live_signal.py`, `backtest.py`, `validate.py`, and `dry_run.py`. Every later milestone (execution, runner, risk guards) should consume config, so this unblocks the rest cheaply. It is also the lowest-risk change — pure refactor, easy to unit-test.

### Scope (smallest working solution)
1. Add `src/config.py` with `load(path="specs/v1.yaml") -> dict` (+ typed accessors and sane validation: risk_pct > 0, min_rr ≥ 1, k ≥ 1).
2. Replace hardcoded defaults in `live_signal.py`, `backtest.py`, `validate.py` with config reads (CLI flags still override).
3. Add a unit test: config loads, has required keys, and changing a value changes the sizing/backtest output.

### Acceptance criteria
- [ ] Editing `specs/v1.yaml` (e.g. `min_rr: 2.0 → 3.0`) changes GO/NO-GO in `live_signal.py` with no code edit.
- [ ] No strategy constant remains hardcoded in the three entrypoints.
- [ ] `python -m pytest -q` passes (incl. the new config test).

### Estimated complexity
Small — ~1 module, ~3 edits, ~1 test. Half a session.

### Blocker to be aware of
The sandbox Linux VM is currently **down**, so I can write M1 but cannot run `pytest` to prove it this session. Options: (a) I write M1 now and we run tests once the VM is back / on your machine, or (b) we wait for the VM and do write+test together so nothing is marked done untested. Recommendation: **(b)** — it honors the charter's "never skip validation" rule.

### After M1
Proceed to **M2 (execution module)** — the Priority-1 automation spine. See ROADMAP.md.
