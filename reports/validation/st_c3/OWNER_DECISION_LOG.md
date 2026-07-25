# ST-C3 Owner Decision Log

**Purpose:** record the owner's actual decision for each `RESOLUTION_MATRIX.md`
field, distinct from the proposals in that matrix and in `DECISION_PACKAGES.md`.
This file is intentionally mostly empty — it is a log the owner fills in, not
a report the agent generates on the owner's behalf. Filling in a "Decision"
column with a proposed value would defeat its purpose.

**Status: NO DECISIONS RECORDED YET.** Every row below is `PENDING`.

---

| ID | Field | Proposed (see RESOLUTION_MATRIX.md) | Owner Decision | Decided By | Date | Notes |
|---|---|---|---|---|---|---|
| R-01 | `governance_profile` | Depends on R-02 | PENDING | — | — | |
| R-02 | `instruments` | Not proposed | PENDING | — | — | Root decision — see `DEPENDENCY_GRAPH.md` |
| R-03 | `sessions.low_liquidity_filters` | `disabled_by_default` | PENDING | — | — | |
| R-04 | `wick_ratio_min` | `0.5-0.7` range | PENDING | — | — | Needs research pass, not just a pick |
| R-05 | `equal_highs_lows_tolerance` | Research required | PENDING | — | — | |
| R-06 | `max_sweep_age_bars` | `20-60` bars | PENDING | — | — | |
| R-07 | `displacement_body_ratio_min` | `0.6-0.7` | PENDING | — | — | Critical priority |
| R-08 | `buffer_points` | ATR-multiple, e.g. `0.1-0.2 * ATR` | PENDING | — | — | |
| R-09 | `tp2_external_liquidity.rr_min` | `5.0R` | PENDING | — | — | |
| R-10 | `tp3_htf_objective.rr_min` | `8.0R` | PENDING | — | — | Depends on R-09 |
| R-11 | `risk.per_trade_risk_pct` | `0.5%` | PENDING | — | — | Critical priority |
| R-12 | `risk.max_positions` | `3` | PENDING | — | — | |
| R-13 | `risk.portfolio_heat_pct` | `3.0%` or `4.0%` | PENDING | — | — | Two existing platform precedents; owner picks |
| R-14 | `risk.daily_loss_pct` | `3.0%` | PENDING | — | — | Critical priority |
| R-15 | `risk.weekly_loss_pct` | `7.0%` | PENDING | — | — | |
| R-16 | `rcr_preregistration.primary_metric` | `expectancy_r` | PENDING | — | — | Not needed before A2 |
| R-17 | `rcr_preregistration.secondary_metrics` | `[profit_factor, sharpe_ratio, maximum_drawdown_r]` | PENDING | — | — | Not needed before A2 |
| R-18 | `rcr_preregistration.existence_check_floor` | Compute after R-02/R-16/R-20 | PENDING | — | — | Not needed before A2 |
| R-19 | `rcr_preregistration.population_feasibility_floor` | `300` trades | PENDING | — | — | Not needed before A2 |
| R-20 | `rcr_preregistration.statistical_claim_floor` | PF≥1.40, expectancy≥0.20R, Sharpe≥1.20 | PENDING | — | — | Not needed before A2 |

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
