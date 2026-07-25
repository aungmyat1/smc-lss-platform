# ST-C2 Architecture Contract

**Strategy:** ST-C2 v1.2.0 GBPUSD
**Canonical contract:** `specs/st_c2/st_c2_contract.yaml`
**Authority spec:** `specs/st-c2_v1.2.0.yaml`
**Governance stage:** A2 conformance, still open until every contract rule is implemented, tested, and traceable.

## Governance Position

This artifact does not change trading rules and does not authorize MT5 or
broker-facing execution work. It defines the conformance architecture needed to
prove the frozen ST-C2 specification matches the research implementation.

## Seven-Stage Funnel

| Stage | Purpose | Required Outputs | Failure Coverage | Metrics |
|---|---|---|---|---|
| Market Context | Determine HTF allowed direction from structural evidence. | bias, trend state, confidence, reason, bias evidence timestamp | R2 plus deterministic structure rejections | HTF bias accuracy, ambiguity count |
| Session Filter | Validate tradable London/New York conditions and session exits. | session valid, session name, reason | R6/R7, session config, DST/news exclusions | session acceptance and rejection rates |
| Market Structure LTF | Confirm LTF BOS/CHoCH/MSS alignment. | structure valid, trend state, reason, confirmation event ID | R5, internal BOS, close confirmation, setup expiry | BOS precision, CHoCH precision, swing accuracy |
| Liquidity | Select pools and confirm sweep/reclaim behavior. | liquidity event, type, sweep direction, confidence | R1, wick ratio, reclaim, age, tie-break failures | sweep accuracy, false positive rate |
| POI | Validate OTE, premium/discount, FVG chain, mitigation state. | POI valid, type, distance, strength, mitigation, FVG IDs | R3/R4, OTE, FVG, mitigation failures | detection precision, mitigation accuracy |
| Entry Confirmation | Approve closed-candle trigger and next-bar eligibility. | entry approved, trigger type, confidence, reason, invalidation swing, execution bar | R5, duplicate setup, expiry, next-bar timing | trigger success and false trigger rates |
| Risk Validation | Build the logical trade plan using existing SL/TP and risk rules. | trade approved, risk %, RR, SL, TP, reason, trade plan ID | R6, stop, target, net-R, cost, duplicate failures | invalid RR, invalid SL, duplicate prevention |

## Contract-To-Implementation Traceability

Every A2 rule appears exactly once in `st_c2_contract.yaml` under
`traceability`. Each entry declares:

- funnel stage
- component
- implementation symbol or explicit `null` for a known gap
- test references
- validation metric
- conformance status

The CI guardrail is intentionally strict about drift and intentionally honest
about incompleteness. A rule may remain incomplete only if its contract status
states that fact; implemented rules must point to importable code and at least
one test.

## A2 Closure Criteria

A2 may close only when:

- every rule in `reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json` exists
  in the contract;
- every contract rule exists in the coverage matrix;
- every implemented rule has an importable implementation mapping;
- every implemented rule has at least one test;
- every rule has a validation metric;
- output-shape and failure-code conformance tests pass;
- no MT5, broker, order-routing, or live execution module is introduced.

## Current Known Gaps

The contract records existing gaps as conformance statuses such as
`not_implemented`, `implemented_missing_tests`, `partial_missing_tests`, and
`partial_tested`. Those statuses are not A2 closure; they are the traceable work
queue required before statistical validation can unlock.
