# ST-C3 Owner Decision Log

**Purpose:** record the owner's actual decision for each `RESOLUTION_MATRIX.md`
field, distinct from the proposals in that matrix and in `DECISION_PACKAGES.md`.
This file is intentionally mostly empty — it is a log the owner fills in, not
a report the agent generates on the owner's behalf. Filling in a "Decision"
column with a proposed value would defeat its purpose.

**Status (as of 2026-07-26): 19 of 26 fields decided (R-01, R-02, R-05,
R-07, R-08*, R-09, R-10, R-12, R-13, R-14, R-15, R-16, R-17, R-19, R-20,
R-23, R-24, R-25, R-26); 2 more explicitly DEFERRED (R-21, R-22).** `*`
R-08's numeric value is decided but its guard formulation has a flagged
correctness issue (non-directional invalidation check) needing owner
confirmation before implementation — see R-08's Notes. R-11 was decided
then superseded same-day by the Open Conflict 1 resolution (fixed lot
replaces percentage risk; field removed from v1.x). Both Open Conflicts
are now RESOLVED. Two scope decisions (break-even/trailing out of scope;
TP2/TP3 revert to frozen) are recorded below. Six new fields have been
added since the original 20 (R-21 fixed lot size, R-22 instrument
selection logic, R-23 OB freshness, R-24 FVG freshness, R-25 max positions
per instrument, R-26 daily max trades). **Critical path is fully clear.**
**Two unresolved dependencies:** R-24's "FVG expiration" reference
(mismatched R-06 citation) and R-08's directional-check gap. **Four items
ruled out of v1.x scope** (deferred to a possible v2.x cycle): break-even,
trailing-stop, session-close forced-exit ("R-20" mismatch — distinct from
the real, now-decided R-20 field below), and dual-timeframe bias
confirmation ("R-03" mismatch — distinct from the real, still-pending R-03
field below). **R-04 and R-06 are now decided (2026-07-26) via empirical research against
GBPUSD M15 — see `reports/validation/st_c3/R04_R06_RESEARCH_REPORT.md`. R-03
(`sessions.low_liquidity_filters`) is now decided (2026-07-26) via the
RCR-ST-C3-v1.0.2 governance parameter-freeze directive — see its row above.**
**Remaining 1 row genuinely `PENDING`: R-18 (`existence_check_floor` — needs
a working signal function across the entire funnel plus real price-level
detection modules run against real candle data; the ST-C3 reference kernel
(`validation/st_c3/kernel.py`) now exists and is existence-check-tool
wire-compatible, but a real R-18 number still requires those price-level
detection modules, which the v1.0.2 parameter freeze does not itself build —
see `reports/governance/st_c3/RCR_ST-C3_v1.0.2_REPORT.md`).**
**Status: 22 of 26 fields decided, 2 deferred, 4 ruled out of v1.x scope,
1 pending. All 22 decided fields are folded into `specs/st-c3_v1.0.2.yaml`
(see `reports/governance/st_c3/RCR_ST-C3_v1.0.2_REPORT.md`).**

**2026-07-26 update:** R-21 (`fixed_lot_size` = 0.01) is now decided.
A submission mislabeled "R-22" actually revised R-02's already-decided
`instruments` value (XAUUSD removed) rather than resolving R-22 itself —
see the R-02 and R-22 rows above. **Status: 23 of 26 fields decided
(R-21 newly added), 1 revised (R-02), 1 deferred (R-22, still genuinely
unresolved), 4 ruled out of v1.x scope, 1 pending (R-18). Folded into
`specs/st-c3_v1.0.3.yaml`** (see `reports/governance/st_c3/RCR_ST-C3_v1.0.3_REPORT.md`).

**2026-07-26 update (same day, later):** R-22 (`instrument.selection_logic`)
is now separately, correctly decided — computed_rr-based tie-break with an
EURUSD fixed-priority fallback; see its row above. **Status: 24 of 26
fields decided, 1 revised (R-02), 4 ruled out of v1.x scope, 1 pending
(R-18 — the only field left unresolved of the original 26). Folded into
`specs/st-c3_v1.0.4.yaml`** (see `reports/governance/st_c3/RCR_ST-C3_v1.0.4_REPORT.md`).

**2026-07-26 update (same day, later still):** attempting to begin real R-18
price-level detection work surfaced a new, lower-level gap — the
structural-detection *algorithms* (swing/fractal lookback, BOS confirmation
bars, FVG/OB identification, pullback definition) have no defined
parameters anywhere, unlike the filter thresholds R-04/R-06/R-07 etc.
already decided. Tracked as new **R-27 through R-30** (all `PENDING`, none
proposed on the owner's behalf per this log's own convention). See
`R18_DETECTION_GAP_REPORT.md`. R-18 itself remains blocked on these — no
code was written, no parameter was invented or inherited from ST-C2.

**2026-07-26 update (same day, later still):** owner directed R-27–R-30 to
proceed via the empirical-research path (same precedent as R-04/R-06) rather
than direct owner-supplied values. See `R18_R27_R30_RESEARCH_PLAN.md`.

