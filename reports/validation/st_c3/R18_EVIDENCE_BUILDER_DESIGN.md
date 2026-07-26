# R-18 Evidence Builder Design Proposal

**Type:** Design artifact / R-18 engineering proposal, pending owner
ratification. This document does not implement anything, does not modify
`specs/st-c3_v1.0.5.yaml`, and does not grant implementation authorization
beyond what A2/S1-G2 (`reference_funnel_assembly`, scoped 2026-07-26) already
covers. It exists to give the owner a single, concrete decision point before
`validation/st_c3/`'s `EvidenceBundle` builder is written, matching the design
-> ratification -> implementation sequence `RCR_ST-C3_v1.0.5_REPORT.md`
recommended in its Next Steps.
**Date:** 2026-07-26
**Status:** PROPOSED — not yet reviewed or approved by the owner.

---

## 1. Why this document exists

`R18_DETECTION_GAP_REPORT.md` and `RCR_ST-C3_v1.0.5_REPORT.md` establish that
R-18 (`existence_check_floor`) now needs exactly one remaining engineering
artifact: a function that turns a window of raw candles into the
`EvidenceBundle` object `validation/st_c3/kernel.py`'s `run_kernel()` already
consumes. `validation/st_c3/kernel.py`'s own docstring is explicit that the
kernel "never computes structure from price data itself" — evidence
construction is deliberately out of its scope
(`validator_never_computes_structure`, `detection_modules_produce_evidence`
in the frozen spec's `validator_rules`). That construction is the entirety of
what's missing.

Roughly half of the 15 required `Evidence` kinds can be produced by direct
calls into the existing, already-tested `src/smc_engine.py` primitives using
v1.0.5's now-frozen parameters (R-27/R-28/R-29/R-30 plus the earlier
R-04..R-09 filter thresholds). The other half require new glue logic that
`smc_engine.py` has no function for at all today. A third, smaller group
cannot be implemented at all yet, because the spec fields they depend on are
still literal placeholder strings, not numbers — a gap distinct from, and not
yet tracked alongside, R-18/R-27-30. Section 5 covers that group; nothing in
this document invents a value for it.

## 2. Function signature

```python
def build_evidence_bundle(candles: Sequence[dict], i: int, spec: dict) -> EvidenceBundle:
    """Build one bar's worth of ST-C3 EvidenceBundle from raw candles.

    candles: ascending OHLC dicts (smc_engine.load_candles() shape).
    i: bar index the candidate setup is evaluated as of.
    spec: the loaded specs/st-c3_v1.0.5.yaml dict (frozen parameters only —
          never a source of invented values).
    """
```

Intended caller, matching `tools/existence_check.py`'s `SignalFn` contract
exactly (no new interface):

```python
def signal_fn(candles, i):
    bundle = build_evidence_bundle(candles, i, spec)
    result = run_kernel(bundle)
    return ExistenceOutcome(
        signal=result.outcome == "VALID",
        rejection_code=result.rejection.code if result.rejection else None,
    )
```

This is the only integration point. Nothing about `tools/existence_check.py`,
`validation/st_c3/kernel.py`, or `validation/st_c3/evidence.py` needs to
change.

## 3. Tier 1 — direct reuse of existing `smc_engine.py` primitives

No new algorithm; the primitive already exists, already has tests, and the
v1.0.5-frozen parameter already matches its signature.

