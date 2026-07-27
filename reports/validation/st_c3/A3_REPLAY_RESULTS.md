# A3 Replay Results — ST-C3

**Date:** 2026-07-27
**Spec:** `specs/st-c3_v1.0.6.yaml`
**Tool:** `validation/st_c3/a3_replay_engine.py` (`run_a3_replay()`) via
`validation/run_st_c3_a3_replay.py`. Reuses the exact same
`build_evidence_bundle()`/`run_kernel()` call pattern as R-18's existence
check — no new detection logic. Adds post-S13 TradePlan lifecycle
simulation (SL/TP1-3 tracking, RR realization, BIAS_FLIP monitoring) and
replay-wide metrics aggregation, which the existence-check harness never
had a reason to build.
**Raw output:** `reports/a3/ST-C3_v1.0.6_GBPUSD_M15_a3_replay.json`
**Authorization:** owner decision, 2026-07-26, "A3 statistical validation —
OPENED" entry in `OWNER_DECISION_LOG.md`.

---

## Result

| Metric | Value |
|---|---|
| Symbol / timeframe | GBPUSD / M15 |
| Window scanned | 2026-06-05 17:00 -> 2026-07-24 11:30 (same window as R-18) |
| Total M15 bars scanned | 3,339 |
| Signals (S13 `TRADE_PLAN_EMIT` reached) | **0** |
| TradePlans simulated | **0** |
| Closed trades / win rate / avg RR | N/A — no TradePlan ever emitted |

Rejection breakdown (identical to R-18, same funnel + same data):

| Code | Count |
|---|---|
| `R1_HTF_BIAS_UNCLEAR` | 304 |
| `R2_NO_SWEEP` | 304 |
| `R3_NO_DISPLACEMENT_BOS` | 202 |
| `R4_NO_OTE_PULLBACK` | 16 |
| `R6_NO_LTF_CONFIRMATION` | 2 |

Session bar counts: LONDON 420, NY 408, outside-session (`INVALID`) 2,511.

## What this run does and does not establish

- **Confirms the replay engine itself is functionally correct** on the
  signal-detection path: it reproduces R-18's exact rejection-code
  breakdown bar-for-bar, because it calls the identical
  `build_evidence_bundle()`/`run_kernel()` pair over the identical data.
  This is a useful cross-check, not a new finding about the strategy.
- **Does not exercise the new code this file actually adds.** TradePlan
  lifecycle simulation (`_simulate_lifecycle`: SL/TP1-3 tracking, RR
  realization, partial-exit accounting, BIAS_FLIP re-evaluation) never ran
  against a real TradePlan, because none was ever emitted on this window.
  The lifecycle logic is exercised by construction/code-review only here,
  not by empirical data. It has no unit-test coverage yet either — that is
  a real gap, not a hidden one.
- **Does not produce any RR distribution, win rate, session-behavior, or
  robustness data** — the entire point of A3 — because the underlying
  funnel never fires often enough on the only data available (a 7-week
  GBPUSD window) to generate a single trade to measure.
- **Does not indicate ST-C3 v1.0.6 is invalid.** The same caveats R-18
  documented still apply: a 7-week single-symbol window is far short of
  `specs/st-c3_v1.0.6.yaml`'s own 3-10 year replay-requirement note for a
  real A3 statistical read, and the bottleneck (S1 HTF-bias ambiguity and
  S2 sweep absence, roughly evenly split) is a funnel-strictness signature
  over a short window, not a demonstrated defect.

## What would actually move A3 forward

A3 remains open but effectively blocked on **data volume**, not code:

1. **More history for GBPUSD**, or **EURUSD data deep enough to replay**
   (currently EURUSD's H4/M15 CSVs have only ~20 rows — unusable, per
   `R27_R30_RESEARCH_REPORT.md`) — the only way to get the funnel to fire
   often enough to produce lifecycle/RR/session data.
2. ~~Lifecycle-logic unit tests against synthetic TradePlans~~ — **done,
   2026-07-27**: `tests/st_c3/test_a3_lifecycle.py` (5 tests) exercises
   `_simulate_lifecycle` directly against hand-built `TradePlan` fixtures
   and scripted price paths — TP1-only partial close, full TP1-TP2-TP3
   closure, immediate SL, partial-TP1-then-SL, and a BIAS_FLIP termination
   (via an engineered `smc_engine.swings()`/`trend()` zigzag on synthetic
   H4 data). All 5 pass; full suite remains green (280 passed). This
   closes the test-coverage gap identified above, independent of data
   availability — see `reports/validation/st_c3/A3_SYNTHETIC_LIFECYCLE_RESULTS.md`
   for detail.

## Deliverables

- `validation/st_c3/a3_replay_engine.py` — replay loop, lifecycle
  simulation, metrics accumulator.
- `validation/run_st_c3_a3_replay.py` — GBPUSD runner.
- `reports/a3/ST-C3_v1.0.6_GBPUSD_M15_a3_replay.json` — raw result.
- This report.
