# ST-C3 S1-G1C Rerun Report — v1.0.1

**Reruns:** the structural-completeness checks from
[`ST-C3_S1-G1C_LOGIC_CONFORMANCE_REPORT.md`](ST-C3_S1-G1C_LOGIC_CONFORMANCE_REPORT.md)
against `specs/st-c3_v1.0.1.yaml` instead of `specs/st-c3_v1.0.0.yaml`.
**Trigger:** owner approval (2026-07-25) of
[`ST-C3_v1.0.1_PATCH_RECOMMENDATION.md`](ST-C3_v1.0.1_PATCH_RECOMMENDATION.md),
confirmed sound by [`GOVERNANCE_REVIEW_REPORT.md`](GOVERNANCE_REVIEW_REPORT.md).
**Result: PASS. R-1, R-2, R-3, and GR-1 are CLOSED (not merely tracked).**

---

## Executive Summary

`specs/st-c3_v1.0.1.yaml` was cut from `specs/st-c3_v1.0.0.yaml` with exactly
the four approved diffs (new `R8` code, `S12` failure-code repoint in all
three representations, `R3`/`R4` trigger-list extensions) and nothing else.
Re-running the S1-G1C structural checks confirms: all prior PASS results
still hold (16/16/16 structural invariants, evidence-chain integrity,
cross-link integrity, freeze-state integrity, validator readiness), and the
three previously-tracked rejection-code findings plus the governance
review's migration gap are now closed rather than tracked. No new defect was
introduced by the revision.

Per success criteria stated in the patch recommendation and the RCR entry:
"same PASS result, with R-1/R-2/R-3 closed (not merely tracked) and GR-1
folded into the migration" — **met**.

---

## Re-Verification Against Original Audit Sections

### Structural Completeness (original §4 / audit Sections 3.1-3.4)

- Evidence objects: 16 (unchanged; confirmed by direct count in
  `specs/st-c3_v1.0.1.yaml` `evidence:` registry — same 16 names, same
  order as v1.0.0).
- States: 16 (unchanged).
- Transitions: 16 (unchanged).
- Reference integrity: unchanged — no evidence type, state, or transition
  was added, removed, or renamed by this revision. **Status: PASS.**

### Evidence Chain Integrity (original §5)

- S13 chain: unchanged, still consumes the same 15 pre-entry evidence
  objects in the same order. **Status: PASS.**
- Evidence bindings: unchanged except `S12_RISK_SLTP.reject`
  (`R5_NO_FVG_OB_CONFLUENCE` -> `R8_INVALID_RISK_OR_TARGET`) — a rejection
  code label change, not a binding/consumption/production change.
  **Status: PASS.**

### Rejection & Termination Mapping (original §6) — where the fixes land

**R-1: CLOSED.** `S12_RISK_SLTP` now rejects with `R8_INVALID_RISK_OR_TARGET`
in both `evidence_bindings.S12_RISK_SLTP.reject` and
`validator_rules.state_rules.S12_RISK_SLTP.reject`
(`specs/st-c3_v1.0.1.yaml` lines 658, 744). `R8`'s own `triggers:` list
(`invalidation_swing_undefined_or_ambiguous`, `no_valid_target_evidence`,
`computed_rr_below_min_rr`) accurately names the S12 guard's own failure
modes — the mislabeling as an FVG/OB confluence failure no longer exists.
No occurrence of `R5_NO_FVG_OB_CONFLUENCE` remains anywhere in the `S12`
context (verified by direct grep — zero matches).

**R-2: CLOSED.** `state_machine.transitions` `S12` entry's `failure_code` is
now the literal code `R8_INVALID_RISK_OR_TARGET`
(`specs/st-c3_v1.0.1.yaml` line 573), replacing the placeholder string
`appropriate_r_code_for_risk_or_target_rule_failure`. All three
representations of S12's failure code (`transitions`, `evidence_bindings`,
`validator_rules`) are now identical — the internal self-contradiction is
resolved.

**R-3: CLOSED.** `rejection_codes.ST-C3-R3.triggers` gained
`bos_extreme_pullback_not_detected` and `rejection_codes.ST-C3-R4.triggers`
gained `dealing_range_invalid_or_undefined`. `S5_BOS_EXTREME_LOCK`'s reuse
of `R3` and `S6_DEALING_RANGE`'s reuse of `R4` are now justified by their
target code's own trigger list, matching the pattern already used correctly
by the `S3`->`R2` and `S10`->`R6` reuse cases.

**Unmapped-code audit:** still zero — 8 R-codes (`R1`-`R8`), each referenced
by at least one state, none defined-but-unused, none referenced-but-undefined.
**Status: PASS**, no residual findings.

**Determinism audit for codes:** guard-level determinism still holds
(unchanged). Code-level diagnostic distinguishability, previously a GAP for
`R3`/`R4`/`R5` (S12's mislabeling, S5/S6's unjustified reuse), is now
resolved: every code's trigger list matches every state that emits it.
**Status: PASS (both guard-level and code-level).**

