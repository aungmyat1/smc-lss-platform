# NEXT_ACTION.md

**One milestone at a time. This is the active governance milestone.**

## S1-G2 - ST-C2 Reference Implementation Authorization

Current lifecycle position:

| Field | State |
|---|---|
| Stage | Strategy Validation |
| Gate | S1-G2 Reference Implementation |
| Strategy | ST-C2 v1.1.0 |
| Status | Frozen |
| Readiness | GREEN |
| Frozen | YES |
| Implementation | BLOCKED |
| Historical Validation | BLOCKED |
| Execution | BLOCKED |
| Demo | BLOCKED |
| Production | BLOCKED |

## Objective

Decide whether to grant scoped reference implementation authorization for frozen
`specs/st-c2_v1.1.0.yaml`.

This is not execution authorization.

## Proposed First Scope

If authorization is granted, the first implementation scope is limited to:

- golden-case tests
- conformance kernel as research code
- minimum XAUUSD detector slice
- existence-check run

Forbidden in this milestone:

- MT5
- broker adapter
- execution layer
- order management
- live trading
- risk execution pipeline

## Evidence To Review

- `specs/st-c2_v1.1.0.yaml`
- `reports/ST-C2_SPEC_AUDIT.md`
- `reports/ST-C2_IMPLEMENTATION_READINESS.md`
- `reports/audit/ST_C2_HYBRID_LIQUIDITY_FIRST_RCR.md`
- `reports/research_log.md`

## Acceptance Criteria

- Scoped authorization is either granted or denied explicitly.
- Decision is recorded in ADR/RCR/research-log documentation.
- If granted, implementation scope is limited to Stage 1 reference artifacts.
- Execution, demo, live, broker, and production authority remain blocked.

## Out Of Scope

- Strategy redesign
- YAML parameter changes
- MT5 or broker integration
- Demo or live trading
- Production promotion
