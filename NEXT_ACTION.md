# NEXT_ACTION.md

**One milestone at a time. This is the active milestone.**

## ST-C3 S1-G1 Preparation - Owner Review and Freeze Readiness

Current lifecycle position:

| Field | State |
|---|---|
| Stage | Stage A - Strategy Validation |
| Substage | A1 - Strategy Logic Contract and Conformance |
| Gate | Pre-S1-G1 Owner Review / Specification Freeze Preparation |
| Strategy | ST-C3 v1.0.0 |
| Status | Draft |
| Readiness | YELLOW |
| Frozen | NO |
| Implementation | BLOCKED |
| Backtest | BLOCKED |
| A1 Logic Conformance | NOT STARTED |
| A2 Signal Conformance | BLOCKED: S1-G1 NOT PASSED |
| A3 Statistical Validation | BLOCKED: A2 NOT PASSED |
| Execution | BLOCKED |
| Demo | BLOCKED |
| Production | BLOCKED |

## Objective

Prepare ST-C3 for its own S1-G1 specification-freeze decision without changing
ST-C2, implementing ST-C3, running backtests, or granting execution authority.

## Current Evidence

- ST-C3 intake ADR:
  `docs/adr/ADR-0004-st-c3-candidate-intake.md`.
- ST-C3 draft spec:
  `specs/st-c3_v1.0.0.yaml`.
- ST-C3 funnel overhaul plan:
  `reports/ST-C3_FUNNEL_OVERHAUL_PLAN.md`.
- ST-C3 foundation documents:
  `docs/strategy/st_c3/ST-C3_STRATEGY_ARCHITECTURE.md`,
  `docs/strategy/st_c3/ST-C3_FUNNEL_LIFECYCLE.md`,
  `docs/strategy/st_c3/ST-C3_EVIDENCE_OBJECT_SPEC.md`, and
  `docs/strategy/st_c3/ST-C3_REJECTION_CODE_SPEC.md`.
- ST-C3 parameter sheet:
  `docs/strategy/st_c3/ST-C3_PARAMETER_SHEET.md`.
- ST-C3 state machine:
  `docs/strategy/st_c3/ST-C3_STATE_MACHINE.md`.
- ST-C3 RCR/intake entry:
  `reports/research_log.md`.
- Source reference documents:
  `docs/reference/smc-definitive-guide-dailypriceaction.md` and
  `docs/reference/smc-8step-entry-model-dailypriceaction.md`.

## Acceptance Criteria

- Confirm or correct the provisional thresholds in
  `reports/ST-C3_FUNNEL_OVERHAUL_PLAN.md` section 16.
- Confirm or correct the risk envelope described in the plan and represented
  as unresolved fields in `specs/st-c3_v1.0.0.yaml`.
- Confirm or correct the `F1`/`F2`/`F3` relabeling from ADR-0004.
- Confirm whether the six proposed agent roles should be formalized by
  ADR-0005 before S1-G1 freeze.
- Resolve all `UNRESOLVED` fields required for S1-G1 freeze readiness.
- Keep the four ST-C3 foundation documents aligned with the draft spec and
  funnel overhaul plan.
- Keep the ST-C3 state machine aligned with lifecycle, evidence, rejection,
  termination, and trade-plan contracts.
- Prepare the S1-G1 audit package, but do not freeze the spec until the owner
  explicitly approves the freeze act.

## Blocking Gaps

- Symbol scope and session windows are unresolved.
- Sweep tolerance, wick-ratio, sweep age, `BOS_MIN_IMPULSE`, FVG/OB freshness,
  exact `N_SWEEP`, exact `MAX_ENTRY_BARS`, stop buffer, TP2/TP3 RR floors, and
  portfolio risk controls are unresolved or provisional.
- Validation metrics and floors are unresolved.
- Rejection-code coverage and session-close trigger policy still need S1-G1
  decisions.
- No ST-C3 reference kernel, golden-case tests, existence scanner, backtest,
  or execution integration exists or is authorized.

## Guardrails

- Do not modify `specs/st-c2_v1.2.0.yaml`.
- Do not continue ST-C2 S1-G2 implementation work under this milestone.
- Do not implement ST-C3 code, tests, kernels, broker integration, demo
  trading, live trading, or production paths.
- Keep ST-C3 `status: draft`, `engine_implements_spec: false`, and
  `implementation_authorization: null` until a separate S1-G1 freeze act
  authorizes a different state.
