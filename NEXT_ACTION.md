# NEXT_ACTION.md

**One milestone at a time. This is the active milestone.**

## ST-C3 A3 OPEN — Replay Engine Built, Data-Blocked — Active Milestone

Current lifecycle position:

| Field | State |
|---|---|
| Stage | Stage A - Strategy Validation |
| Substage | A3 - Statistical Edge and Robustness Qualification |
| Gate | S1-G7 Historical Baseline / Replay |
| Strategy | ST-C3 v1.0.6 (evidence-builder Tier 3 gap resolution, revision of v1.0.5, see `specs/st-c3_v1.0.6.yaml`) |
| Status | FROZEN -> S1-G1C CLOSED -> A2/S1-G2 PASSED -> A3 OPEN (owner decisions, 2026-07-26) |
| Readiness | GREEN |
| Frozen | YES |
| Implementation | S1-G2 scoped reference implementation complete; A3 replay engine built and run once |
| Backtest | A3 replay engine built and run (zero signals on available data) — full historical baseline still requires more data |
| A1 Logic Conformance | PASSED — see `reports/validation/st_c3/S1-G1C_RERUN_REPORT.md` |
| A2 Signal Conformance | PASSED: owner decision 2026-07-26 — see `reports/validation/st_c3/OWNER_DECISION_LOG.md`, "A2/S1-G2 gate closure" entry |
| A3 Statistical Validation | OPEN: owner decision 2026-07-26. First replay run (2026-07-27) produced 0 TradePlans — data-blocked, not code-blocked. See `reports/validation/st_c3/A3_REPLAY_RESULTS.md`. |
| Execution | BLOCKED (explicitly not authorized) |
| Demo | BLOCKED |
| Production | BLOCKED |

**A2/S1-G2 closure (owner decision, 2026-07-26):** all R-01–R-33 tracker
fields resolved; spec `v1.0.6` frozen (resolves R-31/R-32/R-33:
`sweep_reclaim_max_bars=2`, `entry_window_bars=4`, session UTC bounds);
reference funnel (all 15 evidence types) fully implemented and conformant;
R-18 existence-check floor computed (`signal_rate=0.0`, real GBPUSD
H4/M15/M3 data, see `reports/validation/st_c3/R18_EXISTENCE_CHECK_RESULTS.md`).

**A3 opening (owner decision, 2026-07-26):** authorized —
`historical_baseline`, `cost_adjusted_backtest`, `walk_forward` research
per `docs/strategy/st_c3/ST-C3_BACKTEST_SPEC.md`. `validation/st_c3/a3_replay_engine.py`
built (reuses `evidence_builder`/`kernel` unchanged, adds TradePlan
lifecycle simulation and metrics rollup) and run once against real GBPUSD
data (2026-07-27): **0 TradePlans emitted**, same rejection breakdown as
R-18 — confirms the engine's signal-detection path but never exercised its
new lifecycle-simulation code. See `reports/validation/st_c3/A3_REPLAY_RESULTS.md`.
**Still explicitly NOT authorized:** execution, optimization, demo
trading, live trading, production promotion — each requires its own
separate future owner decision. See `governance/st_c3_stage_status.yaml`
`a2_signal_conformance` / `a3_statistical_validation` for the authoritative
record.

## Objective

S1-G1C logic-conformance preparation is complete for ST-C3. The original
S1-G1C audit against v1.0.0 found three tracked rejection-code findings
(R-1, R-2, R-3); a governance review found one additional migration-scope
gap (GR-1); the owner approved the patch recommendation on 2026-07-25; the
fixes were cut as `specs/st-c3_v1.0.1.yaml` (v1.0.0 preserved unchanged as
historical record); and the S1-G1C structural checks were re-run clean
against v1.0.1 with zero critical/major findings
(`reports/validation/st_c3/S1-G1C_RERUN_REPORT.md`).

