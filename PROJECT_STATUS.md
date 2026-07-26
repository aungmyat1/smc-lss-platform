# PROJECT_STATUS.md - SMC-LSS Platform

**Audit date:** 2026-07-26
**Governance model:** `MASTER_PLAN.md` v4.1.2 Stage A/Stage B validation architecture
**Current lifecycle position:** Stage A - Strategy Validation, A2 / S1-G2 -
ST-C3 Reference Implementation Authorization PASSED (owner decision, 2026-07-26)

This file records current gate state, evidence, blockers, and metrics. It is
subordinate to `MASTER_PLAN.md` and should not duplicate the full lifecycle
rules.

---

## Current State

| Field | State |
|---|---|
| Stage | Stage A - Strategy Validation |
| Substage | A2 - Indicator, Event and Signal Conformance |
| Gate | S1-G2 Reference Implementation Authorization |
| Strategy | ST-C3 v1.0.6 (evidence-builder Tier 3 gap resolution, revision of v1.0.5, itself a structural-detection algorithm parameter revision of v1.0.4, itself an instrument tie-breaking revision of v1.0.3, itself a fixed-lot + instrument-scope revision of v1.0.2, itself a governance parameter-freeze revision of v1.0.1, itself a revision of v1.0.0) |
| Status | FROZEN -> S1-G1C CLOSED -> A2/S1-G2 PASSED (owner decision, 2026-07-26) |
| Readiness | GREEN |
| Frozen | YES |
| Implementation | S1-G2 scoped reference implementation complete |
| Backtest | BLOCKED (historical_baseline is A3/S1-G7) |
| A1 Logic Conformance | PASSED — `reports/validation/st_c3/S1-G1C_RERUN_REPORT.md` |
| A2 Signal Conformance | PASSED — owner decision 2026-07-26, see `reports/validation/st_c3/OWNER_DECISION_LOG.md`, "A2/S1-G2 gate closure" entry |
| A3 Statistical Validation | BLOCKED: opening A3 is a separate, distinct future owner decision, not yet made |
| Execution | BLOCKED (explicitly not authorized) |
| Demo | BLOCKED |
| Production | BLOCKED |

ST-C3 v1.0.0 was frozen by owner-approved S1-G1 action. The S1-G1C audit
against v1.0.0 found three tracked rejection-code findings (R-1, R-2, R-3);
a governance review found one additional migration-scope gap (GR-1); the
owner approved a patch recommendation on 2026-07-25; `specs/st-c3_v1.0.1.yaml`
was cut with exactly those fixes (v1.0.0 preserved unchanged as historical
record); and the S1-G1C structural checks were re-run clean against v1.0.1
with zero critical/major findings. Specification Closure then resolved all
33 tracked parameter fields (owner decisions logged in
`reports/validation/st_c3/OWNER_DECISION_LOG.md`), with 2 explicitly
deferred to a possible v2.x cycle (later separately decided as R-21/R-22)
and 4 proposed architecture changes ruled out of v1.x scope (none applied
to the frozen funnel). On 2026-07-26 the owner opened A2/S1-G2 with an
explicitly scoped authorization (reference-funnel assembly, golden/negative-case
tests, existence-check research), and — once that scoped work was complete,
spec `v1.0.6` was frozen, and R-18's existence-check floor was computed
against real GBPUSD data (`signal_rate=0.0`) — declared **A2/S1-G2 PASSED**
the same day. This closure still does **not** authorize execution,
optimization, A3 opening, demo, or live — each remains a separate, future
owner decision. See `governance/st_c3_stage_status.yaml`
`a2_signal_conformance` for the authoritative record. ST-C2 v1.2.0 remains
preserved as the frozen GBPUSD-scoped specification with its own S1-G2
open, but new ST-C2 work is paused by owner direction. None of this
approves, rejects, mutates, supersedes, or executes ST-C2.

---

## Objective

S1-G1C logic conformance is complete for ST-C3 (v1.0.1). Specification
Closure resolved all tracked parameter fields (33/33 decided, R-01–R-33).
A2/S1-G2 was opened with a scoped authorization (build a reference funnel
for golden/negative-case testing and existence-check research), that
scoped work completed with spec `v1.0.6` frozen and R-18's existence-check
floor computed, and the owner declared **A2/S1-G2 PASSED** on 2026-07-26 —
still without execution, optimization, backtesting/historical baseline,
broker integration, demo trading, live trading, A3 opening, or production,
each of which remains its own separate future owner decision.

