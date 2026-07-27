# NEXT_ACTION.md

**One milestone at a time. This is the active milestone.**

## ST-C3 A2/S1-G4 ACCEPTED, A2/S1-G5 NOT YET STARTED — Active Milestone

Current lifecycle position:

| Field | State |
|---|---|
| Stage | Stage A - Strategy Validation |
| Substage | A2 - Indicator, Event and Signal Conformance (S1-G2, S1-G3, S1-G4 accepted; S1-G5-S1-G6 not started) |
| Gate | S1-G4 Event and State Conformance — **ACCEPTED 2026-07-27** (S1-G2/S1-G3 remain ACCEPTED 2026-07-27) |
| Strategy | ST-C3 v1.0.7 (fresh R-31/R-32/R-33 decisions, revision of v1.0.5, see `specs/st-c3_v1.0.7.yaml`) |
| Status | FROZEN -> S1-G1C CLOSED -> A2/S1-G2 ACCEPTED (v1.x funnel frozen at 9/12 stages) |
| Readiness | GREEN |
| Frozen | YES |
| Implementation | AUTHORIZED: S1-G2 SCOPED RESEARCH/VALIDATION ONLY (unchanged — S1-G2 acceptance does not expand authorization) |
| A1 Logic Conformance | PASSED — see `reports/validation/st_c3/S1-G1C_RERUN_REPORT.md` |
| A2 Signal Conformance | S1-G2 **ACCEPTED** 2026-07-27; S1-G3 **ACCEPTED** 2026-07-27; S1-G4 **ACCEPTED** 2026-07-27 (see below). The broader A2 substage (S1-G5 through S1-G6) is still not started — none of this is the same as passing all of A2. A separate 2026-07-26 "A2 PASSED" claim (conflating a single gate with the full substage) was REJECTED 2026-07-27. |
| A3 Statistical Validation | BLOCKED — a 2026-07-26 "OPEN" claim was REJECTED 2026-07-27. S1-G2 acceptance does not open A3; unaffected. |
| Execution | BLOCKED (explicitly not authorized) |
| Demo | BLOCKED |
| Production | BLOCKED |

## 2026-07-27: v1.x funnel frozen at 9/12 stages; S1-G2 accepted; R-18 closed

**Owner decision:** freeze the v1.x reference-implementation scope at the
9 stages already implemented (S1, S2, S3, S4, S5, S6, S8, S10, S11),
leaving S7 (OTE), S9 (LTF confirmation), and S12 (risk/SL/TP guard
direction) permanently out of scope for v1.x. **Governance labeling only**
— no change to `specs/st-c3_v1.0.7.yaml`'s frozen state machine, evidence
registry, or trade-plan schema, and no code written to fabricate any
result for the three excluded stages.

**R-18 (`existence_check_floor`) is CLOSED at `signal_rate = 0.0`** — not
by running a literal kernel pass (which would trivially always halt at
S7, the earliest of the three excluded stages, without ever exercising
the real S8/S10/S11 detection code), but by the state machine's own
sequential-guard rule: S7 permanently precedes and blocks S8-S12, so 0.0
is a logically necessary, honest closure value. See
`reports/validation/st_c3/V1X_FUNNEL_FREEZE_AND_R18_CLOSURE.md` for the
full reasoning, and `reports/validation/st_c3/OWNER_DECISION_LOG.md`'s
"v1.x funnel freeze and R-18 closure" entry for the decision record.

**S1-G2 (Reference Implementation Authorization and Completion Review) is
ACCEPTED on this basis** — every field on the R-01–R-33 tracker is now
resolved. This does **NOT**:
- pass the broader A2 substage (S1-G3 through S1-G6 have not started);
- authorize A3, execution, optimization, demo, or live trading — each
  remains its own separate future owner decision;
