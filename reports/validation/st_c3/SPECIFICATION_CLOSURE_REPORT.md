# ST-C3 Specification Closure Report — Phase 2.5

**Status: NOT CLOSED.** Zero of 20 unresolved items have an owner decision
recorded. This report exists to make that gap explicit and trackable, not to
claim closure that hasn't happened.

---

## What Exists

| Deliverable | Status |
|---|---|
| `SPECIFICATION_VALIDATION.md` (Phase 1) | DONE — catalogued 20 unresolved fields (corrected from that report's own off-by-one "19" claim), 8 provisional values, 3 ambiguous terms. |
| `RESOLUTION_MATRIX.md` | DONE — all 20 fields classified by decision owner (research-required / owner-decision-required / already-defined-elsewhere), each with a proposed starting point and priority ranking. |
| `DEPENDENCY_GRAPH.md` | DONE — shows R-02 (instrument scope) as the root dependency; risk, target, sweep, and RCR-pre-registration chains mapped. |
| `DECISION_PACKAGES.md` | DONE — bundles the 20 fields into 8 review packages (E through H) with a recommended review order. |
| `ST-C3_v1.0.2_DRAFT.yaml` | DONE — annotated copy of `specs/st-c3_v1.0.1.yaml` with `PROPOSED` comments next to every unresolved field. **No value was changed from v1.0.1** — every field that was `UNRESOLVED` remains `UNRESOLVED` in this draft; only comments were added. Deliberately placed outside `specs/` to avoid being mistaken for a real candidate spec. |
| `OWNER_DECISION_LOG.md` | DONE — a 20-row log, every row `PENDING`. This is the actual gate: closure is only real once every row here is filled in and ratified. |

## What Does NOT Exist Yet

- **Any owner decision.** `OWNER_DECISION_LOG.md` is entirely `PENDING`.
- **A real `specs/st-c3_v1.0.2.yaml`.** The draft YAML in this directory is
  explicitly not that file — per its own header, promoting it in place
  would skip the RCR process used for R-1/R-2/R-3.
- **Any research work.** Several proposals (R-04 through R-08, R-18) are
  explicitly marked "research required," not "owner decision required" —
  meaning even owner sign-off on those specific rows should trigger a
  research pass (e.g. via `tools/existence_check.py` once an instrument is
  chosen), not just acceptance of the proposed range as final.

## Zero Unresolved Specification Items — NOT YET TRUE

This task's own success criteria for "Specification Closure" requires a
report confirming **zero unresolved specification items**. That is not the
case today: all 20 fields in `RESOLUTION_MATRIX.md`/`OWNER_DECISION_LOG.md`
remain unresolved. This report does not claim otherwise.

## Path to Actual Closure

1. Owner reviews `DECISION_PACKAGES.md` in the recommended order (Package E
   first — instrument/session scope is the root dependency).
2. Owner fills in `OWNER_DECISION_LOG.md` row by row — accept, amend, or
   defer each proposal.
3. For any field marked "research required" whose proposed *range* the
   owner accepts in principle, the actual research step still needs to run
   (`tools/existence_check.py` / `tools/power_planning.py` against real
   candle data for the chosen instrument) before a single final number can
   be picked.
4. Once `OWNER_DECISION_LOG.md` has no `PENDING` rows left, file an RCR
   entry in `reports/research_log.md` (same six-question template used for
   the rejection-code fix), then cut a real `specs/st-c3_v1.0.2.yaml` with
   only the ratified values — mirroring exactly how v1.0.1 was produced
   from the approved patch recommendation.
5. Only after that real v1.0.2 exists would a fresh S1-G1C-style structural
   re-check make sense (confirming the new values didn't introduce a
   structural, cross-link, or determinism regression) — this report does
   not run that re-check since there is no ratified v1.0.2 to check yet.

## Relationship to A2/S1-G2

Independent decisions, per `VALIDATION_PROGRESS.md`'s earlier finding:
resolving these 20 fields does not require A2/S1-G2 to be open, and opening
A2/S1-G2 does not by itself resolve these fields. Both gates must clear
before Phase 3 (Golden Case Verification) can meaningfully begin — a
reference implementation built against 20 undefined thresholds would either
invent values (prohibited) or be nonfunctional.

## Recommendation

Per this task's own promotion-gate rule ("if any criterion fails: recommend
remain in Research Stage, list every blocking issue, ranked by severity"):

**Remain in Research Stage — Specification Closure.**

Blocking issues, ranked:

1. **Critical:** R-02 (instrument scope) — root of the entire dependency
   graph, blocks all research-required fields.
2. **Critical:** R-01, R-07, R-11, R-14 — see `RESOLUTION_MATRIX.md` priority
   summary.
3. **High:** R-04, R-08.
4. **Medium/Low:** all remaining rows — see `RESOLUTION_MATRIX.md`.

No blocking issue here requires the agent to invent a resolution; each is
recorded as pending the owner's actual decision.