Current path:

```text
ST-C3 v1.0.0 frozen specification
-> S1-G1C logic-conformance closure (DONE, closed as v1.0.1)
-> Specification Closure (DONE: 33/33 decided, R-01-R-33, 2 deferred-then-decided, 4 ruled out of v1.x scope)
-> S1-G2 scoped reference implementation authorization (PASSED, owner decision 2026-07-26)
-> A2/S1-G3-S1-G6 conformance qualification (satisfied within S1-G2 scope; gate declared PASSED)
-> A3/S1-G7-S1-G10 statistical edge and robustness qualification (BLOCKED — opening A3 not authorized)
-> Stage B execution qualification (BLOCKED)
```

---

## Evidence On Record

ST-C3 evidence:

- `docs/strategy/st_c3/ST-C3_FREEZE_ACTION_LOG.md` - S1-G1 freeze action log.
- `docs/strategy/st_c3/ST-C3_WORKTREE_CHECKPOINT.md` - freeze checkpoint.
- `specs/st-c3_v1.0.0.yaml` - original frozen candidate specification (preserved
  unchanged as historical record).
- `specs/st-c3_v1.0.1.yaml` - active frozen specification; rejection-code-layer
  revision closing R-1/R-2/R-3/GR-1.
- `reports/validation/st_c3/ST-C3_S1-G1C_LOGIC_CONFORMANCE_REPORT.md` - S1-G1C
  audit against v1.0.0.
- `reports/validation/st_c3/ST-C3_v1.0.1_PATCH_RECOMMENDATION.md` - patch
  recommendation for R-1/R-2/R-3.
- `reports/validation/st_c3/GOVERNANCE_REVIEW_REPORT.md` - technical review of
  the patch recommendation; found GR-1.
- `reports/validation/st_c3/S1-G1C_RERUN_REPORT.md` - S1-G1C rerun against
  v1.0.1; PASS, zero critical/major findings.
- `governance/st_c3_stage_status.yaml` - machine-readable stage-status tracking,
  including the A2/S1-G2 opening decision and its exact scope.
- `reports/validation/st_c3/RESOLUTION_MATRIX.md`,
  `DEPENDENCY_GRAPH.md`, `DECISION_PACKAGES.md`,
  `OWNER_DECISION_LOG.md`, `SPECIFICATION_CLOSURE_REPORT.md`,
  `R04_R06_RESEARCH_REPORT.md` - Specification Closure artifacts (21/26
  fields decided, 2 deferred, 2 pending: R-03, R-18).
- `docs/strategy/st_c3/ST-C3_FREEZE_CHECKLIST.md` - freeze checklist.
- `docs/strategy/st_c3/ST-C3_STRATEGY_ARCHITECTURE.md` - foundation architecture.
- `docs/strategy/st_c3/ST-C3_FUNNEL_LIFECYCLE.md` - ordered funnel lifecycle.
- `docs/strategy/st_c3/ST-C3_EVIDENCE_OBJECT_SPEC.md` - evidence object contract.
- `docs/strategy/st_c3/ST-C3_REJECTION_CODE_SPEC.md` - rejection and error codes.
- `docs/strategy/st_c3/ST-C3_PARAMETER_SHEET.md` - parameter sheet.
- `docs/strategy/st_c3/ST-C3_STATE_MACHINE.md` - deterministic state-machine
  blueprint.
- `docs/strategy/st_c3/ST-C3_EVIDENCE_BINDINGS.md` - state-to-evidence binding
  contract.
- `docs/strategy/st_c3/ST-C3_TRADE_PLAN_SCHEMA.md` - canonical S13 trade-plan
  object schema.
- `docs/strategy/st_c3/ST-C3_VALIDATOR_RULES.md` - deterministic validator
  enforcement contract.
- `docs/strategy/st_c3/ST-C3_EXECUTION_AGENT_SPEC.md` - proposed Stage B
  execution-agent contract; no execution authority.
