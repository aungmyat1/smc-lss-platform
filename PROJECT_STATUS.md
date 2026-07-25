# PROJECT_STATUS.md - SMC-LSS Platform

**Audit date:** 2026-07-25
**Governance model:** `MASTER_PLAN.md` v4.1.2 Stage A/Stage B validation architecture
**Current lifecycle position:** Stage A - Strategy Validation, A1 / S1-G1C -
ST-C3 Logic-Conformance CLOSED (v1.0.1)

This file records current gate state, evidence, blockers, and metrics. It is
subordinate to `MASTER_PLAN.md` and should not duplicate the full lifecycle
rules.

---

## Current State

| Field | State |
|---|---|
| Stage | Stage A - Strategy Validation |
| Substage | A1 - Strategy Logic Contract and Conformance |
| Gate | S1-G1C Logic-Conformance Closure |
| Strategy | ST-C3 v1.0.1 (revision of v1.0.0) |
| Status | FROZEN -> S1-G1C CLOSED |
| Readiness | GREEN |
| Frozen | YES |
| Implementation | BLOCKED |
| Backtest | BLOCKED |
| A1 Logic Conformance | PASSED — `reports/validation/st_c3/S1-G1C_RERUN_REPORT.md` |
| A2 Signal Conformance | BLOCKED: S1-G2 not yet opened as a milestone |
| A3 Statistical Validation | BLOCKED: A2 NOT PASSED |
| Execution | BLOCKED |
| Demo | BLOCKED |
| Production | BLOCKED |

ST-C3 v1.0.0 was frozen by owner-approved S1-G1 action. The S1-G1C audit
against v1.0.0 found three tracked rejection-code findings (R-1, R-2, R-3);
a governance review found one additional migration-scope gap (GR-1); the
owner approved a patch recommendation on 2026-07-25; `specs/st-c3_v1.0.1.yaml`
was cut with exactly those fixes (v1.0.0 preserved unchanged as historical
record); and the S1-G1C structural checks were re-run clean against v1.0.1
with zero critical/major findings. ST-C2 v1.2.0 remains preserved as the
frozen GBPUSD-scoped specification with S1-G2 open, but new ST-C2 work is
paused by owner direction. Neither the ST-C3 freeze nor this revision
approves, rejects, mutates, supersedes, or executes ST-C2.

---

## Objective

S1-G1C logic conformance and validation planning is complete for ST-C3
(v1.0.1). Remaining work before A2 opens: an explicit owner decision to open
S1-G2, still without implementation, backtesting, broker integration, demo
trading, live trading, or production.

Current path:

```text
ST-C3 v1.0.0 frozen specification
-> S1-G1C logic-conformance closure (DONE, closed as v1.0.1)
-> S1-G2 scoped reference implementation authorization and completion review (awaiting owner decision to open)
-> A2/S1-G3-S1-G6 conformance qualification
-> A3/S1-G7-S1-G10 statistical edge and robustness qualification
-> Stage B execution qualification
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
- `governance/st_c3_stage_status.yaml` - machine-readable stage-status tracking.
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

---

## Blockers

S1-G1C blockers: none remaining — closed as v1.0.1, see
`reports/validation/st_c3/S1-G1C_RERUN_REPORT.md`.

Stage A2 / A3 / Stage B blockers:

- S1-G2 (Reference Implementation Authorization) has not been opened as a
  milestone; requires its own explicit owner decision and `NEXT_ACTION.md`
  update.
- No ST-C3 reference kernel, golden-case library, existence scanner, backtest,
  broker integration, demo path, live path, or production path exists or is
  authorized.
- ST-C3 backtest specification exists as planning material only; backtest
  execution is blocked until A2 passes and A3 is authorized.

---

## Next Action

Await owner decision on opening ST-C3 A2/S1-G2. Do not authorize
implementation, backtesting, broker integration, demo, live, or production
until later gates explicitly permit them.

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
