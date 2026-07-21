# ST-C1 v3.8 (R2.1 — G6 Population Feasibility) Pre-Edit Findings

Recorded: 2026-07-21 (session continuation)

## 1. Git state — verified, not assumed

- `git fetch --all --prune` run; no new remote branches beyond what was expected.
- `research/st-c1-baseline-runner-v2-clean` @ `0510dca5a9d925ae154ba18c95dac53ecb0b292a` — matches prompt exactly.
- `research/st-c1-phase-a-closure` @ `8e43e0af4c8e3cf32911e46e081b8f7aa4aff13b` — matches prompt exactly.
- `research/st-c1-v37-article-conformance` @ `4fb080c3d0425fc92fee6ad6e483dd430cceff18` — matches prompt exactly.
- Merge base of v3.7 HEAD vs. Phase A closure = `8e43e0af4c8e3cf32911e46e081b8f7aa4aff13b` — v3.7 is exactly one commit ahead of Phase A closure, nothing else layered in.
- PR #3: open, draft, `mergeable: MERGEABLE`, head still `8e43e0af...` (Phase A closure — unrelated to and untouched by v3.7/v3.8 work).
- Exact-HEAD CI for `4fb080c3d0425fc92fee6ad6e483dd430cceff18`: GitHub Actions `pytest` check — `completed` / `success` (run 29850937132).
- Worktree: clean before this task's edits (`git status` — nothing to commit).
- New branch created: `research/st-c1-v38-g6-population-feasibility`, from the verified v3.7 HEAD above.

### Discrepancy: v3.7 work is now committed and pushed

The prior session's final report stated nothing was committed or pushed. It
now is: commit `4fb080c` ("Add ST-C1 v1.1.0 / spec v3.7 gate tests and
historical replay engine") sits on `origin/research/st-c1-v37-article-conformance`,
authored by `aungmyat1 <aung.pro1@gmail.com>`, dated `2026-07-21 23:28:04
+0630`. This happened **outside this agent's actions** (no commit or push was
issued in the prior session). `git show --stat 4fb080c` confirms the commit
contains exactly the 14 deliverable files from that session plus one
incidental line in `.claude/scheduled_tasks.lock` — no governance document,
no `specs/v1.yaml`/`v3.5.yaml`/`v3.6.yaml`, and no `ST-C1_v1.yaml` was
touched. This is reported as a factual discrepancy from the prior session's
own claim, not as an unsafe or research-meaning-altering drift: the resulting
SHA matches exactly what this task's prompt expected, and the diff is
limited to the intended deliverables.

### `.claude/scheduled_tasks.lock` discrepancy

Confirmed via `git log -p -- .claude/scheduled_tasks.lock`: the only change
in commit `4fb080c` is:
```
-{"sessionId":"c83d9fa6-...","pid":4064,"acquiredAt":1784306732884}
+{"sessionId":"103d3e5d-...","pid":2876,"acquiredAt":1784651166527}
```
This is a harness-internal session/process lock record (session ID, OS PID,
acquisition timestamp) — it is **not source or research evidence** of any
kind; it changes every time a Claude Code session acquires the scheduler
lock and was swept into the commit as a side effect of committing the whole
working tree, not a deliberate edit. Resolution: **ignored, not reversed.**
Rewriting it in a new commit would not "unlock" anything (the live lock is
read from disk state, not git history) and reversing it would itself be a
content change to already-published history on a shared branch, which is
explicitly out of scope ("Do not rewrite published history"). This branch's
own commits (if any) will add specific files only (never `git add -A`), so
this file will not be swept into v3.8 work.

## 2. Current strategy/spec/cost/symbol state (verified on disk)

- `specs/v3.7.yaml`: `status: draft`, `implementation_status.engine_implements_spec: false` (line 301, "SAFETY INTERLOCK — nothing implements v3.7 yet").
- `strategies/candidates/ST-C1_v1.1.0.yaml`: `status: candidate`, `validation.status: pending`, `validation.approval_status: pending`, `validation.qualification: ablation_only`.
- `config/watchlist.yaml` autonomy block (unchanged since Phase A): `demo: proposal_only`, `live: disabled`, `engine_implements_spec: false`, `promote_to_live: false`.
- `config/research_costs.yaml`: unchanged — forex spread 25 pts / slippage 3 pts / commission 0 / swap 0 (explicitly flagged an assumption in the v3.7 spec, not measured broker truth).
- Symbol universe unchanged: EURUSD, GBPUSD, XAUUSD (`ST-C1_v1.1.0.yaml market_universe.instruments`).

## 3. Exact G6 funnel counts from all 12 prior v3.7 cells (`reports/ablation/st_c1_v37_ablation_raw.json`)

