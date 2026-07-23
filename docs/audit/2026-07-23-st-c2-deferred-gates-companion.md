# ST-C2 Deferred Gates — Companion to the Owner-Decision Brief (2026-07-23)

**Companion to:** `docs/audit/2026-07-23-st-c2-owner-decision-brief.md`, which scopes
today's session to three items (G4, G7, RCR pre-registration gaps). This document
covers the other **seven** open items from `reports/audit/ST_C2_GOVERNANCE_CONFORMANCE_AUDIT.md`'s
post-addendum consolidated blocker list, which the owner-decision brief does not
address.

**This document decides nothing and recommends nothing.** It exists only to (a)
restate each item's current status verbatim from the governance audit, (b) classify
whether the open residual looks closeable by checking an already-implemented,
tested convention elsewhere in this repo versus genuinely requiring a fresh owner
design choice, and (c) state plainly that all seven are deferred from today's
session. Where a classification below is "mixed," that reflects the actual
evidence — it is not forced into a false binary.

---

## 1. G1/G2 — HTF/external swing definition, external-vs-internal distinction, protected high/low lifecycle

**Status per audit:** PARTIAL — "same-bar BOS/CHoCH ambiguity closed; swing
definition + protected-structure lifecycle open."

**Classification: MIXED — narrower than originally drawn, corrected after checking
`specs/st-c2.yaml` directly.**
- The fractal-swing *algorithm itself* is real, tested, reusable code:
  `src/smc_engine.py:22` (`def swings(c, k=2)`), already reused across
  `liquidity_sweeps()`, `inducement()`, and the ST-C1 v3.7–v3.10 engines. Adopting
  this same *method* for ST-C2's swing detection is reasonably a verification-level
  question ("does ST-C2 intend the same fractal definition ST-C1 uses").
- BUT: `specs/st-c2.yaml` specifies **no fractal-confirmation parameter (`k`) for
  H4 at all** — the only related field is `liquidity_stage.lookback_bars_htf: 300`,
  which is a *search-window* size, not the fractal confirmation window. There is
  nothing in the spec to verify a chosen `k` against for H4. Whether H4 should use
  the same `k=2` baked into the existing LTF-oriented functions, or a different
  value suited to a 300-bar HTF window, is an **unstated parameter choice**, not a
  fact checkable by reading existing code. This part **needs owner input**, same as
  the swing-lifecycle question below — my original wording collapsed this into
  "verification" by conflating the search-window field with the confirmation-window
  parameter; corrected here.
- "External vs internal swing distinction" and "protected-structure lifecycle"
  (when a protected high/low stops being protected) have **no existing
  implementation** — `swings()` returns raw fractal points only, with no
  external/internal tagging or lifecycle tracking anywhere in the codebase. This
  part **needs owner judgment**.

---

## 2. G2 — stable identifier / tie-break field composition

**Status per audit:** part of the same G2 PARTIAL row — "pool selection/tie-break
closed; internal/external distinction + identifier composition open."

