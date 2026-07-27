# S1-G3 Primitive and Indicator Conformance — Evidence Report

**Date:** 2026-07-27
**Strategy:** ST-C3 v1.0.7 (GBPUSD/EURUSD-scoped)
**Status:** EVIDENCE GATHERED — NOT PASSED, NOT ACCEPTED. Whether S1-G3 is
considered complete is a separate, explicit owner decision, mirroring the
S1-G2 acceptance pattern (see `NEXT_ACTION.md`). This report documents what
evidence exists; it does not itself close the gate.

## Scope

Per `MASTER_PLAN.md`, S1-G3 ("Primitive and Indicator Conformance") is the
first A2 gate unblocked once S1-G2 (Reference Implementation Authorization
and Completion Review) is accepted — which happened 2026-07-27. Its
required evidence categories, and how each is covered:

| Required evidence | Status | Where |
|---|---|---|
| Candle body, wick, range | COVERED | `tests/st_c3/test_s1_g3_primitives.py::test_displacement_body_ratio_fixed_value`, `::test_sweep_wick_ratio_fixed_value` — hand-crafted candles, manually computed expected ratios (0.75, 8/11), checked against `detection.py`'s `displacement_evidence_for`/`detect_sweep_at` arithmetic. |
| Point normalization | N/A | ST-C3 has no pip/point-denominated threshold in the frozen spec — every decided filter (R-27 through R-33) is expressed in ATR-multiples or bar counts. Distinct lineage from ST-C2 per ADR-0004; ST-C2's `validation/st_c2/symbols.py` pip conversion is not inherited and has no ST-C3 analogue to test. |
| Sessions | COVERED | `tests/st_c3/test_s1_g3_primitives.py::test_session_boundaries_fixed_values` (fixed-timestamp NY-open/NY-close/midnight edge cases) plus existing `tests/st_c3/test_detection.py::test_session_window_evidence_is_spec_conformant`. |
| Swings | COVERED | `tests/st_c3/test_s1_g3_primitives.py::test_swing_high_and_low_fixed_values` (hand-built 5-bar sequence, manually verified swing-high/low index against `smc_engine.swings`' own `is_hi`/`is_lo` definition), `::test_swings_are_causal_no_lookahead_by_construction`. |
| Premium and discount | COVERED (bare arithmetic only) | New `validation/st_c3/detection.py::premium_discount_zone()` — interval-midpoint classification, tested in `::test_premium_discount_zone_fixed_values`/`::test_premium_discount_zone_rejects_degenerate_range`. **This is not the S7_OTE gate.** It does not use, reference, or depend on `ote_band_min`/`ote_band_max`/`equilibrium_boundary`, which remain provisional and out of v1.x scope per the 2026-07-27 funnel-freeze decision (`V1X_FUNNEL_FREEZE_AND_R18_CLOSURE.md`). It is not wired into any funnel stage — provided solely as a primitive-conformance artifact. |
| Risk/reward distance tests | COVERED | New `validation/st_c3/detection.py::compute_rr()` — matches the frozen `trade_plan.schema.risk.computed_rr` field's arithmetic (reward/risk from entry/stop/target). Tested with fixed LONG/SHORT examples (`::test_compute_rr_long_fixed_value`, `::test_compute_rr_short_fixed_value`) and error paths (zero-risk, invalid direction). Not wired into the kernel — S12 (which would consume it) remains out of v1.x scope. |
| Fixed expected values and causal cutoff checks | COVERED | All of the above use hand-crafted, manually-verified inputs/outputs rather than real market data; causal-cutoff behavior for swings and ATR is exercised directly against `smc_engine`'s own loop bounds. |
| No broker, time, network, or mutable-global dependency | COVERED | `tests/st_c3/test_s1_g3_primitives.py::test_detection_module_has_no_broker_time_network_dependency` — static source-text check of `validation/st_c3/detection.py` for `mt5`/`MetaTrader`/`socket`/`requests`/`urllib`/`datetime.now(`/`time.time(`. All 27 detection/primitive functions take `candles`/parameters as explicit arguments; none read `datetime.now()`, wall-clock time, or mutate module-level state. |

## Test count

`tests/st_c3/test_s1_g3_primitives.py`: 13 new tests, all passing. Combined
with pre-existing `tests/st_c3/` suites (golden/negative cases, detection
behavioral tests, structural-conformance causal/determinism tests), the
full `tests/st_c3/` directory now stands at 54 passing tests.

## New primitives added this session

- `validation/st_c3/detection.py::compute_rr(entry, stop, target, direction)`
  — reward/risk ratio arithmetic; raises `ValueError` on zero risk or an
  invalid direction string.
- `validation/st_c3/detection.py::premium_discount_zone(price, range_low, range_high)`
  — bare midpoint classification ("premium"/"discount"/"equilibrium");
  raises `ValueError` on a degenerate (non-positive-width) range.

Neither function is wired into `kernel.py`'s guard sequence or any
`EvidenceBundle` field — both are pure-arithmetic primitives provided to
satisfy S1-G3's evidence categories without touching the frozen state
machine or reopening S7/S12, both of which remain out of v1.x scope.

## What this report does NOT claim

- It does not claim S1-G3 is passed or accepted — that remains a separate
  owner decision.
- It does not claim the broader A2 substage (S1-G3 through S1-G6) is
  complete.
- It does not reopen S7 (OTE) or S12 (risk/SL/TP), both frozen out of
  v1.x scope by the 2026-07-27 funnel-freeze decision.
- It does not authorize execution, demo, live, or production work.

## Full suite status

`python -m pytest -q` run confirms no regressions from adding
`compute_rr()`/`premium_discount_zone()` and the new test file:
**317 passed, 0 failed** (2 pre-existing deprecation warnings in
`tests/test_backtest_v35.py`, unrelated to this work).
