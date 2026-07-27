# R-18 Detection Module — Scope and Limits Report

**Date:** 2026-07-26
**Module:** `validation/st_c3/detection.py`
**Tests:** `tests/st_c3/test_detection.py` (16 tests, real GBPUSD H4/M15 data)

---

## What this delivers

Real price-level detection functions that produce spec-conformant
`Evidence` objects (via the existing `validation.st_c3.evidence.
make_evidence`), parameterized entirely from `specs/st-c3_v1.0.5.yaml`'s
now-frozen values (R-04, R-05, R-06, R-07, R-23, R-24, R-27, R-28, R-29,
R-30). These integrate with the existing, already-tested kernel
(`validation/st_c3/kernel.py`'s `EvidenceBundle`/`run_kernel()`) rather than
duplicating it — a corrected design from an earlier proposed API that would
have bypassed the kernel entirely.

Covers, with real detection logic against candle data:

| Stage | Function | Frozen parameters used |
|---|---|---|
| S1_HTF_BIAS | `detect_htf_bias_events`, `htf_bias_evidence_at` | R-27 (k=2) |
| S2_SWEEP (raw only) | `detect_sweep_at` | R-04 (wick_ratio_min=0.50), R-05 (equal_tolerance=0.10x MF_ATR(1)), R-06 (max_age=15), R-27 (k=2) |
| S4_DISPLACEMENT_BOS | `find_bos_candidates`, `bos_confirmed`, `displacement_evidence_for`, `bos_evidence_for` | R-07 (body_ratio_min=0.50, ATR floor=1.0), R-28 (N=2), R-27 (k=2) |
| S5_BOS_EXTREME_LOCK | `bos_extreme_evidence_for` | R-30 (pullback depth=0.30x ATR(1)) |
| S6_DEALING_RANGE | `dealing_range_evidence_for` | R-27 (k=2) — derived geometry, no threshold needed |
| S8_FVG_OB_CONFLUENCE | `fvg_evidence_near`, `order_block_evidence_near` | R-29 (FVG min gap=0.15x MF_ATR(1)), R-23 (OB freshness<=3 swings), R-24 (FVG freshness<=1 swing), R-27 (k=2) |

All reuse only existing generic `src.smc_engine` primitives (`swings`,
`atr`, `fvgs`, `order_blocks`) — no ST-C3-specific detection algorithm was
invented beyond translating already-decided spec parameters into calls
against those primitives, per the discipline established in
`scripts/research_r27_r30_gbpusd.py`.

**Correctness note on freshness (R-23/R-24):** the spec's freshness rule is
phrased in terms of "MF swing index," not bar count. `detection.py`
measures this properly via `_mf_swing_index_series`/`_swings_between`
(counting actual confirmed swings between an FVG/OB's creation bar and the
current bar), not a bars-elapsed proxy — an earlier draft of this module
used an invented "bars per swing" conversion factor, which was caught and
replaced before this was finalized.

## What this does NOT deliver — genuinely blocked stages

Six funnel stages remain out of scope, each blocked on a field that was
never ratified (distinct from R-27–R-30, which now are):

| Stage | Blocked on |
|---|---|
| S3_SWEEP_RECLAIM | `liquidity_sweep_stage.sweep_reclaim_max_bars` — `PROVISIONAL_1_TO_3`, never ratified |
| S7_OTE | `ote_stage.ote_band_min`/`ote_band_max`/`equilibrium_boundary` — reference-doc provisional, never owner-ratified |
| S9_LTF_CONFIRMATION | no owner-ratified M3/M1 CHoCH detection parameters exist at all |
| S10_SESSION_GATEKEEPER | `sessions.london_window_utc`/`ny_window_utc` — `PROVISIONAL`, never ratified |
| S11_ENTRY_WINDOW | `entry_window_stage.entry_window_bars` — `PROVISIONAL_3_TO_5_M3_BARS`, never ratified |
| S12_RISK_SLTP | `stop_loss_stage.buffer_points_atr_multiplier`'s guard *direction* formulation is explicitly flagged unconfirmed in `OWNER_DECISION_LOG.md` (R-08) |

**Consequence:** a full S0→S13 real signal-rate existence-check (a
complete R-18 answer) cannot run yet — the funnel would reach S6/S8 with
real detection, then have nothing to feed S7 (OTE) onward. `detect_module`
functions for S7/S9-S12 were not written and no threshold was invented for
them; `NOT_YET_SUPPORTED` in `detection.py` documents this explicitly so
a future caller doesn't assume otherwise.

## One scoping simplification, noted explicitly

**S2 (sweep) uses the single nearest prior confirmed swing level**, not a
clustered equal-highs/lows liquidity pool (as `validation/st_c2/structure.
py` builds for ST-C2). R-05's tolerance is applied for the pierce-check
itself, but full pool selection/ranking across multiple equal levels is a
scoping choice for this pass, not a spec gap — a future pass could extend
`detect_sweep_at` to pool-based selection without needing any new owner
decision.

## Verification performed

- All four v1.0.5 parameters (k=2, N=2, 0.15, 0.30) plus R-04/R-05/R-06/
  R-07/R-23/R-24 confirmed pulled directly from `specs/st-c3_v1.0.5.yaml`
  via `htf_bias_params()`/`sweep_params()`/`displacement_bos_params()`/
  `fvg_ob_params()` — asserted exactly in
  `test_params_match_frozen_spec_values`, so drift from the frozen spec
  would fail a test, not go unnoticed.
- `tests/st_c3/test_detection.py` (16 tests) run against real GBPUSD H4
  (5,000 candles)/M15 (30,000 candles) data — determinism, spec-conformant
  Evidence shape, and monotonic threshold behavior (stricter parameters
  reject at least as many candidates as looser ones) are all asserted, not
  just "runs without crashing."
- Every produced `FVGEvidence`/`OrderBlockEvidence` asserts
  `inside_ote is False` — since S7 (OTE) is `NOT_YET_SUPPORTED`, nothing
  in this module is allowed to silently claim OTE confluence.
- Full repo suite: 291 passed (275 previous + 16 new), 0 failed.

## What did NOT happen

- No execution, optimization, backtesting, demo, live, or A3 logic.
- No signal-rate/existence-check run performed yet — that requires either
  (a) accepting a partial funnel that stops at S6/S8, which would not be a
  meaningful R-18 answer, or (b) first resolving the six still-blocked
  fields above. Neither was done here.
- No spec revision — `specs/st-c3_v1.0.5.yaml` is unchanged; this is pure
  implementation against what's already frozen.

## Next steps

To actually compute R-18 (a real existence-check signal rate), the owner
needs to resolve the six blocked fields above (`sweep_reclaim_max_bars`,
OTE band/equilibrium, M3/M1 CHoCH parameters, session windows,
`entry_window_bars`, R-08's guard direction) — likely via the same
empirical-research-then-ratify pattern used for R-27–R-30. Until then, this
module is real, tested, spec-conformant detection code for six of the
sixteen funnel stages, wired to feed the existing kernel once the rest are
unblocked — not a complete R-18 answer by itself.
