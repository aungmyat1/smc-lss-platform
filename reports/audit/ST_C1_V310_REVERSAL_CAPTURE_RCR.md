# Research Change Request — "Reversal Capture" preset v1 (E1 gap-reversal + M2 CHoCH shift)

Filed per `docs/RESEARCH-CHARTER.md` before any new backtest runs. Owner
supplied a fully specified parameter preset ("ST-C1 UPGRADE CONFIG v2")
directly, in the same mode `specs/v3.9.yaml`'s "Clean SMC" preset was
supplied — this RCR documents it before any code was written.

## Change: "ST-C1 Reversal Capture" parameter preset (spec version: v3.9 (parked as historical control) -> v3.10, contract v1.2.0 -> v1.3.0)
Date: 2026-07-22
Author: Claude (research agent), on behalf of owner-supplied preset

### Why
v3.9 ("Clean SMC") is structure-only: it takes E2/E3 continuation setups
with no check on whether the higher-timeframe trend agrees or disagrees
with the trade direction, and E1 (D1 gap reaction) is disabled outright.
The owner directed a new objective: capture **reversal** trades specifically
— price fills (at least partially) a D1 gap while the H4 trend still points
the other way, then a lower-timeframe CHoCH + displacement confirms supply
has flipped to demand (or vice versa) before entry. This is a materially
different trade thesis from v3.9's continuation-only design, not a parameter
tweak to it — hence a new spec version rather than an edit to
`specs/v3.9.yaml`, which remains an immutable candidate/control per this
repo's established versioning discipline (v3.9 itself was never an edit to
v3.6 for the same reason).

### Evidence
- `reports/audit/ST_C1_V39_POPULATION_ABLATION_SPEC.md`: v3.9 is
  continuation-only (E-trigger bias = trade direction always) and E1 is
  disabled entirely — no code path in this repository has ever captured a
  reversal-against-HTF-bias trade. This is a structural gap, not a
  previously-tested-and-rejected hypothesis.
- Owner-supplied parameter preset ("ST-C1 UPGRADE CONFIG v2", full YAML)
  is the direct specification for this change — reproduced verbatim in
  `specs/v3.10.yaml`.
- No prior backtest evidence exists for this exact design (unlike v3.9,
  which had the v3.7/v3.8 funnel diagnosis to react to) — **this is
  disclosed as a limitation, not concealed.** The "expected improvement"
  below is therefore a design intent, not a number derived from this
  repo's own prior backtest data.

### Hypothesis
Requiring (a) H4 trend-bias divergence from the D1 gap-reaction's own
direction, (b) a partial-fill tolerance (75-100% of the gap) rather than
full fill, (c) a 3-bar demand/supply-zone hold confirmation, (d) acceptance
of internal (not just external) liquidity sweeps for E3, and (e) an
auto-detected displacement direction feeding a dynamic, displacement-length-
scaled R:R target, will together identify genuine HTF-reversal setups that
v3.9's continuation-only design structurally cannot see — without
collapsing into noise, because the H4-divergence requirement and the
3-bar hold confirmation are themselves restrictive gates.

### Expected improvement
Stated before running anything, as design intent rather than a number
derived from prior data (see Evidence's disclosed limitation):
1. The engine produces at least one qualifying reversal signal on each of
   EURUSD/GBPUSD/XAUUSD's local history (a existence/non-triviality check,
   not a population-size claim — this preset's population-feasibility
   floor has not been separately precommitted here and should be, before
   any funnel result is treated as pass/fail).
2. `min_rr: 3.0` remains a hard floor; `dynamic_rr` only changes *how* the
   target is chosen (displacement-length-scaled) not the acceptance floor.
If no symbol produces a qualifying signal, the H4-divergence + 3-bar-hold
combination is REJECTED as too restrictive within this data window, to be
revisited via a targeted relaxation (same discipline as R2.1/the Clean SMC
line), not silently loosened.

### Success criteria
(a) Engine implements the full preset with point-in-time, no-look-ahead
detection and passing positive/negative/mirror tests; (b) `min_rr: 3.0`
enforced unchanged; (c) at least a qualitative existence check (>=1 signal
per symbol) — a full population-feasibility floor is deferred to a
follow-up RCR addendum once initial signal counts are observed, since none
was precommitted for this specific preset; (d) no fail-open or look-ahead
defect in the new H4-bias, gap-tolerance, zone-hold, internal-sweep, or
dynamic-R:R logic.

### Rollback criteria
- Zero qualifying signals across all three symbols -> REJECTED within this
  preset's exact parameters; report the funnel and escalate to the owner
  for parameter reconsideration rather than ad hoc loosening.
- Any fail-open/look-ahead defect found -> stop, fix, re-verify before any
  run is treated as evidence.
- If dynamic R:R produces targets that violate `min_rr: 3.0` net of cost on
  net-of-cost review -> flag explicitly, do not silently accept.

---
Logged to `reports/research_log.md` in date order alongside this entry, per
`docs/RESEARCH-CHARTER.md`. No backtest was run before this template was
filed. `specs/v3.10.yaml` and `strategies/candidates/ST-C1_v1.3.0.yaml` are
created as RESEARCH_CANDIDATE / candidate-only artifacts with
`engine_implements_spec: false` initially, flipped only after the engine
below is built and its dedicated tests pass — this RCR does not itself
constitute a backtest run or an ACCEPT verdict. `specs/v3.9.yaml` and
`ST-C1_v1.2.0.yaml` are retained unmodified as the immutable prior
candidate/control (its own open cost/quality question, logged in
`PROJECT_STATUS.md` §5, remains open and unresolved by this RCR).
