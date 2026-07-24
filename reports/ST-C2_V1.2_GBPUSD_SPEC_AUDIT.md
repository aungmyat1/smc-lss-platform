# ST-C2 v1.2.0 GBPUSD Specification Audit

**Date:** 2026-07-24
**Scope:** S1-G1 review of `specs/st-c2_v1.2.0.yaml`, created by owner
instruction to use GBPUSD as the default symbol. Documentation/spec governance
only; no implementation, backtest, execution, demo, live, or production work.

## Verdict

**S1-G1 STATUS: READY TO FREEZE**

The GBPUSD candidate is correctly filed as a new candidate version instead of
mutating frozen ST-C2 v1.1.0, and the basic symbol/cost switch is mechanically
clear:

- GBPUSD enabled.
- XAUUSD and EURUSD disabled.
- G8 cost row points to `config/research_costs.yaml` -> `GBPUSD`.
- `engine_implements_spec: false`.
- `implementation_authorization: null`.

The initial audit found several XAUUSD-derived thresholds that were
instrument-scale sensitive. The follow-up S1-G1 decision closes that issue
conservatively: inherit the thresholds unchanged as **PROVISIONAL** for the
first GBPUSD reference implementation and existence check only. This makes the
spec deterministic enough to freeze without pretending those values are
statistically validated for GBPUSD.

## Closed S1-G1 Items

1. **GBPUSD threshold portability**
   - `min_stop_distance_points: 35`
   - `max_stop_distance_points: 150`
   - `invalidation_buffer_distance_points: 2.5`
   - `spread_spike_points: 20`

   Decision: inherited unchanged as **PROVISIONAL** for GBPUSD. These values are
   sufficient for S1-G2 reference implementation and existence checking, but
   they are not production-validated and may require a future RCR if validation
   shows instrument-scale distortion.

2. **GBPUSD existence-check criterion**
   Decision: accepted. The first S1-G2 existence check is `>=1 qualifying
   GBPUSD signal across available local history`.

3. **GBPUSD population-feasibility wording**
   - `population_feasibility_floor: 30` remains in the spec.
   Decision: deferred beyond the first existence check. The initial S1-G2 scope
   is golden cases, conformance kernel, minimum GBPUSD detector slice, and
   existence check. Population-feasibility is a later validation question.

## Non-Blocking Notes

- GBPUSD cost profile exists: spread 25.0 points, slippage 3.0 points,
  commission 0.0.
- No source code, validation code, tests, execution config, demo state, or live
  state was changed.
- ST-C2 v1.1.0 remains preserved as the prior frozen XAUUSD-scoped
  specification.

## Freeze Decision

ST-C2 v1.2.0 is eligible for freeze with the provisional GBPUSD threshold
decisions above. Freezing v1.2.0 does not authorize implementation, execution,
demo, live, broker, or production work.

## Authorization Update

S1-G2 scoped reference implementation authorization was granted after freeze for
golden-case tests, conformance kernel, minimum GBPUSD detector slice, and the
GBPUSD existence-check run only. Execution, demo, live, broker, production, and
strategy redesign remain blocked.
