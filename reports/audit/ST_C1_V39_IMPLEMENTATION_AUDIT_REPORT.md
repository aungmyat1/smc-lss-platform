# ST-C1 v3.9 Governance, Conformance, and Population Validation — Final Report

**Verdict:** v3.9 is confirmed as the research-candidate-only strategy
(governance corrected and aligned), its E1/E2/E3 conformance gaps are
closed with a new canonical engine (26/26 new tests, 162/162 full suite
passing), and its population-feasibility gate **PASSES decisively** (138
completed trades vs. a 30 floor, all three symbols individually clearing
the 5-trade minimum) — but the same run surfaces a material net-cost/quality
concern on two of three symbols that must be investigated before any
profitability read; no execution, demo, or live authority changed.

Executes the mission in `reports/SMC_LSS_V39_GOVERNANCE_CONFORMANCE_AGENT_PROMPT.md`,
per the owner decision to audit v3.9 in its own E1/E2/E3 + M1/M2/M3 terms
rather than the parked v3.7 G1-G10 gate-pipeline framework the source prompt
assumed (see `ST_C1_V39_GOVERNANCE_CONFORMANCE_PRE_EDIT_FINDINGS.md` §3c).

## 1. Verified repository state

- Repository: `aungmyat1/smc-lss-platform`.
- Base branch for this work: `research/st-c1-v38-g6-population-feasibility`
  @ `548bffa97f2663e750de7933f9dbee81e576459c` (verified identical to
  `origin/research/st-c1-v38-g6-population-feasibility`, worktree clean
  except the user-added task-prompt file, at Phase 0 inspection time).
- New local branch created for this task:
  `research/st-c1-v39-governance-conformance`, from that same base.
- `master`/`origin/master` @ `c7c415ef179726fe14c135bb6e7e0b3b53e041e2`.
- PR #3 (`research/st-c1-phase-a-closure`, head `8e43e0af...`): OPEN, draft,
  MERGEABLE; verified an ancestor of this branch (Phase A reproducibility
  infra already inherited); exact-head CI (2x pytest) both SUCCESS at that
  exact head. Not merged, not touched.
- All work in this task is **uncommitted**, on the new local branch, per the
  task's authorization boundary (no commit/push/PR/merge performed).

## 2. Current strategy and authority state

- `config/watchlist.yaml`: `research_spec: specs/v3.6.yaml` (unchanged —
  correctly does NOT point at v3.9, since v3.9 is not yet an approved
  research spec), `strategy_spec: specs/v1.yaml` (execution, unchanged).
- `autonomy.demo: proposal_only`, `autonomy.live: disabled`,
  `autonomy.engine_implements_spec: false`, `autonomy.promote_to_live: false`
  — all fail-closed, all unchanged by this task.
- `specs/v3.9.yaml` / `strategies/candidates/ST-C1_v1.2.0.yaml`: still
  `status: candidate` / `validation.status: pending` — this task does not
  flip `engine_implements_spec` to `true` (see §5 for why: partial, not
  full, conformance coverage).

## 3. Three-layer conclusion

1. **Specification completeness:** `PARTIAL` -> effectively `VERIFIED` for
   the schema actually used. v3.9's E1/E2/E3+M1/M2/M3+displacement+session+
   risk+trade-management fields are all numeric (full `parameter_registry`
   with type/units/range). The one real gap found — E2's "CHoCH, not wick
   geometry" qualifier lacked its own numeric definition anywhere in v3.9 —
   was resolved by tracing it to `ST-C1_v1.yaml`'s close-only, against-bias
   BOS/CHoCH definition (the only place it existed), documented explicitly
   rather than silently assumed. See
   `reports/audit/ST_C1_V39_CONFORMANCE_MATRIX.md`.