- `docs/strategy/st_c3/ST-C3_BACKTEST_SPEC.md` - A3 planning specification;
  backtesting remains blocked.
- `docs/adr/ADR-0004-st-c3-candidate-intake.md` - accepted intake ADR.
- `reports/research_log.md` - ST-C3 RCR/intake entry.
- `reports/validation/st_c3/S1-G2_REFERENCE_FUNNEL_REPORT.md` - A2/S1-G2
  reference-funnel deliverable: deterministic evidence-to-trade-plan
  validator kernel (`validation/st_c3/`), golden/negative-case tests, and
  existence-check readiness (`tests/st_c3/`, 20/20 passing). Does not
  include real price-bar SMC detection modules — see report for the
  frozen-spec-vs-OWNER_DECISION_LOG scope boundary (now partially closed by
  the v1.0.2 revision below).
- `specs/st-c3_v1.0.2.yaml` / `reports/governance/st_c3/RCR_ST-C3_v1.0.2_REPORT.md`
  / `docs/strategy/st_c3/ST-C3_CHANGELOG.md` - governance parameter-freeze
  revision folding in 22 owner-decided fields (R-01 through R-26 minus
  R-11/R-18/R-21/R-22, plus both resolved Open Conflicts). No structural
  (evidence/state/guard/code) change.
- `specs/st-c3_v1.0.3.yaml` / `reports/governance/st_c3/RCR_ST-C3_v1.0.3_REPORT.md`
  - decides R-21 (`fixed_lot_size`=0.01) and revises R-02 (`instruments`
  narrowed to EURUSD/GBPUSD); corrects a submission mislabeled "R-22" (that
  field is unrelated).
- `specs/st-c3_v1.0.4.yaml` / `reports/governance/st_c3/RCR_ST-C3_v1.0.4_REPORT.md`
  - decides R-22 (`risk.instrument_tie_breaking_rule`: higher `computed_rr`
  wins between EURUSD/GBPUSD, EURUSD fallback on exact tie). Stage B /
  portfolio-level only, no execution code. R-18 is the only unresolved
  field of the original 26 tracked.
- `reports/validation/st_c3/R18_DETECTION_GAP_REPORT.md` (2026-07-26) -
  attempting to begin real R-18 price-level detection found a deeper gap:
  the structural-detection algorithms (swing/fractal lookback, BOS
  confirmation bars, FVG/OB identification, pullback definition) have no
  defined parameters anywhere. Tracked as new R-27 through R-30 in
  `RESOLUTION_MATRIX.md`. No code written, nothing invented or inherited
  from ST-C2.
- `reports/validation/st_c3/R27_R30_RESEARCH_REPORT.md` - empirical
  distribution analysis (GBPUSD H4/M15) producing tradeoff curves for
  R-27/R-28/R-30 and a candidate range for R-29's FVG half; R-29's OB half
  needed no new number (`smc_engine.order_blocks()` already structural).
- `specs/st-c3_v1.0.5.yaml` / `reports/governance/st_c3/RCR_ST-C3_v1.0.5_REPORT.md`
  - owner ratified all four: R-27 k=2, R-28 N=2, R-29 (FVG) 0.15x
  MF_ATR(1), R-30 0.30x ATR(1). **Every field on the R-01-R-30 tracker is
  now decided except R-18**, which needs only real detection-module code
  and a data run, not a further spec decision.
- `specs/st-c3_v1.0.6.yaml` / `reports/governance/st_c3/RCR_ST-C3_v1.0.6_REPORT.md`
  - resolves R-31 (`sweep_reclaim_max_bars`=2), R-32 (`entry_window_bars`=4),
  R-33 (session UTC bounds ratified) — the Tier 3 evidence-builder gap found
  while scoping `build_evidence_bundle()`. `validation/st_c3/evidence_builder.py`
  (442 lines, all 15 evidence types) built and run against real GBPUSD
  H4/M15/M3 data via `validation/run_st_c3_existence_check.py`: **R-18
  resolved, `signal_rate=0.0`** over 3,339 M15 bars (2026-06-05 ->
  2026-07-24) — see `reports/validation/st_c3/R18_EXISTENCE_CHECK_RESULTS.md`.
  Every field on the R-01-R-33 tracker is now resolved. Owner declared
  **A2/S1-G2 PASSED** the same day — see
  `reports/validation/st_c3/OWNER_DECISION_LOG.md`, "A2/S1-G2 gate
  closure" entry, and `governance/st_c3_stage_status.yaml`
  `a2_signal_conformance`.

