# RCR-ST-C3-v1.0.2 — Revision Report

**Type:** Governance decision parameter freeze (not a research/backtest RCR
under `docs/RESEARCH-CHARTER.md` — no tunable strategy behavior was tested
or changed; every value folded in here was already an explicit owner
decision on record in `OWNER_DECISION_LOG.md`, or is a new owner decision
made in the same directive that opened this revision, R-03).
**From:** `specs/st-c3_v1.0.1.yaml` **To:** `specs/st-c3_v1.0.2.yaml`
**Date:** 2026-07-26
**Directive:** owner-issued "RCR-ST-C3-v1.0.2" chat directive, this session.

---

## Why

`OWNER_DECISION_LOG.md`/`RESOLUTION_MATRIX.md` accumulated 21 owner-decided
fields (R-01, R-02, R-04 through R-10, R-12 through R-17, R-19, R-20, R-23
through R-26) plus two resolved Open Conflicts (fixed-lot sizing model; TP1
`rr_min`=3.0 authoritative) across the 2026-07-25/26 specification-closure
work, but none of it had been folded into a frozen spec revision — the
active frozen spec remained v1.0.1, which still marks all of those fields
`UNRESOLVED`/`PROVISIONAL`. Per "Specification is the source of truth" and
"No implementation before specification freeze," this blocked any real
price-level SMC detection work and the R-18 existence-check floor. This
revision closes that gap for every field the owner has actually decided.

## What changed

`specs/st-c3_v1.0.2.yaml` is a full copy of v1.0.1's structure (`id`,
`pipeline`, `rejection_codes`, `evidence`, `state_machine`,
`validator_rules`, `evidence_object_schema`, `trade_plan`,
`execution_agent`, `risk`, `conformance`, `diagnostics`,
`rcr_preregistration`, `reference_material`) with these fields patched:

| Field | v1.0.1 | v1.0.2 | Source |
|---|---|---|---|
| `governance_profile` | `null` (UNRESOLVED) | `STRICT_DETERMINISTIC_GOVERNANCE_PROFILE` | R-01 |
| `instruments` | `[]` (UNRESOLVED) | `[EURUSD, GBPUSD, XAUUSD]` | R-02 |
| `sessions.low_liquidity_filters` | UNRESOLVED | structured low-liquidity signature | R-03 (decided in this directive) |
| `parameters.MIN_RR` | `CONFIGURABLE_PROVISIONAL_3R` | `3.0`, status `decided` | Open Conflict 2 |
| `liquidity_sweep_stage.wick_ratio_min` | UNRESOLVED | `0.50` | R-04 |
| `liquidity_sweep_stage.equal_highs_lows_tolerance` | UNRESOLVED | `0.10 * MF_ATR(1)` | R-05 |
| `liquidity_sweep_stage.max_sweep_age_bars` | UNRESOLVED | `15` | R-06 |
| `displacement_bos_stage.displacement_body_ratio_min` | `CONFIGURABLE_UNRESOLVED` | `0.50` | R-07 |
| `displacement_bos_stage.displacement_atr_floor_multiplier` | *(did not exist)* | `1.0` | R-07 (companion ATR-floor condition, AND-combined) |
| `fvg_ob_confluence_stage.freshness_definition` | UNRESOLVED (single field) | split into `ob_freshness_max_mf_swings: 3`, `fvg_freshness_max_mf_swings: 1` | R-23, R-24 |
| `stop_loss_stage.buffer_points_atr_multiplier` | *(did not exist as `buffer_points: UNRESOLVED`)* | `0.20` — **value only**, guard direction still unconfirmed | R-08 |
| `targets_stage.tp2_external_liquidity.rr_min` | UNRESOLVED | `2.0` | R-09 |
| `targets_stage.tp3_htf_objective.rr_min` | UNRESOLVED | `3.5` | R-10 |
| `trade_plan.schema.risk.risk_per_trade_pct` | present | removed; replaced with `sizing_model: FIXED_LOT` / `fixed_lot_size: DEFERRED` | Open Conflict 1 |
| `execution_agent.order.risk_pct` | present | replaced with `lot_size` pointer | Open Conflict 1 (consistency) |
| `risk.per_trade_risk_pct` | UNRESOLVED | removed; replaced with `sizing_model`/`fixed_lot_size` | Open Conflict 1 |
| `risk.min_rr` | `CONFIGURABLE_PROVISIONAL_3R` | `3.0` | Open Conflict 2 |
| `risk.max_positions` | UNRESOLVED | `2` | R-12 |
| `risk.portfolio_heat_pct` | UNRESOLVED | `3.0` | R-13 |
| `risk.daily_loss_pct` | UNRESOLVED | `3.0` | R-14 |
| `risk.weekly_loss_pct` | UNRESOLVED | `7.0` | R-15 |
| `risk.max_positions_per_instrument` | *(did not exist)* | `1` | R-25 |
| `risk.daily_max_trades` | *(did not exist)* | `4` | R-26 |
| `rcr_preregistration.primary_metric` | UNRESOLVED | `expectancy_r` | R-16 |
| `rcr_preregistration.secondary_metrics` | UNRESOLVED | `[profit_factor, sharpe_ratio, maximum_drawdown_r]` | R-17 |
| `rcr_preregistration.population_feasibility_floor` | UNRESOLVED | `300` | R-19 |
| `rcr_preregistration.statistical_claim_floor` | UNRESOLVED | `{pf_min: 1.40, expectancy_min_r: 0.20, sharpe_min: 1.20}` | R-20 |