| Symbol | Cell | evaluated | session_pass | rejected_g1 | rejected_g4 | rejected_g5 | **rejected_g6 (= G5-qualified population)** | candidate_ready |
|---|---|---|---|---|---|---|---|---|
| EURUSD | A0 | 79963 | 25524 | 14369 | n/a (off) | 7627 | **3528** | 0 |
| EURUSD | A1 | 79963 | 25524 | 14369 | 8917 | 1674 | **564** | 0 |
| EURUSD | A2 | 79963 | 25524 | 14369 | n/a (off) | 7627 | **3528** | 0 |
| EURUSD | A3 | 79963 | 25524 | 14369 | 8917 | 1674 | **564** | 0 |
| GBPUSD | A0 | 79974 | 25524 | 15231 | n/a (off) | 6611 | **3682** | 0 |
| GBPUSD | A1 | 79974 | 25524 | 15231 | 8738 | 1183 | **372** | 0 |
| GBPUSD | A2 | 79974 | 25524 | 15231 | n/a (off) | 6611 | **3682** | 0 |
| GBPUSD | A3 | 79974 | 25524 | 15231 | 8738 | 1183 | **372** | 0 |
| XAUUSD | A0 | 79959 | 26793 | 14298 | n/a (off) | 7473 | **5022** | 0 |
| XAUUSD | A1 | 79959 | 26793 | 14298 | 10844 | 940 | **711** | 0 |
| XAUUSD | A2 | 79959 | 26793 | 14298 | n/a (off) | 7473 | **5022** | 0 |
| XAUUSD | A3 | 79959 | 26793 | 14298 | 10844 | 940 | **711** | 0 |

Every G5-qualified candidate (the `rejected_g6` count, since `candidate_ready`
is 0 in all 12 cells) failed at G6. Diagnostic testing in the prior session
(interactive, not part of the locked ablation) traced the cause on one real
EURUSD sample: the nearest matching M5 sweep after a genuine POI touch
occurred 127 bars after the touch — roughly 4x the current
`poi_entry_to_sweep_max_m5_bars=30` allowance.

## 4. Residual v3.7 conformance gaps (carried forward, unresolved by this task's scope)

Per `reports/audit/ST_C1_V37_TRACEABILITY_MATRIX.md` "Known, disclosed
simplifications": (1) G6's POI-touch search window (`m5_poi_entry_search_bars=3200`)
is a tractability bound, not the full theoretical staleness window a POI
could have; (2) G2's reusable/consumed-liquidity tracking is target-only, not
a full ACTIVE/SWEPT/INVALIDATED structure lifecycle. Neither is touched by
this task — this task's independent variable is `poi_entry_to_sweep_max_m5_bars`
only.

## 5. Governance/status-document conflicts (carried forward from the v3.7 session, re-verified unchanged)

`CLAUDE.md`'s "Owner directives (2026-07-18)" section (Risk Engine Phase 3,
locked `specs/v1.yaml`, v3.5 parked) remains superseded by `MASTER_PLAN.md`
v3.0.0 (2026-07-19, explicitly supersedes that framing) per `CLAUDE.md`'s own
authority order. `ROADMAP.md` still shows Phase 2 as "🟡 CURRENT" though
`PROJECT_STATUS.md`/`NEXT_ACTION.md` have already moved to Phase 3 M3
(execution layer skeleton) — a documentation-lag inconsistency, not a hard
conflict. This task's STEP 9 will update `PROJECT_STATUS.md`, `ROADMAP.md`,
and `NEXT_ACTION.md` to reflect that the project is in strategy
research/validation, not execution-layer work, and will NOT edit
`MASTER_PLAN.md` (no genuine authority-level change is required here — noted
per the instruction to stop and request authorization if one were needed,
which it is not).

## 6. Data provenance — NOT final/pristine OOS

Full local history per symbol, unchanged since the v3.7 ablation:

| File | SHA-256 |
|---|---|
| `data/EURUSD_M5.csv` | `6228afee869e0dbed2116bc4fe2e8f461d09448facdc618dffef653aa55d7cf7` |
| `data/GBPUSD_M5.csv` | `7bcae00fd463b3d04f0a373f062c0a4d78cac3e723fcb2592cf065753a7afff4` |
| `data/XAUUSD-VIP_M5.csv` | `7cf3f97c1ad95e4bb5c6fbc879d2ea51effac2add58210cf531926ba260d778f` |
| `data/EURUSD_H1.csv` | `8c413d3c352a33af1cbee4a968e0cce93a997911bb4885bcb401b0d7b4cc837d` |
| `data/GBPUSD_H1.csv` | `b127999ea51d50174e2fd6191dc37633eccb3c0afbe8fa10a5228df7baff0c39` |
| `data/XAUUSD-VIP_H1.csv` | `25c44ee2050feca8a9ea86da67bbc2979add5a1c5e1db6ec6d37f026789cc5a1` |
| `data/EURUSD_D1.csv` | `9f3376de401cc148a1fc514fe85808ec532ccb6a2fc93cf732ccbed71fce3e6f` |
| `data/GBPUSD_D1.csv` | `51115df20898095c62c727bc7e9c2c784d049ab759646159b8a77630308f1a40` |
| `data/XAUUSD-VIP_D1.csv` | `5d747df9bf0fc2c7b0d985d4ed906be77f448fe943727c8ba1979073f8d64c2c` |

Known synthetic-repair counts (carried from Phase A, unchanged): EURUSD M5 4,
GBPUSD M5 15, XAUUSD M5 0. **This history has already been used for v3.7
diagnosis** (the causal-displacement bug fix and window-size fix were
verified against it, and the locked A0–A3 ablation ran on it). It is
development/diagnostic-exposed data, not a sealed OOS partition, and must
not later be described as pristine final OOS evidence — this is the same
"development" data the B0/B1/B2 experiment below will also use, by design
(this is a population-feasibility diagnostic, not a performance validation).

No strategy rule or parameter was edited to produce this report.
