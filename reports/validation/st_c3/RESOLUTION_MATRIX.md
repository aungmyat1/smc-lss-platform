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
| R-02 | `instruments` | No symbol enabled | Owner decision required | Not proposed — this is the single highest-leverage decision in the whole matrix | Blocks Phase 3-9 entirely; determines which historical data even matters | Critical |
| R-03 | `sessions.low_liquidity_filters` | No filter rule despite `optional_low_liquidity_filters: true` | Owner decision required | PROPOSED: `disabled_by_default` (simplest deterministic starting point; can be added as a v1.0.3 addendum once R-02/R-04 data exists to justify a filter) | Low — only affects edge-case session windows | Low |
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
| R-21 | `risk.fixed_lot_size` **(NEW — added 2026-07-25)** | R-11 (`per_trade_risk_pct`) was decided then superseded same-day: owner chose fixed lot as the authoritative v1.x sizing model, removing the percentage-risk field. "Fixed lot" states a model, not a number — the actual lot size is undecided | Owner decision required | Not proposed — no natural cross-instrument reference point the way percentage-risk had a CHARTER/ST-C2 convention to cite. Owner should also decide: one value for all three R-02 instruments, or per-instrument values (EURUSD/GBPUSD/XAUUSD pip values differ by orders of magnitude) | High — blocks any position-sizing computation, but NOT Phases 3-8 (R-multiple statistics/replay/golden-cases don't depend on lot size) | **DEFERRED 2026-07-25** — see `OWNER_DECISION_LOG.md` |
| R-22 | `instrument.selection_logic` **(NEW — added 2026-07-25)** | Cross-instrument prioritization ("which pair under which conditions") not addressed by R-02's instrument-scope decision | Owner decision required | Not proposed | Low for Stage A (state machine/golden cases run per-instrument independently); relevant later for R-12/R-13 tie-breaking at Stage B | **DEFERRED 2026-07-25** — see `OWNER_DECISION_LOG.md` |
| R-23 | `fvg_ob_confluence_stage.freshness_definition` — **OB half** **(NEW — split from the ambiguous "fresh" term, `SPECIFICATION_VALIDATION.md` #2)** | No max-age rule for Order Blocks | Research required | **DECIDED 2026-07-25 — OB fresh for <= 3 MF (M15) swings after creation — see `OWNER_DECISION_LOG.md`** | Medium — gates S8 (FVG/OB confluence) for the OB path | Resolved |
| R-24 | `fvg_ob_confluence_stage.freshness_definition` — **FVG half (companion to R-23)** | No max-age rule for FVGs specifically | Research required | **DECIDED 2026-07-26 — FVG fresh for <= 1 MF swing after creation; see `OWNER_DECISION_LOG.md`** — shorter window than R-23's OB rule (1 vs. 3 swings), rationale: FVGs are shorter-lived than OBs | Medium — gates S8 (FVG/OB confluence) for the FVG path | Resolved, with one open dependency (see below) |
| R-25 | `portfolio.max_positions_per_instrument` **(NEW — added 2026-07-26)** | Not previously tracked | Owner decision required | **DECIDED 2026-07-26 — 1; see `OWNER_DECISION_LOG.md`** (consistent with R-12's max-concurrent=2: the 2 slots must be on different symbols) | Low | Resolved |
| R-26 | `risk.daily_max_trades` **(NEW — added 2026-07-26)** | Not previously tracked | Owner decision required | **DECIDED 2026-07-26 — 4 trades/day; see `OWNER_DECISION_LOG.md`** | Low | Resolved |

## Priority Summary

- **Critical:** none remaining.
- **High/Medium:** none remaining — R-04 and R-06 decided 2026-07-26 via
  empirical research.
- **Remaining pending (2 of 26):** R-03 (`sessions.low_liquidity_filters`
  — needs an explicit "low-liquidity signature" definition before any scan
  is meaningful, not attempted yet), R-18 (`existence_check_floor` — needs
  a working signal function across the entire funnel, which would mean
  assembling the ST-C3 reference kernel before A2/S1-G2 is open; held
  pending that decision).
- **Superseded, no longer tracked as its own decision:** R-11 (`per_trade_risk_pct`) — removed from v1.x scope 2026-07-25; see `OWNER_DECISION_LOG.md`.
- **Decided (see `OWNER_DECISION_LOG.md` for authoritative values — this
  matrix keeps the original proposals for audit-trail comparison only):**
  R-01, R-02, R-05, R-07, R-08 (value only, guard direction flagged), R-09,
  R-10, R-12, R-13, R-14, R-15, R-16, R-17, R-19, R-20, R-23, R-24, R-25,
  R-26 (19 total).
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
