# ST-C3 Governance Review Report — Patch Recommendation v1.0.1

**Stage:** Stage 1 — Governance Review (technical review only)
**Reviews:** [`ST-C3_v1.0.1_PATCH_RECOMMENDATION.md`](ST-C3_v1.0.1_PATCH_RECOMMENDATION.md)
**Status:** Technical review complete. **This report is NOT an approval.**
Approval of a strategy revision is an owner decision per `MASTER_PLAN.md`
("no production before promotion approval," "approved strategies are
immutable... every strategy revision requires a new candidate version") and
cannot be self-granted by the agent that authored the recommendation being
reviewed. See "Approval Status" at the end of this report.

---

## Executive Summary

The three proposed rejection-code fixes (R-1, R-2, R-3) are each justified by
a concrete, cited defect in the frozen `specs/st-c3_v1.0.0.yaml`, none
require reinterpreting or redesigning strategy logic, and none touch an
entry/exit/session/RR threshold. The version bump to `v1.0.1` is consistent
with `MASTER_PLAN.md` Governance Rule 7 ("every strategy revision requires a
new candidate version"). No unintended strategy change was found. One gap
was found in the recommendation's own migration coverage (see "Migration
Impact Gaps" below) that should be closed before a v1.0.1 spec is cut.

**Recommendation to owner:** the three fixes are sound and low-risk to
approve. This report does not itself authorize cutting `v1.0.1` — that
requires your explicit sign-off (see the question at the end of this turn).

---

## Verification Checklist

### Every recommendation is justified

| Finding | Evidence cited | Verified against frozen spec |
|---|---|---|
| R-1 | `evidence_bindings.S12_RISK_SLTP.reject` and `validator_rules.state_rules.S12_RISK_SLTP.reject` both hard-code `R5_NO_FVG_OB_CONFLUENCE`; `R5`'s own `triggers:` list (`no_fresh_fvg_or_ob_inside_ote`, `confluence_zone_mitigated_or_invalid`, `confluence_contradicts_htf_bias`) names only FVG/OB confluence conditions. | Confirmed by direct read of `specs/st-c3_v1.0.0.yaml` lines 297-306, 607-611, 695-697. No trigger in `R5` describes an invalidation-swing, target-evidence, or RR condition. |
| R-2 | `state_machine.transitions` state `S12` (line 526) uses literal string `appropriate_r_code_for_risk_or_target_rule_failure` as `failure_code`, while `evidence_bindings`/`validator_rules` (same file) hard-code `R5_NO_FVG_OB_CONFLUENCE` for the identical guard. | Confirmed — this is a literal placeholder string, not a code identifier matching the `R\d_[A-Z_]+` pattern used by every other transition's `failure_code`. |
| R-3 | `S5_BOS_EXTREME_LOCK` reuses `R3_NO_DISPLACEMENT_BOS` (line 576) and `S6_DEALING_RANGE` reuses `R4_NO_OTE_PULLBACK` (line 581); neither `R3` nor `R4`'s `triggers:` list names a pullback-detection or dealing-range condition (lines 282-286, 292-296). | Confirmed. Contrast with the two reuse cases the audit found correctly justified (`S3`→`R2` via `sweep_reclaim_exceeds_n_sweep`, `S10`→`R6` via `choch_outside_allowed_sessions`) — those triggers do exist in the target code's list; R3/R4 do not have equivalents for S5/S6. |

All three findings are reproducible by direct inspection of
`specs/st-c3_v1.0.0.yaml` and require no backtest, replay, or execution
evidence to confirm — consistent with the S1-G1C audit's own claim that these
are static, cross-reference-detectable defects.

### No unintended strategy change

- Detection logic unaffected: HTF bias, sweep, displacement/BOS, OTE zone
  (62-79%), FVG/OB confluence, LTF confirmation, session gating, and entry
  window guards are all untouched by every proposed diff.
- Risk/target construction guard unaffected: `S12`'s guard
  (`InvalidationSwingEvidence.valid == true AND TargetEvidence.valid == true
  AND computed_rr >= MIN_RR`) is not modified by any R-1/R-2 diff — only its
  **failure_code label** changes. A trade that would have been accepted or
  rejected under v1.0.0 is accepted or rejected identically under the
  proposed v1.0.1; only the diagnostic string attached to a rejection
  changes.
- `MIN_RR` and all other `[TUNABLE]`-class parameters in
  `ST-C3_PARAMETER_SHEET.md` are not referenced by any proposed diff.
- Evidence object count (16), state count (16), transition count (16) are
  explicitly stated as preserved in the recommendation and confirmed by
  inspection — no diff adds, removes, or renames a state or evidence object.
- **Finding: not a strategy-behavior change.** This supports treating R-2 (and
  arguably R-1, R-3) as closer to the Research Charter's bug-fix carve-out
  than a design change, though the recommendation correctly errs toward
  running the RCR process anyway given R-1/R-3 involve judgment calls
  (severity classification, no dedicated-code-vs-trigger-list-amendment
  choice for R-3).

### Version bump follows governance

- `MASTER_PLAN.md` Governance Rule 7: "every strategy revision requires a new
  candidate version." `v1.0.0` → `v1.0.1` (patch-level bump) is proportionate
  to the scope of change (diagnostic-layer only, no state/evidence/threshold
  change) and follows the same precedent as ST-C2's `v1.1.0` → `v1.2.0`
  versioned-revision pattern.
- Freeze immutability preserved: the recommendation does not propose editing
  `specs/st-c3_v1.0.0.yaml` in place; it proposes cutting a new file
  `specs/st-c3_v1.0.1.yaml`, leaving v1.0.0 intact as historical record.
  Confirmed no in-place edit was made — `git status`/file contents unchanged
  since the report was written.

### Affected sections identified

Recommendation correctly scopes affected sections to exactly four locations
per fix, all enumerated with line-level specificity:

- R-1: `rejection_codes` (new `ST-C3-R8` entry), `rejection_code_json_schema.R_CODES`
  (new entry), `evidence_bindings.S12_RISK_SLTP.reject`, `validator_rules.state_rules.S12_RISK_SLTP.reject`.
- R-2: `state_machine.transitions` (`S12` entry `failure_code` only).
- R-3: `rejection_codes.ST-C3-R3.triggers`, `rejection_codes.ST-C3-R4.triggers` (list append only).

No other spec section (`pipeline`, `trade_plan.schema`, `parameter_sheet`,
`execution_agent`) is touched by any proposed diff. Companion doc updates
correctly named: `ST-C3_EVIDENCE_BINDINGS.md`, `ST-C3_VALIDATOR_RULES.md`,
`ST-C3_REJECTION_CODE_SPEC.md`.

### Migration impact documented — partial, one gap found

The recommendation documents the spec-side migration (steps 1-5) but has a
coverage gap:

**Gap found (minor, documentation-only):** `ST-C3_STATE_MACHINE.md` is not
listed among the companion docs to update in the recommendation's "Required
next steps" step 3, but it independently states each state's `failure_code`
in prose (confirmed present in the S1-G1C audit's own scope list, Section 3).
If `S12`'s `failure_code` changes from a placeholder to `R8_INVALID_RISK_OR_TARGET`
in the YAML, `ST-C3_STATE_MACHINE.md`'s prose description of `S12` must be
updated in the same migration step, or the doc and YAML will disagree the
same way R-2 already flagged the YAML disagreeing with itself. Recommend
adding `ST-C3_STATE_MACHINE.md` to the file list in the patch
recommendation's step 3 before it is executed.

No other migration gaps found. `ST-C3_PARAMETER_SHEET.md`,
`ST-C3_EXECUTION_AGENT_SPEC.md`, `ST-C3_TRADE_PLAN_SCHEMA.md`,
`ST-C3_EVIDENCE_OBJECT_SPEC.md`, `ST-C3_FUNNEL_LIFECYCLE.md` do not reference
rejection codes and correctly need no update.

---

## Findings Summary

| ID | Severity | Evidence | Affected files | Recommendation | Approval required |
|---|---|---|---|---|---|
| GR-1 | Minor | `ST-C3_STATE_MACHINE.md` omitted from patch recommendation's migration file list, despite containing S12 failure-code prose | `reports/validation/st_c3/ST-C3_v1.0.1_PATCH_RECOMMENDATION.md` (step 3 list); `docs/strategy/st_c3/ST-C3_STATE_MACHINE.md` (future edit target) | Add `ST-C3_STATE_MACHINE.md` to the migration file list before executing step 3 of the patch recommendation | Owner (documentation completeness, no strategy change) |
| — | Informational | R-1/R-2/R-3 all independently verified as accurately described and low-risk | `specs/st-c3_v1.0.0.yaml` | No further action beyond GR-1 | — |

No critical or major findings. Per this pipeline's own decision policy
(critical → stop; major → governance approval required; minor → continue
with documentation; informational → record only), GR-1 does not block
proceeding — it is recorded here and should be folded into the migration
step whenever it executes.

---

## Draft RCR (Revision Change Request) — NOT YET FILED

The following is prepared per `docs/RESEARCH-CHARTER.md`'s six-question
template and this task's request for an RCR structure, but is held here as a
**draft** rather than appended to `reports/research_log.md`. Filing it as an
accepted log entry implies the change is proceeding; that should not happen
before the owner decision below.

```markdown
## Change: ST-C3 rejection-code layer fix (spec version: v1.0.0 -> v1.0.1)
Date: 2026-07-25
Author: AI agent (governance review); pending owner approval

### Why
S1-G1C logic-conformance audit (ST-C3_S1-G1C_LOGIC_CONFORMANCE_REPORT.md)
found three rejection-code defects (R-1 significant, R-2 internal
inconsistency, R-3 minor) that would cause a spec-faithful validator to
mislabel RR/stop/target failures and two other guard failures with
inaccurate rejection codes, corrupting rejection-log diagnostics without
affecting which trades are accepted or rejected.

### Evidence
Direct line-level citation against specs/st-c3_v1.0.0.yaml (lines 297-306,
526, 576, 581, 607-611, 695-697) confirmed in this governance review's
Verification Checklist above and in the original S1-G1C audit.

### Hypothesis
Adding a dedicated R8 code for S12 and repointing S12's placeholder
failure_code at it (R-1/R-2), plus extending R3/R4's trigger lists to cover
the S5/S6 reuse (R-3), will make every rejection code's own trigger
definition match the state(s) that actually emit it, with zero change to
trade acceptance/rejection behavior.

### Expected improvement
Not a performance change — no trade-count, win-rate, or R-multiple
difference is expected or measurable, since no guard condition changes.
The only measurable difference is rejection-log code accuracy (100% of S12
rejections currently mislabeled as R5; 0% after the fix).

### Success criteria
Re-run S1-G1C structural checks against v1.0.1: same PASS result, with
R-1/R-2/R-3 closed (not merely tracked) and GR-1 folded into the migration.

### Rollback criteria
If re-running S1-G1C against v1.0.1 finds any new structural, cross-link,
or determinism defect introduced by the patch, revert to v1.0.0 as the
active frozen spec and re-open R-1/R-2/R-3 as tracked residuals pending a
corrected patch.
```

---

## Approval Status

- **Technical review: PASS.** All three findings verified accurate; one
  minor migration-scope gap (GR-1) found and should be folded in.
- **Governance approval: NOT YET GRANTED.** This report is written by the
  same agent that authored the patch recommendation being reviewed — that
  makes it a rigorous technical check, not an independent or ownership-level
  approval. Per `MASTER_PLAN.md`'s hard rules, only the owner can approve a
  strategy revision.
- **Spec state: unchanged.** `specs/st-c3_v1.0.0.yaml` remains the sole
  frozen ST-C3 spec. No `v1.0.1` file exists yet.
- **Next action:** owner decision on whether to approve R-1/R-2/R-3 (with or
  without the R-3 alternative, and with GR-1 folded in) before the draft RCR
  above is filed and `specs/st-c3_v1.0.1.yaml` is cut. Stage 2 onward
  (spec freeze, S1-G1C rerun) does not begin until that decision is made.
  Stages 3-8 (implementation conformance, replay, statistics, robustness,
  demo, production) remain additionally gated by their own separate
  authorizations per `NEXT_ACTION.md`/`PROJECT_STATUS.md`, regardless of this
  report's outcome.