### Cross-Link Integrity (original §7)

- All R-code and ERR-code references across `specs/st-c3_v1.0.1.yaml`,
  `ST-C3_REJECTION_CODE_SPEC.md`, `ST-C3_STATE_MACHINE.md`,
  `ST-C3_EVIDENCE_BINDINGS.md`, and `ST-C3_VALIDATOR_RULES.md` point to
  codes that exist and match the v1.0.1 revision. Verified each of the four
  companion docs was updated in lockstep with the spec (S12's
  `R8_INVALID_RISK_OR_TARGET`; `R3`/`R4` trigger additions documented in
  `ST-C3_REJECTION_CODE_SPEC.md`).
- **GR-1: CLOSED.** `ST-C3_STATE_MACHINE.md`'s transition-table row for
  `S12` (previously the prose placeholder "Appropriate R-code if any risk
  or target rule fails," itself an unlinked description) now names the real
  code `R8_INVALID_RISK_OR_TARGET`, matching the other three companion
  docs and the YAML. This was the migration-scope gap the governance review
  found and folded into this revision.
- No new missing artifact: `governance/st_c3_stage_status.yaml` (G-4) was
  already closed prior to this revision. **Status: PASS.**

### Determinism Verification (original §8)

- Funnel lifecycle, state machine, evidence chain, trade-plan emission,
  expiry logic: all unchanged, still deterministic. **Status: PASS.**
- Rejection/ERR mapping: previously "deterministic at the guard level; not
  fully deterministic at the code level." **Now fully deterministic at both
  levels** — every guard failure emits exactly one code, and every code's
  trigger definition uniquely identifies the guard(s) that emit it.
  **Status: PASS (upgraded from partial).**

### Freeze-State Integrity (original §9)

- `strategy_frozen = true`, `engine_implements_spec = false`,
  `implementation_authorization = null`: all confirmed unchanged in
  `specs/st-c3_v1.0.1.yaml` (lines 42-44 equivalent block).
- No mutation of `specs/st-c3_v1.0.0.yaml`: confirmed — v1.0.0 remains on
  disk unchanged, preserved as historical record; v1.0.1 is a new file.
- Execution/demo/live/production remain BLOCKED — unaffected by this
  revision. **Status: PASS.**

### Validator Readiness (original §10)

- All state rules present, no duplicates, no missing/deprecated ID
  references. `S12_RISK_SLTP`'s rule now references `R8`, which is itself
  fully defined in `rejection_codes` and `rejection_code_json_schema`.
  **Status: PASS**, `R8` reuse/mapping gap from original §10.5/10.8 closed.

---

## Gap Analysis — Delta From Original Audit

| ID | Original severity | v1.0.1 status |
|---|---|---|
| R-1 | Significant | **CLOSED** |
| R-2 | Internal inconsistency | **CLOSED** |
| R-3 | Minor | **CLOSED** |
| G-4 | Preparation gap | **CLOSED** (prior to this revision, via `governance/st_c3_stage_status.yaml`) |
| GR-1 | Minor (found during governance review, not the original audit) | **CLOSED** |

- Structural gaps: none (unchanged from original audit).
- Determinism gaps: **none** (was R-1/R-2/R-3; now closed).
- Mapping gaps: **none** (was mismapped R-1/R-3; now closed).
- Cross-link gaps: **none** (was G-4/GR-1; now closed).
- Validator gaps: **none** (inherited R-1/R-2/R-3 from state_rules; now closed).
- Freeze-state violations: none.

**Critical findings: 0. Major findings: 0.** Matches the expected result
stated in the patch recommendation's Stage 2 acceptance criteria.

---

## Final Assessment

- All checklist items from the original S1-G1C audit re-verified PASS
  against `specs/st-c3_v1.0.1.yaml`.
- Zero critical or major findings remain.
- `specs/st-c3_v1.0.0.yaml` preserved unchanged as historical record;
  `specs/st-c3_v1.0.1.yaml` is now the active frozen ST-C3 spec.
- Implementation authorization remains: **null**.
- Strategy remains frozen; this rerun confirms structural/diagnostic
  correctness only — it does not itself authorize S1-G2.
- Current governance position: **A1 -> S1-G1C CLOSED (v1.0.1)**.

## What This Rerun Does NOT Do

- Does not authorize A2/S1-G2 reference implementation. That is a separate
  owner decision, gated on its own criteria (per `NEXT_ACTION.md`/
  `PROJECT_STATUS.md`), not automatically unlocked by a clean S1-G1C rerun.
- Does not touch detection logic, thresholds, or any file outside the
  rejection-code diagnostic layer and its four companion docs.
- Does not run backtesting, replay, demo, or production work — all remain
  BLOCKED regardless of this result.

## Next Action

Owner decision on whether to open A2/S1-G2 (Reference Implementation
Authorization) as a new milestone in `NEXT_ACTION.md`. Until that decision is
made and recorded, ST-C3 remains at S1-G1C-closed / A2-not-yet-opened, and no
implementation, backtest, replay, demo, or production work is authorized.