Specification Closure ran alongside/after S1-G1C and is now complete: all
33 tracked parameter/decision fields (R-01–R-33) are resolved — see
`reports/validation/st_c3/OWNER_DECISION_LOG.md` and `RESOLUTION_MATRIX.md`.
2 items were explicitly deferred to a possible v2.x cycle (fixed lot size,
instrument selection logic — both later separately decided as R-21/R-22),
4 proposed architecture changes were ruled out of v1.x scope (break-even,
trailing-stop, session-close forced-exit, dual-timeframe bias confirmation
— all deferred to v2.x, none applied to the frozen funnel), and R-18
(existence-check floor) was resolved last, via a real detection-module run
against real GBPUSD data (`signal_rate=0.0`).

The owner opened A2/S1-G2 on 2026-07-26 with a scoped authorization
(reference-funnel assembly, golden/negative-case testing, existence-check
research) and, later the same day, declared **A2/S1-G2 PASSED** once that
scoped work was complete and R-18 was resolved — see
`reports/validation/st_c3/OWNER_DECISION_LOG.md`, "A2/S1-G2 gate closure"
entry. This closure does NOT authorize execution, optimization, A3
opening, demo, live, or production work, which all remain blocked pending
their own separate, future owner decisions.

## Current Evidence

- **ST-C3 v1.0.6 revision + A2/S1-G2 closure (2026-07-26):** resolves
  R-31 (`sweep_reclaim_max_bars`=2), R-32 (`entry_window_bars`=4), and R-33
  (London/NY session UTC bounds ratified) — the Tier 3 evidence-builder
  numeric-placeholder gap found while scoping `build_evidence_bundle()`.
  `validation/st_c3/evidence_builder.py` (442 lines) implements all 15
  evidence types (Tier 1 direct `smc_engine` reuse, Tier 2 glue logic) and
  is wired into `tools/existence_check.py`'s unmodified `SignalFn` contract
  via `validation/run_st_c3_existence_check.py`. Run against real GBPUSD
  H4/M15/M3 data (3,339 M15 bars, 2026-06-05 -> 2026-07-24): **R-18 resolved,
  signal_rate = 0.0** — see `reports/validation/st_c3/R18_EXISTENCE_CHECK_RESULTS.md`
  for the full rejection-code breakdown and documented caveats (short
  window, implementation simplifications, funnel-strictness bottleneck at
  S1/S2). Every field on the R-01–R-33 tracker is now resolved, and the
  owner declared A2/S1-G2 **PASSED** the same day — see
  `specs/st-c3_v1.0.6.yaml`, `reports/governance/st_c3/RCR_ST-C3_v1.0.6_REPORT.md`,
  `governance/st_c3_stage_status.yaml` `a2_signal_conformance`.
- **ST-C3 v1.0.5 revision (2026-07-26):** decides R-27 (swing/fractal
  `k`=2), R-28 (BOS confirmation bars `N`=2), R-29 FVG half (min gap-size
  = 0.15x MF_ATR(1)), and R-30 (pullback depth = 0.30x ATR(1)) — the
  structural-detection-algorithm gap found while attempting real R-18
  work. Each value was chosen by the owner from an empirically-researched
  tradeoff curve in `reports/validation/st_c3/R27_R30_RESEARCH_REPORT.md`
  (GBPUSD H4/M15 real data; reused existing generic `smc_engine`
  primitives, no invented or ST-C2-inherited logic). R-29's OB half needed
  no new number (already a structural rule via `smc_engine.order_blocks()`).
  See `specs/st-c3_v1.0.5.yaml`, `reports/governance/st_c3/RCR_ST-C3_v1.0.5_REPORT.md`.
  **Every field on the R-01–R-30 tracker is now decided except R-18**,
  which no longer needs a spec decision — only real detection-module code
  and a data run (a separate engineering task, not yet started; still
  within the existing A2/S1-G2 scope, no new authorization granted).
