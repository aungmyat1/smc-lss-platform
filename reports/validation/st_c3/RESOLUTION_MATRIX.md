# ST-C3 Specification Resolution Matrix — Phase 2.5

**Purpose:** classify every unresolved field from `SPECIFICATION_VALIDATION.md`
by who owns the decision, propose a starting point, and rank priority. No
value here is final — every "Recommended default/range" is a **proposal**
requiring explicit owner sign-off in `OWNER_DECISION_LOG.md` before it can
enter a frozen spec.

**Correction from `SPECIFICATION_VALIDATION.md`:** that report's own field
table lists 20 rows, not 19 as its prose summary claimed (an off-by-one
error in that report — corrected here, not silently). All 20 are enumerated
below.

**Reference values cited below from `specs/st-c2_v1.2.0.yaml`** are
comparison points only, per ADR-0004's ruling that ST-C3 is a new lineage
and must independently decide its own values, not inherit ST-C2's.

---

## Classification Legend

- **Research required** — needs an existence-check/backtest-style
  investigation before a value can be justified (not just asked of the owner).
- **Owner decision required** — a risk-appetite or scope choice only the
  owner can make; no amount of research resolves it.
- **Derived mathematically** — computable from other already-decided fields.
- **Already defined elsewhere** — a platform-wide convention exists
  (`docs/CHARTER.md`) that could be adopted by owner ratification, not derived.

## Matrix