**Classification: leans engineering verification.**
Directly confirmed in code, not just from `NEXT_ACTION.md`'s account: both
`validation/historical_replay_engine_v39.py:232` and
`historical_replay_engine_v310.py:189` pass `index_offset=m5_window_start` into
`analyze()`, and both derive `structure_key = str(result.get("structure_key"))`
(`v39.py:255`, `v310.py:211`), then use it for dedup (`v39.py:414,418`:
`if signal.structure_key in consumed: ... consumed.add(signal.structure_key)`).
This is a real, bug-fixed, currently-operating identifier convention, not just a
historical note — giving ST-C2 a concrete scheme to check against rather than
designing a new one. Residual risk: confirming the fix generalizes to ST-C2's
different stage structure (H4/M15/M3 vs. ST-C1's H4/H1/M5) is a verification task,
not fresh design — unless that check finds it doesn't fit, in which case this
would need owner input after all.

---

## 3. G3 — wick-probe-rejection mechanics; first-break-vs-later-shift distinction

**Status per audit:** PARTIAL — "BOS/CHoCH classification boundary closed;
wick-probe mechanics + multi-CHoCH sequencing open."

**Classification: leans engineering verification.**
Two rules already exist at the skill/spec level, not just as audit notes:
- `.claude/skills/choch-bos/SKILL.md` (read this session): "Wick-only break =
  unconfirmed" and "Require candle close beyond level (not just wick)" — directly
  answers "wick-probe rejection" as a rule, already implemented via
  `close_beyond_structure_required: true` in the spec parameters the audit itself
  lists as defined evidence for G1/G3.
- The same file: "CHoCH is the earliest reversal signal; BOS confirms
  continuation" — a defined first-break-vs-continuation rule.
Residual: "multi-CHoCH sequencing" (what happens on a second, third, etc.
counter-trend break after the first CHoCH) is not addressed by the existing rule
and would need owner input if verification confirms the gap is real.

---

## 4. G5 — 3-candle FVG formation/size formula, zone-boundary definition, multi-zone tie-break, penetration-ratio rounding

**Status per audit:** PARTIAL — "freshness/invalidation rule closed; FVG formation
formula, zone-boundary definition, multi-zone tie-break, rounding convention open."

**Classification: DOWNGRADED — field-by-field re-check (2026-07-24) found this
overstated the match; not just splittable like G1/G2, the core claim itself was
too strong.**

`fvg_stage` in `specs/st-c2.yaml` (lines 92-103) has six actual fields:
`htf_fvg.min_displacement_bars: 3`, `htf_fvg.max_age_bars: 60`,
`mf_fvg.must_overlap_htf_fvg: true`, `mf_fvg.max_distance_pips: 10`,
`ltf_fvg.required_for_entry: true`, `ltf_fvg.max_age_bars: 20`.
`fvgs(c, min_gap=0.0)` (`src/smc_engine.py:135-143`) has exactly one parameter
(`min_gap`, an absolute price threshold) and implements only the raw 3-candle gap
test.

Checked field-for-field, not concept-for-concept:
- `min_displacement_bars: 3` — **ambiguous, not a clean match.** Could mean "the
  fixed 3-candle geometry `fvgs()` already hardcodes," or could mean "the
  displacement move spans >=3 bars" (a distinct, variable-length idea `fvgs()` has
  no parameter for). Not resolvable by reading the function.
- `htf_fvg.max_age_bars: 60` / `ltf_fvg.max_age_bars: 20` — **doesn't match, not
  implemented.** `fvgs()` has no age/expiry tracking of any kind; it returns bare
  detection events.
- `mf_fvg.must_overlap_htf_fvg: true` — **doesn't match, not implemented.**
  `fvgs()` runs on one candle series; there is no cross-timeframe zone-overlap
  logic anywhere in it.
- `mf_fvg.max_distance_pips: 10` — **doesn't match, not implemented.** No
  distance-to-POI computation exists in the function.
- `ltf_fvg.required_for_entry: true` — **spec-silent relative to this function** —
  a pipeline gate flag, outside what a gap-detector function would represent
  regardless.
- `fvgs()`'s own `min_gap` parameter has **no corresponding spec field** — the one
  size-threshold field nearby, `gap_min_points: 10`, belongs to
  `liquidity_stage.poi_gap_reaction`, a different stage entirely, not `fvg_stage`.

Every one of `fvg_stage`'s six real fields is either unimplemented by `fvgs()` or
ambiguous against it, and the function's only parameter maps to nothing in this
stage. `fvgs()` is a plausible raw geometry primitive to start an implementation
from, but "leans toward engineering verification" overstated it. Corrected
classification: **the core 3-candle detection primitive exists, but the actual G5
gate (freshness/expiry, cross-timeframe overlap, distance tolerance, and unclear
displacement-bars semantics) is largely unimplemented and needs real engineering
work — most of it new, not verification of something already present.** "Multi-zone
tie-break" and "penetration-ratio rounding convention" remain open as originally
noted, now alongside this larger set of unimplemented fields.

---

## 5. G6 — liquidity-sweep reclaim-close timing; max_setup_bars vs. 15-bar expiry relationship; first-qualifying-bar behavior; LTF CHoCH/displacement confirmation

**Status per audit:** PARTIAL — "fill timing + expiry closed; sweep reclaim-close
timing + window relationship + first-qualifying-bar detection open."

**Classification: SPLIT (2026-07-24 field-by-field re-check) — stronger on one part
than originally stated, weaker on another, and one part missing entirely from the
original write-up.**

`liquidity_stage.detect_sweep` (`specs/st-c2.yaml:52-55`): `wick_ratio_min: 0.6`,
`close_back_in_range_required: true`, `max_sweep_age_bars_htf: 20`.
`ltf_confirmation_stage` (`specs/st-c2.yaml:108-118`): `choch.internal_bos_required`,
`choch.break_structure_close_required`, `choch.displacement_body_ratio_min: 0.5`,
`stronger_choch.max_setup_bars: 20`, `entry_window_bars: 15`.
`liquidity_sweeps(c, k=2, min_wick_ratio=0.5)` (`src/smc_engine.py:190-221`).

