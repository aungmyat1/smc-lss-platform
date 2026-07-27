# A3 Synthetic Lifecycle Test Results — ST-C3

**Date:** 2026-07-27
**Module under test:** `validation/st_c3/a3_replay_engine._simulate_lifecycle`
**Test file:** `tests/st_c3/test_a3_lifecycle.py` (5 tests, all passing)
**Authorization:** A3 opening (owner decision, 2026-07-26); directed as the
next step after `A3_REPLAY_RESULTS.md` flagged this as an untested gap.

---

## Why this exists

The one real A3 replay run to date (GBPUSD, 7 weeks) produced zero
TradePlans, so `_simulate_lifecycle` — the only genuinely new logic
`a3_replay_engine.py` adds on top of the existing kernel/evidence-builder —
had never actually run against real data. These tests close that gap with
hand-built `TradePlan` fixtures and scripted price paths, independent of
whether or when real data ever triggers the same code paths.

## What was tested

| Test | Branch exercised | Key assertion |
|---|---|---|
| `test_tp1_only_hit_partial_close_open_at_end` | TP1 touch, partial close, data ends before resolution | `realized_rr=0.30`, `unrealized_rr≈0.70`, `OPEN_AT_DATA_END` |
| `test_all_targets_hit_full_closure` | TP1→TP2→TP3 sequential touches | `realized_rr≈3.2`, `remaining_fraction≈0`, `ALL_TARGETS_HIT` |
| `test_sl_hit_immediately_no_targets` | SL touched before any target | `realized_rr=-1.0`, `SL_HIT`, no hits |
| `test_partial_tp1_then_sl_hit` | TP1 partial close, then remaining stopped out | `realized_rr≈-0.4`, `SL_HIT` |
| `test_bias_flip_terminates_before_any_sl_tp_touch` | BIAS_FLIP detection via re-evaluated H4 bias | `BIAS_FLIP` at the engineered bar, no SL/TP interpretation |

Result: **all 5 pass**; full repo suite remains green.

## Corrections made against the originally proposed test plan

The plan this was built from proposed calling `run_a3_replay(data)` and
asserting round-number RRs (`≈1.0`/`≈2.0`/`≈3.0` per target). Neither
matches the real implementation:

1. **Wrong entrypoint.** `run_a3_replay()` requires a full multi-TF candle
   set and drives detection through `build_evidence_bundle()` — there is
   no way to hand it a single scripted TradePlan. `_simulate_lifecycle()`
   is the actual unit that owns TP/SL/BIAS_FLIP logic; these tests call it
   directly, the same level `test_golden_cases.py`/`test_negative_cases.py`
   test `run_kernel()` at.
2. **Partial exits, not full closes.** ST-C3's TP1/TP2/TP3 exits are
   30%/30%/40% partial closes (`ST-C3_BACKTEST_SPEC.md` section 9), so
   hitting only TP1 realizes `0.30 * tp1_rr`, not the full `tp1_rr`. Test
   expectations reflect the partial-exit math throughout.
3. **Entry-window is out of scope for lifecycle tests.** The proposed plan
   included an "entry-window handling" fixture, but `EntryWindowEvidence`
   is a pre-entry S11 funnel guard, already covered by
   `test_golden_cases.py`/`test_negative_cases.py` — it plays no role in
   post-entry lifecycle simulation, so no fixture was built for it here.
4. **Chain-frequency counters don't exist yet.** The plan also proposed
   testing "chain-frequency counters," but sweep→reclaim→BOS /
   OB-FVG-interaction frequency metrics are not implemented anywhere in
   `a3_replay_engine.py` (flagged as a future extension in
   `ST-C3_A3_METRICS_SPEC.md` section 2.2/6) — there is nothing to test.
5. **File path.** Placed at `tests/st_c3/test_a3_lifecycle.py`, matching
   the existing `tests/st_c3/` convention (`test_golden_cases.py`,
   `test_negative_cases.py`, `test_existence_check_readiness.py`), not the
   proposed `tests/validation/st_c3/` (that directory doesn't exist).

## Incidental cleanup

While designing these tests, an unused `original_bias` local variable was
found and removed from `_simulate_lifecycle` (dead code from an earlier
draft of the BIAS_FLIP check — the actual flip test compares the rebuilt
bias against the trade's own `direction`, not against a stored original
value). No behavior change; confirmed by these tests passing before and
after.

## What this does and does not establish

- **Does** confirm `_simulate_lifecycle`'s SL/TP/partial-exit/BIAS_FLIP
  logic behaves as designed, independent of real data availability.
- **Does not** replace real-data validation — these are synthetic,
  hand-constructed price paths chosen specifically to exercise one branch
  at a time; they say nothing about how often these conditions actually
  occur in real markets (that remains data-blocked, per
  `A3_REPLAY_RESULTS.md`).
- **Does not** authorize execution, optimization, demo, or live trading.
