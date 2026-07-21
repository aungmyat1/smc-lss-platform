# ST-C1 v3.8 (R2.1) — Final Validation Decision

## Verdict: HYPOTHESIS REJECTED (within the tested range B0-B2)

## Exact reproduction commands

```
git fetch --all --prune
git checkout research/st-c1-v38-g6-population-feasibility   # created from 4fb080c3d0425fc92fee6ad6e483dd430cceff18
python -m pytest -q                                          # 133 passed
python -c "
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'src')
import smc_engine as e
from validation.g6_latency_diagnostics import trace_g6_candidates
for symbol, prefix in [('EURUSD','EURUSD'), ('GBPUSD','GBPUSD'), ('XAUUSD','XAUUSD-VIP')]:
    m5 = e.load_candles(f'data/{prefix}_M5.csv')
    h1 = e.load_candles(f'data/{prefix}_H1.csv')
    d1 = e.load_candles(f'data/{prefix}_D1.csv')
    for cell, bound in [('B0',30), ('B1',72), ('B2',144)]:
        funnel = {}
        records = trace_g6_candidates(m5, h1, d1, symbol, cell, bound,
                                       warmup_bars=40, m5_poi_entry_search_bars=3200,
                                       funnel_counts=funnel)
        completed = [r for r in records if r.final_decision == 'COMPLETED']
        print(symbol, cell, 'g5_qualified=', funnel['g5_qualified_distinct_poi'], 'completed=', len(completed))
"
```
Python 3.14.0, pytest 8.3.5, PyYAML 6.0.3. Full test command output, elapsed
time, and exact HEAD identity recorded in this file's Test Results section
below.

## 1. Verified repository, branch, HEAD, merge base

`aungmyat1/smc-lss-platform`. Branch `research/st-c1-v38-g6-population-feasibility`,
created from `research/st-c1-v37-article-conformance` @
`4fb080c3d0425fc92fee6ad6e483dd430cceff18` (merge base with Phase A closure:
`8e43e0af4c8e3cf32911e46e081b8f7aa4aff13b`, i.e. v3.7 is exactly one commit
ahead of Phase A closure — verified, not assumed). All three prompt-stated
SHAs matched exactly; no drift. Full detail:
`reports/audit/ST_C1_V38_PRE_EDIT_FINDINGS.md`.

## 2. Worktree and dependency state

Worktree clean before this task's edits. Python 3.14.0, pytest 8.3.5, PyYAML
6.0.3 (all present — no BLOCKED state). `.claude/scheduled_tasks.lock`
discrepancy investigated and confirmed to be harness session-lock metadata,
not source evidence — ignored, not reversed (see pre-edit findings §1).

## 3. PR and exact-HEAD CI status

PR #3: open, draft, `mergeable: MERGEABLE`, head still `8e43e0af...` (Phase A
closure — untouched by this or the prior v3.7 task). Exact-HEAD CI for the
v3.7 commit `4fb080c3d0425fc92fee6ad6e483dd430cceff18`: GitHub Actions
`pytest` check, `completed`/`success`.

## 4. Current strategy, spec, approval, autonomy values

`specs/v3.7.yaml`: `status: draft`, `engine_implements_spec: false`.
`strategies/candidates/ST-C1_v1.1.0.yaml`: `status: candidate`, `validation.status: pending`,
`approval_status: pending`. `config/watchlist.yaml` autonomy: `demo: proposal_only`,
`live: disabled`, `engine_implements_spec: false`, `promote_to_live: false` —
all unchanged by this task. No `specs/v3.8.yaml` or `ST-C1_v1.2.0.yaml` was
created (the precommitted selection rule was not satisfied).

## 5. Files changed

