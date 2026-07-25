# NEXT_ACTION.md

**One milestone at a time. This is the active milestone.**

## ST-C3 A2/S1-G2 OPEN (Scoped Research/Validation) — Active Milestone

Current lifecycle position:

| Field | State |
|---|---|
| Stage | Stage A - Strategy Validation |
| Substage | A2 - Indicator, Event and Signal Conformance |
| Gate | S1-G2 Reference Implementation Authorization |
| Strategy | ST-C3 v1.0.1 (revision of v1.0.0, see `specs/st-c3_v1.0.1.yaml`) |
| Status | FROZEN -> S1-G1C CLOSED -> A2/S1-G2 OPEN (scoped) |
| Readiness | GREEN |
| Frozen | YES |
| Implementation | AUTHORIZED: S1-G2 SCOPED RESEARCH/VALIDATION ONLY |
| Backtest | BLOCKED (historical baseline is A3/S1-G7) |
| A1 Logic Conformance | PASSED — see `reports/validation/st_c3/S1-G1C_RERUN_REPORT.md` |
| A2 Signal Conformance | IN PROGRESS: opened 2026-07-26 by owner directive, scoped (see below) |
| A3 Statistical Validation | BLOCKED: A2 NOT PASSED, and A3 opening itself explicitly not authorized yet |
| Execution | BLOCKED (explicitly not authorized) |
| Demo | BLOCKED |
| Production | BLOCKED |

**A2/S1-G2 scope (owner directive, 2026-07-26):** authorized —
reference-funnel assembly, golden-case tests (Phase 3), negative-case
tests (Phase 4), existence-check conformance runs (resolves R-18),
research/validation tasks. **Explicitly NOT authorized:** execution,
optimization, opening A3, demo trading, live trading, production
promotion. See `governance/st_c3_stage_status.yaml`
`a2_signal_conformance.opened` for the authoritative record.

## Objective

S1-G1C logic-conformance preparation is complete for ST-C3. The original
S1-G1C audit against v1.0.0 found three tracked rejection-code findings
(R-1, R-2, R-3); a governance review found one additional migration-scope
gap (GR-1); the owner approved the patch recommendation on 2026-07-25; the
fixes were cut as `specs/st-c3_v1.0.1.yaml` (v1.0.0 preserved unchanged as
historical record); and the S1-G1C structural checks were re-run clean
against v1.0.1 with zero critical/major findings
(`reports/validation/st_c3/S1-G1C_RERUN_REPORT.md`).

Specification Closure ran alongside/after S1-G1C: 21 of 26 tracked
parameter/decision fields are now owner-decided (see
`reports/validation/st_c3/OWNER_DECISION_LOG.md` and `RESOLUTION_MATRIX.md`),
2 explicitly deferred to a possible v2.x cycle (fixed lot size, instrument
selection logic), 4 proposed architecture changes ruled out of v1.x scope
(break-even, trailing-stop, session-close forced-exit, dual-timeframe bias
confirmation — all deferred to v2.x, none applied to the frozen funnel),
and 2 still pending (R-03 low-liquidity filter definition, R-18 existence
check floor — R-18 now unblocked by this milestone).

The owner opened A2/S1-G2 on 2026-07-26 with the scope stated above. This
milestone authorizes assembling a scoped ST-C3 reference funnel for
golden/negative-case testing and existence-check research — it does NOT
authorize execution, optimization, A3 opening, demo, live, or production
work, which all remain blocked pending their own separate, future owner
decisions.

## Current Evidence

- ST-C3 active frozen spec: `specs/st-c3_v1.0.1.yaml` (revision of
  `specs/st-c3_v1.0.0.yaml`, preserved unchanged as historical record).
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

## Acceptance Criteria (S1-G1C — met; A2/S1-G2 — scoped and open)

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

## Guardrails

- Do not modify frozen ST-C3 strategy logic except through a new
  governance-approved revision or candidate lineage.
- Do not modify `specs/st-c2_v1.2.0.yaml`.
- `engine_implements_spec` may become `true` only once a reference funnel
  actually exists under the A2/S1-G2 scope below; `implementation_authorization`
  is now `scoped_reference_implementation_granted` (owner directive,
  2026-07-26) — not full/unscoped authorization.
- A2/S1-G2's scope is exactly what's listed in
  `governance/st_c3_stage_status.yaml` `a2_signal_conformance.opened` —
  execution, optimization, A3 opening, demo, and live are explicitly not
  authorized by this milestone and each require their own future, separate
  owner decision.

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
