# ST-C1 v1.1.0 / spec v3.7 — Locked 2×2 Ablation Report

Per `reports/audit/ST_C1_V37_RESEARCH_CHANGE_REQUEST.md`. Cells:

- **A0**: current-style location logic OFF (G4 not enforced) + gross 2R gate
- **A1**: G4 premium/discount enforced + gross 2R gate
- **A2**: G4 not enforced + net 3R gate (G8)
- **A3**: G4 enforced + net 3R gate (both new rules ON — the full v3.7 contract)

Every other rule (G1, G2, G3, G5, G6, G7, G9, G10, costs) is held identical
across all four cells and across all three symbols. Engine:
`validation/historical_replay_engine_v37.py::HistoricalReplayEngineV37`.
Contract: `strategies/candidates/ST-C1_v1.1.0.yaml`. Data: full local history
per symbol (`data/{SYMBOL}_M5.csv` + H1 + D1), no date-range subsetting.

## Results

| Symbol | Cell | Trades | Signals | G6 rejects | Elapsed |
|---|---|---|---|---|---|
| EURUSD | A0 | 0 | 0 | 3528 | 184.2s |
| EURUSD | A1 | 0 | 0 | 564 | 72.7s |
| EURUSD | A2 | 0 | 0 | 3528 | 156.7s |
| EURUSD | A3 | 0 | 0 | 564 | 71.5s |
| GBPUSD | A0 | 0 | 0 | 3682 | 157.1s |
| GBPUSD | A1 | 0 | 0 | 372 | 54.8s |
| GBPUSD | A2 | 0 | 0 | 3682 | 173.9s |
| GBPUSD | A3 | 0 | 0 | 372 | 71.2s |
| XAUUSD | A0 | 0 | 0 | 5022 | 210.6s |
| XAUUSD | A1 | 0 | 0 | 711 | 60.4s |
| XAUUSD | A2 | 0 | 0 | 5022 | 176.2s |
| XAUUSD | A3 | 0 | 0 | 711 | 57.7s |

Raw funnel counts for every cell: `reports/ablation/st_c1_v37_ablation_raw.json`.

## Reading the result

**Zero trades in every one of the 12 cells.** This is not an artifact of one
ablation flag — A0 (the loosest cell: no location gate, gross 2R) produced
zero trades on EURUSD just as A3 (the strictest) did. The bottleneck is
common to all four cells: **G6** (the M5 poi-entry→sweep→displacement→CHoCH→
retrace sequence), which neither ablation flag touches.

Per the Research Change Request's own pre-committed rollback rule: *"If A0
does not reproduce the existing baseline's qualitative shape... treat as an
engine-parity defect (INCONCLUSIVE), not a strategy result — fix parity
before drawing conclusions from A1-A3."* A0 did not reproduce anything close
to the Phase A baseline's 363-trade shape (it produced zero). Diagnostic work
during this task (see `reports/audit/ST_C1_V37_PRE_EDIT_FINDINGS.md` and the
traceability matrix) found and fixed two genuine **engine defects** before
running this ablation:

1. The M5 window used to search for "price enters the fresh HTF POI" was
   sized for the base engine's cheaper per-bar feature calculations (60
   bars ≈ 5 hours), far too small for a POI that can legitimately be up to
   60 H1 bars / 10 D1 bars old. Fixed by widening the search window
   (`m5_poi_entry_search_bars`, engine-tractability parameter, not a
   strategy rule).
2. The G5 causal-displacement check compared a D1 gap's array index directly
   against H1 displacement bounds (a cross-timeframe index mismatch), and
   required the displacement to start *before* an order-block/external-sweep
   POI's own index instead of *after* it — both defects made the causal
   check nearly always fail for two of the three POI origins. Fixed in
   `src/signal_v37.py::_causal_displacement_ok`.

After both fixes, G5 now finds far more candidate POIs (funnel counts for G6
input rose from dozens to 3500+ per symbol) — but **all** of them still fail
the very next step (`poi_entry_i` is found for essentially none within the
search window, or the subsequent sweep is not found within
`poi_entry_to_sweep_max_m5_bars=30` bars of the touch). Direct diagnostic
testing (documented interactively during this task) traced the specific
remaining bottleneck: on the real EURUSD sample checked, the nearest matching
M5 sweep after a POI touch was found **127 bars** away — roughly 4x the
30-bar allowance — and this appears representative rather than a one-off
(bear-direction sweeps occur roughly once every ~50 bars on average in the
checked window, making a same-direction sweep landing within any specific
30-bar post-touch window a low-probability event by construction).

## Why this was not "fixed" by loosening the parameter

`poi_entry_to_sweep_max_m5_bars=30` is a declared, versioned, **strategy**
parameter (`specs/v3.7.yaml` parameter_registry, `tunable: true`), not an
engine-plumbing detail like the two bugs above. Per this task's explicit
instruction ("Do not optimize parameters during this task") and
`docs/RESEARCH-CHARTER.md` (no parameter change without a six-question
template filed *before* seeing the result), the number is left exactly as
originally set and the zero-trade outcome is reported as the true result of
the locked configuration — not adjusted after the fact to manufacture
trades.

## Ablation interpretation

Because G6 saturates rejections identically across all four cells, **this
ablation cannot discriminate the location-gate effect from the net-reward-
gate effect** — that was its stated purpose, and it is INCONCLUSIVE for that
purpose. This is itself the result: the locked parameter set, taken as
originally committed, does not produce enough surviving candidates at G6 for
the G4/G8 comparison to ever become visible. A follow-up Research Change
Request specifically targeting G6's sequencing bounds (`poi_entry_to_sweep_max_m5_bars`,
`displacement_to_choch_max_m5_bars`, `choch_to_retrace_entry_max_m5_bars`)
would need to be filed, with its own falsifiable hypothesis and expected
numbers committed in advance, before any such change is tested.

## Safety

No parameters were tuned based on these results. No broker orders were sent.
Demo/live execution remains disabled throughout.