---

## Blockers

S1-G1C blockers: none remaining — closed as v1.0.1, see
`reports/validation/st_c3/S1-G1C_RERUN_REPORT.md`.

S1-G2 blockers: none remaining — A2/S1-G2 declared PASSED by owner
decision, 2026-07-26. All 33 tracked fields (R-01–R-33) resolved,
including R-18 (`existence_check_floor`, computed against real GBPUSD
data) and R-03 (`sessions.low_liquidity_filters`, decided via the
v1.0.2 governance parameter-freeze directive).

Stage A3 / Stage B blockers (unaffected by A2/S1-G2 closure):

- A3 opening itself is explicitly not authorized by the A2/S1-G2 closure
  decision — requires its own separate future owner decision.
- No backtest, historical baseline, broker integration, demo path, live
  path, or production path exists or is authorized.
- ST-C3 backtest specification exists as planning material only; backtest
  execution remains blocked until A3 is separately authorized.

---

## Next Action

A2/S1-G2 is closed. The reference funnel (evidence-to-trade-plan validator
kernel plus real price-level detection via
`validation/st_c3/evidence_builder.py`, all 15 evidence types), golden-case
tests, negative-case tests, and the R-18 existence-check run are complete
— see `reports/validation/st_c3/S1-G2_REFERENCE_FUNNEL_REPORT.md` and
`reports/validation/st_c3/R18_EXISTENCE_CHECK_RESULTS.md`. `specs/st-c3_v1.0.2.yaml`
through `v1.0.6.yaml` have frozen every numeric parameter on the R-01–R-33
tracker: detection *filter* thresholds, sizing/instrument-scope values,
instrument tie-breaking rule, structural-detection *algorithm* parameters
(swing/fractal `k`=2, BOS confirmation `N`=2, FVG min gap=0.15x MF_ATR(1),
pullback depth=0.30x ATR(1)), and the evidence-builder Tier 3 values
(`sweep_reclaim_max_bars`=2, `entry_window_bars`=4, session UTC bounds).
Every field is resolved, and R-18's existence-check floor produced
`signal_rate=0.0` over a 3,339-bar GBPUSD H4/M15/M3 window — a real data
point, not a strategy-level verdict (see the results report for caveats).
**Awaiting a separate owner decision on whether to open A3.** Do not
authorize execution, optimization, backtesting, broker integration, demo,
live, or A3 opening until their own separate owner decisions permit them.

---

## Levers Track Progress (separate from ST-C3, opened 2026-07-25)

| Lever | Description | Status | Governance Gate |
|---|---|---|---|
| A | Existence-check tool (cheap-before-expensive falsification) | Complete — `tools/existence_check.py`, tested | Closed |
| B | Power-planning / sample-size pre-registration helper | Complete — `tools/power_planning.py`, tested | Closed |
| C | Engine collapse / STRATEGY_OF_RECORD unification | Not started — pending RCR | Blocked |
| D | Shared feature/structure-shift primitives | Not started this session — already substantially covered by existing `src/features.py`; further refactor of `signal_v35.py`/`live_signal.py` needs its own RCR | Open |
| E | Parallel batch validation runner | Not started this session — already substantially covered by existing `validation/batch_validation_runner.py` (resumable/cached, sequential); true parallelization not implemented | Open |
| F | A2-closure gate enforcement | Complete — `scripts/check_a2_closure.py`, tested, verified against the real `A2_RULE_COVERAGE_MATRIX.json` | Closed |

Summary: A/B/F implemented and tested this session. C is blocked pending
RCR authorization — it changes which engine's decisions are authoritative
for live/backtest routing, a detection-logic-governing change under
`docs/RESEARCH-CHARTER.md`, not infrastructure. D and E remain open but
unstarted this session, since existing code already substantially addresses
their stated goal; touching the live detection modules they'd otherwise
refactor carries the same RCR requirement as C. No demo or live trading is
permitted on account of any of this work — no execution layer exists, and
no A2/A3 evidence exists for ST-C2 or ST-C3.
