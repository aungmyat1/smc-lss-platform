# ST-C3 Determinism Report — Phase 2

**Consolidates** determinism findings already established by
`ST-C3_S1-G1C_LOGIC_CONFORMANCE_REPORT.md` §8 and the `S1-G1C_RERUN_REPORT.md`
re-verification against `specs/st-c3_v1.0.1.yaml`, rather than re-deriving
them from scratch — per this task's own "avoid duplicating completed work"
instruction. Where those reports already answered a question, this report
cites them directly; it only adds analysis they didn't already cover.

**Result: SPECIFICATION-LEVEL DETERMINISM CONFIRMED. IMPLEMENTATION-LEVEL
DETERMINISM CANNOT YET BE VERIFIED** (no code exists to test — see
"Scope Limitation" below).

---

## What "Determinism" Means at Two Different Levels

1. **Specification-level determinism** — does the *written spec* define, for
   each rule, a boolean/numeric condition with no fuzzy logic, confidence
   scores, or discretionary interpretation? This is answerable today by
   reading the spec.
2. **Implementation-level determinism** — given identical input candle data,
   does an actual detector/validator always produce identical output? This
   requires running code twice on the same input and diffing results. **No
   ST-C3 code exists** (`engine_implements_spec: false`, confirmed unchanged
   in v1.0.1) — this cannot be tested yet, and this report does not attempt
   to fabricate a result for it.

## Specification-Level Determinism — Per Rule Category

| Category | Guard/Definition | Deterministic? | Evidence |
|---|---|---|---|
| HTF bias | `HTFBiasEvidence.valid == true`, structure in `{HHHL, LHLL, UNCLEAR}` | YES | Boolean guard, enum-typed field, no probability. |
| Market structure (swings) | `structure_source: hh_hl_lh_ll` | YES | Same enum-typed evidence object. |
| Liquidity sweep | `SweepEvidence.valid == true` | YES (guard) / **PARTIAL** (content) | Guard is boolean, but `wick_ratio_min`/`equal_highs_lows_tolerance`/`max_sweep_age_bars` are `UNRESOLVED` (`SPECIFICATION_VALIDATION.md`) — the guard is deterministic in form, not yet in threshold. |
| CHoCH / BOS | `BOSEvidence.valid == true`, `bos_direction ∈ {UP, DOWN}`, `body_close_break: bool` | YES | Boolean guard and enum; body-close rule is unambiguous. |
| FVG | `FVGEvidence.valid == true`, `fresh: bool`, `inside_ote: bool` | YES (guard) / **PARTIAL** (content) | `freshness_definition: UNRESOLVED` — same class of gap as sweep. |
| Order Block | `OrderBlockEvidence.valid == true` | YES (guard) / **PARTIAL** (content) | Same freshness gap as FVG (shared `fvg_ob_confluence_stage.freshness_definition`). |
| Premium/Discount | `pd_zone` derived from `equilibrium_boundary: 0.5` vs. price | YES | Purely numeric comparison, no discretion — `0.5` itself is PROVISIONAL per Phase 1 but the *computation* is deterministic once ratified. |
| Entry trigger | `LTFConfirmationEvidence.valid == true AND sweep_local_liquidity == true` | YES | Boolean guard. |
| SL | `mode: structural_invalidation`, anchored to M3 swing that formed CHoCH | YES (form) / **PARTIAL** (content) | `buffer_points: UNRESOLVED` — anchor rule is deterministic, exact price is not yet fully computable. |
| TP | `TargetEvidence.valid == true`, `rr` field numeric | YES (form) / **PARTIAL** (content) | TP1 `rr_min: 3.0` is fixed; TP2/TP3 `rr_min: UNRESOLVED`. |
| Risk calculation | `computed_rr >= MIN_RR` | YES (guard) / **PARTIAL** (content) | `MIN_RR` is `CONFIGURABLE_PROVISIONAL_3R` (Phase 1); guard form is a plain numeric comparison. |
| Session filters | `SessionWindowEvidence.session IN {LONDON, NY}` | YES | Enum membership test, no discretion. |
| News filters | *(not present in spec)* | N/A | ST-C3's frozen spec does not define a news filter at all — not a determinism gap, an absent feature. Noted here since the task's Phase 2 checklist asked for it; it is out of scope for v1.0.1 rather than unresolved within it. |

## Guard-Level vs. Code-Level Determinism (rejection/termination codes)

Already fully verified in `S1-G1C_RERUN_REPORT.md` ("Determinism
Verification" section): guard-level determinism holds (every guard failure
emits exactly one code) and, as of v1.0.1's R-1/R-2/R-3 fixes, code-level
diagnostic distinguishability now also holds (every code's trigger list
uniquely identifies the guard(s) that emit it). Not re-verified here since
nothing about it changed between that rerun and this report.

## Determinism of the Overall Funnel

Already fully verified in the original S1-G1C audit §7-8 (funnel lifecycle,
state machine, evidence chain, trade-plan emission, expiry logic all
confirmed deterministic — forward-only state advancement, no re-entry, one
guard per state, single trade-plan emission point). Re-confirmed unchanged
by the S1-G1C rerun against v1.0.1, since the revision touched only
rejection-code labels, not guard logic or state transitions.

---

## Scope Limitation (why Phase 3 onward cannot proceed today)

Every "PARTIAL" row above traces back to a `Phase 1` `UNRESOLVED`/
`PROVISIONAL` field, not to a flaw in the guard logic itself. The guards
*as written* are already boolean and reproducible; what's missing is the
concrete threshold each guard would need to evaluate against real candle
data. This means:

- **Golden-case verification (Phase 3)** cannot produce a real "actual
  outcome" column — there is no code to run a golden case through, and even
  a hand-simulated walkthrough would have to invent values for the 19
  `UNRESOLVED` fields, which is not verification, it's silent spec
  authorship.
- **Historical replay (Phase 5)** and **statistical validation (Phase 6)**
  require exactly the reference implementation that A2/S1-G2 exists to
  authorize and scope — which remains **not opened**, by explicit owner
  decision, as of this session.

This report does not attempt Phases 3+ for this reason. See
`VALIDATION_PROGRESS.md` for the full phase-by-phase status and the
concrete blocker for each remaining phase.
