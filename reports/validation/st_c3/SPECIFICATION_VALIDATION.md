# ST-C3 Specification Validation — Phase 1

**Audits:** `specs/st-c3_v1.0.1.yaml` (active frozen spec).
**Distinct from:** `ST-C3_S1-G1C_LOGIC_CONFORMANCE_REPORT.md`, which audited
structural completeness (16/16/16 invariants, cross-links, rejection-code
mapping). This report instead catalogues every `UNRESOLVED`/`PROVISIONAL`/
`CONFIGURABLE_UNRESOLVED` field and every ambiguous term — i.e. whether the
spec's *content* is deterministic, measurable, and objective, not whether
its *structure* is internally consistent.

**Result: NOT YET FULLY DETERMINISTIC.** The spec is structurally complete
(per S1-G1C) but contains 19 unresolved parameters and 3 ambiguous
definitions that must be resolved before a reference implementation could
be built without inventing values. This is expected and by design — the
spec's own header states `UNRESOLVED` fields "must be resolved at S1-G1
before this file may leave draft status" — but it means **A2/S1-G2 cannot
meaningfully open yet even if authorized**, since a reference implementation
would have nothing concrete to implement for these fields.

---

## Unresolved Parameters (must be resolved before implementation)

| Field | Location | Current value | Why it blocks implementation |
|---|---|---|---|
| `governance_profile` | top-level | `null` | Symbol/session scope not decided — no instrument is enabled. |
| `instruments` | §1 | `[]` | No symbol has been authorized for ST-C3 at all. |
| `sessions.low_liquidity_filters` | §1 | `UNRESOLVED` | Owner mentioned optional filters but gave no rule. |
| `wick_ratio_min` | §3.1 liquidity_sweep_stage | `UNRESOLVED` | No minimum wick-penetration ratio defined; "wick through the level" is not itself measurable. |
| `equal_highs_lows_tolerance` | §3.1 | `UNRESOLVED` | No tolerance band for equal highs/lows liquidity pools. |
| `max_sweep_age_bars` | §3.1 | `UNRESOLVED` | No upper bound on how old a swept level may be. |
| `displacement_body_ratio_min` | §3.2 displacement_bos_stage | `CONFIGURABLE_UNRESOLVED` | "Impulsive candles" has no measurable threshold — see Ambiguous Terms below. |
| `buffer_points` | §3.8 stop_loss_stage | `UNRESOLVED` | Structural stop has no numeric buffer; "never arbitrary" alone isn't computable. |
| `tp2_external_liquidity.rr_min` | §3.9 targets_stage | `UNRESOLVED` | No RR floor for TP2. |
| `tp3_htf_objective.rr_min` | §3.9 | `UNRESOLVED` | No RR floor for TP3. |
| `risk.per_trade_risk_pct` | §6 | `UNRESOLVED` | No position-sizing basis. |
| `risk.max_positions` | §6 | `UNRESOLVED` | No portfolio concurrency limit. |
| `risk.portfolio_heat_pct` | §6 | `UNRESOLVED` | No aggregate open-risk cap. |
| `risk.daily_loss_pct` | §6 | `UNRESOLVED` | No daily circuit-breaker. |
| `risk.weekly_loss_pct` | §6 | `UNRESOLVED` | No weekly circuit-breaker. |
| `rcr_preregistration.primary_metric` | §8 | `UNRESOLVED` | No pre-registered success metric for A3. |
| `rcr_preregistration.secondary_metrics` | §8 | `UNRESOLVED` | Same. |
| `rcr_preregistration.existence_check_floor` | §8 | `UNRESOLVED` | No minimum signal rate defined for Lever-A-style existence checks. |
| `rcr_preregistration.population_feasibility_floor` | §8 | `UNRESOLVED` | No minimum trade-population target. |
| `rcr_preregistration.statistical_claim_floor` | §8 | `UNRESOLVED` | No pre-registered statistical bar (PF/expectancy/Sharpe) to test against. |

**Count: 19 unresolved fields.** None of these were touched by the R-1/R-2/
R-3/GR-1 rejection-code revision — they were `UNRESOLVED` in v1.0.0 and
remain `UNRESOLVED` in v1.0.1, since that revision was scoped strictly to
the diagnostic layer.

## Provisional Parameters (have a value, but explicitly not yet ratified)

