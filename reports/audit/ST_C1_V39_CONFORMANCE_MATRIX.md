# ST-C1 v3.9 Conformance Matrix (E1/E2/E3 + M1/M2/M3 terms)

Companion to `reports/audit/ST_C1_V39_GOVERNANCE_CONFORMANCE_PRE_EDIT_FINDINGS.md`.
Per owner decision, this audits `specs/v3.9.yaml` in its own schema (E1/E2/E3
triggers, M1/M2/M3 models, displacement, sequencing, session, risk, trade
management) rather than the parked v3.7 G1-G10 gate-pipeline labels. Where a
row corresponds conceptually to one of the original prompt's G1-G10 gates,
that mapping is noted for traceability, but the authoritative structure is
v3.9's own.

Evidence for "current definition" columns comes from a source-level audit of
`specs/v3.6.yaml`, `docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md`,
`strategies/candidates/ST-C1_v1.yaml`, `src/smc_engine.py`, and
`src/signal_v35.py` — the last of these, despite its filename, implements the
v3.6 spec (its own comments cite "v3.6 spec Sec 2-4" etc. throughout), so it
is the actual code v3.9 inherits "unchanged geometry" from. `ST-C1_v1.yaml`
is a prose normalization of v3.6 and in places **diverges from the v3.6
YAML/code** (flagged below) — those divergences are pre-existing and not
created by v3.9.

Classification per gate: `VERIFIED` (numeric, deterministic, traceable to
spec+code), `PARTIAL` (numeric but incomplete or internally conflicting),
`NOT IMPLEMENTED` (flag/field exists, no executable logic), `UNKNOWN`
(no definition found anywhere).

---

## E1 — D1 gap reaction (HTF trigger) — *(≈ prompt's G1/G5 concept)*

- **v3.9 status:** `enabled: false`. All thresholds zeroed
  (`e1_gap_max_age_d1_bars: 0`, `e1_reaction_window_h1_bars: 0`,
  `e1_reaction_wick_ratio_min: 0`).
- **Point-in-time inputs:** none evaluated (gate is skipped entirely).
- **Boolean expression:** `E1_eligible := False` (constant).
- **Rejection code:** `REJECTED_E1_DISABLED` (new — no prior code path
  needs this since E1 was previously always-on; must be added so the
  engine explicitly records "not evaluated" rather than silently omitting
  E1 from the funnel).
- **Classification:** `VERIFIED` (trivially — a disabled gate is fully
  deterministic). No test needed beyond confirming E1 never contributes a
  trigger and is never silently re-enabled.

## E2 — H1 POI/order-block reaction — *(≈ prompt's G5 concept: fresh HTF POI)*

