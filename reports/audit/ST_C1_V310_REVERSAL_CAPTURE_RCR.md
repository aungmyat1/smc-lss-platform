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

---

## Addendum (2026-07-22) — engine built, existence check result, a real data gap found and fixed

`src/signal_v310.py` and `validation/historical_replay_engine_v310.py` are
built; 14 dedicated tests pass (positive/negative/mirror for H4 bias, the
divergence gate's fail-closed RANGING behavior, E1/E2/E3, dynamic R:R,
cutoff-invariance, no-broker-import), plus 3 new tests for a new
`smc_engine.resample()` helper (see below). Full repository suite: 178
passed.

**A real bug was found and fixed while building fixtures**, per this
repo's established practice of constructing tests interactively against
the actual functions rather than by inspection alone: `_e1_trigger_reversal`
originally required `c["close"] > body_lo` in addition to the wick-ratio
check for a bullish reaction — since `body_lo == close` whenever a candle's
open equals its close (a doji), this silently excluded exactly the
textbook doji-rejection-candle case a gap-reaction reversal setup should
recognize. Fixed by removing the redundant condition; wick-ratio geometry
alone is now the sole discriminator, matching the same pattern already
established in `signal_v39.py`'s E2/E3 reaction logic.

**A real data gap was found and worked around, not silently absorbed into
a false result:** the first full-history existence-check attempt on
EURUSD (the only symbol with any H4 file at all) produced **zero trades
across the entire ~80k-bar M5 history**. Root cause: `data/EURUSD_H4.csv`
contains only 18 bars spanning 3 days, and GBPUSD/XAUUSD have no H4 file
whatsoever — so `trend_bias_h4_bars: 20`'s lookback window was empty for
the overwhelming majority of the replay period, and the divergence gate's
deliberate fail-closed-on-`RANGING` design (empty H4 window -> `RANGING`
bias -> gate always rejects) then correctly, but misleadingly, rejected
everything. **This was a data-availability confound, not evidence the
preset's parameters are over-restrictive** — reported as such rather than
either (a) silently accepting "zero trades -> REJECTED" per this RCR's own
rollback criterion (which would have been a false negative caused by
missing data, not the design), or (b) quietly loosening a parameter to
compensate. Fix: added `smc_engine.resample()` (aggregates N consecutive
candles, e.g. 4 H1 bars -> 1 H4 bar; new function, additive, does not
change any existing engine's behavior) to derive full-history H4 from the
already-available, full-history H1 series for all three symbols, rather
than fabricating H4 data or reporting a confounded null result as a clean
rejection.

### Existence-check result (H1-derived H4, full local history per symbol)

| Symbol | Trades |
|---|---|
| EURUSD | 135 |
| GBPUSD | 112 |
| XAUUSD | 120 |
| **Total** | **367** |

**Result: the existence-check success criterion (>=1 signal per symbol) is
cleared decisively** for all three symbols, once the H4 data gap is fixed.
This is population evidence, not yet cost/quality evidence — no gross/net
R, win rate, or profit factor was computed in this pass (deferred to a
follow-up run using the same cost model already validated for v3.9, before
any profitability claim). `engine_implements_spec` is left `false` in
`specs/v3.10.yaml` for now, matching this repo's conservative posture for
v3.9 at the equivalent stage (full engine built and tested, population/
existence evidence produced, but a full net-of-cost read not yet run).

### Next step
A population-feasibility floor was never precommitted for this preset (see
the RCR's disclosed limitation above); given the existence check clears so
decisively (367 total vs. an informal >=1 bar), the natural next step is
the same net-cost read already applied to v3.9 — computing gross_r/net_r/
profit factor per symbol via the existing, reused cost model — before any
comparison to v3.9's own open cost/quality question. Not run in this pass;
recorded as the immediate next milestone in `NEXT_ACTION.md`.
