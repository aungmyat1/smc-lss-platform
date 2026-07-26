# PROJECT_STATUS.md - SMC-LSS Platform

**Audit date:** 2026-07-26
**Governance model:** `MASTER_PLAN.md` v4.1.2 Stage A/Stage B validation architecture
**Current lifecycle position:** Stage A - Strategy Validation, A2 / S1-G2 -
ST-C3 Reference Implementation Authorization OPEN (scoped)

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
| Strategy | ST-C3 v1.0.4 (instrument tie-breaking revision of v1.0.3, itself a fixed-lot + instrument-scope revision of v1.0.2, itself a governance parameter-freeze revision of v1.0.1, itself a revision of v1.0.0) |
| Status | FROZEN -> S1-G1C CLOSED -> A2/S1-G2 OPEN (scoped) |
| Readiness | GREEN |
| Frozen | YES |
| Implementation | AUTHORIZED: S1-G2 SCOPED RESEARCH/VALIDATION ONLY |
| Backtest | BLOCKED (historical_baseline is A3/S1-G7) |
| A1 Logic Conformance | PASSED — `reports/validation/st_c3/S1-G1C_RERUN_REPORT.md` |
| A2 Signal Conformance | IN PROGRESS — opened 2026-07-26 by owner directive, scoped |
| A3 Statistical Validation | BLOCKED: A2 NOT PASSED; A3 opening itself not authorized |
| Execution | BLOCKED (explicitly not authorized) |
| Demo | BLOCKED |
| Production | BLOCKED |

ST-C3 v1.0.0 was frozen by owner-approved S1-G1 action. The S1-G1C audit
against v1.0.0 found three tracked rejection-code findings (R-1, R-2, R-3);
a governance review found one additional migration-scope gap (GR-1); the
owner approved a patch recommendation on 2026-07-25; `specs/st-c3_v1.0.1.yaml`
was cut with exactly those fixes (v1.0.0 preserved unchanged as historical
record); and the S1-G1C structural checks were re-run clean against v1.0.1
with zero critical/major findings. Specification Closure then resolved 21
of 26 tracked parameter fields (owner decisions logged in
`reports/validation/st_c3/OWNER_DECISION_LOG.md`), deferred 2 to a possible
v2.x cycle, and ruled 4 proposed architecture changes out of v1.x scope
(none applied to the frozen funnel). On 2026-07-26 the owner opened
A2/S1-G2 with an explicitly scoped authorization: reference-funnel
assembly, golden/negative-case tests, and existence-check research —
**not** execution, optimization, A3 opening, demo, or live. See
`governance/st_c3_stage_status.yaml` `a2_signal_conformance.opened` for the
authoritative scope record. ST-C2 v1.2.0 remains preserved as the frozen
GBPUSD-scoped specification with its own S1-G2 open, but new ST-C2 work is
paused by owner direction. None of this approves, rejects, mutates,
supersedes, or executes ST-C2.

---

## Objective

S1-G1C logic conformance is complete for ST-C3 (v1.0.1). Specification
Closure resolved the great majority of tracked parameter fields (21/26
decided). A2/S1-G2 is now open with a scoped authorization: build a
reference funnel for golden/negative-case testing and existence-check
research — still without execution, optimization, backtesting/historical
baseline, broker integration, demo trading, live trading, A3 opening, or
production.

Current path:

```text
ST-C3 v1.0.0 frozen specification
-> S1-G1C logic-conformance closure (DONE, closed as v1.0.1)
-> Specification Closure (DONE: 21/26 decided, 2 deferred, 2 pending — R-03, R-18)
-> S1-G2 scoped reference implementation authorization (OPEN as of 2026-07-26, scoped to research/validation)
-> A2/S1-G3-S1-G6 conformance qualification (in progress within S1-G2 scope)
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
  portfolio-level only, no execution code. **R-18 is now the only
  unresolved field of 26 tracked.**

---

## Blockers

S1-G1C blockers: none remaining — closed as v1.0.1, see
`reports/validation/st_c3/S1-G1C_RERUN_REPORT.md`.

S1-G2 blockers: none remaining for the scoped authorization — opened
2026-07-26. R-18 (`existence_check_floor`) is now unblocked and may be
computed once a reference funnel exists; R-03 (`sessions.low_liquidity_filters`)
still needs an explicit low-liquidity-signature definition before it can
be researched.

Stage A3 / Stage B blockers (unaffected by A2/S1-G2 opening):

- A3 opening itself is explicitly not authorized by the current A2/S1-G2
  scope — requires its own separate future owner decision.
- No backtest, historical baseline, broker integration, demo path, live
  path, or production path exists or is authorized.
- ST-C3 backtest specification exists as planning material only; backtest
  execution remains blocked until A3 is separately authorized.

---

## Next Action

The reference funnel (evidence-to-trade-plan validator kernel), golden-case
tests, negative-case tests, and existence-check readiness are built and
passing — see `reports/validation/st_c3/S1-G2_REFERENCE_FUNNEL_REPORT.md`.
`specs/st-c3_v1.0.2.yaml` through `v1.0.4.yaml` have since frozen the
detection thresholds, sizing/instrument-scope values, and instrument
tie-breaking rule that were blocking. R-18 (existence-check floor) is now
the only unresolved field of 26 tracked. Remaining within A2/S1-G2 scope:
build real price-level detection modules against v1.0.4's now-frozen
thresholds (a distinct engineering task, not yet started), then run a real
R-18 existence-check pass against market data using those modules. Do not
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