- **v3.9 status:** `enabled: true`, `poi_max_age_h1_bars: 120`,
  `reaction_wick_ratio_min: 0.0` (wick filter off — "qualification is via
  CHoCH, not wick geometry" per spec comment).
- **Current numeric definition (v3.6/code):**
  - POI = order block per `smc_engine.order_blocks()` (last opposite-color
    candle before a close breaks the last confirmed swing, k=2 fractal) or
    FVG per `smc_engine.fvgs()` (`c[i-2].high < c[i].low}` bull case).
  - Freshness/mitigation: FRESH -> MITIGATED -> INVALIDATED via
    `mitigation_status()`; INVALIDATED = close fully through the far side;
    MITIGATED = any touch without an invalidating close. Age gate in v3.6
    is 60 H1 bars; v3.9 widens this to 120.
  - "Touch" = numeric overlap test (`low<=high and high>=low`).
- **Gap found:** v3.9's own comment says E2 qualifies "via CHoCH... instead
  of wick geometry," but **no CHoCH function exists in `smc_engine.py` or
  `signal_v35.py`.** Those files use raw swing-break logic without a
  BOS/CHoCH label. The only numeric BOS-vs-CHoCH definition anywhere is in
  `strategies/candidates/ST-C1_v1.yaml` (prose contract, not code): BOS =
  close beyond the last confirmed swing *continuing* the established bias;
  CHoCH = the same close-break but *against* it. Wicks explicitly excluded
  — close-only. This is a real, usable, numeric definition, but it has
  never been implemented in an engine and v3.9 does not restate it itself.
- **Boolean expression (to adopt, pending §"Open items" sign-off below):**
  `E2_eligible := POI.status in {FRESH, MITIGATED} AND POI.age_h1_bars <= 120
  AND CHoCH_confirmed(reaction_bar, bias)` where `CHoCH_confirmed` uses the
  close-only, against-bias rule from `ST-C1_v1.yaml` L100-108.
- **Rejection codes:** `REJECTED_POI_STALE`, `REJECTED_POI_INVALIDATED`,
  `REJECTED_NO_CHOCH`.
- **Classification:** `PARTIAL`. POI freshness/mitigation is `VERIFIED`
  numeric; the CHoCH qualifier v3.9 depends on is `NOT IMPLEMENTED` in any
  engine and must be built new for v3.9, using `ST-C1_v1.yaml`'s definition
  as the numeric source (a genuine implementation gap, not a silent
  reinterpretation — flagged here before Phase 4, per the audit
  requirement).

## E3 — H1 liquidity sweep, structure-only — *(≈ prompt's G6 concept: LTF sweep+structure)*

- **v3.9 status:** `enabled: true`, `range_lookback_h1_bars: 60`,
  `sweep_wick_ratio_min: 0.0` (disabled), `reclaim_window_h1_bars: 0`
  (disabled — v3.6 used a 1-bar reclaim window; v3.9 removes the window
  entirely, which is a real, intentional relaxation per the RCR).
- **Current numeric definition (v3.6/code):** `smc_engine.liquidity_sweeps()`
  — bullish sweep = wick pierces a prior confirmed swing low, close
  reclaims above it, lower-wick ratio >= threshold (v3.6 default 0.5, v3.9
  sets 0.0 = off). Reclaim window in v3.6 is same-bar or next H1 bar only.
- **Correction (found via testing, see `ST_C1_V39_CLEAN_SMC_RCR.md`'s
  retraction addendum):** an earlier draft of this matrix claimed
  `reclaim_window_h1_bars: 0` was an undisclosed fourth relaxation. Direct
  testing (`tests/test_signal_v39.py`) proved this parameter has **no
  observable effect at any value** — `smc_engine.liquidity_sweeps()`
  already requires the reclaim close on the *same* bar as the sweep wick
  by definition (its own docstring), so `_e3_trigger`'s "reclaim window"
  loop always matches on its first iteration regardless of the configured
  window. There is no code path that can produce a delayed-reclaim signal
  at all, in v3.6, v3.7, or v3.9. **This is not a relaxation of any kind**
  — it is a no-op parameter inherited unchanged. The RCR's original account
  (three relaxations: E1 disabled, E2/E3 wick zeroed, displacement
  body-ratio-only) stands as correct.
- **Boolean expression:** `E3_eligible := sweep_and_same_bar_reclaim(range,
  lookback=60)` — reclaim is part of the sweep definition itself, not a
  separate windowed check.
- **Rejection codes:** `REJECTED_NO_SWEEP` (covers both "no sweep" and "no
  same-bar reclaim," since `liquidity_sweeps()` only reports events where
  both already occurred together).
- **Classification:** `VERIFIED` — numeric, deterministic, and (after
  correction) fully understood; no open item remains for this row.

## Displacement — body-ratio-only redefinition

- **v3.9 status:** `atr_period: 0`, `atr_mult: 0.0` (ATR-magnitude gate
  off), `body_ratio_min: 0.6`, `max_run_bars: 12`.
- **Current numeric definition (v3.6/code):**
  `smc_engine.displacement_move()` — run of same-direction candles,
  `body_ratio >= 0.5`, run starts within 2 bars of the sweep, max 3-bar
  run, **and** cumulative directional range `>= 1.5 * ATR(14)`.
- **v3.9 change:** drops the ATR/cumulative-range clause entirely, keeps
  only body-ratio (raised 0.5 -> 0.6), and widens the max run from 3 to 12
  bars. This is exactly the change the RCR names and justifies (targeting
  `REJECTED_NO_DISPLACEMENT`) — **matches the RCR, no gap.**
- **Boolean expression:** `Displacement_eligible := body_ratio(bar) >= 0.6
  for a same-direction run of 1..12 bars starting within
  start_offset_bars(=0) of the sweep bar`.
- **Rejection code:** `REJECTED_NO_DISPLACEMENT`.
- **Classification:** `VERIFIED` — fully numeric, and the divergence from
  v3.6 is the RCR's declared, intentional change.

## M1/M2/M3 — entry model, stop anchor

- **M1** (inducement sweep + CHoCH -> pullback/FVG midpoint): inducement =
  most recent confirmed swing (same swing detector as elsewhere — no
  separate numeric criteria). **Gap:** no numeric "valid pullback depth"
  exists distinct from "price reaches the FVG" — `retrace_max_bars: 30` is
  a time bound only, not a depth requirement. `NOT IMPLEMENTED`/`PARTIAL`.
- **M2** (OB ∩ FVG "Gold Zone" -> overlap midpoint): fully numeric via
  `smc_engine.order_blocks()` + `fvgs()` overlap test, unchanged from v3.6.
  `VERIFIED`.
- **M3** (sweep + displacement -> IFVG -> >=50% retrace entry): IFVG
  inversion and retrace-to-midpoint logic unchanged from v3.6, only the
  upstream displacement definition changes (see above, already reconciled).
  `VERIFIED`.
- **Stop anchor + buffer — two existing, DIFFERENT implementations found:**
  (a) `signal_v35.py`'s `INSTRUMENT_PROFILES` uses a **flat per-instrument-
  class constant** (fx_major 0.00030, fx_jpy 0.030, metal 0.50, crypto
  60.0); (b) `validation/historical_replay_engine.py._determine_stop()`
  uses `buffer = atr(window, -1, 14) * stop_buffer_atr_mult` (default
  `stop_buffer_atr_mult=0.15`) — genuinely **ATR-based**, which actually
  matches `ST-C1_v1.yaml`'s "ATR buffer" prose (L187); it is
  `signal_v35.py`'s flat constant that is the outlier, not the YAML prose.
  **v3.9 does not state a buffer value or method itself.** `PARTIAL` —
  since the replay harness (the actual executable path for any v3.9
  backtest) already uses the ATR-based method and it matches prose intent,
  Phase 4 should carry the ATR-based buffer forward for v3.9 rather than
  reintroducing `signal_v35`'s flat constant — this is reuse of the
  already-validated replay-engine convention, not a new design choice.

## Sequencing / first-qualifying-bar

- `sequencing.enforce_order: true`, `first_qualifying_bar_only: true`.
  Matches v3.6 spec §7 ordering (E-trigger before M-model before entry).
  `VERIFIED`.

## Session / timing

- London 07:00-16:00 UTC, NY 12:00-21:00 UTC, `dst_adjusted: false` (fixed
  UTC windows — a documented, accepted approximation, unchanged posture
  from v3.6). `max_e_to_m_h1_bars: 0` and `signal_ttl_bars: 0` are both
  **disabled** in v3.9 (v3.6 used `signal_ttl_bars: 1` — exactly one fill
  attempt). Disabling TTL means a qualifying signal never expires by bar
  count alone. This is consistent with v3.9's "minimal/structural-only"
  design intent stated in its own header, so not flagged as a gap — but it
  is a real, funnel-relevant relaxation worth naming explicitly in the
  population-ablation report (Phase 6) since it removes an implicit
  population ceiling that existed in v3.6/v3.7/v3.8.
- **Weekend/forced exit:** `weekend_exit: true`, `forced_exit: true` are
  set in v3.9 (inherited flags) but **no executable weekend-exit or
  forced-exit logic exists in `signal_v35.py` or `smc_engine.py`** — only
  session-hour gating (`_in_session()`) is implemented. `NOT IMPLEMENTED`.
  Must be built in Phase 4, not assumed to already work.

## Reward / cost model — *(≈ prompt's G8: net reward net of costs)*

- **Correction to an earlier draft of this matrix:** the gross-vs-net gap
  described below applies to `signal_v35.py`/`smc_engine.py` (the pure
  detection layer) only. `validation/historical_replay_engine.py` — the
  actual harness that produced `ST-C1_BASELINE_BACKTEST_REPORT.md` — already
  implements a real cost model: `HistoricalReplayEngine._cost_to_r()`
  computes spread/slippage/commission in price terms from
  `config/research_costs.yaml` + per-symbol metadata
  (`src/symbol_metadata.py`), converts to R, and `TradeRecord` carries both
  `gross_r` and `net_r` separately (`gross_r - cost_r = net_r`,
  `_simulate_trade_detail` L778-780). Break-even (+1R) and 50%-partial trade
  management are also already implemented there (L765-771), not just
  declared in YAML. **This closes part of the original gap** — a cost model
  and gross/net distinction exist and are reusable for v3.9; they do not
  need to be designed from scratch in Phase 4.
- **What is still missing for v3.9 specifically:** `HistoricalReplayEngine`
  currently sources its signal detection from `live_signal.latest_signal(c,
  k, window)` (`src/live_signal.py`), which takes only 3 positional
  arguments — no E1/E2/E3 enable flags, no wick-ratio thresholds, no POI/
  reclaim-window ages, no displacement body-ratio parameter. It cannot
  express v3.9's relaxations (E1 off, E2/E3 wick zeroed, unbounded reclaim,
  body-ratio-only displacement) no matter what contract YAML is passed to
  `contract_path` — pointing it at `ST-C1_v1.2.0.yaml` today would silently
  run v3.6-era default detection logic under a v3.9 label. This is exactly
  the "ad hoc surrogate... presented as v3.9" the task prohibits.
  **Classification: `NOT IMPLEMENTED`** for v3.9-specific detection; the
  cost/fill/trade-management scaffolding around it is `VERIFIED` and
  reusable once a v3.9-aware detection function replaces `latest_signal`.