- open S1-G3 — S1-G2 acceptance only removes S1-G3's blocking
  precondition per `MASTER_PLAN.md` ("BLOCKED until S1-G2 completion
  review is accepted"); starting S1-G3 is its own separate decision.
- change `specs/st-c3_v1.0.7.yaml` — S7/S9/S12 remain specified in the
  frozen spec exactly as before, available to a future v1.1/v2.x cycle.

**A2/S1-G2 scope (owner directive, 2026-07-26, unaffected by any of the
above):** authorized — reference-funnel assembly, golden-case tests (Phase
3), negative-case tests (Phase 4), existence-check conformance runs
(now closed, see above), research/validation tasks. **Explicitly NOT
authorized:** execution, optimization, opening A3, demo trading, live
trading, production promotion. See `governance/st_c3_stage_status.yaml`
`a2_signal_conformance.opened`/`s1_g2_gate` for the authoritative record.

## 2026-07-27: S1-G3 (Primitive and Indicator Conformance) evidence-gathering begun

**Owner directive:** begin S1-G3 structural validation (explicit choice,
2026-07-27) now that S1-G2 acceptance removed its blocking precondition
per `MASTER_PLAN.md`.

**This is evidence-gathering only — S1-G3 is NOT declared passed or
accepted.** Whether the evidence below is sufficient to accept S1-G3
remains a separate, explicit owner decision, exactly like the S1-G2
acceptance pattern above.

Evidence built: two new pure-arithmetic primitives in
`validation/st_c3/detection.py` (`compute_rr()` for risk/reward distance,
`premium_discount_zone()` for bare interval-midpoint premium/discount
classification — **not** the S7_OTE gate, and not wired into the kernel or
any funnel stage), plus 13 new fixed-expected-value tests in
`tests/st_c3/test_s1_g3_primitives.py` covering candle body/wick/range,
ATR(1), swings, sessions, risk/reward, and premium/discount against
hand-crafted inputs with manually-verified expected outputs (as distinct
from the existing behavioral/real-data tests in `test_detection.py`).
Point normalization is N/A for ST-C3 (no pip/point threshold exists in the
frozen spec; distinct lineage from ST-C2 per ADR-0004). No broker, time,
network, or mutable-global dependency was confirmed via a static source
check. Full detail: `reports/validation/st_c3/S1_G3_PRIMITIVE_CONFORMANCE_REPORT.md`.

Neither new primitive changes `specs/st-c3_v1.0.7.yaml`, the kernel's guard
sequence, or any `EvidenceBundle` field — both are additive test-support
arithmetic only.

**Completion audit filed:** `reports/validation/st_c3/S1_G3_PRIMITIVE_CONFORMANCE_COMPLETION_AUDIT.md`
finds every MASTER_PLAN.md-required S1-G3 evidence category covered or
correctly N/A (point normalization — no such threshold exists in the
frozen spec) and recommends the evidence is **sufficient for
acceptance**.

**S1-G3 is ACCEPTED (owner decision, 2026-07-27),** on the completion
audit's finding above. This does **NOT**:
- pass the broader A2 substage (S1-G4 through S1-G6 have not started);
- authorize A3, execution, optimization, demo, or live trading — each
  remains its own separate future owner decision;
- change `specs/st-c3_v1.0.7.yaml`, `kernel.py`'s guard sequence, or any
  `EvidenceBundle` field — `compute_rr()`/`premium_discount_zone()` remain
  standalone, unwired arithmetic.

S1-G4 (Event and State Conformance) is now unblocked per `MASTER_PLAN.md`
("BLOCKED until S1-G3 passes") — but starting S1-G4 is its own separate,
not-yet-made owner decision, same pattern as S1-G2 -> S1-G3. See
`governance/st_c3_stage_status.yaml` `a2_signal_conformance.s1_g3_gate`
for the authoritative record.

## 2026-07-27: S1-G4 (Event and State Conformance) evidence-gathering begun

**Owner directive:** begin S1-G4 using `MASTER_PLAN.md`'s real required
evidence (a pasted checklist misstated the categories as
"session-window alignment, swing-state invariants, premium/discount zone
state transitions, RR-state correctness" — none of which are S1-G4's
actual required evidence; the real list is structured evidence for BOS,
CHoCH, liquidity pools, sweeps, reclaim, FVG, POI interaction,
displacement, DOL, plus legal/illegal transition tests, expiry/invalidation
tests, duplicate prevention, and rejection-code evidence).

**This is evidence-gathering only — S1-G4 is NOT declared passed or
accepted.** Whether the evidence below is sufficient to accept S1-G4
remains a separate, explicit owner decision, exactly like the S1-G2/S1-G3
acceptance pattern above.

Evidence built: `tests/st_c3/test_s1_g4_event_state_conformance.py` (23
new tests) covering a structured-evidence-to-spec-field coverage map for
all 10 MASTER_PLAN concepts, legal/illegal transition monotonicity checks,
new expiry/invalidation coverage for `evaluate_expiry()` (had no prior
test coverage), and duplicate-prevention coverage scoped honestly to the
frozen spec's actual mechanism (`SUPERSEDED` -> `ERR_SUPERSEDED_SETUP`) —
no cross-candidate dedup algorithm was invented, since none exists in the
frozen spec. Full detail:
`reports/validation/st_c3/S1_G4_EVENT_STATE_CONFORMANCE_REPORT.md`.

No change to `specs/st-c3_v1.0.7.yaml`, `kernel.py`'s guard sequence, or
any `EvidenceBundle` field — this work only adds tests.

**Completion audit filed:** `reports/validation/st_c3/S1_G4_EVENT_STATE_CONFORMANCE_COMPLETION_AUDIT.md`
finds every MASTER_PLAN.md-required S1-G4 evidence category covered, each
traceable to a real, spec-registered mechanism (no invented dedup or
lifecycle logic), and recommends the evidence is **sufficient for
acceptance**.

**S1-G4 is ACCEPTED (owner decision, 2026-07-27),** on the completion
audit's finding above. This does **NOT**:
- pass the broader A2 substage (S1-G5 through S1-G6 have not started);
- authorize A3, execution, optimization, demo, or live trading — each
  remains its own separate future owner decision;
- change `specs/st-c3_v1.0.7.yaml`, `kernel.py`'s guard sequence, or any
  `EvidenceBundle` field.

S1-G5 (Signal and Trade-Plan Conformance) is now unblocked per
`MASTER_PLAN.md` — but starting S1-G5 is its own separate, not-yet-made
owner decision, same pattern as prior gates. See
`governance/st_c3_stage_status.yaml` `a2_signal_conformance.s1_g4_gate`
for the authoritative record.

## 2026-07-27 correction: a quarantined line of work was rejected

A separate line of work (`specs/st-c3_v1.0.6.yaml`,
`validation/st_c3/evidence_builder.py`, `validation/st_c3/a3_replay_engine.py`)
appeared in this repo's commit history claiming: R-18 resolved
(`signal_rate=0.0`), A2/S1-G2 declared **PASSED**, and A3 **OPENED**. This
file and `PROJECT_STATUS.md` were briefly overwritten to reflect those
claims. An audit (`reports/governance/v1.0.6_RECONCILIATION_AUDIT.md`)
found:

- **Provenance unverifiable.** No conclusive evidence a human authorized
  the A2-PASSED/A3-OPENED decisions; circumstantial signs (an overnight
  commit gap, a configured scheduled-tasks mechanism) suggest possible
  unattended/autonomous execution.
- **Independent technical defects, regardless of provenance:** the
  "A2 PASSED" claim conflates a single gate (S1-G2, reference-implementation
  authorization) with the full A2 substage (S1-G3 through S1-G6, per this
  file's own documented path below); the "R-18 resolved" claim depended on
  `validation/st_c3/evidence_builder.py` hardcoding the still-provisional
  OTE band (`OTE_MIN, OTE_MAX = 0.62, 0.79`) as if frozen.

**Owner decision, 2026-07-27: A2-PASSED and A3-OPENED are REJECTED.** A2
remains in progress (not passed); A3 remains blocked (not open); R-18
remains open. The quarantined files are preserved on disk as historical
record, not deleted, not merged, not authoritative.

**R-31/R-32/R-33's field values were separately reconfirmed with clean
provenance** (owner decision, 2026-07-27, no empirical justification
claimed): `sweep_reclaim_max_bars=2`, `entry_window_bars=4`, session UTC
bounds ratified unchanged. Folded into a fresh `specs/st-c3_v1.0.7.yaml`
(not v1.0.6, which stays quarantined) — see
`reports/governance/st_c3/RCR_ST-C3_v1.0.7_REPORT.md`.

## Objective

S1-G1C logic-conformance preparation is complete for ST-C3. The original
S1-G1C audit against v1.0.0 found three tracked rejection-code findings
(R-1, R-2, R-3); a governance review found one additional migration-scope
gap (GR-1); the owner approved the patch recommendation on 2026-07-25; the
fixes were cut as `specs/st-c3_v1.0.1.yaml` (v1.0.0 preserved unchanged as
historical record); and the S1-G1C structural checks were re-run clean
against v1.0.1 with zero critical/major findings
(`reports/validation/st_c3/S1-G1C_RERUN_REPORT.md`).

Specification Closure resolved 27 of 33 tracked parameter/decision fields
(R-01–R-33, excluding R-11 superseded): 2 items deferred to a possible
v2.x cycle (fixed lot size, instrument selection logic — both later
separately decided as R-21/R-22), 4 proposed architecture changes ruled
out of v1.x scope (break-even, trailing-stop, session-close forced-exit,
dual-timeframe bias confirmation — all deferred to v2.x), and **R-18
(existence-check floor) remains the only unresolved field on the entire
tracker** — a quarantined claim that it was resolved is rejected (see
above); real status is documented in
`reports/validation/st_c3/R18_CLOSURE_REPORT.md`.

The owner opened A2/S1-G2 on 2026-07-26 with the scoped authorization
above. This milestone authorizes assembling a scoped ST-C3 reference
funnel for golden/negative-case testing and existence-check research — it
does NOT authorize execution, optimization, A3 opening, demo, live, or
production work, which all remain blocked pending their own separate,
future owner decisions.

## Current Evidence

- **S1-G4 event/state conformance evidence (2026-07-27, ACCEPTED):**
  `reports/validation/st_c3/S1_G4_EVENT_STATE_CONFORMANCE_REPORT.md`,
  `tests/st_c3/test_s1_g4_event_state_conformance.py` (23 new tests).
  **ACCEPTED** on this basis, 2026-07-27 — see
  `S1_G4_EVENT_STATE_CONFORMANCE_COMPLETION_AUDIT.md`.
- **S1-G3 primitive/indicator conformance evidence (2026-07-27, ACCEPTED):**
  `reports/validation/st_c3/S1_G3_PRIMITIVE_CONFORMANCE_REPORT.md`,
  `tests/st_c3/test_s1_g3_primitives.py` (13 new fixed-expected-value tests),
  new `compute_rr()`/`premium_discount_zone()` primitives in
  `validation/st_c3/detection.py`. **ACCEPTED** on this basis, 2026-07-27
  — see `S1_G3_PRIMITIVE_CONFORMANCE_COMPLETION_AUDIT.md`.
- **ST-C3 v1.0.7 revision (2026-07-27):** decides R-31
  (`sweep_reclaim_max_bars`=2), R-32 (`entry_window_bars`=4), R-33 (session
  UTC bounds ratified, unchanged) — fresh owner decisions with clean
  provenance, superseding the quarantined v1.0.6 line's disputed versions
  of the same three fields. See `specs/st-c3_v1.0.7.yaml`,
  `reports/governance/st_c3/RCR_ST-C3_v1.0.7_REPORT.md`. **R-18 is the
  only field on the entire R-01–R-33 tracker still open** — it needs real
  detection-module code for 3 remaining stages (S7, S9, S12; S3/S10/S11
  now implemented per R-31/32/33), not a
  further spec decision.
- **Real price-level detection module (`validation/st_c3/detection.py`,
  2026-07-26):** implements S1 (HTF bias), S2 (raw sweep), S4
  (displacement+BOS), S5 (BOS extreme lock), S6 (dealing range), S8
  (FVG/OB) against real GBPUSD H4/M15 data, using every filter/algorithm
  parameter frozen through v1.0.7. `tests/st_c3/` (41 passing) includes
  detection tests and causal-invariance/determinism structural-conformance
  tests. Three stages (S7, S9, S12) still have no detection code —
  see `reports/validation/st_c3/R18_DETECTION_MODULE_REPORT.md`,
  `R18_CLOSURE_REPORT.md`.
- **Diagnostic studies (GBPUSD only — EURUSD's H4/M15 CSVs have only
  19-21 rows):** `R18_PARTIAL_FUNNEL_SIGNAL_RATE_GBPUSD.md` (joint S4-S8
  pass rate ~20.3% on the full 30,000-bar series), `S1_G3_STRUCTURAL_CONFORMANCE.md`
  (causal invariance/determinism verified), `S1_G4_STRUCTURAL_CONSISTENCY.md`
  (confirms `detection.py` is symbol-agnostic; EURUSD re-run needs no code
  change once real data exists). None of these are gate-passage
  declarations or a full R-18 answer.
- **v1.0.6 reconciliation audit:** `reports/governance/v1.0.6_RECONCILIATION_AUDIT.md`
  — full findings on the quarantined line; basis for the 2026-07-27
  rejection decisions above.
- ST-C3 v1.0.5 revision: `specs/st-c3_v1.0.5.yaml`,
  `reports/governance/st_c3/RCR_ST-C3_v1.0.5_REPORT.md`. Decided R-27
  (swing/fractal `k`=2), R-28 (BOS confirmation bars `N`=2), R-29 FVG half
  (min gap-size = 0.15x MF_ATR(1)), R-30 (pullback depth = 0.30x ATR(1)),
  each from empirically-researched tradeoff curves in
  `reports/validation/st_c3/R27_R30_RESEARCH_REPORT.md` (GBPUSD H4/M15 real
  data; existing generic `smc_engine` primitives, no invented or
  ST-C2-inherited logic).
- ST-C3 v1.0.4 revision: `specs/st-c3_v1.0.4.yaml`,
  `reports/governance/st_c3/RCR_ST-C3_v1.0.4_REPORT.md`. Decides R-22
  (`risk.instrument_tie_breaking_rule`: higher `computed_rr` wins between
  EURUSD/GBPUSD; EURUSD fixed-priority fallback on exact tie). Stage B /
  portfolio-level arbitration only — no execution code, no change to the
  S0-S13 state machine.
- ST-C3 v1.0.3 revision: `specs/st-c3_v1.0.3.yaml`,
  `reports/governance/st_c3/RCR_ST-C3_v1.0.3_REPORT.md`. Decides R-21
  (`fixed_lot_size` = 0.01, owner rationale: $1000 account capital) and
  revises R-02 (`instruments` narrowed to EURUSD/GBPUSD). **Correction on
  record:** the instrument-scope change was submitted mislabeled as "R-22"
  — R-22 (`instrument.selection_logic`, cross-instrument tie-breaking) is a
  different field; the change was recorded as an R-02 revision instead.
- ST-C3 v1.0.2 governance parameter-freeze revision:
  `specs/st-c3_v1.0.2.yaml`, `reports/governance/st_c3/RCR_ST-C3_v1.0.2_REPORT.md`,
  `docs/strategy/st_c3/ST-C3_CHANGELOG.md`. Folds in 22 owner-decided fields
  (R-01 through R-26 minus R-11/R-18/R-21/R-22, plus both resolved Open
  Conflicts). No evidence object, state, transition, guard, or
  rejection/termination code changed.
- ST-C3 active frozen spec: `specs/st-c3_v1.0.7.yaml` (fresh R-31/32/33
  decisions on `specs/st-c3_v1.0.5.yaml`, skipping the quarantined
  `specs/st-c3_v1.0.6.yaml`; v1.0.5 itself a structural-detection-algorithm
  revision of v1.0.4, itself an instrument tie-breaking revision of
  v1.0.3, itself a fixed-lot + instrument-scope revision of v1.0.2, itself
  a governance parameter-freeze revision of v1.0.1, itself a
  rejection-code revision of v1.0.0 — all preserved unchanged as
  historical record, including the quarantined v1.0.6).
- ST-C3 Specification Closure tracking: `reports/validation/st_c3/RESOLUTION_MATRIX.md`,
  `DEPENDENCY_GRAPH.md`, `DECISION_PACKAGES.md`, `OWNER_DECISION_LOG.md`,
  `SPECIFICATION_CLOSURE_REPORT.md`, `R04_R06_RESEARCH_REPORT.md`.
- ST-C3 A2/S1-G2 opening decision: `governance/st_c3_stage_status.yaml`
  `a2_signal_conformance.opened` (owner directive, 2026-07-26).
- ST-C3 S1-G1C audit (against v1.0.0): `reports/validation/st_c3/ST-C3_S1-G1C_LOGIC_CONFORMANCE_REPORT.md`.
- ST-C3 patch recommendation (R-1/R-2/R-3): `reports/validation/st_c3/ST-C3_v1.0.1_PATCH_RECOMMENDATION.md`.
- ST-C3 governance review (verified findings, found GR-1): `reports/validation/st_c3/GOVERNANCE_REVIEW_REPORT.md`.
- ST-C3 S1-G1C rerun (against v1.0.1, PASS): `reports/validation/st_c3/S1-G1C_RERUN_REPORT.md`.
- ST-C3 governance stage-status tracking: `governance/st_c3_stage_status.yaml`.
- ST-C3 freeze action log: `docs/strategy/st_c3/ST-C3_FREEZE_ACTION_LOG.md`.
- ST-C3 worktree checkpoint: `docs/strategy/st_c3/ST-C3_WORKTREE_CHECKPOINT.md`.
- ST-C3 freeze checklist: `docs/strategy/st_c3/ST-C3_FREEZE_CHECKLIST.md`.
- ST-C3 strategy architecture: `docs/strategy/st_c3/ST-C3_STRATEGY_ARCHITECTURE.md`.
- ST-C3 funnel lifecycle: `docs/strategy/st_c3/ST-C3_FUNNEL_LIFECYCLE.md`.
- ST-C3 evidence object specification: `docs/strategy/st_c3/ST-C3_EVIDENCE_OBJECT_SPEC.md`.
- ST-C3 rejection/termination code specification: `docs/strategy/st_c3/ST-C3_REJECTION_CODE_SPEC.md`.
- ST-C3 parameter sheet: `docs/strategy/st_c3/ST-C3_PARAMETER_SHEET.md`.
- ST-C3 state machine: `docs/strategy/st_c3/ST-C3_STATE_MACHINE.md`.
- ST-C3 evidence binding layer: `docs/strategy/st_c3/ST-C3_EVIDENCE_BINDINGS.md`.
- ST-C3 trade-plan schema: `docs/strategy/st_c3/ST-C3_TRADE_PLAN_SCHEMA.md`.
- ST-C3 validator rules: `docs/strategy/st_c3/ST-C3_VALIDATOR_RULES.md`.
- ST-C3 proposed execution agent specification: `docs/strategy/st_c3/ST-C3_EXECUTION_AGENT_SPEC.md`.
- ST-C3 backtest specification: `docs/strategy/st_c3/ST-C3_BACKTEST_SPEC.md`.
- ST-C3 intake ADR: `docs/adr/ADR-0004-st-c3-candidate-intake.md`.
- ST-C3 RCR/intake entry: `reports/research_log.md`.

## Acceptance Criteria (S1-G1C — met; A2/S1-G2 — scoped and open)

- Build an S1-G1C logic-conformance checklist for the frozen ST-C3 artifacts. DONE.
- Verify artifact cross-links and no dangling references. DONE.
- Verify YAML structural invariants: 16 evidence objects, 16 states, 16
  transitions, S13 evidence chain, R/ERR code maps, and blocked execution
  authority. DONE — re-verified against v1.0.1.
- Prepare a validation report outline for ST-C3. DONE (audit + rerun report).
- Resolve tracked rejection-code findings (R-1, R-2, R-3, GR-1) via a
  governance-approved revision before treating S1-G1C as closed. DONE —
  `specs/st-c3_v1.0.1.yaml`, owner-approved 2026-07-25.
- Preserve `docs/strategy/st_c3/ST-C3_BACKTEST_SPEC.md` as A3 planning
  material only; do not run backtests (historical_baseline is A3/S1-G7)
  until A2 passes and A3 is separately authorized. Still in force — A3
  remains blocked (the 2026-07-26 "OPEN" claim was rejected 2026-07-27).
- Within A2/S1-G2's scoped authorization: build golden-case tests,
  negative-case tests, and existence-check research against a reference
  funnel. NOT authorized within this scope: execution, optimization,
  demo, live, or production paths, or opening A3.
  PARTIALLY DONE — kernel, golden/negative-case tests, and real detection
  for 6 of 12 gating stages exist (`validation/st_c3/`, `tests/st_c3/`, 41
  passing). R-18's real existence-check number still requires the
  remaining 3 stages' detection code — see `R18_CLOSURE_REPORT.md`.

## Guardrails

- Do not modify frozen ST-C3 strategy logic except through a new
  governance-approved revision or candidate lineage.
- Do not modify `specs/st-c2_v1.2.0.yaml`.
- `engine_implements_spec` is `false` — only 6 of 12 gating stages have
  real detection code; no full funnel exists. A quarantined claim that
  this was `true` (via `evidence_builder.py`) is rejected.
- A2/S1-G2's scope is exactly what's listed in
  `governance/st_c3_stage_status.yaml` `a2_signal_conformance.opened` —
  execution, optimization, A3 opening, demo, and live are explicitly not
  authorized by this milestone and each require their own future, separate
  owner decision. A2 itself remains `in_progress`, not passed.
- Do not treat `specs/st-c3_v1.0.6.yaml`, `validation/st_c3/evidence_builder.py`,
  `validation/st_c3/a3_replay_engine.py`, or their associated reports as
  authoritative — quarantined per `reports/governance/v1.0.6_RECONCILIATION_AUDIT.md`.
  Preserved on disk as historical record only.

---

## Levers Track — Engineering Infrastructure (separate from ST-C3)

Parallel, documentation/tooling-only track opened 2026-07-25 alongside the
ST-C3 work above, per `MASTER_PLAN.md`/ADR-0001 precedent that governance
and infrastructure work on one track does not block another; only
implementation capacity is one-at-a-time.

- Lever A (existence-check tool): DONE — `tools/existence_check.py`,
  `scripts/run_existence_for_candidate.py`, tested.
- Lever B (power-planning tool): DONE — `tools/power_planning.py`, tested.
- Lever F (A2-closure gate): DONE — `scripts/check_a2_closure.py`, tested,
  verified against the real `reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json`.
- Lever D (shared feature/structure-shift primitives): NOT STARTED this
  session. Already substantially covered by existing `src/features.py`
  (a pre-existing per-candle feature layer with the same "compute once,
  reuse everywhere" goal). Any further refactor of `src/signal_v35.py` or
  `src/live_signal.py` to consume it touches live detection code and would
  itself need an RCR under `docs/RESEARCH-CHARTER.md`, same as Lever C.
- Lever E (parallel batch runner): NOT STARTED this session. Already
  substantially covered by existing `validation/batch_validation_runner.py`
  (resumable, cached, per-symbol sequential runner). True multiprocessing
  parallelization was not implemented — doing so safely would require
  reworking its caching/report-writing model, not a drop-in `Pool.map`.
- Lever C (engine collapse / STRATEGY_OF_RECORD unification): BLOCKED —
  pending RCR authorization. Changes which engine's decisions are
  authoritative for live/backtest routing; requires a pre-registered RCR
  under `docs/RESEARCH-CHARTER.md` before any change to `src/daily_runner.py`
  or creation of a `STRATEGY_OF_RECORD` wrapper. No RCR has been filed yet.
- No demo or live trading is authorized by any of the above, independent of
  Lever C's status — no execution layer exists, and no A2/A3 evidence exists
  for either ST-C2 or ST-C3.
