# R-18 Existence-Check Results

**Date:** 2026-07-26
**Spec:** `specs/st-c3_v1.0.6.yaml`
**Tool:** `tools/existence_check.py` (unmodified) via
`validation/run_st_c3_existence_check.py`, `signal_fn` backed by
`validation/st_c3/evidence_builder.build_evidence_bundle()`.
**Raw output:** `reports/existence/ST-C3_v1.0.6_GBPUSD_M15_existence.json`

---

## Result

| Metric | Value |
|---|---|
| Symbol / timeframe | GBPUSD / M15 |
| Window scanned | 2026-06-05 17:00 -> 2026-07-24 11:30 (real calendar time) |
| Total M15 windows scanned | 3,339 |
| Signals (S13 `TRADE_PLAN_EMIT` reached) | **0** |
| Signal rate | **0.0** |

Rejection breakdown (bars that reached `S0_INIT` but failed a later guard):

| Code | Stage | Count | % of in-session bars |
|---|---|---|---|
| `R2_NO_SWEEP` | S2/S3 | 304 | 36.7% |
| `R1_HTF_BIAS_UNCLEAR` | S1 | 304 | 36.7% |
| `R3_NO_DISPLACEMENT_BOS` | S4/S5 | 202 | 24.4% |
| `R4_NO_OTE_PULLBACK` | S6/S7 | 16 | 1.9% |
| `R6_NO_LTF_CONFIRMATION` | S9/S10 | 2 | 0.2% |
| `R5_NO_FVG_OB_CONFLUENCE`, `R7_ENTRY_WINDOW_EXPIRED`, `R8_INVALID_RISK_OR_TARGET` | S8, S11, S12 | 0 | — |

828 of 3,339 bars reached `S0_INIT` (session open); the remaining 2,511 were
`NOT_STARTED` (outside the London/NY session windows — consistent with
London+NY covering 6 of 24 UTC hours, ~24.8% of bars, matching the 828/3339
= 24.8% observed).

## Why this is a real R-18 data point, with real caveats

This is a genuine run against real GBPUSD price data through the real,
frozen v1.0.6 funnel — not a synthetic readiness check
(`run_st_c3_existence_readiness.py`'s hand-built bundles) and not a
backtest (no trade simulation, sizing, or P&L; `run_kernel()` only
evaluates whether S13 is reached). It answers exactly the question R-18
asks: does the funnel ever fire on real data. **As of this run, over this
window, it does not.**

Three things temper how much weight this single number should carry:

1. **Short window.** The H4/M15/M3 overlap is bounded by `data/GBPUSD_M3.csv`'s
   start date (2026-06-05) — only ~7 weeks. `specs/st-c3_v1.0.6.yaml`'s own
   replay-requirement note (`instruments` field) calls for 3-10 years per
   instrument at Phase 5 (A3); this is nowhere near that, by design — R-18
   is an existence check, not a statistical validation, and A3 remains
   blocked regardless of this result.
2. **Implementation simplifications, documented in
   `validation/st_c3/evidence_builder.py`, not hidden:**
   - `SweepReclaimEvidence`: `smc_engine.liquidity_sweeps()` only returns
     already-reclaimed sweep events (the wick-pierce and reclaiming close
     are the same candle in that primitive's definition), so
     `reclaim_within_bars` is always 0 — R-31's `max_allowed_bars=2` ceiling
     is therefore never binding. This cannot explain the R2 rejections
     (304 of them are "no sweep found at all," not "sweep found but not
     reclaimed in time").
   - `TargetEvidence` TP2/TP3: derived from `smc_engine.liquidity_pools()`
     and HTF `swings()` respectively — a reasonable but not
     owner-ratified-in-detail mapping from the spec's prose definitions
     (`equal_highs_lows`/`major_liquidity_pool`, `h4_swing`/`deeper_liquidity_target`).
     Irrelevant to this result, since 0 setups ever reached S8 (FVG/OB
     confluence), let alone S12 (targets).
   - `LTFConfirmationEvidence`'s CHoCH check reuses `smc_engine.swings()`/`trend()`
     on the M3 series rather than a dedicated CHoCH-vs-BOS primitive
     (`smc_engine.py` has none) — also irrelevant here, since only 2 bars
     ever reached S9.
3. **The bottleneck is upstream, at S1/S2, roughly evenly split** — HTF
   bias ambiguity (R-27's `k=2` swing detection on H4 often doesn't resolve
   a clear HH/HL or LH/LL over this short window) and no qualifying
   external sweep (R-04's `wick_ratio_min=0.50` combined with R-06's
   15-bar freshness window). Only 202 bars (24.4%) even reach the
   displacement/BOS stage, and of those, none clear all of S4 through S12.
   This is a funnel-strictness signature, not an implementation-bug
   signature — every stage that did produce a rejection produced the
   correct, spec-defined rejection code for a genuinely-absent structural
   feature, not an exception or a malformed bundle.

## What this does and does not mean

- **Does not** mean ST-C3 v1.0.6 is invalid, rejected, or should be
  abandoned — a 7-week window on one symbol is far too small to draw a
  strategy-level conclusion, and R-18 was never meant to (that is A3's job,
  separately blocked).
- **Does** satisfy the mechanical requirement `NEXT_ACTION.md`/`PROJECT_STATUS.md`
  described for R-18: a real signal_fn, backed by real detection code
  against real candle data, producing an actual signal-rate number instead
  of `UNRESOLVED`.
- **Does not** authorize A3, execution, optimization, demo, or live —
  unaffected by this result, exactly as before.
- A natural next research question (not answered here, not authorized by
  this document) is whether a longer overlapping HTF/MF/LTF dataset would
  change this outcome, or whether R1/R2's near-even 304/304 split reflects
  parameters (R-27's `k=2`, R-04's `wick_ratio_min=0.50`) worth revisiting
  through a proper RCR rather than this existence check alone.

## Deliverables

- `validation/st_c3/evidence_builder.py` — real detection-module code,
  `build_evidence_bundle()`.
- `validation/run_st_c3_existence_check.py` — GBPUSD runner, wires
  `evidence_builder` into `tools/existence_check.py`'s unmodified
  `SignalFn` contract.
- `reports/existence/ST-C3_v1.0.6_GBPUSD_M15_existence.json` — raw result.
- This report.