- ST-C3 v1.0.4 revision: `specs/st-c3_v1.0.4.yaml`,
  `reports/governance/st_c3/RCR_ST-C3_v1.0.4_REPORT.md`. Decides R-22
  (`risk.instrument_tie_breaking_rule`: higher `computed_rr` wins between
  EURUSD/GBPUSD; EURUSD fixed-priority fallback on exact tie). Stage B /
  portfolio-level arbitration only — no execution code, no change to the
  S0-S13 state machine. **R-18 (existence-check floor) is now the only
  unresolved field of the 26 tracked.**
- ST-C3 v1.0.3 revision: `specs/st-c3_v1.0.3.yaml`,
  `reports/governance/st_c3/RCR_ST-C3_v1.0.3_REPORT.md`. Decides R-21
  (`fixed_lot_size` = 0.01, owner rationale: $1000 account capital) and
  revises R-02 (`instruments` narrowed to EURUSD/GBPUSD). **Correction on
  record:** the instrument-scope change was submitted mislabeled as "R-22"
  — R-22 (`instrument.selection_logic`, cross-instrument tie-breaking) is a
  different field and remains genuinely unresolved; the change was recorded
  as an R-02 revision instead, per the same ID-mismatch-detection precedent
  `OWNER_DECISION_LOG.md` already applies elsewhere. Only R-18
  (existence-check floor) and R-22 remain unresolved of the 26 tracked
  fields. No structural (evidence/state/guard/code) change.
- ST-C3 v1.0.2 governance parameter-freeze revision:
  `specs/st-c3_v1.0.2.yaml`, `reports/governance/st_c3/RCR_ST-C3_v1.0.2_REPORT.md`,
  `docs/strategy/st_c3/ST-C3_CHANGELOG.md`. Folds in 22 owner-decided fields
  (R-01 through R-26 minus R-11/R-18/R-21/R-22, plus both resolved Open
  Conflicts) that had accumulated in `OWNER_DECISION_LOG.md`/
  `RESOLUTION_MATRIX.md` but were not yet in a frozen spec. No evidence
  object, state, transition, guard, or rejection/termination code changed —
  parameter values and `trade_plan.risk` sizing fields only. R-03
  (`sessions.low_liquidity_filters`) was decided as part of this revision's
  own directive. Only R-18 (existence-check floor), R-21 (fixed-lot value),
  and R-22 (instrument selection logic) remain unresolved.
- ST-C3 A2/S1-G2 reference funnel (evidence-to-trade-plan validator kernel,
  golden/negative-case tests, existence-check readiness):
  `reports/validation/st_c3/S1-G2_REFERENCE_FUNNEL_REPORT.md`,
  `validation/st_c3/` (now pointed at `specs/st-c3_v1.0.5.yaml`),
  `tests/st_c3/` (20/20 passing). Builds the deterministic kernel the frozen
  spec fully specifies (`state_machine`/`evidence_bindings`/`trade_plan.schema`);
  does not build real price-bar SMC detection. With v1.0.2 now freezing the
  detection thresholds, that price-level detection work is unblocked in
  principle but remains a separate, not-yet-started engineering task — R-18's
  real existence-check number still requires it.
- ST-C3 active frozen spec: `specs/st-c3_v1.0.5.yaml` (structural-detection
  algorithm parameter revision of `specs/st-c3_v1.0.4.yaml`, itself an
  instrument tie-breaking revision of `specs/st-c3_v1.0.3.yaml`, itself a
  fixed-lot + instrument-scope revision of `specs/st-c3_v1.0.2.yaml`,
  itself a governance parameter-freeze revision of
  `specs/st-c3_v1.0.1.yaml`, itself a rejection-code revision of
  `specs/st-c3_v1.0.0.yaml` — all five preserved unchanged as historical
  record).
- ST-C3 Specification Closure tracking: `reports/validation/st_c3/RESOLUTION_MATRIX.md`,
  `DEPENDENCY_GRAPH.md`, `DECISION_PACKAGES.md`, `OWNER_DECISION_LOG.md`,
  `SPECIFICATION_CLOSURE_REPORT.md`, `R04_R06_RESEARCH_REPORT.md`.