**Unchanged, deliberately:** `pipeline.htf_bias_stage`, `ote_stage`
(`equilibrium_boundary`/`ote_band_min`/`ote_band_max`), `entry_window_stage`
(`entry_window_bars`), `parameters.N_SWEEP`/`MAX_ENTRY_BARS`/`OTE_MIN`/
`OTE_MAX`/`SESSION_LONDON`/`SESSION_NY`, `sessions.london_window_utc`/
`ny_window_utc` — none of these has an owner decision on record. All of
`rejection_codes`, `termination_codes`, `rejection_code_json_schema`,
`evidence` (registry), `state_machine` (states/transitions/
evidence_bindings), `validator_rules`, `evidence_object_schema` — no
decided field touches any of these; R-01's own decision note explicitly
confirms "No funnel/state-machine change results from this decision."

## What did NOT change (guardrails honored)

- No new evidence object, state, transition, guard, or rejection/termination
  code.
- No execution, optimization, or A3-stage content added or authorized.
- No price-level SMC detection module was built — this is a spec-text
  freeze only. Real detection modules (sweep/displacement/freshness/etc.
  computed from candles) remain a separate, later engineering task, now
  unblocked in principle since the thresholds are frozen, but not built by
  this revision.
- R-08's buffer *value* (0.20x MF ATR(1)) is recorded, but its guard
  *formulation* is explicitly flagged non-directional and unconfirmed in
  `OWNER_DECISION_LOG.md` — not implemented as executable guard logic here,
  matching the source decision's own caveat rather than inventing a fix.
- R-24's FVG-freshness rule's "AND FVG is not expired" clause references an
  undefined "FVG expiration" concept never tracked anywhere — that clause is
  not implemented; only the freshness-window condition is frozen.
- `entry_window_bars`, `equilibrium_boundary`, OTE band, session windows,
  and `N_SWEEP` remain provisional/unresolved — no owner decision exists for
  them, so nothing was frozen.
- R-18 (`existence_check_floor`), R-21 (`fixed_lot_size` value), and R-22
  (`instrument.selection_logic`) remain unresolved/deferred, unchanged.

## R-03 — new decision made in this directive

`sessions.low_liquidity_filters` had only a `PROPOSED: disabled_by_default`
placeholder on record (`RESOLUTION_MATRIX.md`, still "Owner decision
required"). The owner's RCR-ST-C3-v1.0.2 directive supplied a specific
low-liquidity signature (`wick_body_ratio_min: 2.0`,
`spread_expansion_factor: 1.5`, `atr_compression_ratio: 0.40`,
`excluded_time_windows`). This was verified against the real
`OWNER_DECISION_LOG.md`/`RESOLUTION_MATRIX.md` before being accepted —
those specific numbers were not previously on record — and confirmed with
the owner as a live decision (not a restatement of an existing one) before
being folded in. Recorded in `OWNER_DECISION_LOG.md`'s R-03 row, dated
2026-07-26.

## Deliverables

- `specs/st-c3_v1.0.2.yaml` — frozen, internally consistent (validated via
  `yaml.safe_load`, evidence-registry key set diffed identical to v1.0.1).
- `reports/validation/st_c3/OWNER_DECISION_LOG.md` — R-03 row filled in;
  top-of-file status updated to 22/26 decided, 1 pending (R-18).
- `reports/validation/st_c3/RESOLUTION_MATRIX.md` — R-03 row and priority
  summary updated to reflect integration into v1.0.2.
- `governance/st_c3_stage_status.yaml` — `spec`/`version` bumped to v1.0.2,
  `v1_0_2_revision` metadata block added.
- `validation/st_c3/evidence.py` — `SPEC_PATH` repointed to
  `specs/st-c3_v1.0.2.yaml` (evidence registry and rejection-code sections
  are byte-identical to v1.0.1, so no kernel behavior changed); all 20
  `tests/st_c3/` tests re-verified passing against v1.0.2.
- This report.

## Consequence for R-18 and next steps

R-18 (existence-check floor) remains the only pending field. It is now
unblocked *in principle* — the detection thresholds it needs are frozen —
but still requires someone to build real price-level SMC detection modules
(sweep, displacement, freshness, buffer) against these now-frozen numbers,
run them over real candle data via `tools/existence_check.py` +
`tools/power_planning.py`, and record a result. That is a distinct,
follow-on A2/S1-G2 engineering task (still within the existing scoped
authorization's `reference_funnel_assembly`/`existence_check_conformance_run`
items), not something this parameter-freeze RCR builds itself, per its own
"no new logic" constraint.
