# ST-C2 Implementation Readiness Report

**Date:** 2026-07-24
**Prepared per:** owner instruction to "prepare ST-C2 for implementation
authorization" — explicitly **not** an instruction to begin implementation.
Companion to `reports/ST-C2_SPEC_AUDIT.md` (full gate-by-gate matrix) and
`specs/st-c2_v1.1.0.yaml` (consolidated candidate spec).

## Verdict

# READY WITH OWNER DECISIONS PENDING

**Updated 2026-07-24 (sixth addendum):** the owner closed four more of
the five remaining substantive blockers (FVG zone-boundary formula,
liquidity-pool stable-identifier composition, post-fill event-priority
ordering, and — partially — session-close-forces-exit) plus ratified the
emergency-exit numeric thresholds as PROVISIONAL working values. **Exactly
one substantive gap now remains: the numeric "invalidation-buffer
distance" for the session-close-exit rule** (the concept is decided; the
number is not, and is explicitly not inferred from the unrelated G7 stop
buffer). Six low-risk/narrow items from the audit are also still open.
The verdict stays READY WITH OWNER DECISIONS PENDING rather than READY FOR
IMPLEMENTATION, per this task's own rule that only a report with zero
remaining blockers earns that conclusion — one missing number is still a
missing number, not a rounding-up case.

Not READY FOR IMPLEMENTATION. Not NOT READY. Nine of twelve gate-matrix
rows (G2, G3, G4, G5, G7, G8, G9, order-simulation, RCR pre-registration)
are now fully closed with deterministic, measurable, testable rules, and
a tenth (G6) is closed except for a single low-risk restatement. G1
carries two low-risk open items; G10 carries exactly one missing number.
Per this task's own instruction, none of them is resolved by assumption
here. **Implementation should not be recommended or started until the
blocking item below is closed and this report is re-issued.**

---

## Why not READY FOR IMPLEMENTATION

Exactly one gap remains that would force an implementer to invent a rule
mid-build:

1. **Session-close "invalidation-buffer distance" (G10)** — the sixth
   addendum's Decision 3 settled the rule's *shape* (at session close,
   exit only if price is within an invalidation-buffer distance of
   structural invalidation; otherwise the position stays open), but
   supplied no number or formula for that distance. It was explicitly not
   assumed to reuse the G7 stop buffer (a different concept — stop
   placement, not exit-trigger proximity) per this project's practice of
   not inferring across unrelated fields. One number closes this.

Everything else on the original five-item list from the fifth-addendum
version of this report is now closed:

- ~~FVG zone-boundary formula (G5)~~ — closed, sixth addendum Decision 1
  (wick-to-wick displacement, verified directly against
  `src/smc_engine.py:135-143`'s `fvgs()`, not just asserted).
- ~~Liquidity-pool "stable identifier" (G2)~~ — closed, sixth addendum
  Decision 2 (SHA-256 hash of structural attributes).
- ~~Post-fill event-priority ordering (order-simulation)~~ — closed,
  sixth addendum Decision 4 (stop → target → management → diagnostics).
- ~~Emergency-exit numeric thresholds (G10)~~ — closed as PROVISIONAL
  working values, sixth addendum Decision 5 (the existing 20 pts / 60 s
  illustrative values, now knowingly ratified rather than merely
  unreviewed).
- ~~`duplicate_setup_policy` (order-simulation)~~ — closed, fifth
  addendum Decision A.

The remaining low-risk items (bull/bear classification statement,
bias-evidence-timestamp field, 4th+ CHoCH sequencing,
`protected_level_lifecycle.create_on`, `internal_bos_required`
restatement, rejection-code ratification) are unchanged from the prior
version of this report — narrow, non-blocking in the same sense, but not
resolved here either.

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

One substantive item: **the invalidation-buffer distance number** for
Decision 3's conditional session-close-exit rule (a points/pips value or
an explicit formula, e.g. "within N points of the structural invalidation
level").

The six low-risk items (bull/bear classification statement,
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

Do not begin implementation. One number away: supply the
invalidation-buffer distance (ideally as a seventh RCR addendum, matching
this project's established pattern), re-run this consolidation, and
re-issue this report. Only a future version of this report concluding
**READY FOR IMPLEMENTATION** should be treated as grounds to seek
`IMPLEMENTATION AUTHORIZATION: GRANTED` — and per the project-governance-
agent ruling recorded in this session, that authorization act, plus
sequencing by `project-governance-agent`, are both still required after
this report turns green before any `src/` code is written; the RCR
addenda authorize spec content, never execution-layer code, on their own.