| ID | Field | Missing Information | Decision Owner | Recommended Default/Range (PROPOSED) | Impact | Priority |
|---|---|---|---|---|---|---|
| R-01 | `governance_profile` | Symbol/session scope not chosen | Owner decision required | **DECIDED 2026-07-25 — see `OWNER_DECISION_LOG.md`** ("Strict Deterministic Governance Profile"; clarified as not altering the frozen funnel's required gates) | Blocks everything; nothing can run without a scope | Critical |
| R-02 | `instruments` | No symbol enabled | Owner decision required | **DECIDED 2026-07-25 — EURUSD, GBPUSD, XAUUSD; REVISED 2026-07-26 — EURUSD, GBPUSD (XAUUSD removed, fixed-lot risk envelope at $1000 capital); see `OWNER_DECISION_LOG.md`** | Blocks Phase 3-9 entirely; determines which historical data even matters | Resolved |
| R-03 | `sessions.low_liquidity_filters` | No filter rule despite `optional_low_liquidity_filters: true` | Owner decision required | **DECIDED 2026-07-26 — structured low-liquidity signature (wick_body_ratio_min=2.0, spread_expansion_factor=1.5, atr_compression_ratio=0.40, excluded_time_windows); see `OWNER_DECISION_LOG.md` and `specs/st-c3_v1.0.2.yaml`** | Low — only affects edge-case session windows | Resolved |
| R-04 | `wick_ratio_min` | No minimum wick-penetration ratio | Research required | **DECIDED 2026-07-26 — 0.50, from empirical GBPUSD M15 distribution; see `R04_R06_RESEARCH_REPORT.md` and `OWNER_DECISION_LOG.md`** | Medium — affects sweep detection sensitivity | Resolved |
| R-05 | `equal_highs_lows_tolerance` | No tolerance band for equal-highs/lows pools | Research required | **DECIDED 2026-07-26 — 0.10 x MF ATR(1), same unit convention as R-07; see `OWNER_DECISION_LOG.md`** (owner decided directly rather than via an existence-check pass — not empirically validated against historical data yet) | Medium | Resolved |
| R-06 | `max_sweep_age_bars` | No upper bound on swept-level age | Research required | **DECIDED 2026-07-26 — 15 bars, from empirical GBPUSD M15 distribution (proposed 20-60 range was non-binding above ~30); see `R04_R06_RESEARCH_REPORT.md` and `OWNER_DECISION_LOG.md`** | Medium | Resolved |
| R-07 | `displacement_body_ratio_min` | "Impulsive candles" has no numeric threshold | Research required | **DECIDED 2026-07-25 — 0.50 body-ratio AND total_range >= 1.0 x MF ATR(1); see `OWNER_DECISION_LOG.md`** (owner value below this matrix's proposed 0.6-0.7 range, combined with a new ATR-floor condition not previously tracked) | High — this gates the entire displacement/BOS stage (§3.2), the funnel's second major filter | Resolved — was Critical, last remaining Critical item |
| R-08 | `buffer_points` | No numeric buffer on the structural stop | Research required | **DECIDED (value) 2026-07-26 — 0.20 x MF ATR(1); guard formulation flagged as non-directional, needs correction — see `OWNER_DECISION_LOG.md`** | Medium — affects every SL price computed | Resolved (value), open (guard direction) |
| R-09 | `tp2_external_liquidity.rr_min` | No RR floor for TP2 | Owner decision required | PROPOSED: `5.0R` (between TP1's fixed `3.0R` and a plausible TP3, preserving strict ordering TP1 < TP2 < TP3) | Medium | Medium |
| R-10 | `tp3_htf_objective.rr_min` | No RR floor for TP3 | Owner decision required | PROPOSED: `8.0R` (same ordering logic as R-09) | Medium | Medium |
| R-11 | `risk.per_trade_risk_pct` | No position-sizing basis | Owner decision required | Already defined elsewhere: `docs/CHARTER.md` platform convention is `0.5%` demo / `1.0%` live — PROPOSED: ratify `0.5%` for ST-C3 research/demo phase, matching `specs/st-c2_v1.2.0.yaml:323` | High — required before any position sizing exists | Critical (blocks Package A) |
| R-12 | `risk.max_positions` | No concurrency limit | Owner decision required | **DECIDED 2026-07-26 — 2 (below this matrix's proposed 3); see `OWNER_DECISION_LOG.md`** | Medium | Resolved |
| R-13 | `risk.portfolio_heat_pct` | No aggregate open-risk cap | Owner decision required | **DECIDED 2026-07-26 — 3.0%; see `OWNER_DECISION_LOG.md`** | Medium | Resolved |
| R-14 | `risk.daily_loss_pct` | No daily circuit-breaker | Owner decision required | **DECIDED 2026-07-25 — 3.0% of account balance, realized losses only — see `OWNER_DECISION_LOG.md`** | High — safety-critical | Critical (blocks Package A) |
| R-15 | `risk.weekly_loss_pct` | No weekly circuit-breaker | Owner decision required | **DECIDED 2026-07-26 — 7.0%; see `OWNER_DECISION_LOG.md`** | Medium | Resolved |
| R-16 | `rcr_preregistration.primary_metric` | No pre-registered A3 success metric | Owner decision required | **DECIDED 2026-07-26 — expectancy_r; see `OWNER_DECISION_LOG.md`** | Medium — needed before A3, not before A2 | Resolved |
| R-17 | `rcr_preregistration.secondary_metrics` | No secondary metrics list | Owner decision required | **DECIDED 2026-07-26 — [profit_factor, sharpe_ratio, maximum_drawdown_r]; see `OWNER_DECISION_LOG.md`** | Low | Resolved |
| R-18 | `rcr_preregistration.existence_check_floor` | No minimum signal rate | Research required | Unblocked (R-02/R-16/R-20 all decided) but still needs an actual `tools/existence_check.py` + `tools/power_planning.py` run — not an owner-pick field | Low — a Lever-A/B concern, not a blocker for Phases 3-4 | Low, research-required |
| R-19 | `rcr_preregistration.population_feasibility_floor` | No minimum trade-population target | Owner decision required | **DECIDED 2026-07-26 — 300 trades; see `OWNER_DECISION_LOG.md`** | Low | Resolved |
| R-20 | `rcr_preregistration.statistical_claim_floor` | No pre-registered PF/expectancy/Sharpe bar | Owner decision required | **DECIDED 2026-07-26 — PF >= 1.40, expectancy >= 0.20R, Sharpe >= 1.20; see `OWNER_DECISION_LOG.md`** | Low — needed before A3, not before A2 | Resolved |
| R-21 | `risk.fixed_lot_size` **(NEW — added 2026-07-25)** | R-11 (`per_trade_risk_pct`) was decided then superseded same-day: owner chose fixed lot as the authoritative v1.x sizing model, removing the percentage-risk field. "Fixed lot" states a model, not a number — the actual lot size is undecided | Owner decision required | **DECIDED 2026-07-26 — 0.01 (micro-lot), single value for all enabled instruments; see `OWNER_DECISION_LOG.md`** | High — blocks any position-sizing computation, but NOT Phases 3-8 (R-multiple statistics/replay/golden-cases don't depend on lot size) | Resolved |
| R-22 | `instrument.selection_logic` **(NEW — added 2026-07-25)** | Cross-instrument prioritization ("which pair under which conditions") not addressed by R-02's instrument-scope decision | Owner decision required | **DECIDED 2026-07-26 — computed_rr-based tie-break (higher wins), EURUSD fixed-priority fallback on exact tie; see `OWNER_DECISION_LOG.md`** | Low for Stage A (state machine/golden cases run per-instrument independently); relevant later for R-12/R-13 tie-breaking at Stage B | Resolved |
| R-23 | `fvg_ob_confluence_stage.freshness_definition` — **OB half** **(NEW — split from the ambiguous "fresh" term, `SPECIFICATION_VALIDATION.md` #2)** | No max-age rule for Order Blocks | Research required | **DECIDED 2026-07-25 — OB fresh for <= 3 MF (M15) swings after creation — see `OWNER_DECISION_LOG.md`** | Medium — gates S8 (FVG/OB confluence) for the OB path | Resolved |
| R-24 | `fvg_ob_confluence_stage.freshness_definition` — **FVG half (companion to R-23)** | No max-age rule for FVGs specifically | Research required | **DECIDED 2026-07-26 — FVG fresh for <= 1 MF swing after creation; see `OWNER_DECISION_LOG.md`** — shorter window than R-23's OB rule (1 vs. 3 swings), rationale: FVGs are shorter-lived than OBs | Medium — gates S8 (FVG/OB confluence) for the FVG path | Resolved, with one open dependency (see below) |
| R-25 | `portfolio.max_positions_per_instrument` **(NEW — added 2026-07-26)** | Not previously tracked | Owner decision required | **DECIDED 2026-07-26 — 1; see `OWNER_DECISION_LOG.md`** (consistent with R-12's max-concurrent=2: the 2 slots must be on different symbols) | Low | Resolved |
| R-26 | `risk.daily_max_trades` **(NEW — added 2026-07-26)** | Not previously tracked | Owner decision required | **DECIDED 2026-07-26 — 4 trades/day; see `OWNER_DECISION_LOG.md`** | Low | Resolved |
| R-27 | HTF swing/fractal lookback definition (`htf_bias_stage.structure_source`) **(NEW — added 2026-07-26, found attempting real R-18 detection work; see `R18_DETECTION_GAP_REPORT.md`)** | No fractal lookback (`k`) for identifying HH/HL/LH/LL swing points on H4; unlike `specs/st-c2_v1.2.0.yaml`'s explicit `htf_swing_fractal_k_h4`, ST-C3 has no equivalent | Owner decision required (or research required, owner's choice — same category as R-04/R-06) | **DECIDED 2026-07-26 — k=2, chosen from the k=1..5 tradeoff curve in `R27_R30_RESEARCH_REPORT.md`; see `OWNER_DECISION_LOG.md`** | Critical — blocks S1_HTF_BIAS real detection, and everything downstream of it | Resolved |
| R-31 | `liquidity_sweep_stage.sweep_reclaim_max_bars` (N_SWEEP) **(NEW — added 2026-07-26, found during `R18_EVIDENCE_BUILDER_DESIGN.md` Tier 3 gap analysis: a placeholder string, not a number, and not previously tracked under any R-item)** | Spec carried literal `"PROVISIONAL_1_TO_3"` — no number a builder could compare against | Owner decision required | **DECIDED 2026-07-26 — 2 bars, phase-conditional owner guidance (2 for A2/S1-G2 research/validation, 1 for future A3+/production tightening, 3 for exploratory robustness testing); current phase is A2/S1-G2, so 2 applies now; see `OWNER_DECISION_LOG.md`** | Medium — gates `SweepReclaimEvidence.reclaimed`, blocks S3 | Resolved |
| R-32 | `entry_window_stage.entry_window_bars` (MAX_ENTRY_BARS) **(NEW — added 2026-07-26, same Tier 3 gap analysis)** | Spec carried literal `"PROVISIONAL_3_TO_5_M3_BARS"` — no number a builder could compare against | Owner decision required | **DECIDED 2026-07-26 — 4 M3 bars, owner's stated middle-of-range pick for A2/S1-G2 to avoid biasing the signal-rate study toward either extreme; see `OWNER_DECISION_LOG.md`** | Medium — gates `EntryWindowEvidence.inside_window`, blocks S11 | Resolved |
| R-33 | `sessions.london_window_utc` / `sessions.ny_window_utc` **(NEW — added 2026-07-26, same Tier 3 gap analysis)** | Spec carried literal `"PROVISIONAL_07_00_TO_10_00"` / `"PROVISIONAL_13_00_TO_16_00"` — placeholder strings, not ratified session bounds | Owner decision required | **DECIDED 2026-07-26 — owner ratified the values already sitting in the spec text as final: London 07:00-10:00 UTC, NY 13:00-16:00 UTC; see `OWNER_DECISION_LOG.md`** | Medium — gates `SessionWindowEvidence`, blocks S10 | Resolved |
| R-28 | BOS confirmation-bar rule (`displacement_bos_stage.bos_confirmation_rule`) **(NEW — added 2026-07-26)** | `body_close_required` states a body close breaks structure but gives no confirmation-bar count | Owner decision required (or research required) | **DECIDED 2026-07-26 — N=2 bars, chosen from the N=0..5 tradeoff curve in `R27_R30_RESEARCH_REPORT.md`; see `OWNER_DECISION_LOG.md`** | Critical — blocks S4_DISPLACEMENT_BOS real detection | Resolved |
| R-29 | FVG minimum gap-size definition + OB candle-selection rule (`fvg_ob_confluence_stage`) **(NEW — added 2026-07-26)** | No numeric floor for what counts as a fair-value gap; no rule for which candle qualifies as an order block | Owner decision required (or research required) | **DECIDED 2026-07-26 (FVG half) — 0.15x MF_ATR(1), chosen from the 0.1-0.3x candidate range in `R27_R30_RESEARCH_REPORT.md`; OB half needs no new number (already answered by `smc_engine.order_blocks()`'s existing structural rule); see `OWNER_DECISION_LOG.md`** | High — blocks S8_FVG_OB_CONFLUENCE real detection | Resolved |
| R-30 | Pullback definition for `BOS_EXTREME_LOCK` (`displacement_bos_stage.bos_extreme_lock_policy`) **(NEW — added 2026-07-26)** | "Lock after first pullback" has no numeric or structural definition of what counts as a pullback | Owner decision required (or research required) | **DECIDED 2026-07-26 — 0.30x ATR(1) depth, chosen from the depth-filtered 0.1-1.0x ATR(1) tradeoff curve in `R27_R30_RESEARCH_REPORT.md`; see `OWNER_DECISION_LOG.md`** | High — blocks S5_BOS_EXTREME_LOCK real detection | Resolved |

## Priority Summary

**2026-07-26 addition:** R-27 through R-30 are a *new gap category*, found
while attempting to begin real R-18 price-level detection work — see
`R18_DETECTION_GAP_REPORT.md`. They are structural-detection-*algorithm*
parameters (swing fractal lookback, BOS confirmation bars, FVG/OB
identification rules, pullback definition), not filter thresholds like the
original 26 fields. They are additional to, not part of, the "26 tracked
fields" count used elsewhere in this document and in `OWNER_DECISION_LOG.md`.
R-27/R-28 are Critical (they block `S1_HTF_BIAS`/`S4_DISPLACEMENT_BOS`
respectively, i.e. everything); R-29/R-30 are High. **Update, same day:**
all four now `DECIDED` — R-27 k=2, R-28 N=2, R-29 (FVG half) 0.15x
MF_ATR(1), R-30 0.30x ATR(1) depth, folded into `specs/st-c3_v1.0.5.yaml`.
R-18 is now the only field left unresolved of every R-item tracked in this
document, and it no longer needs a spec decision — only real
detection-module code built against this now-fully-frozen parameter set.

- **Critical (original 26):** none remaining.
- **High/Medium:** none remaining — R-04 and R-06 decided 2026-07-26 via
  empirical research; R-03 decided 2026-07-26 via the RCR-ST-C3-v1.0.2
  directive.
- **Remaining pending (1 of 26):** R-18 (`existence_check_floor` — the
  ST-C3 reference kernel now exists (`validation/st_c3/kernel.py`,
  A2/S1-G2) and is existence-check-tool wire-compatible, but a real R-18
  number still needs price-level detection modules run against real
  candle data, which the v1.0.2/v1.0.3 parameter freezes do not themselves
  build).
- **Superseded, no longer tracked as its own decision:** R-11 (`per_trade_risk_pct`) — removed from v1.x scope 2026-07-25; see `OWNER_DECISION_LOG.md`.
- **Decided and integrated into `specs/st-c3_v1.0.4.yaml`** (see
  `OWNER_DECISION_LOG.md` for authoritative values — this matrix keeps the
  original proposals for audit-trail comparison only): R-01, R-02 (revised
  2026-07-26), R-03, R-04, R-05, R-06, R-07, R-08 (value only, guard
  direction flagged), R-09, R-10, R-12, R-13, R-14, R-15, R-16, R-17, R-19,
  R-20, R-21, R-22, R-23, R-24, R-25, R-26 (24 total).
- **Deferred (explicit owner decision, not blocking Phases 3-8):**
  R-21 (`risk.fixed_lot_size`), R-22 (`instrument.selection_logic`). Both
  remain blocking for Stage B execution work specifically, which was
  already blocked regardless.
- **Ruled out of v1.x scope (deferred to a possible v2.x cycle, not
  applied):** break-even/trailing-stop management, TP2/TP3 redefinition
  (rejected, frozen definitions retained), session-close forced-exit
  (mismatched "R-20" submission), dual-timeframe bias confirmation
  (mismatched "R-03" submission). See `OWNER_DECISION_LOG.md`'s "Scope
  Decisions" section for full detail on each.

Note that R-01/R-02 (instrument and session scope) are the true root of the
dependency graph — see `DEPENDENCY_GRAPH.md` — because `wick_ratio_min`,
`max_sweep_age_bars`, and the existence-check floor (R-18) cannot even be
researched without first knowing which symbol's candle data to scan.
