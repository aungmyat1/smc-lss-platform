# S1-G5 Readiness Checklist — ST-C3

**Date:** 2026-07-27
**Note on precedent:** modeled on `S1_G3_READINESS_CHECKLIST.md`. A pasted
message proposed an elaborate 5-category (A-E) required-evidence
structure for S1-G5 ("signal-generation conformance," "trade-plan schema
conformance," "signal-to-plan transition legality," "plan
expiry/invalidation," "duplicate-prevention") — verified against
`MASTER_PLAN.md` and found **not present there**. The real S1-G5 section
(`MASTER_PLAN.md`, "A2 / S1-G5 - Signal and Trade-Plan Conformance") has
no "Required evidence" bullet list at all, unlike S1-G3/S1-G4 — only a
one-line Purpose statement, quoted verbatim below. This checklist is built
from that actual text, not the invented structure.

## 1. Purpose

Per `MASTER_PLAN.md`, S1-G5's stated purpose is:

> verify BUY/SELL, entry, stop, target, RR, expiration, source event IDs,
> and rejection reasons match the frozen strategy contract.

This checklist evaluates whether ST-C3 satisfies the prerequisite for
S1-G5. It does not authorize, open, or accept the gate — it records
current readiness only, and it does not itself define S1-G5's evidence
categories in detail; that is future evidence-gathering work's job, done
against this one-line purpose statement and the frozen
`specs/st-c3_v1.0.7.yaml`'s `trade_plan.schema`, not an invented checklist.

## 2. Precondition for S1-G5

| Precondition | Status |
|---|---|
| S1-G4 completion audit produced | Done — `S1_G4_EVENT_STATE_CONFORMANCE_COMPLETION_AUDIT.md` |
| S1-G4 accepted | Done — owner decision, 2026-07-27, see `governance/st_c3_stage_status.yaml` `a2_signal_conformance.s1_g4_gate` |

**This precondition is met.** Unlike the S1-G3 checklist (written before
S1-G2 was accepted, and correctly found S1-G3 not ready), S1-G5's sole
blocking precondition is already satisfied.

## 3. Evidence Summary (supporting context, not independent gates)

- **Trade-plan schema:** frozen and unchanged in `specs/st-c3_v1.0.7.yaml`
  (`trade_plan.schema`); `validation/st_c3/trade_plan.py`'s `TradePlan`
  dataclass and `kernel.py`'s `_emit_trade_plan()` already construct it
  from evidence at S13 — this is what S1-G5 evidence-gathering would
  examine, not new code to write.
- **Golden-case coverage:** `test_golden_cases.py` already asserts
  direction, entry zone, SL price, targets, and RR on emitted trade plans
  for both LONG and SHORT — a starting point for S1-G5, not a
  substitute for it (S1-G5 evidence-gathering would need to state this
  coverage explicitly against the purpose statement above, the way
  S1-G3/S1-G4's reports did for their own categories).
- **Test suite:** 340 passed, 0 failed (full repo run, confirmed
  2026-07-27 after S1-G4's evidence work).
- **Spec:** `specs/st-c3_v1.0.7.yaml` frozen; unchanged by S1-G2/S1-G3/S1-G4
  acceptance.
- **Governance sync:** `MASTER_PLAN.md` (v4.1.7), `PROJECT_STATUS.md`,
  `governance/st_c3_stage_status.yaml`, `OWNER_DECISION_LOG.md`,
  `NEXT_ACTION.md` all reflect S1-G4's acceptance consistently as of this
  checklist.
- **Quarantine:** `specs/st-c3_v1.0.6.yaml` and its evidence-builder/A3
  replay artifacts remain preserved but non-authoritative; not used as
  evidence anywhere in this checklist.

## 4. Readiness Evaluation

**ST-C3 is ready for S1-G5 evidence-gathering to begin, if the owner
chooses to start it.** The sole blocking precondition (S1-G4 acceptance)
is satisfied. Readiness is not the same as starting — per this session's
established pattern (S1-G2 -> S1-G3, S1-G3 -> S1-G4), beginning S1-G5
work is its own separate, explicit owner decision, not automatic from
this checklist.

## 5. Next Actions (owner decisions, not inferred)

If the owner directs beginning S1-G5:

1. Derive concrete evidence categories directly from the one-line purpose
   statement above (BUY/SELL direction, entry, stop, target, RR,
   expiration, source event IDs, rejection reasons) and the frozen
   `trade_plan.schema` — not from the invented A-E structure in the
   pasted message.
2. Identify what's already covered by `test_golden_cases.py`/`test_negative_cases.py`
   versus what needs new, dedicated tests (similar to how S1-G4's
   expiry/invalidation and duplicate-prevention categories had zero prior
   coverage before that session's work).
3. Produce `S1_G5_SIGNAL_TRADE_PLAN_CONFORMANCE_REPORT.md`, then (if the
   owner wants a recommendation) a completion audit — same two-artifact
   pattern as S1-G3/S1-G4.
4. Acceptance remains a separate, explicit owner decision after that.

Neither is chosen by this checklist.

## 6. Agent Notes

- No lifecycle, execution, or A3 logic was introduced or referenced.
- No content from the quarantined v1.0.6 line was used as evidence.
- No new R-number, spec field, or governance file status was created or
  changed by this checklist — it is a read-only evaluation.
- No gate was opened, accepted, or escalated.
- The pasted 5-category (A-E) evidence structure was explicitly rejected
  as not present in `MASTER_PLAN.md` and is not used here.
