# ST-C3 Specification Changelog

Tracks frozen spec revisions only. See `governance/st_c3_stage_status.yaml`
for the machine-readable authoritative status and
`reports/validation/st_c3/OWNER_DECISION_LOG.md` for the full decision
rationale behind every field below.

---

## v1.0.7 — 2026-07-27 (fresh R-31/R-32/R-33 decisions, clean provenance)

**RCR:** `reports/governance/st_c3/RCR_ST-C3_v1.0.7_REPORT.md`
**Supersedes:** v1.0.5 (preserved unchanged as historical record). Skips
v1.0.6 — quarantined, see the entries below and
`reports/governance/v1.0.6_RECONCILIATION_AUDIT.md`.

Decides R-31 (`sweep_reclaim_max_bars=2`), R-32 (`entry_window_bars=4`),
R-33 (session UTC bounds ratified, unchanged) — the same three fields the
quarantined v1.0.6 line had proposed, reconfirmed fresh with clean
provenance directly from the owner, no empirical justification claimed
(same category as R-05/R-21), independent of that line's disputed
provenance. **Every field on the R-01–R-33 tracker is now decided except
R-18**, which needs real detection-module code for six stages (S3, S7, S9,
S10, S11, S12), not a further spec decision.

**Not changed:** any evidence object, state, transition, guard, or
rejection/termination code.

## QUARANTINED — R-18 "closed" claim, 2026-07-26 (REJECTED 2026-07-27)

**This claim is rejected, not authoritative.** Kept for the historical
record only. The original claim: `validation/st_c3/evidence_builder.py`
was wired into `tools/existence_check.py` and run against real GBPUSD
H4/M15/M3 data, producing `signal_rate = 0.0`. **Why rejected:**
`evidence_builder.py` hardcodes `OTE_MIN, OTE_MAX = 0.62, 0.79   #
provisional, numerically usable` and uses it to compute real `S7_OTE`
gating results, despite `specs/st-c3_v1.0.6.yaml` itself still marking
those fields provisional — a confirmed "no implementation before
specification freeze" violation. See
`reports/governance/v1.0.6_RECONCILIATION_AUDIT.md`. R-18's real status:
still open — see `reports/validation/st_c3/R18_CLOSURE_REPORT.md`.

## QUARANTINED — v1.0.6, 2026-07-26 (evidence-builder Tier 3 gap resolution) — REJECTED 2026-07-27

**RCR:** `reports/governance/st_c3/RCR_ST-C3_v1.0.6_REPORT.md`
**Supersedes:** v1.0.5 (preserved unchanged as historical record)

Decides R-31–R-33 — three fields surfaced by `R18_EVIDENCE_BUILDER_DESIGN.md`'s
Tier 3 gap analysis while scoping `build_evidence_bundle()` (R-18's
remaining engineering task, not yet implemented). Unlike R-27–R-30 (missing
algorithms), these had a defined algorithm but the spec text still carried
a literal placeholder string instead of a usable number:

- **R-31** — `sweep_reclaim_max_bars` (N_SWEEP) = **2 bars** (owner's
  phase-conditional pick for the current A2/S1-G2 research/validation
  phase; 1 bar and 3 bars recorded as alternatives for other phases, not
  adopted)
- **R-32** — `entry_window_bars` (MAX_ENTRY_BARS) = **4 M3 bars** (owner's
  mid-range pick, avoiding bias toward either end of the prior provisional
  range)
- **R-33** — `sessions.london_window_utc`/`ny_window_utc` = **London
  07:00-10:00 UTC, NY 13:00-16:00 UTC** (owner ratified the spec's own
  long-standing provisional values as final; clock times unchanged)

**Not changed:** any evidence object, state, transition, guard, or
rejection/termination code. No detection-module code was written — these
are spec-text values only; `build_evidence_bundle()` remains a design
artifact, not implemented code.

**Governance milestone:** every field on the R-01–R-33 tracker is now
decided except **R-18** (`existence_check_floor`), which still needs only
real detection-module implementation and a data run, not any further spec
decision. Execution/optimization/demo/live/A3 remain exactly as blocked as
before.