- `risk.strategy.min_rr: 3.0` should be read as the **net** floor once
  `signal_v39`'s detections are run through the existing `net_r` machinery
  — this matches the platform norm of not overstating edge and requires no
  new design, only correct wiring in Phase 4.

## Target / DOL selection — *(≈ prompt's G9)*

- Priority: nearest un-swept external HTF liquidity within a lookback
  window; else nearest un-swept M5 swing extremum; else
  `REJECT_NO_TARGET` (no synthetic fixed-R substitute — matches
  `ST-C1_v1.2.0.yaml`'s stated target_rule exactly), with a fallback floor
  of `entry +/- risk*min_rr` (`historical_replay_engine._determine_target`,
  L657-669). **Re-examined:** `min()`/`max()` over a list of *prices* is
  deterministic even when two candidate levels are exactly equal in price,
  because tied candidates are interchangeable by construction (identical
  price -> identical entry/stop/target outcome) — there is no observable
  ambiguity to break. `VERIFIED`, not `PARTIAL` as an earlier draft of this
  matrix stated; no additional tie-break rule is needed.

## Trade management — *(≈ prompt's G10)*

- Break-even at +1R, partial take 50% at +1R, trailing disabled, time-stop
  disabled (structure-based invalidation only, consistent with the
  preset's stated minimal design). `stop_widening_allowed: false` matches
  the platform-wide hard rule (stops only tighten). `VERIFIED` as declared;
  execution of break-even/partial logic itself is trade-management code
  (out of this research engine's scope per the platform's System 1/System
  2 split) and is correctly not implemented here.

---

## Summary — status by area

| Area | Classification |
|---|---|
| E1 (disabled) | VERIFIED |
| E2 POI freshness/mitigation | VERIFIED |
| E2 CHoCH qualifier | PARTIAL — needs new implementation from ST-C1_v1.yaml's prose definition |
| E3 sweep/reclaim | VERIFIED — "reclaim window" parameter found to be a no-op, corrected, not a relaxation |
| Displacement | VERIFIED |
| M1 pullback depth | PARTIAL — no numeric depth requirement exists |
| M2 | VERIFIED |
| M3 | VERIFIED |
| Stop buffer | PARTIAL — v3.9 doesn't state a value; carry forward the replay engine's existing ATR-based method (matches ST-C1_v1.yaml prose) |
| Sequencing | VERIFIED |
| Session/TTL | VERIFIED (relaxation is intentional, name it in Phase 6 report) |
| Weekend/forced exit | NOT IMPLEMENTED (flags only, in both signal and replay layers) |
| Cost model / gross-vs-net RR | VERIFIED in `historical_replay_engine.py` (reusable); NOT IMPLEMENTED for v3.9-specific *detection* wiring |
| Target tie-break | VERIFIED — price-equal ties are not observably ambiguous |
| Trade management (declared+implemented) | VERIFIED — break-even/partial already executable in the replay harness |

## Open items requiring resolution before Phase 4 (engine implementation)

These are gaps in the existing v3.6/v3.9 material, not proposed strategy
changes. Filling them is implementation completion, not a research change,
*except* where marked RCR-relevant:

1. **CHoCH numeric definition for E2** — adopt `ST-C1_v1.yaml`'s
   close-only, against-bias definition as the implementation source (no
   alternative exists). Document this explicitly in the engine.
2. ~~E3 unbounded reclaim window~~ — retracted after testing proved the
   parameter is a no-op (see `ST_C1_V39_CLEAN_SMC_RCR.md`'s correction);
   not a relaxation, no action needed.
3. **Stop buffer method** — carry forward `historical_replay_engine.py`'s
   existing ATR-based buffer (`atr(14) * stop_buffer_atr_mult`); do not use
   `signal_v35.py`'s flat `INSTRUMENT_PROFILES` constant for v3.9.
4. **Cost model (gross-vs-net RR)** — reuse
   `historical_replay_engine.py`'s existing `_cost_to_r`/`gross_r`/`net_r`
   machinery; only the *signal detection* layer needs new v3.9-aware code
   (item 6 below), not the cost model itself.
5. ~~Target tie-breaker~~ — resolved on re-examination; no action needed.
6. **v3.9-aware signal detection** — `live_signal.latest_signal()` cannot
   express v3.9's parameters. Build `src/signal_v39.py` (a v3.9-parameterized
   variant of `signal_v35.py`'s E-trigger/M-model detection) and wire a
   `validation/historical_replay_engine_v39.py` that reuses
   `HistoricalReplayEngine`'s cost/fill/trade-management code but calls
   `signal_v39` for detection instead of `live_signal.latest_signal`.
7. **Weekend/forced exit** — must be implemented in the v3.9 replay path
   (point-in-time exit simulation only — no broker interaction); does not
   exist in `historical_replay_engine.py` today either (trades currently
   resolve via STOP/TARGET/TIMEOUT/CENSORED_END_OF_DATA only).

None of these change v3.9's declared behavior — they complete an
underspecified contract using existing, already-validated precedent
wherever one exists (items 3, 4), and build new code only where no
precedent exists (items 1, 6, 7). Item 2 is a disclosure, not a proposal.
