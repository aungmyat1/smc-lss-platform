# ST-C3 Specification Closure — Dependency Graph

Shows which unresolved fields (`RESOLUTION_MATRIX.md` IDs) block which
others, so the owner can resolve root decisions first instead of picking
fields in an arbitrary order.

## Root Dependency

```text
R-02 instruments (which symbol?)
  |
  +--> R-01 governance_profile (session/symbol scope config)
  |
  +--> R-04 wick_ratio_min          (needs real candle data to research)
  +--> R-05 equal_highs_lows_tolerance (needs real candle data to research)
  +--> R-06 max_sweep_age_bars      (needs real candle data to research)
  +--> R-07 displacement_body_ratio_min (needs real candle data to research)
  +--> R-08 buffer_points           (ATR-based; needs a symbol's ATR distribution)
  +--> R-18 existence_check_floor   (tools/existence_check.py needs a symbol's data)
```

**R-02 is the single root node.** Every research-required field (R-04
through R-08, R-18) is unresearchable without it, because
`tools/existence_check.py` and any manual threshold study need real candle
data for a specific symbol.

## Risk Chain (Package A)

```text
R-11 per_trade_risk_pct
  |
  v
Lot Size / Position Sizing (not yet a spec field — computed at
  implementation time from per_trade_risk_pct + SL distance)
  |
  v
R-12 max_positions  ---+
R-13 portfolio_heat_pct +--> Position/Risk Gate (Stage B execution_agent,
R-14 daily_loss_pct      |    out of scope for Stage A but the values must
R-15 weekly_loss_pct  ---+    exist before Stage B can be designed)
  |
  v
Trade Validator (S12_RISK_SLTP guard: computed_rr >= MIN_RR)
  |
  v
Execution (blocked regardless, Stage B)
```

`per_trade_risk_pct` is the root of the risk chain — `max_positions`,
`portfolio_heat_pct`, `daily_loss_pct`, and `weekly_loss_pct` are each
independent caps that compose with it, not dependent on each other.

## Target/Exit Chain (Package D)

```text
TP1 rr_min = 3.0 (already fixed, owner-stated twice per S1-G1C audit)
  |
  v
R-09 tp2_external_liquidity.rr_min  (must be > TP1's 3.0 to preserve
  |                                  strict TP1 < TP2 < TP3 ordering)
  v
R-10 tp3_htf_objective.rr_min       (must be > R-09's resolved value)
```

R-09 must be resolved before R-10 can be sanity-checked (R-10 only needs to
be "greater than whatever R-09 becomes," not an independent number).

## Sweep/Liquidity Chain (Package B)

```text
R-02 instruments (root, see above)
  |
  v
R-04 wick_ratio_min  --+
R-05 equal_highs_lows_tolerance +--> SweepEvidence.valid computation
R-06 max_sweep_age_bars       --+     (S2_SWEEP / S3_SWEEP_RECLAIM guards)
```

These three are independent of each other but share the same root (R-02)
and the same downstream consumer (the sweep-stage guard).

## Order Block / FVG Freshness Chain (Package C)

```text
R-02 instruments (root)
  |
  v
freshness_definition (ambiguous term, not yet its own resolution-matrix
  ID — see SPECIFICATION_VALIDATION.md "Ambiguous Terms" #2)
  |
  v
FVGEvidence.fresh / OrderBlockEvidence.fresh computation
  (S8_FVG_OB_CONFLUENCE guard)
```

## RCR Pre-Registration Chain (Package H) — lowest priority, needed before A3 not A2

```text
R-16 primary_metric
  |
  v
R-20 statistical_claim_floor (the bar primary_metric must clear)
  |
  v
R-19 population_feasibility_floor (trade count needed to test that bar)
  |
  v
R-18 existence_check_floor (requires R-02 + tools/existence_check.py)
```

R-17 (secondary_metrics) has no dependents and can be resolved independently
at any point.

## Summary: Resolution Order That Minimizes Rework

1. **R-02** (instruments) — unlocks everything else.
2. **R-01** (governance_profile) — trivial once R-02 is set.
3. **R-11, R-12, R-13, R-14, R-15** (risk package) — independent of R-02,
   can be resolved in parallel with it.
4. **R-04, R-05, R-06, R-07, R-08** (research-required fields) — need R-02's
   symbol data; run via `tools/existence_check.py` once available.
5. **R-09, R-10** (TP RR floors) — depend on each other's ordering, not on
   R-02.
6. **R-03** (low-liquidity filters) — can be deferred (proposed default:
   disabled).
7. **R-16 through R-20** (RCR pre-registration) — lowest priority, only
   needed before A3, not before A2.
