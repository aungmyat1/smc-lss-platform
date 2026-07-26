# ST-C3 Specification Changelog

Tracks frozen spec revisions only. See `governance/st_c3_stage_status.yaml`
for the machine-readable authoritative status and
`reports/validation/st_c3/OWNER_DECISION_LOG.md` for the full decision
rationale behind every field below.

---

## v1.0.2 — 2026-07-26 (governance decision parameter freeze)

**RCR:** `reports/governance/st_c3/RCR_ST-C3_v1.0.2_REPORT.md`
**Supersedes:** v1.0.1 (preserved unchanged as historical record)

Folds in 22 owner-decided fields that had accumulated in
`OWNER_DECISION_LOG.md`/`RESOLUTION_MATRIX.md` since the v1.0.1 freeze but
had not yet been applied to a frozen spec:

- **Scope/governance:** `governance_profile` (R-01), `instruments` (R-02).
- **Session filtering:** `sessions.low_liquidity_filters` — new structured
  low-liquidity signature (R-03, decided in this revision's own directive).
- **Detection thresholds:** `wick_ratio_min` (R-04), `equal_highs_lows_tolerance`
  (R-05), `max_sweep_age_bars` (R-06), `displacement_body_ratio_min` +
  new ATR-floor companion condition (R-07), OB/FVG freshness windows split
  out of the old single `freshness_definition` field (R-23, R-24).
- **Stop/target numerics:** `buffer_points` ATR multiplier — value only, guard
  *direction* formulation still unconfirmed (R-08); TP2/TP3 `rr_min` (R-09,
  R-10); `MIN_RR`/`risk.min_rr` ratified at 3.0 (Open Conflict 2).
- **Risk/portfolio:** `max_positions` (R-12), `portfolio_heat_pct` (R-13),
  `daily_loss_pct` (R-14), `weekly_loss_pct` (R-15),
  `max_positions_per_instrument` (R-25), `daily_max_trades` (R-26); sizing
  model changed from percentage-risk to fixed-lot, `risk_per_trade_pct`
  removed from `risk` and `trade_plan.schema.risk` (Open Conflict 1) — the
  actual fixed lot size remains deferred (R-21).
- **A3 pre-registration:** `primary_metric` (R-16), `secondary_metrics`
  (R-17), `population_feasibility_floor` (R-19), `statistical_claim_floor`
  (R-20).

**Not changed:** any evidence object, state, transition, guard, or
rejection/termination code (`pipeline` stage *structure*, `rejection_codes`,
`evidence` registry, `state_machine`, `validator_rules`,
`evidence_object_schema` are byte-identical to v1.0.1). No execution,
optimization, or A3-stage logic added. No price-level SMC detection module
built — this is a spec-text freeze, not an implementation step.

**Still unresolved after v1.0.2:** R-18 (`existence_check_floor` — blocked
on price-level detection modules being built against these now-frozen
numbers, a separate follow-on task), R-21 (`fixed_lot_size` value), R-22
(`instrument.selection_logic`).

## v1.0.1 — 2026-07-25 (rejection-code layer fix)

**RCR:** `reports/research_log.md`, "ST-C3 rejection-code layer fix" entry
**Supersedes:** v1.0.0 (preserved unchanged as historical record)

Closed S1-G1C audit findings R-1, R-2, R-3, and governance-review finding
GR-1 — added dedicated `R8_INVALID_RISK_OR_TARGET` code for
`S12_RISK_SLTP` (previously mis-coded), fixed an internally-inconsistent
`failure_code` placeholder, and extended `R3`/`R4` trigger lists to justify
`S5`/`S6`'s reuse of those codes. No detection logic, guard condition,
evidence object, state, transition, or tunable threshold changed — a trade
accepted or rejected under v1.0.0 is accepted or rejected identically under
v1.0.1; only rejection-code diagnostic labels changed.

## v1.0.0 — 2026-07-24 (initial freeze)

**Freeze act:** `docs/strategy/st_c3/ST-C3_FREEZE_ACTION_LOG.md`
**Intake ADR:** `docs/adr/ADR-0004-st-c3-candidate-intake.md`

Initial frozen ST-C3 candidate specification — the "Next-Generation SMC
Funnel," a distinct lineage from ST-C2 per ADR-0004, with its own
rejection-code and funnel-stage-cluster namespace.
