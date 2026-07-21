# ST-C1 v3.8 (R2.1) — Conformance Matrix

R2.1 is a **diagnostic-only** task: it adds no new strategy gate and changes
no G1–G10 rule definition. It exists to test one parameter
(`poi_entry_to_sweep_max_m5_bars`) for population feasibility. Accordingly,
this matrix records what R2.1 added and what remains exactly as documented in
`reports/audit/ST_C1_V37_CONFORMANCE_MATRIX.md` (unchanged, still authoritative
for G1–G10 themselves).

| Component | Status | Evidence |
|---|---|---|
| G1–G5, G7, G9 (unchanged from v3.7) | IMPLEMENTED, unchanged | `src/signal_v37.py`, reused as-is by the diagnostic |
| G6 (unchanged rule definition; new forward-tracing diagnostic view) | IMPLEMENTED, with a disclosed methodology difference between the diagnostic's forward trace and the production engine's backward-window scan (see `validation/g6_latency_diagnostics.py` module docstring) | `tests/test_g6_latency_diagnostics.py` (11 tests) |
| G8, G10 (untouched — no reward-gate or management change in R2.1) | unchanged from v3.7 | n/a to this task |
| G6 latency instrumentation (new) | IMPLEMENTED | `validation/g6_latency_diagnostics.py`; 11 passing tests covering boundary conditions, event ordering, first-qualifying-sweep-only, censoring vs. rejection, mirror long/short symmetry, duplicate-POI dedup, timestamp-vs-cutoff invariance, missing-input fail-closed, and clean/resumed determinism |
| G6 population feasibility at B0/B1/B2 | TESTED, hypothesis REJECTED within range | `reports/ablation/ST_C1_V38_G6_POPULATION_ABLATION.md` |

## What this task does NOT claim

No new specification version was produced (the precommitted selection rule
was not satisfied — see the final validation decision). No G1–G10 rule
changed. No engine behavior changed (the diagnostic module is read-only
research code, never imported by `historical_replay_engine_v37.py` or any
execution path). `specs/v3.7.yaml` and `strategies/candidates/ST-C1_v1.1.0.yaml`
remain the current (unpromoted) research candidates, unmodified by this task.
