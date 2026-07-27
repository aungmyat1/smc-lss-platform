# ST-C3 v1.x Funnel Freeze and R-18 Closure

**Date:** 2026-07-27
**Type:** Owner decision (scope freeze), governance labeling only. No
change to `specs/st-c3_v1.0.7.yaml`'s frozen state machine, evidence
registry, or trade-plan schema. No code written or modified.

---

## The decision

The owner chose, explicitly and directly, to freeze the v1.x reference
funnel's implemented scope at the 9 stages already built
(`validation/st_c3/detection.py`: S1, S2, S3, S4, S5, S6, S8, S10, S11),
rather than pursue owner decisions for S7 (OTE), S9 (LTF confirmation),
and S12 (risk/SL/TP) to reach the full 12.

**What this is:** a decision that no further v1.x reference-implementation
work will be done on S7/S9/S12, and that R-18 is closed on that basis.
**What this is NOT:** a redefinition of the frozen strategy. The 16-state
machine in `specs/st-c3_v1.0.7.yaml` is unchanged — it still specifies
S7/S9/S12 exactly as before. This decision does not alter what a valid
ST-C3 `TRADE_PLAN` requires (a real stop-loss and targets from S12 remain
mandatory in the frozen spec); it only closes out the *reference
implementation and R-18 research question* for v1.x, acknowledging that a
`TRADE_PLAN` can never actually be emitted under the current 9-stage
implementation.

## Why R-18 = 0, and why this is not a fabricated stub result

`S0-S13` are strictly sequential — `priority_rules.no_state_can_be_skipped_or_revisited`.
S7 (OTE) is the earliest of the three out-of-scope stages in that
sequence, immediately after the now-implemented S6 (dealing range). If
S7's evidence is treated as permanently unsatisfiable (no owner-ratified
OTE band exists, and none will be pursued under this freeze), then **every
candidate setup is rejected at S7, unconditionally, before S8, S9, S10,
S11, or S12 are ever reached** — regardless of how often the real,
implemented S8/S10/S11 logic would otherwise pass.

This is why no literal `EvidenceBundle`/`run_kernel()` pass was executed
to "prove" this number: doing so would always halt at S7 and would not
exercise the real S8/S10/S11 detection code at all, making such a run
computationally real but substantively empty — it would report
`R4_NO_OTE_PULLBACK` for 100% of candidates by construction, telling us
nothing beyond what this reasoning already establishes. Running it would
not make the `0` more true; it would just spend real compute reproducing
a result already known from the state machine's own sequencing rule.

**R-18 (`existence_check_floor`) = 0.0, closed by this logical necessity**,
not by a code run. This is accepted as R-18's final, honest v1.x answer:
the reference implementation, as scoped, cannot ever reach `TRADE_PLAN_EMIT`.

## What this does and does not authorize

- **Closes R-18** at `0.0` for the v1.x reference-implementation scope.
- **Accepts S1-G2** (Reference Implementation Authorization and Completion
  Review) on this basis — see `governance/st_c3_stage_status.yaml` for the
  updated status. This reverses the S1-G2 completion audit's earlier
  "remain open" recommendation, per the owner's explicit choice of the
  freeze path that audit identified as one of the two routes to acceptance.
- **Does NOT authorize A3.** A3 opening remains a separate, explicit future
  owner decision, per every prior governance record this session
  (including the rejection of the quarantined line's "A3 OPENED" claim).
  Accepting S1-G2 unblocks S1-G3 as the next *possible* gate to pursue —
  it does not itself open S1-G3, A3, execution, optimization, demo, or
  live trading.
- **Does NOT authorize S1-G3 work to begin.** S1-G3 (Primitive and
  Indicator Conformance) is no longer blocked by an unaccepted S1-G2, but
  starting it is its own separate decision, not implied by this one.
- **Does NOT change `specs/st-c3_v1.0.7.yaml`.** S7/S9/S12 remain
  specified exactly as before, `UNRESOLVED`/blocked. If a future v1.1 or
  v2.x cycle wants to pursue them, it does so as a fresh decision, not a
  reversal of this freeze (this freeze only says "not now, not under
  v1.x's reference-implementation effort" — it does not permanently
  forbid a future revision from taking it up).

## Verification performed

- Confirmed the sequencing argument against `specs/st-c3_v1.0.7.yaml`'s
  `state_machine.priority_rules` (`no_state_can_be_skipped_or_revisited`)
  and the `S1_HTF_BIAS...S12_RISK_SLTP` guard order — S7 genuinely
  precedes S8/S9/S10/S11/S12, so its permanent failure is dispositive for
  the whole chain.
- Confirmed `validation/st_c3/detection.py` and `specs/st-c3_v1.0.7.yaml`
  are unmodified by this decision — checked no diff exists against either
  after this report was written.
- Confirmed this decision was the owner's own explicit choice between two
  clearly-presented alternatives (governance-labeling-only vs. an actual
  state-machine restructure), not inferred or defaulted.

## Deliverables

- This report.
- `reports/validation/st_c3/OWNER_DECISION_LOG.md` — freeze decision and
  R-18 closure entry added.
- `reports/validation/st_c3/RESOLUTION_MATRIX.md` — R-18 row updated to
  `Resolved` (closed at `0.0`, by sequencing necessity).
- `governance/st_c3_stage_status.yaml` — `a2_signal_conformance.status`
  updated to `passed`; `existence_check_r18.status` updated to `closed`.
- `NEXT_ACTION.md`, `PROJECT_STATUS.md`, `MASTER_PLAN.md` — updated to
  reflect S1-G2 acceptance and R-18 closure, with A3/execution/demo/live
  remaining exactly as blocked as before.
