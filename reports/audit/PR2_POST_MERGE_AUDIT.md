# PR #2 Post-Merge Audit

Date: 2026-07-20

## Scope

This audit covers the merged PR #2 changes around corrected baseline verification, symbol metadata, simulator cost handling, cache identity, and research baseline reproducibility.

## What Was Verified

1. Canonical symbol metadata is now available and alias-aware through `src/symbol_metadata.py`.
2. Live sizing uses canonical symbol metadata instead of a generic point model in `src/live_signal.py`.
3. The replay engine now records explicit cost breakdowns, management events, and symbol metadata in `validation/historical_replay_engine.py`.
4. Validation cache identity includes symbol metadata and cost-profile context in `validation/batch_validation_runner.py`.
5. The baseline runner rejects legacy top-level timeframe fields and requires `market_universe.timeframes` in `src/research/run_baseline.py`.
6. Focused tests now cover alias resolution, sizing parity, cost math, conflicting spec rejection, and cache identity.

## Findings

### 1. Baseline spec ambiguity was real

The original research baseline spec carried duplicate timeframe definitions at the top level and inside `market_universe.timeframes`. That is dangerous because a runner can silently consume one model while the spec author thinks another model is active.

Status: fixed by rejecting deprecated top-level keys in `src/research/run_baseline.py` and removing the legacy fields from `specs/research/v1_baseline.yaml`.

### 2. Symbol and cost identity were too generic

Before the repair, symbol aliases could collapse into the same generic point model, and validation cache keys did not fully separate symbol metadata / cost context. That can contaminate replay comparisons across instruments such as `XAUUSD` and `XAUUSD-VIP`.

Status: fixed with canonical symbol resolution and symbol-aware cache identity.

### 3. Cost math is now test-backed

The focused tests validate the corrected cost math and ensure alias/canonical sizing parity. The new regression coverage also verifies that the cache key changes when the symbol metadata or execution model changes.

Status: verified by `tests/test_research_baseline.py`.

### 4. Existing baseline artifacts are stale

The files in `reports/refinement/baseline/` are still the old run and should not be treated as corrected evidence. The manifest currently shows `strategy_version: "unknown"` and was last written at `2026-07-20 1:02 PM` local time.

Status: not trustworthy as the corrected baseline. A fresh rerun is still required before anyone uses those artifacts for decisions.

## Verdict

`VALIDATION_REPAIR_COMPLETE_WITH_FRESH-RERUN_REQUIRED`

The simulator and baseline gate now have the right guardrails, and the focused regression tests pass. However, the pre-existing baseline output remains stale, so the corrected real-data baseline has not yet been re-established from fresh artifacts.

## Evidence

- `src/symbol_metadata.py`
- `src/live_signal.py`
- `validation/historical_replay_engine.py`
- `validation/batch_validation_runner.py`
- `src/research/run_baseline.py`
- `tests/test_research_baseline.py`
- `specs/research/v1_baseline.yaml`

## Recommended Next Step

Run a fresh baseline replay after the repaired validation path is in place, then compare the new manifest and trade outputs against the stale `reports/refinement/baseline/` artifacts before promoting any strategy conclusions.