- ST-C3 A2/S1-G2 opening decision: `governance/st_c3_stage_status.yaml`
  `a2_signal_conformance.opened` (owner directive, 2026-07-26).
- ST-C3 S1-G1C audit (against v1.0.0): `reports/validation/st_c3/ST-C3_S1-G1C_LOGIC_CONFORMANCE_REPORT.md`.
- ST-C3 patch recommendation (R-1/R-2/R-3): `reports/validation/st_c3/ST-C3_v1.0.1_PATCH_RECOMMENDATION.md`.
- ST-C3 governance review (verified findings, found GR-1): `reports/validation/st_c3/GOVERNANCE_REVIEW_REPORT.md`.
- ST-C3 S1-G1C rerun (against v1.0.1, PASS): `reports/validation/st_c3/S1-G1C_RERUN_REPORT.md`.
- ST-C3 governance stage-status tracking: `governance/st_c3_stage_status.yaml`.
- ST-C3 freeze action log:
  `docs/strategy/st_c3/ST-C3_FREEZE_ACTION_LOG.md`.
- ST-C3 worktree checkpoint:
  `docs/strategy/st_c3/ST-C3_WORKTREE_CHECKPOINT.md`.
- ST-C3 freeze checklist:
  `docs/strategy/st_c3/ST-C3_FREEZE_CHECKLIST.md`.
- ST-C3 strategy architecture:
  `docs/strategy/st_c3/ST-C3_STRATEGY_ARCHITECTURE.md`.
- ST-C3 funnel lifecycle:
  `docs/strategy/st_c3/ST-C3_FUNNEL_LIFECYCLE.md`.
- ST-C3 evidence object specification:
  `docs/strategy/st_c3/ST-C3_EVIDENCE_OBJECT_SPEC.md`.
- ST-C3 rejection/termination code specification:
  `docs/strategy/st_c3/ST-C3_REJECTION_CODE_SPEC.md`.
- ST-C3 parameter sheet:
  `docs/strategy/st_c3/ST-C3_PARAMETER_SHEET.md`.
- ST-C3 state machine:
  `docs/strategy/st_c3/ST-C3_STATE_MACHINE.md`.
- ST-C3 evidence binding layer:
  `docs/strategy/st_c3/ST-C3_EVIDENCE_BINDINGS.md`.
- ST-C3 trade-plan schema:
  `docs/strategy/st_c3/ST-C3_TRADE_PLAN_SCHEMA.md`.
- ST-C3 validator rules:
  `docs/strategy/st_c3/ST-C3_VALIDATOR_RULES.md`.
- ST-C3 proposed execution agent specification:
  `docs/strategy/st_c3/ST-C3_EXECUTION_AGENT_SPEC.md`.
- ST-C3 backtest specification:
  `docs/strategy/st_c3/ST-C3_BACKTEST_SPEC.md`.
- ST-C3 intake ADR:
  `docs/adr/ADR-0004-st-c3-candidate-intake.md`.
- ST-C3 RCR/intake entry: `reports/research_log.md`.

## Acceptance Criteria (S1-G1C — met; A2/S1-G2 — PASSED, 2026-07-26)

- Build an S1-G1C logic-conformance checklist for the frozen ST-C3 artifacts. DONE.
- Verify artifact cross-links and no dangling references. DONE.
- Verify YAML structural invariants: 16 evidence objects, 16 states, 16
  transitions, S13 evidence chain, R/ERR code maps, and blocked execution
  authority. DONE — re-verified against v1.0.1.
- Prepare a validation report outline for ST-C3. DONE (audit + rerun report).
- Resolve tracked rejection-code findings (R-1, R-2, R-3, GR-1) via a
  governance-approved revision before treating S1-G1C as closed. DONE —
  `specs/st-c3_v1.0.1.yaml`, owner-approved 2026-07-25.
- Preserve `docs/strategy/st_c3/ST-C3_BACKTEST_SPEC.md` as A3 planning
  material only; do not run backtests (historical_baseline is A3/S1-G7)
  until A2 passes and A3 is separately authorized. Still in force.