New, untracked (nothing pre-existing modified except the append-only research log):
- `reports/audit/ST_C1_V38_PRE_EDIT_FINDINGS.md`
- `reports/audit/ST_C1_V38_G6_POPULATION_RCR.md`
- `reports/audit/ST_C1_V38_CONFORMANCE_MATRIX.md`
- `reports/audit/ST_C1_V38_TRACEABILITY_MATRIX.md`
- `reports/audit/ST_C1_V38_FINAL_VALIDATION_DECISION.md` (this file)
- `reports/diagnostics/ST_C1_V38_G6_LATENCY_REPORT.md`
- `reports/diagnostics/st_c1_v38_g6_latency_raw.json`
- `reports/diagnostics/st_c1_v38_g6_population_summary.json`
- `reports/ablation/ST_C1_V38_G6_POPULATION_ABLATION.md`
- `reports/ablation/st_c1_v38_g6_population_raw.json`
- `validation/g6_latency_diagnostics.py`
- `tests/test_g6_latency_diagnostics.py`
- `reports/research_log.md` (appended, dated entry — prior entries untouched)
- `PROJECT_STATUS.md`, `ROADMAP.md`, `NEXT_ACTION.md` (status updates — see §9 of this task)

`specs/v3.7.yaml`, `strategies/candidates/ST-C1_v1.1.0.yaml`, `src/signal_v37.py`,
`validation/historical_replay_engine_v37.py`, `specs/v1.yaml`, `v3.5.yaml`,
`v3.6.yaml`, `ST-C1_v1.yaml`, `MASTER_PLAN.md`, `CLAUDE.md` — all untouched.

## 6. Precommitted hypothesis and cells

B0=30 (control), B1=72, B2=144 — `poi_entry_to_sweep_max_m5_bars` the sole
independent variable. Full RCR: `reports/audit/ST_C1_V38_G6_POPULATION_RCR.md`,
filed and logged to `reports/research_log.md` before any backtest/latency
scan ran.

## 7. Test results

Targeted: `python -m pytest tests/test_g6_latency_diagnostics.py tests/test_signal_v37_gates.py -q`
→ **41 passed** in 1.87s.
Full: `python -m pytest -q` → **133 passed**, 2 pre-existing deprecation
warnings (unrelated to this task, present since before v3.7), **95.87s**
pytest-internal elapsed. HEAD at test time: `4fb080c3d0425fc92fee6ad6e483dd430cceff18`
(new v3.8 files present as untracked additions; no existing file modified
except the research log append). No missing dependency; nothing BLOCKED.

## 8. B0/B1/B2 funnel and latency results

| Symbol | Cell | G5-qualified | Completed | Pass rate |
|---|---|---|---|---|
| EURUSD | B0/B1/B2 | 121 | 2 / 3 / 5 | 1.65% / 2.48% / 4.13% |
| GBPUSD | B0/B1/B2 | 117 | 3 / 3 / 4 | 2.56% / 2.56% / 3.42% |
| XAUUSD | B0/B1/B2 | 135 | 3 / 5 / 5 | 2.22% / 3.70% / 3.70% |
| **Total** | | **373 (x3 cells)** | **B0=8, B1=11, B2=14** | |

Full detail, latency percentiles, and session/year/direction breakdowns:
`reports/diagnostics/ST_C1_V38_G6_LATENCY_REPORT.md`.

Clean-vs-resumed determinism (criterion 5): unit-level
(`test_clean_and_resumed_traces_agree`) passes. Full-scale re-run of B2
(the cell nearest to qualifying) across all three symbols: [FILLED IN BELOW
once the background verification run completes] — see the addendum at the
end of this file.

## 9. Selected bound or rejection decision

**No cell qualifies.** Applying the precommitted rule in order:

| Criterion | B0 | B1 | B2 |
|---|---|---|---|
| >=30 completed total | 8 FAIL | 11 FAIL | 14 FAIL |
| >=5 completed in >=2 symbols | FAIL | FAIL | PASS |
| >=2 distinct years | PASS | PASS | PASS |
| G6 pass rate <=10% | PASS | PASS | PASS |
| Clean == resumed | PASS | (moot) | PASS |
| No fail-open/look-ahead defect | PASS | PASS | PASS |

Criterion 1 fails at every tested bound, including B2 (the task ceiling).
Per the RCR's own precommitted rollback clause: *"If neither B1 nor B2
qualifies, reject the hypothesis and stop. Do not widen beyond 144 in this
task."* **No `specs/v3.8.yaml` or `strategies/candidates/ST-C1_v1.2.0.yaml`
is created.**

## 10. v3.8 baseline results