| Evidence kind | `smc_engine.py` call | v1.0.5-frozen parameter used |
|---|---|---|
| `HTFBiasEvidence` | `swings(h4_candles, k=2)` + `trend(hi, lo)` | R-27 `swing_fractal_lookback_k=2` |
| `SweepEvidence` | `liquidity_sweeps(candles, k=2, min_wick_ratio=0.50)` | R-04 `wick_ratio_min=0.50` |
| `DisplacementEvidence` + `BOSEvidence` | `displacement_move(candles, sweep_i, direction, body_ratio_min=0.50)` | R-07 `displacement_body_ratio_min=0.50` + `displacement_atr_floor_multiplier=1.0` |
| `FVGEvidence` | `fvgs(candles, min_gap=0.15 * atr(candles, i, 14))` | R-29 `fvg_min_gap_atr_multiplier=0.15` |
| `OrderBlockEvidence` | `order_blocks(candles, k=2)` | R-27's k, reused per `order_blocks()`'s own structural rule (no new number, per `RCR_ST-C3_v1.0.5_REPORT.md`) |
| `InvalidationSwingEvidence` | `swings(m1_or_m3_candles, k=2)` — nearest confirmed opposing swing | R-27's k, applied on LTF |
| `DealingRangeEvidence` | `equilibrium(candles, i, window)` for the origin/extreme pair already located by `BOSExtremeEvidence` (Tier 2) | — (derived, no independent parameter) |
| `OTEEvidence` | `equilibrium(candles, i, window)` compared against `ote_stage.ote_band_min/max` (0.62/0.79, still spec-marked provisional but numerically usable) | `ote_band_min=0.62`, `ote_band_max=0.79` |

Each of these is "wiring," matching the scoping the owner and prior reports
already anticipated: call the existing function, map its return dict onto the
`Evidence` object's required fields via `make_evidence()`, set `valid`
according to whether the primitive found a qualifying event at/near bar `i`.

## 4. Tier 2 — new glue logic, fully spec-supported (no missing numbers)

These have no equivalent `smc_engine.py` function today, but every number
they need is already frozen — this is new code, not a new decision.

| Evidence kind | Algorithm (3-6 sentences) |
|---|---|
| `SweepReclaimEvidence` | Given the `SweepEvidence` bar index and the swept `level`, scan forward bar-by-bar counting how many bars until close crosses back inside the level (`reclaim_within_bars`). Compare against the max-allowed-bars parameter (see Section 5 — this parameter itself is blocked, not this algorithm). `reclaimed=True` iff the reclaim happens within that bound; `valid` mirrors `reclaimed`. |
| `BOSExtremeEvidence` | After a confirmed `BOSEvidence`, track the extreme price reached in the BOS direction as `provisional_extreme`, updating it bar-by-bar until price retraces >= R-30's `pullback_depth_atr_multiplier=0.30 * ATR(1)` against the BOS direction. At that point `locked_extreme` freezes to the last `provisional_extreme` and `pullback_detected=True`. This is a direct, mechanical implementation of R-30's frozen definition — no invented threshold. |
| `LTFConfirmationEvidence` | On the M3/M1 series, run `swings()` + `trend()` (or a local CHoCH check: has the M3/M1 structure flipped direction since the MF confluence bar) to derive `choch_direction`, and `liquidity_sweeps()` on the same LTF series to derive `sweep_local_liquidity`. Both reuse Tier-1 primitives; the "new" part is only the multi-timeframe wiring (evaluating the same primitives on a different candle series and aligning bar indices across timeframes), not a new detection concept. |
| `TargetEvidence` (tp1/tp2/tp3) | Compute `rr = abs(target_level - entry_price) / abs(entry_price - sl_price)` for each of the three target definitions in `targets_stage` (`prior_swing`/`internal_liquidity_pocket` for TP1, `equal_highs_lows`/`major_liquidity_pool` via `liquidity_pools()` for TP2, `h4_swing`/`deeper_liquidity_target` via HTF `swings()` for TP3). `valid` iff a qualifying structural target exists in the correct direction beyond the entry price; the `rr_min` gates (3.0/2.0/3.5) are applied by the kernel itself, not by this evidence — the evidence only needs to report the computed `rr`. |

## 5. Tier 3 — RESOLVED 2026-07-26 (was: blocked, spec value a placeholder)