| Field | Value | Source |
|---|---|---|
| `N_SWEEP` | `PROVISIONAL_1_TO_3` bars | owner example |
| `MAX_ENTRY_BARS` | `PROVISIONAL_3_TO_5` M3 bars | owner example |
| `MIN_RR` / `risk.min_rr` | `CONFIGURABLE_PROVISIONAL_3R` | owner example |
| `sessions.london_window_utc` | `PROVISIONAL_07_00_TO_10_00` | owner example |
| `sessions.ny_window_utc` | `PROVISIONAL_13_00_TO_16_00` | owner example |
| `equilibrium_boundary` | `0.5` | reference doc, not owner-confirmed |
| `ote_band_min` / `ote_band_max` | `0.62` / `0.79` | reference doc, not owner-confirmed |
| `entry_window_bars` | `PROVISIONAL_3_TO_5_M3_BARS` | owner example |

These are not blocking in the same sense as `UNRESOLVED` (a concrete value
exists to implement against), but the spec itself requires they be
"ratified or changed at ST-C3's own S1-G1 spec-freeze act" before being
treated as final — that ratification has not happened separately from the
general freeze.

## Ambiguous Terms (no numeric definition given anywhere in the spec)

1. **"Impulsive candles"** (`displacement_bos_stage.displacement_definition`)
   — the owner's description of displacement, with no body-ratio, ATR
   multiple, or range threshold attached. `displacement_body_ratio_min` is
   explicitly `CONFIGURABLE_UNRESOLVED` for exactly this reason. Without a
   number, two implementers could reasonably disagree on whether a given
   candle "displaces."
2. **"Fresh"** (`fvg_ob_confluence_stage.freshness_definition: UNRESOLVED`)
   — the owner requires FVG/OB zones to be "fresh" but gives no maximum-age
   bar count. `nearest_ob_bull`/`nearest_ob_bear` in the existing
   `src/features.py` primitive already parameterizes this as `poi_max_age`
   for a *different* candidate (ST-C1/ST-C2's own POI logic) — ST-C3's own
   value must be independently decided, not inherited, per ADR-0004's
   "new lineage" ruling.
3. **"Never arbitrary" stop** (`stop_loss_stage.mode: structural_invalidation`)
   — directionally clear (stop must anchor to a swing, not a fixed pip
   count) but `buffer_points` is `UNRESOLVED`, so the exact stop price is
   not yet fully computable from the spec alone.

## Conflicting Rules

None found. Cross-checked all pipeline stage definitions, risk section, and
trade-plan schema for contradictions beyond the R-1/R-2/R-3 findings already
closed in v1.0.1 — no new conflicts identified.

## Hidden Assumptions

- The spec assumes a single concurrent setup per symbol (no explicit
  multi-position-per-symbol handling), consistent with `risk.max_positions`
  being portfolio-wide rather than per-symbol, but this is inferred from
  structure, not stated explicitly — worth an explicit owner confirmation
  before implementation, not treated as resolved here.
- `session_gatekeeper_stage.optional_low_liquidity_filters: true` implies a
  filter exists, but `sessions.low_liquidity_filters` is `UNRESOLVED` — the
  spec assumes this filter's content will be supplied later without stating
  what "optional" means operationally (on by default? off by default?).

---

## Phase 1 Conclusion

**Structural completeness:** PASS (per S1-G1C, unaffected by this report).
**Content determinism:** NOT YET COMPLETE — 19 `UNRESOLVED` fields and 3
ambiguous terms remain, all pre-existing from the original v1.0.0 freeze,
none touched by the v1.0.1 rejection-code revision. These are exactly the
class of gap `NEXT_ACTION.md`'s original S1-G1C acceptance criteria and the
spec's own header already flag as required-before-implementation, not a new
finding this report invents.

**Implication for A2/S1-G2:** even if A2/S1-G2 authorization were granted,
a reference implementation could not be built deterministically today — it
would have to either invent values for 19 fields (violating "never
hardcode... use approved package plus configuration" and "no discretionary
interpretation") or block on resolving them first. Resolving `UNRESOLVED`
fields is itself a spec change requiring the same RCR/governance-revision
process used for R-1/R-2/R-3, since picking `wick_ratio_min: 0.6` (say) is a
design decision, not a bug fix.

**Next action:** none required by this report alone. Recorded for the
owner's awareness ahead of any future A2/S1-G2 decision — resolving these
19 fields would need to happen before or alongside opening A2/S1-G2, not
after.
