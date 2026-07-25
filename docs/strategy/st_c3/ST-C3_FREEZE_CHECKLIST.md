# ST-C3 Freeze Checklist

**Strategy ID:** ST-C3
**Status:** Completed by `docs/strategy/st_c3/ST-C3_FREEZE_ACTION_LOG.md`

This is the official list of requirements that were satisfied before ST-C3
transitioned from pre-freeze exploratory setup to a frozen, validation-ready
strategy candidate.

---

## 1. Core Strategy Artifacts

Each artifact must be present, validated, committed, clean, cross-linked, and
referenced in project governance metadata.

- [x] Strategy Architecture:
  `docs/strategy/st_c3/ST-C3_STRATEGY_ARCHITECTURE.md`
- [x] Funnel Lifecycle:
  `docs/strategy/st_c3/ST-C3_FUNNEL_LIFECYCLE.md`
- [x] Evidence Object Specification:
  `docs/strategy/st_c3/ST-C3_EVIDENCE_OBJECT_SPEC.md`
- [x] Rejection and Termination Code Specification:
  `docs/strategy/st_c3/ST-C3_REJECTION_CODE_SPEC.md`
- [x] State Machine, 16 states and 16 transitions:
  `docs/strategy/st_c3/ST-C3_STATE_MACHINE.md`
- [x] Trade-Plan Object Schema:
  `docs/strategy/st_c3/ST-C3_TRADE_PLAN_SCHEMA.md`
- [x] Parameter Sheet:
  `docs/strategy/st_c3/ST-C3_PARAMETER_SHEET.md`
- [x] Evidence Binding Layer:
  `docs/strategy/st_c3/ST-C3_EVIDENCE_BINDINGS.md`
- [x] Validator Rules:
  `docs/strategy/st_c3/ST-C3_VALIDATOR_RULES.md`
- [x] Proposed Execution Agent Specification:
  `docs/strategy/st_c3/ST-C3_EXECUTION_AGENT_SPEC.md`
- [x] Backtest Specification:
  `docs/strategy/st_c3/ST-C3_BACKTEST_SPEC.md`

---

## 2. YAML Specification Requirements

`specs/st-c3_v1.0.0.yaml` must include:

- [x] `evidence` registry with all 16 evidence objects.
- [x] `state_machine` full ST-C3 FSM.
- [x] `rejection_codes` for R1-R7.
- [x] `termination_codes` for ERR codes.
- [x] `trade_plan` schema emitted at S13.
- [x] `parameters` summary for `N_SWEEP`, `MAX_ENTRY_BARS`, OTE min/max,
  sessions, and RR.

Validation checks:

- [x] YAML parses cleanly after final freeze edits.
- [x] No missing references found by local structural checks.
- [x] No dangling evidence IDs found by local structural checks.
- [x] No unused states or transitions found by local structural checks.

---

## 3. Governance Metadata Files

These files must explicitly reference ST-C3 status, artifacts, and next
governance step:

- [x] `NEXT_ACTION.md`
- [x] `PROJECT_STATUS.md`
- [x] `ROADMAP.md`
- [x] `STRATEGY_INDEX.md` if present; no such file exists at the time this
  checklist was created.

Required status language before the freeze action:

```text
ST-C3 status: PRE-FREEZE -> READY FOR FREEZE
```

This status meant freeze-ready preparation, not frozen approval. The freeze
approval is now recorded in `ST-C3_FREEZE_ACTION_LOG.md`.

---

## 4. Worktree And Repo Hygiene

Before freeze:

- [ ] Clean worktree after freeze commit.
- [ ] No uncommitted changes after freeze commit.
- [ ] No mixed ST-C2 logic.
- [ ] No experimental files outside `docs/strategy/st_c3/` or approved ST-C3
  governance/spec files.
- [ ] `git diff --check` is clean.
- [ ] No trailing whitespace.
- [ ] No merge conflict markers.

---

## 5. Freeze Preconditions

ST-C3 must satisfy:

- [x] Deterministic funnel lifecycle.
- [x] Deterministic state machine.
- [x] Deterministic evidence chain.
- [x] Deterministic rejection/ERR mapping.
- [x] Deterministic trade-plan output.
- [x] Deterministic expiry logic.

If any part is non-deterministic, freeze is blocked.

---

## 6. Freeze-Ready Validation Checklist

All must be true before the freeze action:

- [x] Architecture complete.
- [x] Lifecycle complete.
- [x] Evidence spec complete.
- [x] Rejection/ERR codes complete.
- [x] State machine complete.
- [x] Trade-plan schema complete.
- [x] YAML spec validated for the freeze changeset.
- [ ] Repo hygiene validated in the final freeze commit.
- [x] Governance metadata updated.
- [x] No missing artifacts.
- [x] No cross-candidate contamination by design.
- [x] ST-C3 is isolated from ST-C2 by lineage and guardrails.

---

## 7. Freeze Action

Once every checklist item is complete and the owner explicitly approves the
freeze act, governance may freeze ST-C3 and lock all strategy artifacts.

Target transition:

```text
ST-C3 status: FROZEN -> READY FOR VALIDATION
```

This is the moment ST-C3 becomes a frozen strategy candidate. This checklist
does not perform that transition by itself.
