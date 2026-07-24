# ST-C2 Implementation Readiness Report

**Date:** 2026-07-24
**Prepared per:** owner instruction to "prepare ST-C2 for implementation
authorization" — explicitly **not** an instruction to begin implementation.
Companion to `reports/ST-C2_SPEC_AUDIT.md` (full gate-by-gate matrix) and
`specs/st-c2_v1.1.0.yaml` (consolidated candidate spec).

## Verdict

# READY WITH OWNER DECISIONS PENDING

**Updated 2026-07-24 (fifth addendum):** the owner closed one of the six
original blocking items (`duplicate_setup_policy`, with rationale) and
added a new, explicitly PROVISIONAL portfolio-loss circuit breaker
(`risk.hard_kill_switch`). The verdict is unchanged — five substantive
blockers remain, one of which (emergency-exit numeric thresholds) was
initially mistaken for closed by the same submission and is corrected
back to open below, with the reasoning stated.

Not READY FOR IMPLEMENTATION. Not NOT READY. Six of ten gates
(G3, G4, G7, G8, G9) plus RCR pre-registration are fully closed with
deterministic, measurable, testable rules, and one more (G6) is closed
except for a single low-risk restatement. But four gates (G1, G2, G5, G10)
and the order-simulation rule set each carry at least one genuine,
unresolved gap — some explicitly flagged as unconfirmed by the owner's own
prior addenda, some newly found in this consolidation pass. Per this
task's own instruction, none of them is resolved by assumption here.
**Implementation should not be recommended or started until the blocking
items below are closed and this report is re-issued.**

---

## Why not READY FOR IMPLEMENTATION

A deterministic point-in-time engine cannot be built end-to-end today
without inventing at least the following, none of which exists anywhere in
`specs/st-c2.yaml`, its five RCR addenda, or the codebase:

1. **The FVG zone-boundary formula (G5)** — without this, the pipeline's
   own stage 4 (FVG alignment, required for entry per `ltf_fvg.required_for_entry: true`)
   has no way to compute what a "fair value gap" actually *is* in price
   terms, only how it ages and gets invalidated.
2. **The liquidity-pool "stable identifier" (G2)** — decision 3's own
   tie-break chain (nearest distance → most recent timestamp → stable
   identifier) is incomplete without it when the first two criteria tie.
3. **Post-fill event-priority ordering (order-simulation)** — trade
   management (`management.break_even_activation_r`, `partial_take_r`,
   `runner_enabled`) has no defined behavior when more than one management
   event could apply on the same bar.
4. **Session-close-forces-exit for an open position (G10)** — an
   unaddressed question distinct from the already-closed "no time stop"
   decision.
5. **Emergency-exit numeric thresholds (G10)** — the concept and trigger
   types are decided; the actual numbers that would fire the
   spread-spike/connection-loss/volatility-shock rule are not. (A
   separate, PROVISIONAL portfolio-loss circuit breaker was decided in the
   fifth addendum — that closes a different mechanism, not this one; see
   `reports/ST-C2_SPEC_AUDIT.md` §3 finding 9 for why they aren't the
   same thing.)

`duplicate_setup_policy` (order-simulation) was the sixth item on this
list as of the fourth addendum — **closed** in the fifth addendum with
stated rationale (`one_position_at_a_time`, logged not executed).

Each remaining item is a place where an implementer would otherwise have
to invent a rule mid-build — exactly what the RCR addenda, and this task,
exist to prevent.

## Why not NOT READY

The overwhelming majority of the strategy's semantics **are** closed with
citable, deterministic, testable rules: HTF bias classification, dealing-
range/premium-discount mechanics, FVG freshness/invalidation/alignment
(short of the boundary formula), sweep/CHoCH timing, the entire stop-
distance and cost-model contract, target selection, and the full RCR
statistical pre-registration. Six gates are fully closed; a seventh is one
sentence away. This is not a strategy with foundational gaps — it is a
strategy with a short, enumerable list of specific, isolable open
questions. Framing it as "not ready" in the broad sense would understate
four addenda's worth of real, careful decision-making.

## What "READY WITH OWNER DECISIONS PENDING" requires to become READY

All items in `reports/ST-C2_SPEC_AUDIT.md` §4 must be closed — either by an
explicit owner decision (same format as the four prior addenda) or, for
the items already classified as engineering-verification-only (none
remain unclassified at this time — G2's dedup key was the last such item,
closed by the fourth addendum), by a read-only verification pass. The
blocking subset, restated from the audit:

- `duplicate_setup_policy` — needs an actual decision with rationale, not
  the currently-unconfirmed proposed value.
- Emergency-exit numeric thresholds — needs owner confirmation of final
  numbers (or an explicit statement that the illustrative values become
  final).
- FVG zone-boundary formula — needs either an owner-supplied formula or an
  explicit decision to adopt (and verify) an existing codebase primitive.
- Liquidity-pool stable-identifier composition — needs a decision,
  distinct from the already-closed replay-engine dedup key.
- Session-close-forces-exit — needs an explicit yes/no, not inferred from
  the time-stop answer.
- Post-fill event-priority ordering — needs an explicit precedence rule.

The five low-risk items (bull/bear classification statement,
bias-evidence-timestamp field, 4th+ CHoCH sequencing, the
`protected_level_lifecycle.create_on` inference, the `internal_bos_required`
restatement, and rejection-code ratification) are not blocking in the
same sense but are also not resolved here, per instruction, and should be
confirmed before or during implementation rather than left silent.

## Explicit non-actions in this task

- No strategy logic was modified — `specs/st-c2.yaml` (v1.0.0) is
  unchanged.
- No parameter was optimized or tuned.
- No production code, engine, or test was written.
- No backtest was run.
- No execution, demo, live, or promotion state was changed.
- No `IMPLEMENTATION AUTHORIZATION: GRANTED` string exists anywhere in the
  repo, and this report does not create one.
- `specs/st-c2_v1.1.0.yaml` remains `status: candidate`, not an
  owner-verified canonical/approved spec — the "canonical-specification-
  path question" first raised in the RCR's original addendum is addressed
  by this file's existence, but the file's *approval* is a separate,
  still-open owner act.

## Recommendation

Do not begin implementation. When ready, resolve the six blocking items
above (ideally as a fifth RCR addendum, matching this project's
established pattern), re-run this consolidation, and re-issue this report.
Only a future version of this report concluding **READY FOR IMPLEMENTATION**
should be treated as grounds to seek
`IMPLEMENTATION AUTHORIZATION: GRANTED`.
