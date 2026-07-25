# ST-C3 SL/TP Patch Recommendation — REJECTED (owner decision 2026-07-25)

**Final status: REJECTED.** Owner reviewed the analysis below and rejected
the proposal in full, with rationale recorded in `OWNER_DECISION_LOG.md`
("Open Conflict 2 — RESOLVED" and the two "Scope Decisions" entries).
Nothing in `specs/st-c3_v1.0.1.yaml` or any `docs/strategy/st_c3/*.md` file
was ever modified by this document or by the proposal it reviewed — the
frozen spec is unchanged and remains authoritative in full.

**Owner rationale, verbatim disposition:**
- TP1 `rr_min` stays `3.0R`; the 1.5R reference is removed (it came from
  generic SMC reference material, not the frozen ST-C3 spec, and was never
  intended to override the frozen value).
- Break-even and trailing-stop management are out of scope for ST-C3 v1.x;
  may be revisited in a future v2.x research cycle (own Stage A intake),
  not as a v1.x amendment.
- TP2/TP3 revert to the frozen v1.0.1 definitions — no redefinition, no new
  target types, no change to liquidity hierarchy.
- The three undefined terms ("structure confirms continuation," "liquidity
  ahead is clean," "no major liquidity obstruction ahead") are moot, since
  the break-even/trailing rules that used them are out of scope.

**What remains open:** R-09/R-10 (TP2/TP3 `rr_min` numbers) are still
`PENDING` in `OWNER_DECISION_LOG.md` — this rejection confirms the target
*definitions* are unchanged, it does not supply the still-missing RR floor
numbers. Open Conflict 1 (fixed lot vs. `risk_per_trade_pct`) is also still
open, unaddressed by this decision.

**Original analysis preserved below for the audit trail** (per this
project's "never overwrite previous reports / never delete historical
findings" convention) — describes the proposal as submitted, now
superseded by the rejection above.

---
**Origin:** A "Final Insert" SL/TP specification submitted 2026-07-25,
addressed here per the same treatment as `ST-C3_v1.0.1_PATCH_RECOMMENDATION.md`
rather than applied directly, because it changes already-frozen content and
adds features that don't exist in the frozen spec at all — not a fill-in
for an already-tracked unresolved field.
**Depends on:** `OWNER_DECISION_LOG.md` Open Conflict 2, which this proposal
does not resolve — it restates the same "RR ≥ 1.5R" figure without
addressing the conflict with the frozen `TP1 rr_min: 3.0`.

---

## What This Proposal Actually Changes vs. Frozen v1.0.1

| Section | Proposal | Frozen v1.0.1 | Classification |
|---|---|---|---|
| SL invalidation sources | Swing high/low, CHoCH, BOS, OB invalidation, FVG invalidation (5 sources) | `stop_loss_stage`: anchored specifically to "M3 swing that formed CHoCH" (`short_anchor`/`long_anchor`) — one source, not five | **Behavioral change** — broadens what can invalidate a stop, not a restatement |
| SL buffer | Not addressed | `buffer_points: UNRESOLVED` (R-08) | Still unresolved — this proposal doesn't supply a number |
| TP1 | "Opposing liquidity" (previous swing high/low) | `tp1_internal_liquidity`: `[prior_swing, internal_liquidity_pocket]`, `rr_min: 3.0` | Roughly consistent in spirit; **frozen `rr_min: 3.0` is not mentioned** — see RR conflict below |
| TP2 | "Trend continuation liquidity" — **next** swing high/low | `tp2_external_liquidity`: `[equal_highs_lows, major_liquidity_pool]` — external/opposing liquidity, not continuation | **Behavioral change** — targets a different kind of level entirely (continuation vs. external liquidity pool) |
| TP3 | "Extended liquidity, HTF-confirmed" — requires "HTF bias agrees," "structure is clean," "no major liquidity obstruction ahead" | `tp3_htf_objective`: `[h4_swing, deeper_liquidity_target]` | **Behavioral change** — adds three new guard conditions not present in the frozen spec, two of which ("structure is clean," "no major liquidity obstruction") are not boolean/measurable as stated (see Determinism Problem below) |
| RR floor | Blanket "RR must be ≥ 1.5R for any trade to be valid" | TP1 `rr_min: 3.0` (already frozen, owner-stated twice) | **Unresolved conflict**, not new information — same as `OWNER_DECISION_LOG.md` Open Conflict 2 |
| Break-even rule | New: move SL to break-even when TP1 hit AND "structure confirms continuation" AND "no sweep against entry" | **Does not exist anywhere in frozen v1.0.1** | **New feature** — no evidence object, state, or guard exists for this in the state machine |
| Trailing stop rule | New: trail SL to new structural swing when new BOS forms in trade direction | **Does not exist anywhere in frozen v1.0.1** | **New feature** — same gap as break-even |

## Determinism Problem (self-contradicting the proposal's own §7.5)

The proposal's own §7.5 requires every rule to be "deterministic, measurable,
boolean, objective, reproducible" — but two of its own guard conditions
don't meet that bar as written:

- **"Structure confirms continuation"** (break-even rule) — no boolean
  definition given. Which evidence object/field does this read from? This
  is the exact class of ambiguity `SPECIFICATION_VALIDATION.md` flagged for
  "impulsive candles" and "fresh."
- **"Liquidity ahead is clean"** (trailing rule) — same problem. "Clean" is
  not itself measurable without a threshold (how much liquidity, over what
  distance, is "clean" vs. not?).
- **"No major liquidity obstruction ahead"** (TP3 condition) — same problem
  a third time.

These would need their own resolution-matrix-style entries before they
could be implemented deterministically — adding this proposal as-is would
add three *new* ambiguous terms to the spec while Phase 2.5 is still trying
to close the existing 20.

## Architectural Gap (break-even / trailing stop)

ST-C3's frozen state machine (`specs/st-c3_v1.0.1.yaml` `state_machine`) ends
active management at `S13_TRADE_PLAN_EMIT` -> `S14_EXPIRY_TERMINATION` ->
`S15_TERMINAL`. There is no post-entry, pre-exit management state at all —
`S14`'s guard only monitors `ExpiryEvidence` for the four existing
termination reasons (`BIAS_FLIP`, `ENTRY_WINDOW`, `SL_BREAK`, `SUPERSEDED`).
Break-even and trailing-stop logic would need:

- A new evidence object (e.g. `TradeManagementEvidence`) with fields for
  "structure confirms continuation" and "new BOS in trade direction" —
  currently undefined.
- Either a new state between `S13` and `S14`, or a redefinition of what
  `S14` monitors — a state-machine change, which the S1-G1C audit's own
  16-state/16-transition invariant was built to protect against being
  added casually.
- New rejection/termination-code implications (what code does a
  break-even/trail event even produce? None of the existing 8 R-codes or 4
  ERR-codes cover it).

This is a materially larger change than R-1/R-2/R-3 (which touched only
rejection-code labels, zero state/evidence/guard changes). Framing it as a
"final insert, ready for Specification Closure" understates its scope.

---

## What Would Be Needed to Actually Apply This

1. **Resolve `OWNER_DECISION_LOG.md` Open Conflict 2** first — does 1.5R
   coexist with or override the frozen TP1 3.0R? This proposal restates the
   same unresolved number without answering that question.
2. **Define the three ambiguous terms** ("structure confirms continuation,"
   "liquidity ahead is clean," "no major liquidity obstruction ahead") as
   boolean/measurable conditions — new resolution-matrix entries, not
   skippable.
3. **Design the state-machine extension** for break-even/trailing (new
   evidence object, new state or `S14` redefinition, new codes) — this is
   architecture work, not a documentation insert.
4. **File an RCR** per `docs/RESEARCH-CHARTER.md` — this is unambiguously a
   design change (new features + redefined TP2/TP3), not a bug fix, so it
   cannot go through the lighter bug-fix carve-out R-1/R-2/R-3 partially
   used.
5. **Cut a new versioned spec** (e.g. `specs/st-c3_v1.0.2.yaml` or later,
   depending on what else closure resolves first) with the ratified content
   — never by inserting a markdown section into a doc file in place of the
   YAML source of truth.

## Recommendation

Hold this proposal as **not accepted, not rejected** pending:
(a) your answer to Open Conflict 2, and
(b) whether you want break-even/trailing-stop as new ST-C3 features at all
— that's a scope decision (this changes ST-C3 from an entry-only funnel
into one with active trade management), separate from resolving the
existing 20 unresolved fields.

Nothing has been written to `specs/st-c3_v1.0.1.yaml` or any companion doc.
