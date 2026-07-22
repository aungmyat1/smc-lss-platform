# Research Change Request — Prioritize E1 in v3.10's E-Trigger Selection When It Qualifies

Filed per `docs/RESEARCH-CHARTER.md` before any backtest of the change
below is run. Supersedes no prior RCR; this is additive to
`ST_C1_V310_REVERSAL_CAPTURE_RCR.md`, addressing a gap that RCR's
Hypothesis/Success-Criteria sections never covered: what should happen
when E1 and E2/E3 qualify concurrently. See
`reports/audit/ST_C1_V310_E1_LOCKOUT_DIAGNOSIS.md` for the full diagnostic
evidence this RCR is built on.

## Change: E-trigger tie-break in `detect_e_trigger` (spec version: v3.10, contract v1.3.0 — no version bump; see Notes)
Date: 2026-07-22
Author: Claude (research agent), on behalf of owner-directed sequencing,
reviewed by `project-governance-agent`

### Why
A read-only diagnostic (`ST_C1_V310_E1_LOCKOUT_DIAGNOSIS.md`) found that
`detect_e_trigger`'s selection rule — `max(candidates, key=lambda t:
t["confirm_i"])`, i.e. "most recent confirmation wins" — causes E1 to lose
to E2/E3 in 100% of the 371 checkpoints (across EURUSD/GBPUSD/XAUUSD
combined) where E1's own conditions were satisfied. E1 has never once been
selected as the trade signal. This rule was authored in v3.9's two-trigger
(E2/E3) world (see `src/signal_v39.py`'s `detect_e_trigger` docstring:
"E1 is disabled outright... only E2/E3 compete; freshest wins") and
carried unchanged into v3.10's three-trigger design without anyone
deciding what should happen when E1 — structurally staler by design,
anchored to an aging D1 gap rather than live price action — also
qualifies. `project-governance-agent` ruled this a design change requiring
an RCR, not a bug fix, since no already-agreed rule is being violated by
the current behavior.

### Evidence
`ST_C1_V310_E1_LOCKOUT_DIAGNOSIS.md`, full three-symbol scan:

| Symbol | Checkpoints | E1 qualifies | E1 wins tie-break |
|---|---|---|---|
| EURUSD | 6,639 | 86 (1.30%) | 0/86 |
| GBPUSD | 6,640 | 138 (2.08%) | 0/138 |
| XAUUSD | 6,643 | 147 (2.21%) | 0/147 |
| **Total** | **19,922** | **371 (1.86%)** | **0/371 (0%)** |

Separately, `ST_C1_V39_VS_V310_COMPARISON.md`'s scenario-population
breakdown confirms zero E1-triggered trades exist in v3.10's realized
367-trade (pre-dedup-fix) / 2,217-trade (post-dedup-fix) population, in
any symbol. `ST_C1_V310_REVERSAL_CAPTURE_RCR.md`'s existence-check success
criterion (">=1 signal per symbol") was reported cleared, but not a single
one of those signals came from E1 — the check validated that the engine
produces *some* signal under the new H4-divergence gate, not that the
reversal-capture-via-E1 mechanism specifically works.

### Hypothesis
Changing `detect_e_trigger`'s selection rule to prefer E1 whenever it
qualifies (rather than defaulting to whichever candidate has the most
recent `confirm_i`) will produce the first-ever nonzero E1-triggered trade
population, because the current lockout is caused entirely by the
tie-break rule, not by E1's own gate conditions being unsatisfiable — E1
already qualifies on its own terms in 1.86% of checkpoints (371 of
19,922), it simply never wins the selection.

### Expected improvement
Stated honestly, per `project-governance-agent`'s explicit instruction not
to imply this fixes v3.10's profitability: this change is expected to
produce a nonzero E1-triggered trade population, bounded above by
approximately 371 candidate checkpoints across the three symbols combined
(1.86% of all checkpoints) — i.e., a small population, likely in the
tens of trades per symbol at most once duplicate-structure suppression and
the existing risk/target/session gates are applied on top. **This change
is explicitly NOT expected to materially change v3.10's aggregate net
profit factor** (currently 0.469, corrected) — E1's maximum possible
population share is far too small relative to the existing 2,217-trade
E2/E3-dominated population to move that number. The purpose is solely to
generate a population large enough to characterize E1's trade behavior
(win rate, RR, cost profile) well enough to judge the reversal-capture
thesis on its own terms, separate from the candidate's overall viability.

### Success criteria
- E1-triggered trades appear in the replay output (nonzero count) in at
  least 2 of 3 symbols.
- E1's trade-level `net_r`/win-rate/cost profile is distinguishable from
  E2/E3's (i.e., there is enough of a population, and a large enough
  behavioral difference, to say something about the reversal-capture
  mechanism specifically — not merely "E1 exists now").
- No fail-open, look-ahead, or determinism defect introduced by the
  tie-break change (verified via existing point-in-time/cutoff-invariance
  tests plus this repo's determinism convention).
- **Explicitly NOT a success criterion:** v3.10's aggregate PF crossing any
  threshold. That is not a fair bar for this narrow, honestly-bounded
  change and must not be conflated with it when reporting results.

### Rollback criteria
- If E1 still produces zero or a negligible trade population even after
  being prioritized (e.g., because the ~1.86% solo-qualification rate
  itself reflects gates that are separately too strict) — report as
  `INCONCLUSIVE`, do not further loosen E1's own parameters without a
  separate RCR specifically for that.
- If the tie-break change is found to introduce any look-ahead,
  fail-open, or non-determinism defect — revert immediately, fix, and
  re-verify before treating any run as evidence, per this repo's standing
  practice.
- If E1's resulting trade population is statistically indistinguishable
  from E2/E3's (no differentiated win-rate/RR/cost signature) — report
  as `INCONCLUSIVE` on the reversal-capture thesis specifically, distinct
  from and not to be conflated with v3.10's already-established overall
  net-losing status.

## Notes

This RCR does not authorize: v3.10 redesign beyond the tie-break, a
symbol-restriction change, `specs/v40.yaml` or any v40-labeled work, or
treating this RCR's outcome as resolving whether v3.10 (or the ST-C1
line generally) clears any promotion gate. Both v3.9 and v3.10 remain
net-losing in every symbol (`ST_C1_DEDUP_BUG_AND_CORRECTED_RESULTS.md`)
regardless of this RCR's outcome — that is a separate, larger decision
for the owner (parking the line, as was done for v3.7/v3.8, remains a
live option) that this RCR does not itself address either way.

No spec-version bump is proposed for this change (it is a replay-engine
selection-logic change, not a `specs/v3.10.yaml` parameter change) —
flagged here for the owner/`project-governance-agent` to confirm whether
`detect_e_trigger`'s selection logic should be considered part of the
versioned spec contract or purely engine-internal; this RCR proceeds on
the assumption it is engine-internal pending that confirmation, consistent
with how `src/backtest_v35.py`'s equivalent dedup-key wiring has never
itself been treated as spec-versioned.