- Within A2/S1-G2's scoped authorization: build golden-case tests,
  negative-case tests, and existence-check research against a reference
  funnel. NOT authorized within this scope: execution, optimization,
  demo, live, or production paths, or opening A3.
  DONE — reference funnel (all 15 evidence types) built and conformant
  with `specs/st-c3_v1.0.6.yaml`; R-18 existence-check floor computed
  against real GBPUSD data (`signal_rate=0.0`); every R-01–R-33 tracker
  field resolved. Owner declared A2/S1-G2 PASSED, 2026-07-26 — see
  `reports/validation/st_c3/OWNER_DECISION_LOG.md`, "A2/S1-G2 gate
  closure" entry.

## Guardrails

- Do not modify frozen ST-C3 strategy logic except through a new
  governance-approved revision or candidate lineage.
- Do not modify `specs/st-c2_v1.2.0.yaml`.
- `engine_implements_spec` reflects that the reference funnel (all 15
  evidence types) now exists and is conformant with `specs/st-c3_v1.0.6.yaml`;
  `implementation_authorization` remains `scoped_reference_implementation_granted`
  (owner directive, 2026-07-26) — A2/S1-G2 PASSED does not itself grant
  full/unscoped implementation authority beyond that scope.
- A2/S1-G2's scope was exactly what's listed in
  `governance/st_c3_stage_status.yaml` `a2_signal_conformance.opened`.
  A3's scope is exactly what's listed in that same file's
  `a3_statistical_validation.opened` — `historical_baseline`,
  `cost_adjusted_backtest`, `walk_forward` research only. Execution,
  optimization, demo, and live remain explicitly not authorized and each
  require their own future, separate owner decision.
- A3 is open but its replay engine has produced zero TradePlans on the
  only data available — treat any future A3 report as data-limited until
  a longer/deeper historical dataset exists. Do not treat the current
  zero-signal result as a pass, fail, or statistical verdict on ST-C3.

---

## Levers Track — Engineering Infrastructure (separate from ST-C3)

Parallel, documentation/tooling-only track opened 2026-07-25 alongside the
ST-C3 work above, per `MASTER_PLAN.md`/ADR-0001 precedent that governance
and infrastructure work on one track does not block another; only
implementation capacity is one-at-a-time.

- Lever A (existence-check tool): DONE — `tools/existence_check.py`,
  `scripts/run_existence_for_candidate.py`, tested.
- Lever B (power-planning tool): DONE — `tools/power_planning.py`, tested.
- Lever F (A2-closure gate): DONE — `scripts/check_a2_closure.py`, tested,
  verified against the real `reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json`.
- Lever D (shared feature/structure-shift primitives): NOT STARTED this
  session. Already substantially covered by existing `src/features.py`
  (a pre-existing per-candle feature layer with the same "compute once,
  reuse everywhere" goal). Any further refactor of `src/signal_v35.py` or
  `src/live_signal.py` to consume it touches live detection code and would
  itself need an RCR under `docs/RESEARCH-CHARTER.md`, same as Lever C.
- Lever E (parallel batch runner): NOT STARTED this session. Already
  substantially covered by existing `validation/batch_validation_runner.py`
  (resumable, cached, per-symbol sequential runner). True multiprocessing
  parallelization was not implemented — doing so safely would require
  reworking its caching/report-writing model, not a drop-in `Pool.map`.
- Lever C (engine collapse / STRATEGY_OF_RECORD unification): BLOCKED —
  pending RCR authorization. Changes which engine's decisions are
  authoritative for live/backtest routing; requires a pre-registered RCR
  under `docs/RESEARCH-CHARTER.md` before any change to `src/daily_runner.py`
  or creation of a `STRATEGY_OF_RECORD` wrapper. No RCR has been filed yet.
- No demo or live trading is authorized by any of the above, independent of
  Lever C's status — no execution layer exists, and no A2/A3 evidence exists
  for either ST-C2 or ST-C3.