- **Sweep-reclaim core — stronger match than originally written.**
  `wick_ratio_min: 0.6` maps directly onto the function's `min_wick_ratio`
  parameter (spec value overrides the function's `0.5` default via the existing
  parameter — a genuine, direct, parameter-level match, not just a concept-level
  one). `close_back_in_range_required: true` is exactly the function's
  unconditional `c[i]["close"] > lvl` (or mirror) branch condition. This part
  **holds as engineering verification**, on firmer footing than the original
  draft claimed.
- **`max_sweep_age_bars_htf: 20` — doesn't match, not implemented.** The function
  has no age/staleness concept; it returns raw events with no "bars since
  detection" filter.
- **`stronger_choch.max_setup_bars: 20` / `entry_window_bars: 15` — worse gap than
  originally scoped.** The original text framed this as "the *interaction*
  between the two windows is unresolved," implying both windows already exist in
  code and just need reconciling. They don't: `liquidity_sweeps()` has **no
  window/setup/entry-bar concept at all**. This is a full implementation gap for
  both fields, not a reconciliation question between two implemented things.
  **Needs owner judgment**, more clearly than previously stated.
- **NEW, not in the original write-up: the LTF CHoCH/displacement half of this
  same gate.** `ltf_confirmation_stage.choch`'s three fields
  (`internal_bos_required`, `break_structure_close_required`,
  `displacement_body_ratio_min: 0.5`) are part of G6 per the governance audit's own
  row but have **no relationship to `liquidity_sweeps()` at all** — no body-ratio
  or displacement computation exists anywhere in `src/smc_engine.py`. The original
  G6 section only ever discussed the sweep-reclaim half of
  `liquidity_stage.detect_sweep`; this scope gap is flagged here as its own item,
  not folded into the residuals above.

No candidate resolution is proposed for any of the open pieces — consistent with
this document's no-recommendation rule.

---

## 6. G10 — time stop / session-close / emergency-exit rules for an already-filled position

**Status per audit:** PARTIAL — "pre-fill limit expiry closed; post-fill
time-stop/session-close/emergency-exit open."

**Classification: NEEDS OWNER JUDGMENT.**
`.claude/skills/trade-management/SKILL.md` (read this session) defines breakeven,
partial-take, and trailing rules keyed to R-multiples — nothing about a time-based
stop, forced session-close exit, or an emergency-exit trigger exists anywhere in the
skill or in `src/trade_manager.py`'s documented `manage()` function. This is
genuinely new design surface, not a verification task.

---

## 7. Order simulation — bid/ask treatment, gap-through handling, partial-fill policy, duplicate-setup handling

**Status per audit:** PARTIAL — "price/timing/expiry/same-bar priority closed;
bid/ask, gap-through, partial-fill, duplicate-setup open." Also separately flagged
in the original audit as "the least-specified area of the spec."

**Classification: NEEDS OWNER JUDGMENT — checked file-by-file, not assumed from the
first hit.**
A repo-wide search for `bid`, `ask`, `gap_through`, `partial_fill`, `duplicate_setup`
returned hits in three files, each traced individually:
- `signal_v37.py` (line 7 "Scope by design," line 458): incidental — neither line
  contains the substring at all in a trading sense (the grep matched on other terms
  in the same pattern); no bid/ask logic present.
- `signal_v35.py` (line 99, "...know why it's **ask**ing..."): a genuine substring
  accident — "asking," not a price reference.
- `dry_run.py` (lines 63, 102, 146): **a real, non-accidental hit** —
  `PRICE = {"bid": 1.14426, "ask": 1.14426}`, used once to pick `PRICE["ask"]` for a
  single premium/discount check in an illustrative end-to-end script. This is not a
  substring accident. It is also not a usable convention: bid and ask are hardcoded
  to the same value (no spread), there is no fill logic, no gap-through handling, and
  no duplicate-setup handling anywhere near it — it is a static demo stub, not an
  order-simulation mechanism.

Net conclusion is unchanged (no existing convention covers gap-through, partial-fill,
or duplicate-setup handling anywhere in this codebase), but the original phrasing
overgeneralized "false positive" to all three files when only two of the three
actually were false positives — corrected here.

---

## Session scope note

Per `docs/audit/2026-07-23-st-c2-owner-decision-brief.md`, today's decision session
is scoped to **G4, G7, and the RCR pre-registration gaps only**. All seven items
above are **explicitly deferred**, not resolved, not recommended, and not
prioritized relative to each other by this document. Where an item above leans
"engineering verification," that is a statement about where a future check should
start — it is not a claim that the check has been performed or that the gate is
closed. `specs/st-c2.yaml` remains unmutated; `engine_implements_spec: false`;
no autonomy/promotion flag changed by this document.