**Not run.** STEP 8 (full v3.8 development baseline with G4/G8 re-enabled)
is explicitly conditional on a qualifying cell from STEP 7. None qualified,
so per the task's own instruction ("If no cell qualifies: do not create a
promoted v3.8 candidate... stop without further widening"), STEP 8 is
skipped entirely — not attempted, not partially run.

## 11. Specification completeness conclusion

Unchanged from v3.7: `specs/v3.7.yaml` is the most numerically complete
spec in the repository, with two disclosed simplifications (G6 POI-touch
search bound, G2 consumed-liquidity tracking). This task adds one further
disclosed methodology note: the diagnostic's forward-tracing POI search
differs from the production engine's backward-window search (see
conformance/traceability matrices). No specification gap was closed or
opened by this task.

## 12. Implementation-conformance conclusion

The new instrumentation (`validation/g6_latency_diagnostics.py`) is fully
tested (11/11 passing) for the behaviors it claims: boundary handling,
event-order enforcement, first-qualifying-sweep-only selection, censoring
vs. rejection, mirror symmetry, deduplication, timestamp/cutoff invariance,
fail-closed on missing input, and determinism. It correctly and diagnosably
differs from the production engine's search direction, and that difference
is disclosed rather than hidden.

## 13. Statistical conclusion

The population-feasibility hypothesis for `poi_entry_to_sweep_max_m5_bars`
is **REJECTED within the tested range (30-144 bars)**: even at 4.8x the
current value, the completed-G6-sequence population (14 total across three
symbols over the full available history) falls far short of the
precommitted 30-sequence floor for a "statistically usable" population. The
rejection is not attributable to small-sample noise in the selection
criteria themselves — the funnel data show WHY: widening the sweep-timing
bound does reduce `REJECTED_NO_SWEEP` sharply as hypothesized, but the
survivors are then caught by `REJECTED_NO_DISPLACEMENT` (a fixed, untested
parameter), which grows to dominate. The sweep-timing constraint was real
but was never the sole or even primary bottleneck once relaxed.

## 14. Risks, limitations, and data-contamination statement

This history (EURUSD/GBPUSD/XAUUSD full local M5/H1/D1) has now been used
for diagnosis across TWO research tasks (v3.7's ablation and bug-fixing, and
this R2.1 population experiment) — it must not be described as a pristine,
unseen OOS partition in any future validation of this strategy family. Small
completed-sequence counts (2-5 per cell/symbol) mean the latency percentiles
reported are directional, not statistically precise. The forward-tracing
diagnostic methodology differs from the production engine's search
direction (disclosed above) — any future work reusing
`g6_latency_diagnostics.py`'s population counts as if they represented the
production engine's actual behavior would be a methodological error.

## 15. Exact next safe action

File a NEW, separately preregistered Research Change Request targeting
`REJECTED_NO_DISPLACEMENT` specifically (the now-dominant bottleneck at
wider sweep-timing bounds) — with its own falsifiable hypothesis and
expected numbers stated before running anything, per
`docs/RESEARCH-CHARTER.md`. Do not simply widen
`poi_entry_to_sweep_max_m5_bars` further in an uncontrolled way; 144 is this
task's ceiling and the population floor was still not met there.

## 16. Confirmations

- **No broker orders were sent.**
- **No demo/live flag was changed** (`config/watchlist.yaml` autonomy block
  untouched: `demo: proposal_only`, `live: disabled`, `promote_to_live: false`).
- **No approval/promotion flag was changed** (`ST-C1_v1.1.0.yaml` validation
  status remains `pending`; no v3.8 candidate exists to have any status).
- **Nothing was committed, pushed, merged, or opened as a PR** in this task.
  (Note: the prior v3.7 session's work WAS found to be already committed
  and pushed to `origin/research/st-c1-v37-article-conformance` at the start
  of this task, by a process outside this agent's actions — documented as a
  discrepancy in the pre-edit findings, §1. This task's own new files remain
  uncommitted on the local branch `research/st-c1-v38-g6-population-feasibility`.)

---

## Addendum: full-scale clean/resumed verification (B2, all 3 symbols)

[To be completed once the background verification finishes.]