**2026-07-26 update (same day, later still):** the empirical research pass
ran — `reports/validation/st_c3/R27_R30_RESEARCH_REPORT.md`
(`scripts/research_r27_r30_gbpusd.py`, GBPUSD H4/M15 only — EURUSD's H4/M15
CSVs have only 19-21 rows, insufficient for distribution research). No
value is decided by this report; it surfaces tradeoff curves for R-27
(swing/fractal k) and R-29's FVG half, and initially flagged R-28/R-30 as
needing reformulation.

**2026-07-26 update (same day, later still):** on reflection, R-28's
"modeling ambiguity" finding was a self-correction of an overclaim, not a
real defect — a monotonically-climbing whipsaw rate as the confirmation
window grows is expected (a longer window has strictly more chances to
observe a reversal), and re-read correctly it's the same kind of tradeoff
curve as R-27. Reclassified as ready for ratification. R-30 genuinely did
need reformulation (the naive "first opposite close" measure really is too
permissive); a depth-filtered follow-up ran and produced a real tradeoff
curve. **All four of R-27/R-28/R-29/R-30 are now ready for owner
ratification** — none require further research. See the updated
`R27_R30_RESEARCH_REPORT.md`.

**2026-07-26 update (same day, final):** owner ratified all four —
R-27 k=2, R-28 N=2, R-29 (FVG half) 0.15x MF_ATR(1), R-30 0.30x ATR(1).
Folded into `specs/st-c3_v1.0.5.yaml`. **Status: R-18 is now the only
tracked field left unresolved, and it no longer needs any further spec
decision — only real detection-module code, built against the now-fully-frozen
parameter set, and a run against real candle data.** See
`reports/governance/st_c3/RCR_ST-C3_v1.0.5_REPORT.md`.

**2026-07-26 update (same day, later still): PENDING RATIFICATION — R-18
EvidenceBundle Builder Design.** Before writing the real detection-module
code `RCR_ST-C3_v1.0.5_REPORT.md`'s Next Steps called for, a design pass was
run against the actual repo contracts (`tools/existence_check.py`'s
`SignalFn`, `validation/st_c3/kernel.py`'s `EvidenceBundle`/`run_kernel()`,
`validation/st_c3/evidence.py`'s `make_evidence()` registry validation, and
the hand-built bundles in `_readiness_bundles.py`/`tests/st_c3/fixtures.py`)
to scope `build_evidence_bundle(candles, i, spec) -> EvidenceBundle` before
any code is written. Result: `reports/validation/st_c3/
R18_EVIDENCE_BUILDER_DESIGN.md` — not decided here, per this log's own
convention. Three findings, not proposed as decisions:
- **Tier 1** (direct reuse, no new logic): `HTFBiasEvidence`,
  `SweepEvidence`, `DisplacementEvidence`+`BOSEvidence`, `FVGEvidence`,
  `OrderBlockEvidence`, `InvalidationSwingEvidence`, `DealingRangeEvidence`,
  `OTEEvidence` — each maps directly onto an existing `src/smc_engine.py`
  primitive using already-frozen v1.0.2-v1.0.5 parameters.
