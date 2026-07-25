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
| R-01 | `governance_profile` | Symbol/session scope not chosen | Owner decision required | Not proposed — depends on R-02 (instrument scope) first | Blocks everything; nothing can run without a scope | Critical |
| R-02 | `instruments` | No symbol enabled | Owner decision required | Not proposed — this is the single highest-leverage decision in the whole matrix | Blocks Phase 3-9 entirely; determines which historical data even matters | Critical |
| R-03 | `sessions.low_liquidity_filters` | No filter rule despite `optional_low_liquidity_filters: true` | Owner decision required | PROPOSED: `disabled_by_default` (simplest deterministic starting point; can be added as a v1.0.3 addendum once R-02/R-04 data exists to justify a filter) | Low — only affects edge-case session windows | Low |
| R-04 | `wick_ratio_min` | No minimum wick-penetration ratio | Research required | PROPOSED range: `0.5-0.7`, cite `specs/st-c2_v1.2.0.yaml:104` (`0.6`) as a reference point only, not inherited | Medium — affects sweep detection sensitivity | High (blocks Package B) |
| R-05 | `equal_highs_lows_tolerance` | No tolerance band for equal-highs/lows pools | Research required | PROPOSED: pip/point tolerance to be derived from an existence-check sweep over candidate values (e.g. 2-5 pips on majors) — no single number proposed without that data | Medium | Medium |
| R-06 | `max_sweep_age_bars` | No upper bound on swept-level age | Research required | PROPOSED range: 20-60 bars, cite `specs/st-c2_v1.2.0.yaml:167,175` (`max_age_bars: 60`/`20` for its own OB freshness, different field but same order of magnitude) as reference only | Medium | Medium |
| R-07 | `displacement_body_ratio_min` | "Impulsive candles" has no numeric threshold | Research required | PROPOSED range: `0.6-0.7` body-to-range ratio (matches the general SMC convention this project already uses elsewhere for displacement/BOS body-close rules) | High — this gates the entire displacement/BOS stage (§3.2), the funnel's second major filter | Critical (blocks Package F) |
| R-08 | `buffer_points` | No numeric buffer on the structural stop | Research required | PROPOSED: small ATR-multiple buffer (e.g. `0.1-0.2 * ATR`) rather than a fixed point count, so it scales across symbols — needs research to pick the multiple | Medium — affects every SL price computed | High |
| R-09 | `tp2_external_liquidity.rr_min` | No RR floor for TP2 | Owner decision required | PROPOSED: `5.0R` (between TP1's fixed `3.0R` and a plausible TP3, preserving strict ordering TP1 < TP2 < TP3) | Medium | Medium |
| R-10 | `tp3_htf_objective.rr_min` | No RR floor for TP3 | Owner decision required | PROPOSED: `8.0R` (same ordering logic as R-09) | Medium | Medium |
| R-11 | `risk.per_trade_risk_pct` | No position-sizing basis | Owner decision required | Already defined elsewhere: `docs/CHARTER.md` platform convention is `0.5%` demo / `1.0%` live — PROPOSED: ratify `0.5%` for ST-C3 research/demo phase, matching `specs/st-c2_v1.2.0.yaml:323` | High — required before any position sizing exists | Critical (blocks Package A) |
| R-12 | `risk.max_positions` | No concurrency limit | Owner decision required | Already defined elsewhere: CHARTER convention is `3` — PROPOSED: ratify `3`, matching `specs/st-c2_v1.2.0.yaml:325` | Medium | Medium |
| R-13 | `risk.portfolio_heat_pct` | No aggregate open-risk cap | Owner decision required | Already defined elsewhere: CHARTER convention is `4%`; ST-C2 itself deviated to `3.0%` (`specs/st-c2_v1.2.0.yaml:326`, noted in that file as "not a conflict") — PROPOSED: `3.0%` or `4.0%`, owner's choice between the two existing platform precedents | Medium | Medium |
| R-14 | `risk.daily_loss_pct` | No daily circuit-breaker | Owner decision required | Already defined elsewhere: CHARTER/ST-C2 convention is `3.0%` — PROPOSED: ratify `3.0%` | High — safety-critical | Critical (blocks Package A) |
| R-15 | `risk.weekly_loss_pct` | No weekly circuit-breaker | Owner decision required | Already defined elsewhere: ST-C2's own value is `7.0%` (`specs/st-c2_v1.2.0.yaml:328`, itself noted as having "no CHARTER equivalent to cross-check against") — PROPOSED: ratify `7.0%` as a starting point pending its own review | Medium | Medium |
| R-16 | `rcr_preregistration.primary_metric` | No pre-registered A3 success metric | Owner decision required | PROPOSED: expectancy_r (matches this repo's existing A3 promotion-gate convention, e.g. `docs/CHARTER.md` demo->live gate uses expectancy ≥ +0.2R) | Medium — needed before A3, not before A2 | Medium |
| R-17 | `rcr_preregistration.secondary_metrics` | No secondary metrics list | Owner decision required | PROPOSED: `[profit_factor, sharpe_ratio, maximum_drawdown_r]`, matching the metric set this repo already computes elsewhere (`validation/performance_metrics.py`) | Low | Low |
| R-18 | `rcr_preregistration.existence_check_floor` | No minimum signal rate | Research required | PROPOSED: use `tools/power_planning.py`'s `estimate_required_bars` against whatever `primary_metric` target is chosen (R-16), once R-02 (instrument) is fixed and real candle data can be scanned via `tools/existence_check.py` | Low — a Lever-A/B concern, not a blocker for Phases 3-4 | Low |
| R-19 | `rcr_preregistration.population_feasibility_floor` | No minimum trade-population target | Owner decision required | PROPOSED: `300` trades, matching this repo's own stated A3 promotion-gate convention elsewhere in the project (ST-C2/ST-C1 audits use similar floors) | Low | Low |
| R-20 | `rcr_preregistration.statistical_claim_floor` | No pre-registered PF/expectancy/Sharpe bar | Owner decision required | PROPOSED: PF ≥ 1.40, expectancy ≥ 0.20R, Sharpe ≥ 1.20 (matches this project's own A3 promotion-gate language used elsewhere) | Low — needed before A3, not before A2 | Low |

## Priority Summary

- **Critical (blocks everything, resolve first):** R-01, R-02, R-07, R-11, R-14.
- **High (blocks a specific package but not everything):** R-04, R-08.
- **Medium:** R-05, R-06, R-09, R-10, R-12, R-13, R-15, R-16.
- **Low (can wait until closer to A3, not A2):** R-03, R-17, R-18, R-19, R-20.

Note that R-01/R-02 (instrument and session scope) are the true root of the
dependency graph — see `DEPENDENCY_GRAPH.md` — because `wick_ratio_min`,
`max_sweep_age_bars`, and the existence-check floor (R-18) cannot even be
researched without first knowing which symbol's candle data to scan.