**Update 2026-07-26: resolved.** These three fields were literal placeholder
strings in `specs/st-c3_v1.0.5.yaml`, untracked under any existing R-number,
and distinct from the R-27-R-30 gap (those had missing *algorithms*; these
had a defined algorithm but no usable *number*). The owner decided all
three directly (see `R18_OWNER_DECISION_PACKET.md` and
`OWNER_DECISION_LOG.md`'s R-31/R-32/R-33 rows), folded into
`specs/st-c3_v1.0.6.yaml` via `reports/governance/st_c3/RCR_ST-C3_v1.0.6_REPORT.md`:

| Evidence field | Spec field | v1.0.5 (placeholder) | v1.0.6 (decided) |
|---|---|---|---|
| `SweepReclaimEvidence.max_allowed_bars` | `liquidity_sweep_stage.sweep_reclaim_max_bars` (N_SWEEP) | `"PROVISIONAL_1_TO_3"` | **2 bars** (R-31, A2/S1-G2 phase value) |
| `EntryWindowEvidence.max_allowed_bars` | `entry_window_stage.entry_window_bars` (MAX_ENTRY_BARS) | `"PROVISIONAL_3_TO_5_M3_BARS"` | **4 M3 bars** (R-32) |
| `SessionWindowEvidence.session` gating bounds | `sessions.london_window_utc` / `ny_window_utc` | `"PROVISIONAL_07_00_TO_10_00"` / `"PROVISIONAL_13_00_TO_16_00"` | **London 07:00-10:00 UTC, NY 13:00-16:00 UTC** (R-33, ratified as final) |

`tests/st_c3/` re-verified passing (20/20) after `validation/st_c3/evidence.py`'s
`SPEC_PATH` was repointed to `specs/st-c3_v1.0.6.yaml`. All 15 Evidence
kinds now have every number they need; nothing in Tier 1/2/3 blocks
`build_evidence_bundle()` implementation on spec-value grounds anymore.
R-31's non-adopted phase-conditional alternatives (1 bar for a future
A3+/production-tightening phase, 3 bars for exploratory robustness testing)
are recorded in `OWNER_DECISION_LOG.md`, not implemented — re-opening this
field for a phase change is a future decision, not automatic.

## 6. Evidence registry compliance

- Every `Evidence` object is constructed exclusively through
  `validation.st_c3.evidence.make_evidence()`, which already raises
  `ValueError` if the caller supplies fields outside the exact set
  `specs/st-c3_v1.0.5.yaml`'s evidence registry declares for that `kind` —
  the builder cannot silently drift from the frozen spec even by mistake.
- No new Evidence kind, field, state, transition, or rejection/termination
  code is proposed anywhere in this document.
- No new numeric spec parameter is proposed; Tier 1/Tier 2 use only values
  already frozen in v1.0.2-v1.0.5. Tier 3 explicitly proposes none.
- Rejection reporting flows through the kernel unchanged: `run_kernel()`
  already produces exactly one `Rejection(state, code, reason, evidence_id)`
  per failed guard; `signal_fn()` only needs to read
  `result.rejection.code`.

## 7. What this document is not

- Not code. No file under `validation/st_c3/` or `src/` is created or
  modified by this document.
- Not a spec revision. `specs/st-c3_v1.0.5.yaml` is unchanged.
- Not an authorization to open A3, execute, optimize, demo, or trade live —
  all of that remains blocked exactly as `NEXT_ACTION.md`/`PROJECT_STATUS.md`
  state, independent of whether this design is ratified.
- Not a claim that Tier 3's gap is resolved — it is surfaced, not decided.

## 8. Requested owner decision

1. **Ratified 2026-07-26.** Owner approved the Tier 1 / Tier 2 approach as
   the basis for `validation/st_c3/evidence_builder.py`, as designed, no
   changes requested.
2. **Resolved 2026-07-26.** Tier 3's three fields were owner-decided
   directly (R-31/R-32/R-33), folded into `specs/st-c3_v1.0.6.yaml` — see
   Section 5.
3. **Ratified 2026-07-26.** Owner chose a full S1-S13 run over a partial
   S1-S9 interim run, since Tier 3 no longer blocks it.

All three items are now closed. Implementation of `build_evidence_bundle()`
may proceed within the existing A2/S1-G2 scope
(`reference_funnel_assembly`, `existence_check_conformance_run`).