- **Tier 2** (new glue logic, but every number it needs is already frozen):
  `SweepReclaimEvidence`, `BOSExtremeEvidence` (R-30's pullback definition),
  `LTFConfirmationEvidence`, `TargetEvidence` (tp1/tp2/tp3 RR computation).
- **Tier 3** (blocked — new finding, not previously tracked anywhere):
  `sweep_reclaim_max_bars` (N_SWEEP), `entry_window_bars` (MAX_ENTRY_BARS),
  and `sessions.london_window_utc`/`ny_window_utc` are still literal
  placeholder strings (e.g. `"PROVISIONAL_1_TO_3"`) in
  `specs/st-c3_v1.0.5.yaml` — not numbers a builder can compare against, and
  not tracked under any existing R-number in `RESOLUTION_MATRIX.md`. No
  value is proposed for these here; see the design doc's Section 5 and 8 for
  the three explicit owner decisions requested (ratify Tier 1/2 approach;
  decide how Tier 3 gets resolved — owner-supplied or empirical-research
  path, same as R-04/R-06/R-27-R-30; decide whether a partial S1-S9
  existence-check run is an acceptable interim R-18 data point while Tier 3
  is open). No code has been written; no spec value proposed. R-18 remains
  the only field open on the R-01-R-30 tracker itself, but this design
  surfaces Tier 3 as new, not-yet-numbered gaps the owner has not seen
  before.

**Source of the two decisions below:** an owner-submitted decision document
dated 2026-07-25 used a different ID scheme than `RESOLUTION_MATRIX.md`
(its "R-01/R-07/R-11/R-14" did not correspond to this log's R-01/R-07/R-11/
R-14). Decisions were remapped here by field content, not by the submitted
ID label. Only R-02 and R-11 mapped cleanly onto an actual unresolved field
with a concrete resolvable number; the other three submitted items either
restated already-frozen spec content or introduced a new concept not
tracked as one of the 20 fields — see "Open Conflicts" below.

---

| ID | Field | Proposed (see RESOLUTION_MATRIX.md) | Owner Decision | Decided By | Date | Notes |
|---|---|---|---|---|---|---|
| R-01 | `governance_profile` | Depends on R-02 | **APPROVED: "Strict Deterministic Governance Profile"** | Owner | 2026-07-25 | Value: boolean/measurable/deterministic/reproducible rules only; state machine is sole source of truth, no discretionary overrides; no adaptive thresholds (all numeric thresholds explicit); fixed-lot model frozen with value deferred (matches R-21); no cross-instrument arbitration, per-instrument only (matches R-22). **Clarified scope (owner-confirmed, "Reading A"):** the line "bias, invalidation, and continuation confirmed ONLY by BOS/CHoCH" refers narrowly to `HTFBiasEvidence`'s own value (already true per frozen `htf_bias_stage.structure_source`/`bias_lock_policy`) — it does NOT remove sweep (S2), displacement (S4), FVG/OB confluence (S8), or LTF confirmation (S9) as required funnel gates. Those remain exactly as frozen in v1.0.1: hard, non-skippable stages per `priority_rules.no_state_can_be_skipped_or_revisited`. No funnel/state-machine change results from this decision. |
| R-02 | `instruments` | Not proposed | **APPROVED: EURUSD, GBPUSD, XAUUSD; REVISED 2026-07-26 to EURUSD, GBPUSD** | Owner | 2026-07-25 (original), 2026-07-26 (revision) | Multi-instrument scope. No crypto/indices/exotics. Replay requirement noted: min. 3yr per instrument, preferred 5-10yr (applies at Phase 5, not before). **2026-07-26 revision:** XAUUSD removed — owner rationale: its pip-value x SL-distance geometry exceeds the risk envelope under fixed-lot sizing (R-21=0.01) at the owner's stated $1000 account capital. This revision was submitted mislabeled as "R-22" — see that row. Folded into `specs/st-c3_v1.0.3.yaml`. |
| R-03 | `sessions.low_liquidity_filters` | `disabled_by_default` | **APPROVED: structured low-liquidity signature** | Owner | 2026-07-26 | Decided via the RCR-ST-C3-v1.0.2 directive (governance parameter-freeze revision), superseding the matrix's `disabled_by_default` fallback. Deterministic rule: `low_liquidity_signature: {wick_body_ratio_min: 2.0, spread_expansion_factor: 1.5, atr_compression_ratio: 0.40, excluded_time_windows: [{start: "00:00", end: "02:00"}, {start: "20:00", end: "22:00"}]}`. Folded into `specs/st-c3_v1.0.2.yaml`'s `sessions.low_liquidity_filters`. Not empirically validated against historical data — an owner-decided starting point, same category as R-05's ATR-tolerance decision. |
| R-04 | `wick_ratio_min` | `0.5-0.7` range | **APPROVED: 0.50** | Owner | 2026-07-26 | Decided from the empirical distribution in `reports/validation/st_c3/R04_R06_RESEARCH_REPORT.md`: keeps 28.5% of naturally-occurring pierce+reclaim candidates (median wick ratio 0.33), filters weak/noise sweeps without over-filtering; aligns with ST-C2's 0.6 reference point without inheriting it. |
| R-05 | `equal_highs_lows_tolerance` | Research required | **APPROVED: 0.10 x MF ATR(1)** | Owner | 2026-07-26 | Deterministic rule: `Two highs are equal if \|H1 - H2\| <= 0.10 * MF_ATR(1); two lows are equal if \|L1 - L2\| <= 0.10 * MF_ATR(1).` Prevents micro-tick noise from triggering false sweeps; numeric, frozen, non-adaptive. Reuses the same "MF ATR-1" reference point as R-07's displacement rule — consistent unit convention across both decisions. **Note:** this matrix classified R-05 as "research required" (i.e. needing an `tools/existence_check.py` pass against real candle data before picking a number) — owner decided directly instead, which is a legitimate choice, not a process violation; flagged only so a future review knows this wasn't empirically validated against historical data yet. |
| R-06 | `max_sweep_age_bars` | `20-60` bars | **APPROVED: 15 bars** | Owner | 2026-07-26 | Decided from the empirical distribution in `reports/validation/st_c3/R04_R06_RESEARCH_REPORT.md`: applies a meaningful, binding freshness constraint (between the 89.6%-at-10 and 99.9%-at-20 pass rates) without over-filtering; avoids the non-binding-rule problem the originally proposed 20-60 range had (anything >=30 filtered nothing on the observed data). |
| R-07 | `displacement_body_ratio_min` | `0.6-0.7` | **APPROVED: 0.50, combined with a new ATR-floor condition** | Owner | 2026-07-25 | Submitted as "R-07B" — mapped to this row, same field, not a duplicate. Deterministic rule: `body_size = \|open - close\|; total_range = wick-to-wick range of the MF bar. IF (body_size / total_range) >= 0.50 AND total_range >= 1.0 * MF_ATR(1) THEN displacement = true ELSE false.` Owner's value (0.50) is below this matrix's proposed 0.6-0.7 range — owner's decision stands. **Scope note:** the ATR-floor condition (`total_range >= 1.0 * MF ATR-1`) is *new content*, not previously tracked anywhere in `RESOLUTION_MATRIX.md` or the frozen spec (v1.0.1's `displacement_bos_stage` has no ATR-multiplier field at all) — recorded here as part of R-07's resolution since both conditions gate the same `displacement` boolean via AND, not as a separately invented addition. |
| R-08 | `buffer_points` | ATR-multiple, e.g. `0.1-0.2 * ATR` | **APPROVED (value): 0.20 x MF ATR(1); rule formulation flagged, not accepted as-stated** | Owner | 2026-07-26 | Submitted rule: `Let invalidation_level be the structural invalidation price. IF \|price - invalidation_level\| > (0.20 * MF_ATR(1)) THEN invalidated = true ELSE false.` **Correctness issue:** this formulation is non-directional — `\|price - invalidation_level\|` grows just as much when price moves *favorably* away from the level as when it breaches adversely, so as literally stated this would flag most winning trades as invalidated once price is far enough away in the winning direction. The frozen spec's anchors are directional (`short_anchor: above_m3_swing_that_formed_choch`, `long_anchor: below_m3_swing_that_formed_choch` — bearish invalidation = price closes *above* the anchor, bullish invalidation = price closes *below* it). The 0.20x ATR buffer *value* is recorded as decided; the guard's directional form needs correction before this can be implemented (e.g. `IF (direction == SHORT AND price >= invalidation_level - buffer) OR (direction == LONG AND price <= invalidation_level + buffer) THEN invalidated = true`, or similar — exact form still needs owner confirmation, not invented here). |
| R-09 | `tp2_external_liquidity.rr_min` | `5.0R` | **APPROVED: 2.0R** | Owner | 2026-07-25 | Rationale given: TP2 is trend-continuation/external liquidity, structurally farther than TP1; 2.0R maintains separation from TP1 without collapsing the target model; deterministic and fixed-lot-compatible. **Flagged, not blocking:** 2.0R is *below* TP1's frozen 3.0R floor. Since TP2 (`equal_highs_lows`/`major_liquidity_pool`) is structurally farther from entry than TP1 (`internal_liquidity_pocket`), its actual RR is mechanically >= TP1's RR given the same entry/stop — so this floor is automatically satisfied whenever TP1's is, making it non-binding as an independent gate rather than a meaningful additional constraint. Recorded as decided; owner may revisit if a binding TP2-specific floor was intended. |
| R-10 | `tp3_htf_objective.rr_min` | `8.0R` | **APPROVED: 3.5R** | Owner | 2026-07-25 | Rationale given: TP3 is extended/HTF liquidity requiring HTF alignment and clean structure; 3.5R exceeds TP1's 3.0R (preserves that ordering) and is conservative/deterministic. Correctly exceeds both TP1 (3.0R) and TP2 (2.0R, see R-09 note) — no ordering issue here. |
| R-11 | `risk.per_trade_risk_pct` | `0.5%` | **SUPERSEDED 2026-07-25 — field removed from v1.x, see Open Conflict 1 resolution** | Owner | 2026-07-25 | The 2026-07-25 "1% per trade" decision recorded here is retracted by the same day's Open Conflict 1 resolution: fixed lot is the authoritative v1.x sizing model, and `per_trade_risk_pct` is removed from the active specification entirely (not merely re-valued). Percentage-based risk sizing is DEFERRED to a possible v2.x cycle. |
| R-12 | `risk.max_positions` | `3` | **APPROVED: 2** | Owner | 2026-07-26 | Owner's value (2) is below this matrix's proposed 3 — owner's decision stands. Submitted as "portfolio.max_concurrent_positions" — same field. |
| R-13 | `risk.portfolio_heat_pct` | `3.0%` or `4.0%` | **APPROVED: 3.0%** | Owner | 2026-07-26 | Matches ST-C2 precedent, aligns with R-12 (max positions = 2) and R-25 (max per instrument = 1). Not the same field as the earlier-submitted "R-13 portfolio.max_positions_per_instrument" (recorded separately as R-25). |
| R-14 | `risk.daily_loss_pct` | `3.0%` | **APPROVED: 3.0% of account balance** (confirmed again 2026-07-26, consistent, no change) | Owner | 2026-07-25 | Deterministic rule: `IF realized_loss_today >= 3.0% of account balance THEN disable all new entries until the next session.` Applies to realized losses only (unrealized drawdown does not trigger it); no discretionary overrides. Compatible with the deferred fixed-lot model (R-21) — this breaker is a percentage-of-account-balance check, independent of position-sizing method. Matches this matrix's proposed value exactly (`docs/CHARTER.md`/`specs/st-c2_v1.2.0.yaml:327` convention). Resubmitted 2026-07-26 as "portfolio.daily_loss_percent" with the identical 3.0% value — restates, does not change, this decision. |
| R-15 | `risk.weekly_loss_pct` | `7.0%` | **APPROVED: 7.0%** | Owner | 2026-07-26 | Matches ST-C2's own value (no CHARTER equivalent existed to cross-check against). Not the same field as the earlier-submitted "R-15 portfolio.daily_max_trades" (recorded separately as R-26). |
| R-16 | `rcr_preregistration.primary_metric` | `expectancy_r` | **APPROVED: expectancy_r** | Owner | 2026-07-26 | Matches this repo's existing A3 promotion-gate convention. |
| R-17 | `rcr_preregistration.secondary_metrics` | `[profit_factor, sharpe_ratio, maximum_drawdown_r]` | **APPROVED: [profit_factor, sharpe_ratio, maximum_drawdown_r]** | Owner | 2026-07-26 | Matches `validation/performance_metrics.py`'s existing metric set. |
| R-18 | `rcr_preregistration.existence_check_floor` | Compute after R-02/R-16/R-20 | PENDING | — | — | R-02, R-16, R-20 now all resolved; still needs an actual `tools/existence_check.py` + `tools/power_planning.py` run against real candle data before a number can be computed — this is not an owner-pick field. |
| R-19 | `rcr_preregistration.population_feasibility_floor` | `300` trades | **APPROVED: 300 trades** | Owner | 2026-07-26 | Matches this project's stated A3 promotion-gate convention elsewhere. |
| R-20 | `rcr_preregistration.statistical_claim_floor` | PF≥1.40, expectancy≥0.20R, Sharpe≥1.20 | **APPROVED: PF >= 1.40, expectancy >= 0.20R, Sharpe >= 1.20** | Owner | 2026-07-26 | Matches this project's A3 promotion-gate language used elsewhere. This is the real tracked field — distinct from the earlier-rejected "R-20 session-close forced-exit" mismatch. |
| R-21 | `risk.fixed_lot_size` (NEW — not in original 20; added 2026-07-25 by Open Conflict 1 resolution) | Not proposed | **APPROVED: 0.01 (micro-lot)** | Owner | 2026-07-26 | Decided via chat directive. Rationale given: the only fixed-lot value the owner assessed as keeping risk within ST-C3's frozen caps (`portfolio_heat_pct`/`daily_loss_pct`/`weekly_loss_pct`) at the owner's stated $1000 account capital — an owner-asserted risk-appetite judgment, not independently re-derived here (no SL-distance/pip-value computation was run to verify "only" — recorded as the owner's decision regardless, same category as R-05's directly-decided ATR tolerance). Folded into `specs/st-c3_v1.0.3.yaml`. |
| R-22 | `instrument.selection_logic` (NEW — not previously tracked; added 2026-07-25) | Not proposed | **APPROVED: computed_rr-based tie-break, EURUSD fixed-priority fallback** | Owner | 2026-07-26 | A 2026-07-26 submission had first labeled an R-02 revision "R-22" (see R-02's row and `reports/governance/st_c3/RCR_ST-C3_v1.0.3_REPORT.md` for that correction). The actual R-22 decision followed separately, same day: `IF computed_rr(EURUSD) > computed_rr(GBPUSD) THEN select EURUSD ELIF computed_rr(GBPUSD) > computed_rr(EURUSD) THEN select GBPUSD ELSE select EURUSD (fixed-priority fallback)`. Owner rationale: `computed_rr` is already a frozen `trade_plan.schema.risk` field (no new metric introduced); deterministic, no randomness; EURUSD fallback for lower volatility/tighter spreads near the position cap, consistent with R-02's own XAUUSD-exclusion rationale. This is Stage B / portfolio-level arbitration only — does not affect the S0-S13 state machine, which operates per-instrument independently. Folded into `specs/st-c3_v1.0.4.yaml`'s `risk.instrument_tie_breaking_rule`. |
| R-23 | `fvg_ob_confluence_stage.freshness_definition` — **OB half only** (NEW — split out of the ambiguous term flagged in `SPECIFICATION_VALIDATION.md` #2; not previously a tracked ID) | Research required | **APPROVED: OB remains fresh for 3 MF (M15) swings after creation** | Owner | 2026-07-25 | Deterministic rule: `Let OB.creation_swing = the MF swing in which the OB is formed. IF (current_MF_swing_index - OB.creation_swing_index) <= 3 THEN ob_fresh = true ELSE ob_fresh = false.` MF swing definition is frozen/deterministic; OB freshness is independent of HTF bias, displacement, and sweep; no discretionary overrides. **Scope note:** this decision covers Order Block freshness only. The frozen `freshness_definition` field applies to *both* FVG and OB (`fvg_ob_confluence_stage.required_zone_types: [fresh_h4_or_m15_fvg, fresh_h4_or_m15_order_block]`) — FVG freshness is tracked separately as **R-24**, still pending, since a gap's age isn't necessarily measured the same way as an order block's. |
| R-24 | `fvg_ob_confluence_stage.freshness_definition` — **FVG half** (companion to R-23) | Not proposed | **APPROVED: FVG fresh for <= 1 MF swing after creation** | Owner | 2026-07-26 | Deterministic rule: `Let FVG.creation_swing = MF swing in which the FVG is formed. IF (current_MF_swing_index - FVG.creation_swing_index) <= 1 AND FVG is not expired THEN fvg_fresh = true ELSE false.` Shorter window than R-23's OB rule (1 swing vs. 3) — rationale given: FVGs are short-lived imbalances, OBs have longer structural relevance. **Unresolved dependency, not silently assumed:** the rule's "AND FVG is not expired (R-06)" clause cites R-06, but this log's R-06 is `max_sweep_age_bars` — a sweep-stage field with no relationship to FVGs. No separate "FVG expiration" concept (distinct from this freshness rule) has been tracked or decided anywhere in `RESOLUTION_MATRIX.md`. Until clarified, this rule is recorded with its freshness clause only; the expiration clause's actual condition is undefined. |
| R-25 | `portfolio.max_positions_per_instrument` (NEW — submitted as "R-13," mismatched this log's actual R-13; added 2026-07-26) | Not proposed | **APPROVED: 1** | Owner | 2026-07-26 | Combined with R-12 (max concurrent positions = 2), this means at most 2 total open positions across all instruments, at most 1 per instrument — the 2 concurrent slots must be on 2 different symbols. Internally consistent with R-12, no conflict. |
| R-26 | `risk.daily_max_trades` (NEW — submitted as "R-15," mismatched this log's actual R-15; added 2026-07-26) | Not proposed | **APPROVED: 4 trades/day** | Owner | 2026-07-26 | New concept — a cap on trades *initiated* per day, distinct from R-14's loss-percentage circuit breaker. No conflict with any existing decision. |
| R-27 | HTF swing/fractal lookback definition (NEW — found 2026-07-26 attempting real R-18 detection work; see `R18_DETECTION_GAP_REPORT.md`) | Not proposed | **APPROVED: k=2** | Owner | 2026-07-26 | Chosen from the k=1..5 tradeoff curve in `R27_R30_RESEARCH_REPORT.md` (1,379 swings over 5,000 GBPUSD H4 bars at k=2). Not inherited from ST-C2 (ADR-0004) — independently decided, though it happens to match `smc_engine.swings()`'s own default. Folded into `specs/st-c3_v1.0.5.yaml`'s `htf_bias_stage.swing_fractal_lookback_k`. |
| R-28 | BOS confirmation-bar rule (NEW — found 2026-07-26) | Not proposed | **APPROVED: N=2 bars** | Owner | 2026-07-26 | Chosen from the N=0..5 tradeoff curve in `R27_R30_RESEARCH_REPORT.md` (rejects ~25% of raw body-close breaks as whipsaws on the GBPUSD M15 sample). Folded into `specs/st-c3_v1.0.5.yaml`'s `displacement_bos_stage.bos_confirmation_bars`. |
| R-29 | FVG minimum gap-size / OB candle-selection rule (NEW — found 2026-07-26) | Not proposed | **APPROVED (FVG half): 0.15x MF_ATR(1)** | Owner | 2026-07-26 | Chosen from the 0.1-0.3x candidate range in `R27_R30_RESEARCH_REPORT.md`. OB half needs no number — already a structural rule via `smc_engine.order_blocks()`. Folded into `specs/st-c3_v1.0.5.yaml`'s `fvg_ob_confluence_stage.fvg_min_gap_atr_multiplier`. |
| R-30 | Pullback definition for `BOS_EXTREME_LOCK` (NEW — found 2026-07-26) | Not proposed | **APPROVED: 0.30x ATR(1) depth** | Owner | 2026-07-26 | Chosen from the depth-filtered 0.1-1.0x ATR(1) tradeoff curve in `R27_R30_RESEARCH_REPORT.md` (reaches within 40 bars for 86.3% of BOS candidates, median 2 bars). Folded into `specs/st-c3_v1.0.5.yaml`'s `displacement_bos_stage.pullback_depth_atr_multiplier`. |
| R-31 | `liquidity_sweep_stage.sweep_reclaim_max_bars` (N_SWEEP) (NEW — found 2026-07-26 during `R18_EVIDENCE_BUILDER_DESIGN.md` Tier 3 gap analysis; spec carried the literal placeholder string `"PROVISIONAL_1_TO_3"`, not a number, and was untracked by any R-item) | Not proposed | **APPROVED: 2 bars (for the current A2/S1-G2 phase)** | Owner | 2026-07-26 | Owner gave phase-conditional guidance rather than a single fixed number: 2 bars for the current research/validation phase (A2/S1-G2), 1 bar if/when a future A3+/production-prep phase tightens the funnel, 3 bars for exploratory robustness testing. Since A2/S1-G2 is the active phase per `NEXT_ACTION.md`, **2 bars is the value folded into `specs/st-c3_v1.0.6.yaml`**. The 1-bar and 3-bar alternatives are recorded here, not implemented, in case the owner revisits this for a later phase — re-opening this field for a phase change is a new decision, not an automatic switch. |
| R-32 | `entry_window_stage.entry_window_bars` (MAX_ENTRY_BARS) (NEW — found 2026-07-26, same Tier 3 gap analysis; spec carried literal `"PROVISIONAL_3_TO_5_M3_BARS"`) | Not proposed | **APPROVED: 4 M3 bars** | Owner | 2026-07-26 | Owner's stated rationale: 4 is the mid-range pick for A2/S1-G2, chosen to avoid biasing the signal-rate study toward either the tight (3-bar) or loose (5-bar) end of the spec's own provisional range. Folded into `specs/st-c3_v1.0.6.yaml`'s `entry_window_stage.entry_window_bars`. |
| R-33 | `sessions.london_window_utc` / `sessions.ny_window_utc` (NEW — found 2026-07-26, same Tier 3 gap analysis; spec carried literal `"PROVISIONAL_07_00_TO_10_00"` / `"PROVISIONAL_13_00_TO_16_00"`) | Not proposed | **APPROVED: ratify existing provisional values as final — London 07:00-10:00 UTC, NY 13:00-16:00 UTC** | Owner | 2026-07-26 | Owner chose to keep the spec's own long-standing provisional session times rather than change them; this decision converts them from an unratified placeholder string to a decided, frozen value — the clock times themselves are unchanged. Folded into `specs/st-c3_v1.0.6.yaml`. |

**2026-07-26 update (same day, later still): R-31/R-32/R-33 decided —
Tier 3 of `R18_EVIDENCE_BUILDER_DESIGN.md` resolved.** These three fields
were surfaced by that design document's gap analysis, not previously
tracked anywhere. All three are now folded into `specs/st-c3_v1.0.6.yaml`
via `reports/governance/st_c3/RCR_ST-C3_v1.0.6_REPORT.md`. **R-18 remains
the only field on the entire R-01–R-33 tracker without a resolved value —
and, as before, it needs no further spec decision, only the
`build_evidence_bundle()` implementation and a real data run.**

---

## Open Conflicts (raised 2026-07-25, unresolved — owner input required)

These came from the same submission as the R-02/R-11 decisions above but
do not resolve cleanly onto any of the 20 `RESOLUTION_MATRIX.md` fields, or
conflict with content already frozen in `specs/st-c3_v1.0.1.yaml`. Neither
is accepted or rejected here — both need explicit owner clarification.

### Open Conflict 1 — "Fixed lot" position sizing vs. `risk_per_trade_pct` — **RESOLVED 2026-07-25**

**Owner Decision:** ST-C3 v1.x uses fixed lot as the authoritative sizing
model. The `risk_per_trade_pct: 1%` field is removed from the v1.x
specification entirely (not re-valued, removed). Rationale given: fixed lot
was already approved in Sprint 1; percentage-risk sizing requires dynamic
lot calculation, which contradicts a fixed-lot model; ST-C3 v1.x is
deterministic/rule-based and fixed lot is simpler and stable, consistent
with the frozen state machine. Dynamic (percentage) risk sizing may be
considered for a future v2.x cycle, not the current validation lifecycle.

**Decided by:** Owner, 2026-07-25.

**Consequences / what this opens up (not yet resolved by this decision):**

1. **A new, currently-unproposed field is needed: the actual fixed lot
   size.** "Fixed lot" states the *model*, not a *number* — 0.01 lots and
   10 lots are both "fixed lot" and produce wildly different risk. This is
   a new decision, not yet in `RESOLUTION_MATRIX.md` (tentatively **R-21,
   `risk.fixed_lot_size`** — added to the matrix's scope, status
   `PENDING`, owner-decision-required, no default proposed since fixed-lot
   sizing has no natural reference point the way percentage-risk had
   `docs/CHARTER.md`'s 0.5%/1.0% convention).
2. **Per-instrument risk variance is now a known, accepted consequence, not
   an open conflict.** A single fixed lot size across EURUSD/GBPUSD/XAUUSD
   will produce different risk percentages per instrument (per this
   conflict's own original analysis) — the owner's decision accepts that
   consequence rather than resolving it away. Worth confirming explicitly
   at R-21's resolution whether the fixed lot size should instead be
   **per-instrument** (three values, one per R-02 symbol) rather than one
   value for all three, since the three symbols' pip values differ by
   orders of magnitude.
3. **`trade_plan.schema.risk` in `specs/st-c3_v1.0.1.yaml`** currently
   models `risk_per_trade_pct`/`computed_rr` around the percentage-risk
   framework. `computed_rr` itself is price-ratio-based (target/entry/stop),
   independent of position size, so the `S12_RISK_SLTP` RR guard is
   unaffected structurally. But `risk_per_trade_pct`'s *schema field* would
   need to be replaced with a lot-size field in any future versioned spec
   that ratifies this decision — a spec-file change requiring the same
   RCR/versioning treatment as R-1/R-2/R-3, not implied automatically by
   this log entry.
4. **R-12/R-13/R-14/R-15** (`max_positions`, `portfolio_heat_pct`,
   `daily_loss_pct`, `weekly_loss_pct`) are all still framed as percentages
   in `RESOLUTION_MATRIX.md`'s proposals (matching `docs/CHARTER.md`/ST-C2
   convention). Percentage-based portfolio caps are not inherently
   incompatible with fixed-lot per-trade sizing (heat/drawdown caps can
   still be measured in account-percentage terms even if entry sizing
   itself is lot-based) — but this should be explicitly confirmed when
   those rows are decided, not assumed compatible by default.

### Open Conflict 2 — Blanket "RR ≥ 1.5R" vs. frozen TP1 `rr_min: 3.0` — **RESOLVED 2026-07-25**

**Owner Decision:** TP1 `rr_min` remains `3.0R`. The 1.5R reference is
removed — it originated from generic SMC reference material, not from the
frozen ST-C3 spec, and was never intended to override or coexist with the
frozen value. No coexistence model; the frozen `3.0` is authoritative.

**Decided by:** Owner, 2026-07-25.

**Consequence:** `ST-C3_SLTP_PATCH_RECOMMENDATION.md` is closed as REJECTED
(see that file's updated disposition). R-09/R-10 (TP2/TP3 `rr_min`) remain
`PENDING` below — this decision resolves the *conflict* with TP1, it does
not supply new numbers for TP2/TP3.

---

## Scope Decisions (not RESOLUTION_MATRIX fields — recorded here for the audit trail)

### Break-even and trailing-stop management — **OUT OF SCOPE for ST-C3 v1.x, 2026-07-25**

**Owner Decision:** break-even and trailing-stop rules are declared out of
scope for ST-C3 v1.x. They will not be added to the frozen specification in
the current validation lifecycle. May be considered for a future ST-C3 v2.x
research cycle, which would restart its own Stage A intake (per the same
"new candidate version" precedent used for the v1.0.0 -> v1.0.1 revision),
not an amendment to v1.x.

**Decided by:** Owner, 2026-07-25.

**Consequence:** `ST-C3_SLTP_PATCH_RECOMMENDATION.md`'s break-even/trailing
sections, and the three undefined terms they introduced ("structure
confirms continuation," "liquidity ahead is clean," "no major liquidity
obstruction ahead"), are moot — removed along with the rest of that
proposal. No new resolution-matrix entries needed for them.

### TP2/TP3 redefinition — **REJECTED, revert to frozen definitions, 2026-07-25**

**Owner Decision:** TP2/TP3 revert to the frozen v1.0.1 definitions
(`tp2_external_liquidity: [equal_highs_lows, major_liquidity_pool]`,
`tp3_htf_objective: [h4_swing, deeper_liquidity_target]`). No change to
liquidity hierarchy or target classification; no new target types.

**Decided by:** Owner, 2026-07-25.

**Consequence:** R-09 and R-10 (TP2/TP3 `rr_min`) remain the *only* open
items for the targets_stage — the underlying target definitions themselves
are confirmed unchanged, not reopened.

### Dual-timeframe bias-confirmation rule — **OUT OF SCOPE for ST-C3 v1.x, 2026-07-26**

A submission labeled "R-03" proposed: `bias_confirmed = true` only when
`HTF_bias == MF_bias` AND a valid displacement FVG has formed in that
direction on MF (`IF (HTF_bias = MF_bias) AND (MF_displacement_fvg_valid =
true) THEN bias_confirmed = true ELSE false`).

**Why this needed a scope check before recording:** this log's actual R-03
is `sessions.low_liquidity_filters` — unrelated. More importantly, this
proposal introduces a new `MF_bias` evidence concept (the frozen
`S1_HTF_BIAS` gate checks only `HTFBiasEvidence`, H4-timeframe, with no
mid-frame bias evidence anywhere in `specs/st-c3_v1.0.1.yaml`) and folds
displacement/FVG validity into bias confirmation itself — currently
independent, sequential gates (S4, S8) that don't feed into S1 at all. This
is architecture, not a field value — the same category as the rejected
SL/TP proposal.

**Owner Decision:** out of scope for ST-C3 v1.x. Deferred to a possible
future v2.x research cycle alongside break-even/trailing-stop and the
session-close forced-exit rule.

**Decided by:** Owner, 2026-07-26.

**Consequence:** no new evidence object, state, or gate added.
`sessions.low_liquidity_filters` (the actual R-03) remains untouched,
still `PENDING`.

### Session-close forced-exit rule — **OUT OF SCOPE for ST-C3 v1.x, confirmed 2026-07-26**

A submission labeled "R-20" proposed: force-close any open position at
session close if price is within 2.5 pips of the invalidation level
(`d = |price - invalidation_level|; IF d <= 2.5 pips THEN force_close = true`).

**Why this needed a scope check before recording:** this is new post-entry
trade-management logic. The frozen `S14_EXPIRY_TERMINATION` state monitors
exactly 4 termination reasons (`BIAS_FLIP`, `ENTRY_WINDOW`, `SL_BREAK`,
`SUPERSEDED`) — "near invalidation at session close" is not one of them,
and would need a new evidence object/field and a new termination code, the
same architectural category as the break-even/trailing-stop rules already
ruled out of scope above.

**Owner Decision:** the 2026-07-25 scope decision stands — no new
post-entry management logic in ST-C3 v1.x. This rule is **not recorded as
approved**; it is deferred alongside break-even/trailing-stop to a possible
future ST-C3 v2.x research cycle.

**Decided by:** Owner, 2026-07-26.

**Consequence:** no new field or evidence object added for this. Also note
the submission's `d = |price - invalidation_level|` reuses the same
non-directional formulation flagged in R-08's notes — if this rule is
revisited for a v2.x cycle, that direction issue would need the same fix.

---

## How to use this log

1. Review `RESOLUTION_MATRIX.md` and `DECISION_PACKAGES.md`.
2. For each row, either accept the proposed value, supply a different one,
   or mark it "deferred" with a reason.
3. Once a row's `Owner Decision` is filled in (not `PENDING`), it becomes
   eligible for inclusion in a future `specs/st-c3_v1.0.2.yaml` governance
   revision — via the same RCR process used for the R-1/R-2/R-3 rejection-code
   fixes, not a silent edit.
4. `SPECIFICATION_CLOSURE_REPORT.md` will report zero unresolved items only
   once every row here is filled in and ratified through that RCR process.