## v1.0.5 — 2026-07-26 (structural-detection algorithm parameters)

**RCR:** `reports/governance/st_c3/RCR_ST-C3_v1.0.5_REPORT.md`
**Supersedes:** v1.0.4 (preserved unchanged as historical record)

Decides R-27–R-30 (the structural-detection-algorithm gap found while
attempting real R-18 detection work, distinct from the R-01–R-26 filter
thresholds already frozen), each chosen by the owner from an
empirically-researched tradeoff curve in `R27_R30_RESEARCH_REPORT.md`:

- **R-27** — HTF swing/fractal lookback `k` = 2
- **R-28** — BOS confirmation bars `N` = 2
- **R-29** (FVG half) — FVG minimum gap-size = 0.15x MF_ATR(1) (OB half
  needed no new number — already a structural rule via
  `smc_engine.order_blocks()`)
- **R-30** — pullback depth = 0.30x ATR(1)

**Not changed:** any evidence object, state, transition, guard, or
rejection/termination code. No detection-module code was written — these
are spec-text values only.

**Governance milestone:** every field on the R-01–R-30 tracker is now
decided except **R-18** (`existence_check_floor`), which no longer needs
any further spec decision — only real detection-module implementation and
a data run, a distinct engineering task within the existing A2/S1-G2
scope. Execution/optimization/demo/live/A3 remain exactly as blocked as
before.

## v1.0.4 — 2026-07-26 (instrument tie-breaking rule)

**RCR:** `reports/governance/st_c3/RCR_ST-C3_v1.0.4_REPORT.md`
**Supersedes:** v1.0.3 (preserved unchanged as historical record)

- **R-22 decided:** new `risk.instrument_tie_breaking_rule` field. When
  both R-02 instruments (EURUSD, GBPUSD) qualify concurrently near the
  position cap, the instrument with the higher `computed_rr` wins; on an
  exact tie, EURUSD wins by fixed priority (lower volatility, tighter
  spreads). Reuses the existing `trade_plan.schema.risk.computed_rr` field
  — no new metric introduced.
- Stage B / portfolio-level arbitration only — does not affect the S0-S13
  state machine (which already runs per-instrument independently) and is
  not implemented as executable code, since no execution agent exists or is
  authorized.

**Not changed:** any evidence object, state, transition, guard, or
rejection/termination code.

**Still unresolved after v1.0.4:** R-18 (`existence_check_floor`) — the
only field remaining unresolved of the 26 tracked.

## v1.0.3 — 2026-07-26 (fixed-lot value decision + instrument-scope revision)

**RCR:** `reports/governance/st_c3/RCR_ST-C3_v1.0.3_REPORT.md`
**Supersedes:** v1.0.2 (preserved unchanged as historical record)

- **R-21 decided:** `risk.fixed_lot_size` = `0.01` (micro-lot). Owner
  rationale: the only fixed-lot value assessed as compatible with ST-C3's
  frozen risk caps at a stated $1000 account capital (owner-asserted
  risk-appetite judgment, not independently re-derived).
- **R-02 revised:** `instruments` narrowed from `[EURUSD, GBPUSD, XAUUSD]`
  to `[EURUSD, GBPUSD]`. Owner rationale: XAUUSD's pip-value x SL-distance
  geometry exceeds the risk envelope under 0.01-lot fixed sizing.
- **Correction on record:** the owner's submission labeled the
  instrument-scope change "R-22." R-22 (`instrument.selection_logic`) is
  actually a different, still-unresolved field — cross-instrument
  tie-breaking logic. The change was recorded as a revision to R-02
  instead; R-22 remains genuinely unresolved. See the RCR report for the
  full correction.

**Not changed:** any evidence object, state, transition, guard, or
rejection/termination code. No execution, optimization, demo, live, or A3
logic.

**Still unresolved after v1.0.3:** R-18 (`existence_check_floor`), R-22
(`instrument.selection_logic`).

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
