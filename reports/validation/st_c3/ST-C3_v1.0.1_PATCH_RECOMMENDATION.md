# ST-C3 v1.0.1 Patch Recommendation

**Status:** Recommendation only — NOT APPLIED. No file under `specs/st-c3_v1.0.0.yaml`
or `docs/strategy/st_c3/` has been modified by this document.
**Origin:** Directly requested by
[`ST-C3_S1-G1C_LOGIC_CONFORMANCE_REPORT.md`](ST-C3_S1-G1C_LOGIC_CONFORMANCE_REPORT.md)
§13, which found ST-C3 v1.0.0 "CONDITIONALLY READY" for S1-G1C but flagged
four tracked residuals (R-1, R-2, R-3, G-4) that should be resolved via a
governance-approved revision before A2/S1-G2 authorization.
**Authority:** `MASTER_PLAN.md` Governance Rule 6/7 ("approved strategies are
immutable... every strategy revision requires a new candidate version").
`specs/st-c3_v1.0.0.yaml` is frozen; this document proposes the content of a
`v1.0.1` revision. It does not freeze, apply, or authorize that revision —
only the owner can accept this recommendation and instruct the revision to be
cut.

---

## Why this is a patch recommendation, not a bug-fix edit

`docs/RESEARCH-CHARTER.md` requires a pre-registered change process for any
change to `specs/*.yaml` unless it is a pure implementation bug fix against an
already-agreed spec. R-1 and R-3 add or reinterpret rejection-code semantics
— judgment calls a second engineer could reasonably read as a design
decision, not a typo fix — so they are routed through this recommendation
rather than silently patched. R-2 is closer to a pure internal-consistency
fix (the frozen file contradicts itself about what `S12` already emits), but
is bundled here because its resolution depends on which R-1 fix is accepted.

No detection logic (BOS/CHoCH/sweep/OTE/FVG/session thresholds) changes in
any proposal below. All three findings are confined to the diagnostic
rejection-code layer — what a rejected trade is *labeled* as, not what causes
rejection or how a trade is built.

---

## R-1 (significant) — dedicated code for `S12_RISK_SLTP` failures

**Problem:** `S12_RISK_SLTP` (structural stop + TP1/TP2/TP3 + `RR >= MIN_RR`
guard) is coded as `R5_NO_FVG_OB_CONFLUENCE` in
`evidence_bindings.S12_RISK_SLTP.reject` and
`validator_rules.state_rules.S12_RISK_SLTP.reject`. `R5`'s own `triggers:`
list is exclusively about FVG/OB confluence (stage 8). A spec-faithful
validator would log every RR/stop/target failure as "Rejected: No valid
FVG/OB confluence," which is factually wrong.

**Recommended patch:** add a new rejection code, `ST-C3-R8`
(`R8_INVALID_RISK_OR_TARGET`), and repoint `S12_RISK_SLTP` at it.

```yaml
# rejection_codes: — new entry, inserted after ST-C3-R7
  ST-C3-R8:
    local_code: R8_INVALID_RISK_OR_TARGET
    meaning: invalid_risk_or_target_construction
    message: "Rejected: No valid structural stop, target, or minimum RR."
    stage: risk_sl_tp_build_stage
    triggers:
      - invalidation_swing_undefined_or_ambiguous
      - no_valid_target_evidence
      - computed_rr_below_min_rr
    reason: risk_or_target_construction_failed

# rejection_code_json_schema.R_CODES: — new entry
    R8_INVALID_RISK_OR_TARGET: "Rejected: No valid structural stop, target, or minimum RR."

# evidence_bindings.S12_RISK_SLTP.reject: R5_NO_FVG_OB_CONFLUENCE
#   -> R8_INVALID_RISK_OR_TARGET

# validator_rules.state_rules.S12_RISK_SLTP.reject: R5_NO_FVG_OB_CONFLUENCE
#   -> R8_INVALID_RISK_OR_TARGET
```

This makes 8 R-codes total (`R1`-`R8`). `S1_G1C` checklist counts (16
evidence objects / 16 states / 16 transitions) are unaffected — this only
adds a rejection-code registry entry, not a state, evidence object, or
transition.

## R-2 (internal inconsistency) — remove the placeholder `failure_code`

**Problem:** `state_machine.transitions` (the `S12` entry) gives
`failure_code: appropriate_r_code_for_risk_or_target_rule_failure` — a
descriptive placeholder, not a real code — while `evidence_bindings` and
`validator_rules` in the same file hard-code a real code for the same guard.
The frozen file disagrees with itself.

**Recommended patch:** once R-1 is accepted, replace the placeholder with
the same real code used everywhere else:

```yaml
# state_machine.transitions, state: S12
      failure_code: appropriate_r_code_for_risk_or_target_rule_failure
#     -> failure_code: R8_INVALID_RISK_OR_TARGET
```

This closes the self-contradiction: all three representations of `S12`'s
failure code (`transitions`, `evidence_bindings`, `validator_rules`) become
identical, matching the pattern already used correctly by every other state.

## R-3 (minor) — justify or fix the S5/S6 code reuse

**Problem:** `S5_BOS_EXTREME_LOCK` reuses `R3_NO_DISPLACEMENT_BOS` and
`S6_DEALING_RANGE` reuses `R4_NO_OTE_PULLBACK`, but neither code's own
`triggers:` list names the actual failure condition at that state (missing
pullback detection; malformed dealing range). This is the same class of
diagnostic ambiguity as R-1, but lower severity because the reused stage is
adjacent/related rather than unrelated.

**Recommended patch (trigger-list amendment, not new codes):** extending
`R3`/`R4`'s own `triggers:` lists to explicitly cover the reused state is
lower-cost than adding two more rejection codes (which would grow the
registry from 7/8 to 9/10 codes for what the audit itself called a "minor,
pattern inconsistency," not a missing-code gap like R-1):

```yaml
# rejection_codes.ST-C3-R3.triggers — add:
      - bos_extreme_pullback_not_detected   # covers S5_BOS_EXTREME_LOCK reuse

# rejection_codes.ST-C3-R4.triggers — add:
      - dealing_range_invalid_or_undefined  # covers S6_DEALING_RANGE reuse
```

**Alternative (rejected as the default, offered for owner choice):** add
dedicated `R3b`/`R4b`-style codes instead of extending trigger lists. This
would fully eliminate code-level ambiguity (every guard gets its own code)
at the cost of two more registry entries and two more validator branches for
a finding the audit rated "minor." Recommend the trigger-list amendment
unless the owner wants full 1:1 guard-to-code granularity as a standing
policy for future ST-C3 states too.

## G-4 (preparation gap) — governance stage-status parity file

Not a spec change; addressed separately below as a non-strategy governance
artifact (see "Companion artifact created now").

---

## Net effect of R-1/R-2/R-3 if accepted

- Rejection codes: 7 -> 8 (`R1`-`R8`).
- `S12_RISK_SLTP` gets a diagnostically correct, internally consistent code
  across all three representations (`transitions`, `evidence_bindings`,
  `validator_rules`).
- `S5`/`S6` reuse becomes trigger-justified instead of unexplained.
- No evidence object, state, or transition count changes (16/16/16 preserved).
- No entry/exit/session/RR threshold changes — `MIN_RR`, OTE zone, session
  windows, and all other tunable values are untouched.
- No `engine_implements_spec`/`implementation_authorization` change — both
  remain `false`/`null` until a future, separately authorized gate.

## What this recommendation does NOT do

- Does not edit `specs/st-c3_v1.0.0.yaml` or any `docs/strategy/st_c3/*.md`
  file. All diffs above are proposed text for a future `v1.0.1`, not applied
  changes.
- Does not authorize S1-G2 reference implementation, backtesting, replay,
  demo, or production. Those remain BLOCKED per `NEXT_ACTION.md` and
  `PROJECT_STATUS.md` regardless of this recommendation's disposition.
- Does not constitute owner approval. It is the analysis an owner needs to
  decide whether to instruct a `v1.0.1` revision to be cut.

## Required next steps (in order, only after owner review)

1. Owner reviews and accepts/rejects/amends the R-1/R-2/R-3 proposals above
   (and the R-3 alternative, if preferred).
2. If accepted: file an RCR-style entry in `reports/research_log.md`
   recording this as a pre-registered, non-behavioral rejection-code fix
   (per `docs/RESEARCH-CHARTER.md`'s bug-fix carve-out reasoning above).
3. Cut `specs/st-c3_v1.0.0.yaml` -> `specs/st-c3_v1.0.1.yaml` as a new frozen
   candidate version with only the accepted diffs applied; update
   `docs/strategy/st_c3/ST-C3_EVIDENCE_BINDINGS.md` and
   `ST-C3_VALIDATOR_RULES.md` and `ST-C3_REJECTION_CODE_SPEC.md` to match.
4. Re-run S1-G1C structural checks against `v1.0.1` (expected: same PASS
   result, with R-1/R-2/R-3 now closed instead of tracked).
5. Only then does A2/S1-G2 reference-implementation authorization become a
   live decision — this recommendation does not itself grant it.

---

## Companion artifact created now

`governance/st_c3_stage_status.yaml` is added alongside this report to close
G-4 (governance-tooling parity with `governance/st_c2_stage_status.yaml`).
This is a status-tracking artifact, not strategy logic or a specs/*.yaml
file, so it does not require the RCR gate above — it records the same facts
already stated in `NEXT_ACTION.md`/`PROJECT_STATUS.md` in the machine-readable
form ST-C2 already uses.
