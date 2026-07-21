# Pre-Edit Findings — ST-C1 v3.9 Governance/Conformance/Population Task

Phase 0 read-only preflight for the task defined in
`reports/SMC_LSS_V39_GOVERNANCE_CONFORMANCE_AGENT_PROMPT.md`. No files were
modified to produce this record except this record itself. Written before any
implementation step, per that prompt's Phase 0 requirement.

## 1. Verified repository state

- Repository: `aungmyat1/smc-lss-platform` (origin, fetch=push).
- Current branch at inspection start: `research/st-c1-v38-g6-population-feasibility`.
- Exact HEAD: `548bffa97f2663e750de7933f9dbee81e576459c` (matches
  `origin/research/st-c1-v38-g6-population-feasibility` exactly — no local
  divergence).
- `master` / `origin/master` HEAD: `c7c415ef179726fe14c135bb6e7e0b3b53e041e2`.
  Current branch is 12 commits ahead of `master`, 0 behind.
- Worktree state at inspection start: clean except one untracked file,
  `reports/SMC_LSS_V39_GOVERNANCE_CONFORMANCE_AGENT_PROMPT.md` (the task
  prompt itself, added by the user this session). No other uncommitted or
  overlapping user changes exist.
- PR #3 (`research/st-c1-phase-a-closure` -> `master`): OPEN, draft,
  `mergeable: MERGEABLE`. Head SHA `8e43e0af4c8e3cf32911e46e081b8f7aa4aff13b`.
  Verified this SHA **is an ancestor of the current branch HEAD**
  (`git merge-base --is-ancestor` = true) — the v3.8/v3.9 work already
  contains PR #3's Phase A reproducibility infrastructure as an ancestor.
  PR #3 does not need to be merged first; it can remain open independently.
- PR #3 exact-head CI: two `pytest` check runs, both `SUCCESS`, both recorded
  against `headRefOid = 8e43e0af...` (confirmed via `gh pr view --json
  headRefOid,statusCheckRollup` — exact-head match, not a stale-commit claim).
- Other open PRs: #1 (`arena/019f7116-smc-lss-platform`, unrelated E1M1 gap
  work, OPEN) — out of scope, not touched.

## 2. Authoritative documents inspected

`CLAUDE.md`, `MASTER_PLAN.md` (v3.0.0), `docs/RESEARCH-CHARTER.md`,
`PROJECT_STATUS.md` (audit date 2026-07-22), `ROADMAP.md`, `NEXT_ACTION.md`,
`config/watchlist.yaml`, `specs/v3.9.yaml`, `strategies/candidates/ST-C1_v1.2.0.yaml`,
`reports/audit/ST_C1_V39_CLEAN_SMC_RCR.md`, `reports/research_log.md`
(existence only, not full contents), plus the v3.7/v3.8 lineage
(`ST_C1_V38_FINAL_VALIDATION_DECISION.md`, `ST_C1_V37_ABLATION_REPORT.md`
references cited by the RCR).

## 3. Governance conflicts found (not silently resolved)

### 3a. `NEXT_ACTION.md` contradicts `PROJECT_STATUS.md` §5 and `ROADMAP.md`
`NEXT_ACTION.md` currently names the in-flight milestone as **"PHASE 3 · M3:
Execution Layer Skeleton"**. `PROJECT_STATUS.md` §5 (2026-07-22, most recent
audit) and `ROADMAP.md` (Phase 2 section) both explicitly state the next
milestone is the **v3.9 population-feasibility backtest** and that **"Phase 3
(execution layer) remains explicitly out of scope until a candidate clears
Phase 2's evidence gates."** Per `CLAUDE.md`'s own authority order,
`ROADMAP.md` outranks `NEXT_ACTION.md`, and `PROJECT_STATUS.md` outranks both.
`NEXT_ACTION.md` was evidently not updated in the same 2026-07-22 pass that
updated `PROJECT_STATUS.md`/`ROADMAP.md`. **Resolution: follow the
higher-authority documents (research/population work, not execution-layer
work). `NEXT_ACTION.md`'s stale pointer is a governance-alignment item in
scope for Phase 2 of the task, not an owner decision.**

### 3b. `MASTER_PLAN.md`'s "current priority" line is stale relative to `ROADMAP.md`
`MASTER_PLAN.md` (v3.0.0, 2026-07-19) still reads "CURRENT PRIORITY: PHASE 1,"
but `ROADMAP.md` (same date, later-updated in practice) marks Phase 1
COMPLETE and Phase 2 current. This predates the v3.7/v3.8/v3.9 research line
entirely — `MASTER_PLAN.md` never mentions it. Not a hard block (both
documents agree research/validation precedes execution), but the stale
pointer should be corrected for consistency, per the task's Phase 2 scope.

### 3c. Material conflict: the task's Phase 3 "G1–G10 conformance matrix" does not match v3.9's actual, deliberately different design
This is the significant one. The agent prompt's Phase 3 directs building a
G1–G10 gate-pipeline conformance matrix (objective HTF bias / external
structure / close-confirmed BOS-CHoCH / premium-discount / HTF POI-FVG / LTF
sweep+structure / invalidation / min-reward / target / trade-management) for
v3.9. **That G1–G10 schema is the v3.7 pipeline.** Verified facts:

- `specs/v3.9.yaml` explicitly and by design **returns to the older
  E1/E2/E3 + M1/M2/M3 schema** (v3.6-style), not G1–G10. Its own header
  states: *"v3.9 returns to v3.6's E1/E2/E3 schema... WHY A NEW VERSION (not
  a v3.6/v3.7 edit): v3.6 and v3.7 are left immutable as historical
  controls."*
- `reports/audit/ST_C1_V39_CLEAN_SMC_RCR.md` (the governing, pre-registered
  Research Change Request under `docs/RESEARCH-CHARTER.md`) states the
  change is a return to the E1/E2/E3 schema *"rather than v3.7's G1-G10 gate
  pipeline."*
- `PROJECT_STATUS.md` §5 records that the G1–G10 pipeline (v3.7) produced
  **zero trades in all 12 locked ablation cells** (OVERFILTERED/INCONCLUSIVE)
  and that its v3.8 follow-up (still G1–G10-shaped) reached only 14/30
  required completed sequences even at the widest tested bound — the G1–G10
  design (specifically its G6 gate) is the diagnosed root cause the v3.9
  preset was created to escape.
- No `signal_v39.py` or `historical_replay_engine_v39` exists.
  `src/signal_v37.py` / `validation/historical_replay_engine_v37.py` are the
  only G1–G10-era engine files present; they implement the parked v3.7/v3.8
  line, not v3.9.

Building a literal G1–G10 conformance matrix against v3.9 would either (a)
force-fit v3.9's E1/E2/E3/M1/M2/M3 rules into gate labels they were not
designed as (risking exactly the "silent reinterpretation" the source prompt
itself warns against), or (b) require silently reintroducing the G1–G10
pipeline structure into v3.9 as an implementation choice — which is a
material, undisclosed change to v3.9's declared semantics and would need its
own amended/superseding RCR under `docs/RESEARCH-CHARTER.md`, not an ad hoc
substitution. This matches the prompt's own stop condition: *"v3.9 contains
subjective rules that cannot be resolved from authoritative documents"* (more
precisely here: the requested audit framework and the authoritative spec
disagree on structure, not just on parameter values) and *"repository
instructions conflict with this task."*

**This is flagged as requiring an explicit decision before Phase 3/4 proceeds
(see accompanying report to the user).** No conformance matrix, RCR
amendment, or engine code has been written against either interpretation
yet — nothing has been guessed.

## 4. Three-layer status (current, verified)

1. **Specification completeness (v3.9):** PARTIAL. `specs/v3.9.yaml` is
   numerically complete for an E1/E2/E3+M1/M2/M3-style spec (full
   `parameter_registry` with type/units/range/owner for every field) but has
   **not** been audited against a matching gate-by-gate conformance
   framework (see §3c) — no G1–G10-equivalent matrix exists for this schema
   shape yet.
2. **Implementation conformance:** NOT IMPLEMENTED. `implementation_status.
   engine_implements_spec: false` in `specs/v3.9.yaml`, confirmed consistent
   with `config/watchlist.yaml`'s `engine_implements_spec: false`. No engine
   file implementing v3.9's schema exists.
3. **Statistical validation:** NOT RUN. No v3.9 backtest, no population
   funnel, no ablation has been executed. `ST-C1_v1.2.0.yaml` validation
   status is `pending` / qualification `not_started`.

## 5. Current safety/approval state (verified from `config/watchlist.yaml`)

- `strategy_spec: specs/v1.yaml` (execution-track authority, unchanged).
- `research_spec: specs/v3.6.yaml` — **still points at v3.6, not v3.9.**
  Matches the non-authoritative context's claim; verified true at current
  HEAD. This is expected: v3.9 is not yet an approved research spec, so the
  config should not point at it yet.
- `autonomy.demo: proposal_only`, `autonomy.live: disabled`,
  `autonomy.engine_implements_spec: false`, `autonomy.promote_to_live: false`
  — all fail-closed, all consistent with governance docs. No execution or
  promotion flag needs to change for this task, and none will be changed to
  a less restrictive state.

## 6. Files expected to change (if/when work proceeds)

Governance alignment only, pending the decision in §3c: `NEXT_ACTION.md`
(correct stale Phase 3 pointer), `PROJECT_STATUS.md`/`ROADMAP.md`
(cross-reference this task), possibly `MASTER_PLAN.md` (stale priority line,
versioned per its own changelog convention). No spec, candidate, engine, or
config file will change until the §3c decision is made.

## 7. Unrelated changes preserved

`reports/SMC_LSS_V39_GOVERNANCE_CONFORMANCE_AGENT_PROMPT.md` (untracked,
user-added) is left untouched and will remain on whatever branch it was
added to.

## 8. Go/no-go decision

**NO-GO on Phase 3/4 (spec-conformance audit + engine implementation) until
§3c is resolved.** Phase 0 (this record) and Phase 1 (base verification,
local branch) are safe to complete now. Phase 2 (governance doc alignment)
is safe to do in its narrow, uncontroversial part (§3a/§3b stale-pointer
fixes) without further authorization, since it only aligns lower-authority
documents to already-authoritative ones. Phases 3 onward require the user to
choose how v3.9 should actually be audited, per the accompanying report.
