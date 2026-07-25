# NEXT_ACTION.md

**One milestone at a time. This is the active milestone.**

## ST-C3 S1-G1C Logic-Conformance Preparation

Current lifecycle position:

| Field | State |
|---|---|
| Stage | Stage A - Strategy Validation |
| Substage | A1 - Strategy Logic Contract and Conformance |
| Gate | S1-G1C Logic-Conformance Preparation |
| Strategy | ST-C3 v1.0.0 |
| Status | FROZEN -> READY FOR VALIDATION |
| Readiness | GREEN |
| Frozen | YES |
| Implementation | BLOCKED |
| Backtest | BLOCKED |
| A1 Logic Conformance | NOT STARTED: NEXT ACTIVE WORK |
| A2 Signal Conformance | BLOCKED: S1-G1C NOT PASSED |
| A3 Statistical Validation | BLOCKED: A2 NOT PASSED |
| Execution | BLOCKED |
| Demo | BLOCKED |
| Production | BLOCKED |

## Objective

Begin ST-C3 S1-G1C logic-conformance preparation against the frozen v1.0.0
strategy package without implementing kernels, running backtests, or granting
execution authority.

## Current Evidence

- ST-C3 frozen spec: `specs/st-c3_v1.0.0.yaml`.
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

## Acceptance Criteria

- Build an S1-G1C logic-conformance checklist for the frozen ST-C3 artifacts.
- Verify artifact cross-links and no dangling references.
- Verify YAML structural invariants: 16 evidence objects, 16 states, 16
  transitions, S13 evidence chain, R/ERR code maps, and blocked execution
  authority.
- Prepare a validation report outline for ST-C3 v1.0.0.
- Preserve `docs/strategy/st_c3/ST-C3_BACKTEST_SPEC.md` as A3 planning
  material only; do not run backtests until A2 passes and A3 is authorized.
- Do not implement ST-C3 code, kernels, scanners, backtests, broker adapters,
  demo, live, or production paths.

## Guardrails

- Do not modify frozen ST-C3 strategy logic except through a new
  governance-approved revision or candidate lineage.
- Do not modify `specs/st-c2_v1.2.0.yaml`.
- Keep ST-C3 `engine_implements_spec: false` and
  `implementation_authorization: null` until a later gate authorizes a
  different state.
