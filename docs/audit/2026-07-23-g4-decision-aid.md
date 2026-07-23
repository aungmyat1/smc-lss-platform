# G4 Decision Aid — Premium/Discount Location (2026-07-23)

**Purpose:** side-by-side comparison of the existing seed material and the ST-C2 spec's
current anchor field, so the owner can accept/amend in one sitting rather than re-deriving
this from scratch. This is not the owner-decision brief and not a gate-closure record — it
proposes no rule and closes nothing. Read-only assembly; no file other than this one was
touched.

---

## 1. The seed candidate, verbatim (`.claude/skills/premium-discount/SKILL.md`)

```
## Workflow
1. Identify the valid dealing range (last impulse leg).
2. equilibrium = (high+low)/2.
3. Classify price vs equilibrium.
4. Compute OTE (0.62-0.79 retracement) for refined entries.

## Decision rules
- Longs require price in discount; shorts require premium.
- Entering premium for a long is INVALID.

## Failure handling
- Undefined range -> request market-structure output.
- Price at equilibrium -> no directional edge, wait.
```

**How "last impulse leg" is operationally defined:** it isn't, beyond "from swing structure"
(the skill's Inputs section says "range high & low (from swing structure)"). The skill does
not specify which swing-detection stage, lookback window, or confirmation rule identifies the
leg's start/end — that detail lives wherever "swing structure" is produced upstream, not in
this skill file itself.

**At-equilibrium behavior:** explicit — "no directional edge, wait." This is a genuine third
state (EQUILIBRIUM), distinct from PREMIUM/DISCOUNT, per the skill's own Outputs section
("zone of current price: PREMIUM | DISCOUNT | EQUILIBRIUM").

---

## 2. The alternate reference-doc rule, verbatim (`docs/reference/smc-8step-entry-model-dailypriceaction.md`, Step 4)

```
### Step 4 — Mark premium and discount using OTE
Use a modified Fibonacci with the 50% level as the dividing line. After a bearish CHoCH,
only look for shorts in premium (above 50%). Anything in discount (below 50%) is
ignored for shorts even if price drops fast. Waiting for premium and using Optimal Trade
Entry (OTE) enforces patience and keeps entries aligned with the trend.
```

**Same rule or different?** Same underlying 50%-midpoint rule as #1, phrased narratively
instead of as a formula — no independent numeric definition. Two differences worth noting:
(a) this doc ties the range explicitly to the swing that produced the **CHoCH** confirmed in
its own Step 3, whereas the skill just says "from swing structure" with no named source stage;
(b) this doc never mentions an EQUILIBRIUM/wait state at exactly 50% — it only ever frames the
choice as premium-vs-discount, silent on the boundary itself. This document is explicitly
"external reference material — NOT an authoritative spec" (its own header) and carries no
execution or promotion authority regardless of which way this decision goes.

---

## 3. `specs/st-c2.yaml`'s `swing_extremes` anchor, verbatim

```yaml
ote_stage:
  fib_anchor_mode: swing_extremes
  discount_threshold: 0.5
  premium_threshold: 0.5
  long_only_in_discount: true
  short_only_in_premium: true
  max_retrace_pct: 0.786
```

**Is this the same concept as "last impulse leg"?** Unclear — overlapping-but-undefined,
not clearly the same or clearly different. `fib_anchor_mode: swing_extremes` is a *label*
for an anchoring strategy, not a definition: the spec never states which swing points feed
it. ST-C2's pipeline has two candidate sources that could plausibly supply "swing extremes":
`liquidity_stage.detect_external_liquidity` (H4, 300-bar lookback, external highs/lows) or
`htf_bias_stage`'s BOS/CHoCH-confirmed structural swings. The spec does not say which one
`ote_stage` consumes, or whether it's a third, separately-computed swing pair. This ambiguity
is the actual crux of the reconciliation question — not a conflict between the skill and the
spec, but a gap *within* the spec that the skill's language doesn't resolve either.

---

## 4. Specific friction points (plain either/or, for the owner to answer)

1. **Which swing feeds the range?**
   Either: (a) `ote_stage.fib_anchor_mode: swing_extremes` reads from `liquidity_stage`'s
   external-liquidity swings (300-bar HTF lookback), or (b) it reads from `htf_bias_stage`'s
   BOS/CHoCH-confirmed swing (the one that just flipped bias), or (c) it is a separate,
   not-yet-specified swing computation. Neither the skill nor the spec states which.

2. **Does the range freeze or update live?**
   Either: (a) the dealing range is fixed once identified at the triggering CHoCH/BOS event
   and never recalculated for that setup, or (b) it recalculates on every new bar as swing
   structure evolves, potentially moving the equilibrium price mid-setup. Not addressed in
   the skill, the reference doc, or the spec.

3. **What happens if the anchoring swing is invalidated by a later break of structure?**
   Either: (a) the whole setup is invalidated and must be re-evaluated from scratch, or
   (b) the range persists using the stale swing until a new one is confirmed. Not addressed
   anywhere in the repo's ST-C2 material — this is the "range invalidation and reselection"
   gap the governance audit already flagged as unresolved.

4. **Is there a genuine EQUILIBRIUM (wait) state, or does the spec split cleanly at 0.5?**
   The skill has three zones (PREMIUM / DISCOUNT / EQUILIBRIUM, with EQUILIBRIUM meaning
   "wait"). The spec's `discount_threshold: 0.5` and `premium_threshold: 0.5` being numerically
   identical could mean either: (a) the spec also intends a razor-thin EQUILIBRIUM state at
   exactly 0.5 (matching the skill), or (b) the spec intends a clean binary split with no wait
   state at all (anything ≥0.5 is premium, anything <0.5 is discount, or vice versa — spec
   doesn't say which side owns the boundary either). This is not stated in `specs/st-c2.yaml`.

5. **OTE band mismatch: 0.62–0.79 (skill) vs. `max_retrace_pct: 0.786` (spec).**
   The skill defines a two-sided OTE *band* (0.62 to 0.79). The spec defines a single
   `max_retrace_pct: 0.786` with no stated lower bound. Either: (a) these are meant to be the
   same band and 0.786 is a typo/rounding of 0.79 with an implicit 0.62 floor carried over from
   the skill, or (b) the spec deliberately has no lower OTE bound and accepts any retracement
   up to 0.786. Not reconciled anywhere in the repo.

**Not in the repo — a possible amendment (labeled explicitly, not existing material):**
none proposed here. Every friction point above is a gap between/within existing documents,
not a new rule invented for this aid.

---

## 5. The decision, framed as a checklist

```
[ ] Accept seed equilibrium rule (midpoint of last impulse leg) as-is
[ ] Accept, but pin "last impulse leg" to swing_extremes' existing definition (no new logic)
[ ] Amend: [specify what changes]

[ ] At-equilibrium behavior: wait (as in skill) / other: ___

[ ] Swing source for the range: (a) liquidity_stage external swings / (b) htf_bias_stage
    BOS/CHoCH swing / (c) other: ___

[ ] Range update policy: (a) freeze at trigger event / (b) recalculate live / other: ___

[ ] Anchoring-swing invalidation: (a) invalidate whole setup / (b) persist until new swing
    confirmed / other: ___

[ ] Equilibrium boundary treatment at exactly 0.5: (a) genuine EQUILIBRIUM/wait zone /
    (b) binary split, boundary belongs to premium / (c) binary split, boundary belongs to
    discount / other: ___

[ ] OTE band: (a) 0.62-0.79, treat spec's 0.786 as rounding of 0.79 / (b) 0.786 is the sole
    cap, no lower bound / other: ___
```

---

## Confirmation

No file other than this one was created or edited. `.claude/skills/premium-discount/SKILL.md`,
`docs/reference/smc-8step-entry-model-dailypriceaction.md`, and `specs/st-c2.yaml` were read
only. No spec, skill, RCR, or authority document (`CLAUDE.md`, `MASTER_PLAN.md`, `ROADMAP.md`,
`PROJECT_STATUS.md`, `NEXT_ACTION.md`) was touched. All three source paths existed as expected
— no guessing was required for any of them.