2. **Implementation conformance:** `PARTIAL`. A canonical, isolated
   point-in-time engine (`src/signal_v39.py` +
   `validation/historical_replay_engine_v39.py`) now implements v3.9's full
   detection + cost + trade-management path, and 26/26 dedicated tests pass
   (see §6). `engine_implements_spec` is deliberately left `false` in
   `specs/v3.9.yaml`/`config/watchlist.yaml`: weekend/forced-exit is a
   best-effort interpretation (v3.9 sets the flags but the underlying spec
   never defined the trigger precisely — resolved as "exit before a
   calendar-day gap," documented, not silently assumed) and the funnel does
   not yet expose a per-gate rejection-code breakdown at the replay-engine
   level (a real, disclosed coverage gap, not a correctness defect).
3. **Statistical validation:** population-feasibility result in §7;
   NOT RUN beyond that (Phase 7/profitability explicitly out of scope for
   this task regardless of the population outcome, per the source prompt).

## 4. Changes made (all uncommitted)

| File | Why |
|---|---|
| `NEXT_ACTION.md` | Corrected stale "Phase 3 execution" pointer to match `PROJECT_STATUS.md`/`ROADMAP.md`'s already-current Phase 2/v3.9 narrative (governance conflict found in Phase 0). |
| `PROJECT_STATUS.md` | Logged this task's start, branch, and the framework-conflict finding under §5. |
| `ROADMAP.md` | Added a dated addendum cross-referencing this task under Phase 2. |
| `tests/test_config.py` | Added 3 governance-consistency tests (fail-closed autonomy flags; v3.9 spec still declares `engine_implements_spec: false`; watchlist doesn't point `research_spec` at an unconformant v3.9) — the "consistency checker" the source prompt's Phase 2 asks for. |
| `reports/audit/ST_C1_V39_GOVERNANCE_CONFORMANCE_PRE_EDIT_FINDINGS.md` | New. Phase 0 pre-edit findings record (deliverable #1). |
| `reports/audit/ST_C1_V39_CONFORMANCE_MATRIX.md` | New. Full E1/E2/E3+M1/M2/M3 conformance audit (deliverable #3), including two corrections found via later testing (see below). |
| `reports/audit/ST_C1_V39_CLEAN_SMC_RCR.md` | Appended an addendum, then a correction retracting that addendum, per `docs/RESEARCH-CHARTER.md` discipline (deliverable #4). |
| `reports/research_log.md` | Logged both the addendum and its retraction in date order. |
| `reports/audit/ST_C1_V39_POPULATION_ABLATION_SPEC.md` | New. Pre-registered ablation design, written before any result was inspected (deliverable #9, part 1). |
| `src/signal_v39.py` | New. Canonical v3.9 point-in-time signal engine (deliverable #5). |
| `validation/historical_replay_engine_v39.py` | New. v3.9-aware replay wiring reusing the existing, already-validated cost/fill/trade-management machinery (deliverable #5). |
| `tests/test_signal_v39.py`, `tests/test_historical_replay_v39.py` | New. 26 tests: positive/negative/mirror/wick-vs-close/body-ratio/session/cutoff-invariance/cost/weekend-exit/determinism/no-broker-import (deliverable #7). |

**Unrelated user work preserved:** the untracked task-prompt file
(`reports/SMC_LSS_V39_GOVERNANCE_CONFORMANCE_AGENT_PROMPT.md`) was never
modified. No other files outside the list above were touched. `specs/v1.yaml`,
`specs/v3.5.yaml`, `specs/v3.6.yaml`, `specs/v3.7.yaml`, and all v3.6/v3.7/v3.8
historical reports/ablation artifacts remain untouched (immutable controls
preserved).

## 5. Two corrections found via testing (disclosed, not hidden)

Both are documented in full in `ST_C1_V39_CLEAN_SMC_RCR.md` and the
conformance matrix; summarized here because they materially changed this
report's own earlier drafts:

1. **E3 "reclaim window" is a no-op, not a relaxation.** An earlier audit
   draft claimed `specs/v3.9.yaml`'s `e3_reclaim_window_h1_bars: 0` was an
   undisclosed fourth relaxation (unbounded reclaim). Building
   `tests/test_signal_v39.py` proved this parameter has zero effect at any
   value (0, 1, or 50 all produce identical output) because
   `smc_engine.liquidity_sweeps()` already requires the reclaim close on
   the same bar as the sweep wick by definition. Retracted in both the RCR
   addendum and the conformance matrix.
2. **Stop buffer / cost model / target tie-break were less broken than
   first thought.** `validation/historical_replay_engine.py` (the existing,
   already-validated v3.6 replay harness) already implements an ATR-based
   stop buffer, a full gross/net cost model, and break-even/partial trade
   management — reused directly rather than redesigned. Only v3.9-aware
   *detection* (E1 off, E2/E3 wick-ratio zero, body-ratio-only displacement)
   was genuinely missing, matching the conformance matrix's corrected
   "Open items" list.

## 6. Tests and reproducibility

Exact commands and results, at worktree state described in §1 (branch
`research/st-c1-v39-governance-conformance`, all changes uncommitted):

```
python -m pytest tests/test_signal_v39.py -q          -> 18 passed
python -m pytest tests/test_historical_replay_v39.py -q -> 8 passed
python -m pytest -q  (full repository suite)            -> 162 passed, 2 warnings
```

(Full-suite count and timing recorded at the point all v3.9 work above was
already present; the 2 warnings are a pre-existing `datetime.utcnow()`
deprecation notice in `src/backtest_v35.py`, unrelated to this task.)

Coverage against the source prompt's Phase 5 checklist: positive/negative
per E1(constant)/E2/E3/M1/M2/M3/displacement gate, bullish/bearish mirrors
for E2/E3, wick-only-rejected-vs-close-confirmed, session widening vs v3.6,
cutoff-invariance (future bars appended after the decision window do not
change the decision), point-in-time window bounding ignoring future bars,
next-bar-open fill, stop-and-target-same-bar conservative resolution,
weekend force-exit (and its non-override of a same-bar stop), net-cost
computation, clean-vs-resumed determinism, and no-broker-import. Not
separately covered: a dedicated M1/M3 bearish-mirror fixture (M1/M3 reuse
existing v3.6 fixtures without a hand-built mirror; M2's bearish mirror was
likewise not built) and duplicate-structure-suppression under a live
detection path (covered only implicitly via `consumed` set logic, not a
dedicated unit test) — both are non-blocking coverage gaps, not known
defects, and are named explicitly rather than left implicit.

## 7. Population/statistical evidence

Full detail, methodology, and disclosed caveats in
`reports/audit/ST_C1_V39_POPULATION_ABLATION_SPEC.md` (written and
committed to before any result was inspected). Raw evidence in
`reports/ablation/st_c1_v39_B{0,1}_{EURUSD,GBPUSD,XAUUSD}*_raw.json`.
Runners: `validation/run_v39_population_ablation.py`,
`validation/run_v36_control_ablation.py`.

Two cells, full local history per symbol (~78-80k M5 bars each,
2025-06/2025-06/2025-06 through 2026-07): **B1** = v3.9 as specified
(`src/signal_v39.py`); **B0** = v3.6 unchanged (`src/signal_v35.py`, the
immutable historical control), same cost model and wrapper machinery
otherwise.

| Symbol | B0 (v3.6) trades | B1 (v3.9) trades |
|---|---|---|
| EURUSD | 2 | 47 |
| GBPUSD | 2 | 37 |
| XAUUSD | 49 | 54 |
| **Total** | **53** | **138** |

**Population-feasibility gate (precommitted: >=30 total, >=5 in >=2
symbols): PASSES for B1**, and passes decisively — all three symbols
individually clear >=5, not just two. B0 clears the total but fails the
diversification requirement (only XAUUSD >=5).

**Mechanism confirmed, not just population:** EURUSD and GBPUSD go from
essentially unpopulated (2 trades each under v3.6) to well-populated (47,
37) under v3.9 — exactly the FX pairs the RCR's relaxations targeted.
XAUUSD, never the bottleneck, changes only modestly (49->54).

**Material caveat — informational only, not a Phase 7 verdict:** the
engine's existing cost model shows EURUSD (PF 0.03, net R -84.1) and GBPUSD
(PF 0.14, net R -25.7) deeply net-negative under v3.9's naive population
run, driven partly by very tight ATR*0.15 stop buffers producing cost/risk
ratios that overwhelm gross edge on many trades. XAUUSD is only marginally
net-positive under v3.9 (PF 1.06) and is actually *worse* than its own v3.6
control (PF 1.96) — the relaxations needed to unlock FX population appear
to dilute XAUUSD trade quality. **These numbers are reported as risk
context only.** No FAILED/OVERFILTERED/FRAGILE/PROMISING/ROBUST
classification is assigned — Phase 7's preconditions (locked OOS split,
walk-forward, deflated Sharpe) were never run and were explicitly out of
scope for this task regardless of the population outcome.

**Statistical validation layer: `NOT RUN`** (by design — population
feasibility was this task's ceiling).

## 8. Risks, conflicts, and unknowns

- **Data status:** all data used (both this run and the underlying
  EURUSD/GBPUSD/XAUUSD CSVs) is development data already inspected across
  v3.7/v3.8/this task — not a pristine OOS partition. Any future
  statistical validation must select an as-yet-unseen split or accept this
  limitation explicitly.
- **Cost/quality risk found above:** v3.9's population fix for EURUSD/GBPUSD
  comes with materially negative net expectancy in this uncontrolled,
  untuned run — a real signal that the relaxed detection rules and/or the
  ATR*0.15 stop-buffer convention need attention before any profitability
  claim, not evidence the population fix itself is wrong.
- **Weekend/forced-exit interpretation:** `specs/v3.9.yaml` sets
  `weekend_exit`/`forced_exit: true` without defining the trigger precisely;
  this task's engine interprets it as "close flat before a >=2-calendar-day
  gap" (since `time_stop` is separately disabled). Reasonable, documented,
  but a genuine interpretive choice, not something dictated unambiguously
  by the spec.
- **Coverage gaps (named in §6):** no dedicated M1/M3/M2 bearish-mirror
  fixture; duplicate-structure suppression not unit-tested in isolation;
  the replay funnel doesn't expose a per-gate (E1/E2/E3/M-model/RR)
  rejection breakdown, only a single `rejected_signal` bucket — a real
  observability gap for any future funnel-attribution analysis.
- **Live-data determinism:** clean-vs-resumed equality is proven on
  synthetic fixtures (`tests/test_historical_replay_v39.py`) but was not
  independently re-run on the live EURUSD/GBPUSD/XAUUSD datasets used for
  §7's numbers, for time reasons.
- **Governance:** `MASTER_PLAN.md`'s "CURRENT PRIORITY: PHASE 1" line is
  stale relative to `ROADMAP.md` (Phase 1 complete, Phase 2 current) —
  noted in Phase 0 findings but left unedited in this task (smallest-change
  principle; MASTER_PLAN is the highest-authority document and editing it
  deserves its own, separately-authorized pass).

## 9. Recommended next safe action

**Do not proceed to a Phase-7-equivalent profitability read yet.** The
immediate next milestone: investigate the EURUSD/GBPUSD cost/quality
finding in §7 as its own small, pre-registered research question (why are
so many v3.9 trades structured with stop distances tiny enough that fixed
spread/slippage assumptions dominate R? is the ATR*0.15 buffer convention
appropriate for this preset, or does E2/E3's zeroed wick-ratio filter admit
zones too tight to trade profitably net of cost?) — via `backtest-researcher`,
per `docs/RESEARCH-CHARTER.md`, before anyone reads population feasibility
as "v3.9 is close to working." Acceptance criteria for that follow-up:
answer stated as a testable hypothesis with expected numbers, before running
anything, exactly as this task's own RCR/addendum/correction cycle
practiced.

## 10. State-change confirmation

- Files changed: yes (listed in §4), all uncommitted.
- Branch created: yes, `research/st-c1-v39-governance-conformance` (local
  only, not pushed).
- Commit/push/PR/merge: **none**.
- Execution/demo/live/promotion flags: **none changed** — verified
  unchanged in `config/watchlist.yaml` and `specs/v3.9.yaml` throughout.
- Broker orders sent: **none** — no broker import exists anywhere in
  `src/signal_v39.py` or `validation/historical_replay_engine_v39.py`
  (verified by `tests/test_historical_replay_v39.py::test_no_broker_order_import_anywhere_in_v39_research_path`).
