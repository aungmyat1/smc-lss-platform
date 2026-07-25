# ST-C3 Specification Closure — Decision Packages

Bundles `RESOLUTION_MATRIX.md`'s 20 fields into 8 coherent packages so the
owner reviews related decisions together instead of 20 isolated values.
Every proposed value is a **starting point for owner review**, not a
decision already made.

---

## Package E — Instrument & Session Scope (ROOT — resolve first)

| Field | Proposal |
|---|---|
| R-02 `instruments` | Not proposed — this is the one decision with no reasonable default. Needs the owner to name a symbol (or symbols). |
| R-01 `governance_profile` | Depends on R-02; trivial once instrument(s) chosen. |
| R-03 `sessions.low_liquidity_filters` | PROPOSED: `disabled_by_default`. |

**Why first:** per `DEPENDENCY_GRAPH.md`, R-02 is the root of the entire
research-required branch — nothing in Packages B, C, F, or G can be
researched without real candle data for a named symbol.

---

## Package A — Risk

| Field | Proposal | Basis |
|---|---|---|
| R-11 `per_trade_risk_pct` | `0.5%` | `docs/CHARTER.md` platform convention; matches `specs/st-c2_v1.2.0.yaml:323` |
| R-12 `max_positions` | `3` | Same CHARTER convention; matches ST-C2 |
| R-13 `portfolio_heat_pct` | `3.0%` or `4.0%` (owner's pick between two existing platform precedents) | CHARTER says 4%, ST-C2 itself uses 3% |
| R-14 `daily_loss_pct` | `3.0%` | CHARTER/ST-C2 convention |
| R-15 `weekly_loss_pct` | `7.0%` | ST-C2's own value (no CHARTER equivalent exists) |

**Framing for the owner:** adopting the existing platform risk convention
wholesale is the lowest-friction option, but ST-C3 is a distinct lineage
(ADR-0004) — nothing requires matching ST-C2 exactly. Flagging this as a
genuine choice, not a formality.

---

## Package B — Liquidity / Sweep

| Field | Proposal | Basis |
|---|---|---|
| R-04 `wick_ratio_min` | `0.5-0.7` range | ST-C2 reference point only (`0.6`), not inherited |
| R-05 `equal_highs_lows_tolerance` | Needs research (existence-check sweep across candidate values) | No safe default proposed without data |
| R-06 `max_sweep_age_bars` | `20-60` bars | Order-of-magnitude reference from ST-C2's own (differently-scoped) freshness fields |

**Framing for the owner:** these three cannot be responsibly finalized from
judgment alone — they need Package E resolved first, then a research pass
(`tools/existence_check.py` against real candle data) before locking a
number. This package's role right now is only to confirm the *research
plan*, not to approve final values yet.

---

## Package C — Order Block / FVG Freshness

| Field | Proposal | Basis |
|---|---|---|
| `freshness_definition` (ambiguous term, not yet a resolution-matrix ID) | Needs research, same reasoning as Package B | `src/features.py`'s existing `poi_max_age` parameter is a *different* candidate's (ST-C1/ST-C2) decision — ST-C3 must independently decide per ADR-0004 |

Smallest package (one decision), but shares Package B's "needs research
after Package E" characteristic.

---

## Package D — Targets (TP)

| Field | Proposal | Basis |
|---|---|---|
| R-09 `tp2_external_liquidity.rr_min` | `5.0R` | Between TP1's fixed `3.0R` and a plausible TP3, preserving strict ordering |
| R-10 `tp3_htf_objective.rr_min` | `8.0R` | Same ordering logic |

**Framing for the owner:** TP1's `3.0R` is already owner-stated (not
proposed here — it's existing, ratified spec content). R-09/R-10 are new
proposals that only need to preserve `TP1 < TP2 < TP3`; the owner may pick
any values satisfying that, these are just a reasonable starting point.

---

## Package F — Displacement Threshold

| Field | Proposal | Basis |
|---|---|---|
| R-07 `displacement_body_ratio_min` | `0.6-0.7` | General SMC displacement/BOS body-close convention already used elsewhere in this codebase's detection logic |

Single-field package, but ranked **Critical** priority in the resolution
matrix — it gates the entire displacement/BOS stage (§3.2), the funnel's
second major filter after HTF bias.

---

## Package G — Stop Buffer

| Field | Proposal | Basis |
|---|---|---|
| R-08 `buffer_points` | ATR-multiple (e.g. `0.1-0.2 * ATR`) rather than a fixed point count | Scales across symbols/volatility regimes; needs research to pick the multiple once Package E is resolved |

---

## Package H — RCR Pre-Registration (lowest priority — needed before A3, not A2)

| Field | Proposal | Basis |
|---|---|---|
| R-16 `primary_metric` | `expectancy_r` | Matches this repo's existing A3 gate convention |
| R-17 `secondary_metrics` | `[profit_factor, sharpe_ratio, maximum_drawdown_r]` | Matches `validation/performance_metrics.py`'s existing metric set |
| R-18 `existence_check_floor` | Compute via `tools/power_planning.py` once R-16/R-20 and Package E are resolved | Requires real candle data |
| R-19 `population_feasibility_floor` | `300` trades | Matches this project's own stated A3 promotion-gate convention elsewhere |
| R-20 `statistical_claim_floor` | PF ≥ 1.40, expectancy ≥ 0.20R, Sharpe ≥ 1.20 | Matches this project's own A3 promotion-gate language used elsewhere |

Can be deferred entirely until closer to opening A3 — does not block A2/S1-G2.

---

## Recommended Review Order

1. **Package E** (instrument/session scope) — must go first, unlocks research for B/C/F/G.
2. **Package A** (risk) — independent of E, can be reviewed in parallel.
3. **Package D** (targets) — independent of E, can be reviewed in parallel.
4. **Package F** (displacement threshold) — critical priority, single field, quick decision.
5. **Package B, C, G** (research-required fields) — need Package E resolved first; these produce a *research plan*, not an immediate number.
6. **Package H** (RCR pre-registration) — defer until closer to A3.
