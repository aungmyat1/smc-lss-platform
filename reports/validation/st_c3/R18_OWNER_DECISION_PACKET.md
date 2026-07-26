# Owner Decision Packet — R-18 Evidence Builder (Tier 3)

**Update 2026-07-26: RESOLVED.** All three checklist items below were
answered by the owner and folded into `specs/st-c3_v1.0.6.yaml` via
`reports/governance/st_c3/RCR_ST-C3_v1.0.6_REPORT.md` — see
`OWNER_DECISION_LOG.md`'s R-31/R-32/R-33 rows. `tests/st_c3/` re-verified
passing (20/20) after the spec repoint. Kept below for the historical
record of what was asked and why. Design Section 8's remaining open items
(#1 Tier 1/2 ratification, #3 partial-vs-full run) are unaffected by this
resolution.

**Type:** Decision request, not a decision. Companion to
`R18_EVIDENCE_BUILDER_DESIGN.md` (design, PENDING RATIFICATION per
`OWNER_DECISION_LOG.md`). No value below is proposed or defaulted — each is
an open question for the owner.

## Status

- Design complete: `reports/validation/st_c3/R18_EVIDENCE_BUILDER_DESIGN.md`.
- Tier 1 (8 Evidence kinds, direct `smc_engine.py` reuse): no owner action
  needed, ready to implement once Tier 2 is ratified.
- Tier 2 (5 Evidence kinds, new glue logic, all parameters already frozen):
  needs a ratify/reject decision on the design approach, not new numbers.
- Tier 3 (3 spec fields, still placeholder strings, untracked by any
  R-number): needs actual values before `SweepReclaimEvidence`,
  `EntryWindowEvidence`, and `SessionWindowEvidence` can be built.

## Decision checklist

1. **`sweep_reclaim_max_bars`** (`liquidity_sweep_stage`, spec currently
   `"PROVISIONAL_1_TO_3"`) — how many bars after a sweep must price reclaim
   the swept level for `SweepReclaimEvidence.reclaimed` to hold?
2. **`entry_window_bars`** (`entry_window_stage`, spec currently
   `"PROVISIONAL_3_TO_5_M3_BARS"`) — how many M3 bars after LTF CHoCH does
   the entry window stay open?
3. **Session UTC bounds** (`sessions.london_window_utc`/`ny_window_utc`,
   spec currently `"PROVISIONAL_07_00_TO_10_00"`/`"PROVISIONAL_13_00_TO_16_00"`)
   — final London/NY killzone open/close times.

## After these are answered

- Values get folded into a new spec revision (`specs/st-c3_v1.0.6.yaml` or
  similar) via its own RCR, same as R-27–R-30 -> v1.0.5, with new tracked
  R-numbers for these three fields (they are not currently on the R-01–R-30
  matrix at all).
- Tier 2's design gets a ratify/reject decision.
- Only then does `build_evidence_bundle()` implementation start.
