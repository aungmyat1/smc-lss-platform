# Phase A Pre-Edit Findings

Recorded on: `2026-07-21`

## Git State

- Starting branch: `research/st-c1-baseline-runner-v2-clean`
- Starting HEAD: `0510dca5a9d925ae154ba18c95dac53ecb0b292a`
- Implementation branch: `research/st-c1-phase-a-closure`
- Remote sync after fetch: `0 ahead / 0 behind` versus `origin/research/st-c1-baseline-runner-v2-clean`
- Merge base with `origin/master`: `c7c415ef179726fe14c135bb6e7e0b3b53e041e2`
- Ahead/behind versus `origin/master`: `9 ahead / 0 behind`
- Worktree before edits: clean

## Artifact Freshness

- Stored `reports/audit/phase_a_stop_report.md` records HEAD `d521cdd3e997b1a900c5f0ecf558194921e6cb5c`, not current HEAD `0510dca5a9d925ae154ba18c95dac53ecb0b292a`.
- Stored two-symbol baseline manifests under `reports/refinement/baseline_2sym_a/` and `reports/refinement/baseline_2sym_b/` predate current HEAD and are generated evidence, not source.
- The brief identifies an additional stale baseline manifest HEAD of `a6eb310`.

## Data Coverage

- Required local raw CSV coverage is EURUSD, GBPUSD, and XAUUSD on M5/H1/D1.
- Raw CSVs are gitignored by policy and must remain local inputs.
- Historical generated reports showed GBPUSD missing; the current local workspace contains `GBPUSD_M5.csv`, `GBPUSD_H1.csv`, and `GBPUSD_D1.csv`.

## CI And Tests

- CI incorrectly triggered on `main`; repository default target in this branch is `master`.
- CI already used Python 3.12, installed `requirements.txt`, and ran `python -m pytest -q`.
- Phase A gate default incorrectly called two focused tests its full suite.
- Full local suite status at task start was reported by the brief as `86 passed, 4 skipped, 1 warning`; this must be re-run after changes.
- GitHub CI must remain `unknown` or `blocked` until a successful run is observed for the exact report HEAD.

## Generated Artifacts

- `validation/cache/` and two-symbol replay directories contain reproducible generated outputs and caches.
- Tracked generated outputs should be removed from Git index without deleting local copies.
- Reproducibility should be preserved by source code, specs, compact manifests, hashes, and documented regeneration commands.

## Synthetic Candles

- Existing repair log records 19 flat-previous-close synthetic M5 candles:
  - EURUSD M5: 4
  - GBPUSD M5: 15
- No XAUUSD synthetic repairs are recorded.
- Sensitivity evidence across repaired, affected-session-excluded, and gap-preserving alternatives is not complete at pre-edit time.

## Strategy Specification Versus Replay

- The replay uses H1 data for bounded context and M5 for execution, but much of the ST-C1/v3.6 E-trigger and M-model contract is implemented as a surrogate.
- The baseline must be interpreted as a test of the implemented surrogate unless conformance is proven rule by rule.
