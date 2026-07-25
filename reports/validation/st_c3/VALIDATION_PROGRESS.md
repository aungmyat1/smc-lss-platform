# ST-C3 Validation Progress

**Purpose:** single tracker for the 9-phase validation lifecycle requested
for ST-C3's path toward an execution-promotion recommendation. Updated at
the start of each session per the "inspect state, avoid duplicating
completed work, continue from the first unfinished phase" working method.

---

## Phase Status

| Phase | Name | Status | Artifact | Blocker (if any) |
|---|---|---|---|---|
| 1 | Specification Verification | **DONE** (this session) | `SPECIFICATION_VALIDATION.md` | — |
| 2 | Determinism Verification | **DONE** (this session, consolidating prior S1-G1C evidence) | `DETERMINISM_REPORT.md` | — |
| 2.5 | Specification Closure (inserted this session) | **IN PROGRESS** — matrix/graph/packages/draft/log produced; zero owner decisions recorded yet | `RESOLUTION_MATRIX.md`, `DEPENDENCY_GRAPH.md`, `DECISION_PACKAGES.md`, `ST-C3_v1.0.2_DRAFT.yaml`, `OWNER_DECISION_LOG.md`, `SPECIFICATION_CLOSURE_REPORT.md` | Awaiting owner review of `OWNER_DECISION_LOG.md`; several rows additionally require a research pass, not just a decision |
| 3 | Golden Case Verification | **BLOCKED** | not started | Requires a reference implementation to produce "actual outcome" per case. No ST-C3 code exists (`engine_implements_spec: false`). Also requires Phase 2.5 to close first — golden cases can't be evaluated against 20 undefined thresholds. |
| 4 | Negative Case Verification | **BLOCKED** | not started | Same blocker as Phase 3. |
| 5 | Historical Replay | **BLOCKED** | not started | Requires a working detector to generate real signals/trades from EURUSD/GBPUSD/XAUUSD data. This is exactly the reference-implementation work A2/S1-G2 exists to authorize. |
| 6 | Statistical Validation | **BLOCKED** | not started | Requires Phase 5's trade data to exist first. |
| 7 | Robustness Validation | **BLOCKED** | not started | Requires Phase 5/6 to exist first (stress-tests real trades against spread/slippage/delay). |
| 8 | Walk-Forward Validation | **BLOCKED** | not started | Requires Phase 5/6 to exist first (rolling train/validate needs real trade data). |
| 9 | Execution Readiness Assessment | **BLOCKED** | not started | Depends on Phases 3-8 all completing. |

## Completed Tasks (this session)

- Cross-referenced `SPECIFICATION_VALIDATION.md` against `specs/st-c3_v1.0.1.yaml`
  in full: catalogued 19 `UNRESOLVED` fields, 8 `PROVISIONAL`/`CONFIGURABLE`
  fields, and 3 ambiguous terms not previously enumerated as a single list.
- Consolidated `DETERMINISM_REPORT.md` from the existing S1-G1C audit and
  rerun report evidence, extended with an explicit per-rule-category table
  (HTF bias, structure, sweep, CHoCH/BOS, FVG, OB, premium/discount, entry,
  SL, TP, risk, session, news) the prior reports didn't lay out in that
  exact shape.
- No code was written, no spec was modified, no A2/A3 work was started.

## Current Phase

Phase 2.5 (Specification Closure) — inserted between Phase 2 and Phase 3
per owner-endorsed recommendation, since the strategy specification was
found not yet complete enough to validate or implement. In progress: the
matrix/graph/packages/draft/log are produced; awaiting the owner's actual
decisions in `OWNER_DECISION_LOG.md`.

## Remaining Work

Phases 3-9 all ultimately require one thing that doesn't exist yet: a
reference implementation of ST-C3's detection logic. That, in turn, requires
two things neither of which have happened:

1. **The 19 `UNRESOLVED` spec fields (`SPECIFICATION_VALIDATION.md`) must be
   resolved** — via the same governance-revision process used for R-1/R-2/R-3
   (owner decision + RCR + versioned spec cut), since picking concrete
   thresholds is a design decision, not a bug fix.
2. **A2/S1-G2 (Reference Implementation Authorization) must be opened** —
   an explicit owner decision, separate from and prerequisite to any of
   Phases 3-9. As of this session, this has been explicitly **deferred**
   (owner retracted an earlier "open it now" answer in favor of keeping it
   not-open).

Until both happen, Phases 3-9 remain correctly blocked, not stalled by
oversight.

## Risks and Blockers

- **Risk of silent scope creep:** every one of Phases 3-9 could technically
  be "attempted" by hand-simulating a detector or inventing values for the
  19 unresolved fields — that would not be verification, it would be
  undisclosed spec authorship and undisclosed implementation, both
  prohibited by this task's own rules ("never redesign ST-C3," "never add
  discretionary logic," "never build MT5 execution," "never bypass
  governance"). This report explicitly declines to do that.
- **No blocker exists on Phases 1-2** — both are complete and require no
  further action unless the spec changes again.

## Recommended Next Action

One of, at the owner's discretion — this report does not recommend one over
the other, since both are legitimate:

- **(a)** Resolve some or all of the 19 `UNRESOLVED` fields via a
  governance-approved revision (new RCR, likely `specs/st-c3_v1.0.2.yaml`),
  independent of the A2/S1-G2 decision — this can happen while A2/S1-G2
  stays closed, since it's a spec-content decision, not implementation.
- **(b)** Make the explicit owner decision to open A2/S1-G2, at which point
  Phase 3 (Golden Case Verification) can begin **after** (a) has also
  happened — a reference implementation still cannot be built deterministically
  with 19 fields undefined, even once A2/S1-G2 is authorized.

Per this task's own promotion-gate rule: since Phases 3-9 have not run,
the correct recommendation right now is **"Remain in Research Stage"** —
not "ready to submit RCR for opening A2/S1-G2." Opening A2/S1-G2 is a
necessary but not sufficient precondition for that recommendation; the
19-field resolution gap would remain even if A2/S1-G2 were opened today.
