# S1-G3 Structural Conformance — Implemented Detection Stages

**Date:** 2026-07-26
**Scope:** structural invariants of `validation/st_c3/detection.py`'s
implemented stages (S1, S2-raw, S4, S5, S6, S8) — causal invariance and
determinism, not a gate-passage declaration. No governance file is
modified by this report; it does not assert S1-G3 (or any gate) is
"opened" or "passed" — those remain governance decisions outside this
report's authority. This is diagnostic/QA work within the existing
A2/S1-G2 scoped authorization's `research_and_validation_tasks` item.

---

## What "structural conformance" means here

Two invariants every detection function in `validation/st_c3/detection.py`
must satisfy to be trustworthy as real-data-facing kernel input:

1. **Causal invariance (no lookahead):** evidence computed as of bar `i`
   must be identical whether or not bars after `i` exist. A function that
   silently used future data would produce backtest-only-valid results
   that could never actually fire in a live/replay context — the same
   failure mode ST-C2's `test_structural_context_is_causal_and_deterministic`
   already guards against for that lineage.
2. **Determinism:** identical inputs, called any number of times, produce
   identical outputs. No hidden state, no wall-clock dependence, no
   randomness — consistent with `validator_rules.principles.no_discretion`
   in the frozen spec (`only_boolean_guards_and_numeric_comparisons`).

## Verification method

`tests/st_c3/test_detection_structural_conformance.py` (5 tests, real GBPUSD H4/M15
data): for each implemented stage, evidence is computed once against a
candle window ending at a cutoff bar, then again against the same window
with 50 extra future candles appended, and the two results are asserted
identical (`valid`, and each stage's key numeric/categorical field).
Determinism is checked by calling the same function twice on identical
input and asserting bitwise-identical results.

## Results

| Stage | Causal invariance | Determinism |
|---|---|---|
| S1_HTF_BIAS (`detect_htf_bias_events`/`htf_bias_evidence_at`) | PASS | PASS |
| S2_SWEEP (`detect_sweep_at`) | PASS | PASS |
| S4_DISPLACEMENT_BOS (`displacement_evidence_for`) | PASS | (covered via S2's rerun test + BOS candidate list rerun) |
| S6_DEALING_RANGE (`dealing_range_evidence_for`) | PASS | — |
| S8_FVG_OB_CONFLUENCE (`fvg_evidence_near`, `order_block_evidence_near`) | PASS | — |
| `find_bos_candidates` (S4/S5 anchor) | — | PASS (identical candidate list across two calls) |

All 5 tests pass. No causal-invariance or determinism violation found in
any implemented stage.

## Why this holds structurally

Every function in `detection.py` takes an explicit candle window (`candles`,
often sliced by the caller as `candles[: i + 1]`) and computes purely from
it — no module-level mutable state, no caching keyed by wall-clock time, no
reliance on `len(candles)` beyond the window actually passed in. This
matches the design discipline `validation/st_c2/structure.py` already
established for the ST-C2 lineage (explicit `causal_cutoff` parameters
throughout), applied here without needing to invent a new convention.

## What this does NOT establish

- **Not a claim that S3/S7/S9-S12 are conformant** — they have no
  implementation to check (see `R18_DETECTION_GAP_REPORT.md`/
  `R18_CLOSURE_REPORT.md`).
- **Not a signal-rate or existence-check result** — see
  `R18_PARTIAL_FUNNEL_SIGNAL_RATE_GBPUSD.md` for that, separately.
- **Not a gate decision.** This report does not open, pass, or otherwise
  change the status of S1-G3 or any other gate — that remains an explicit
  governance action, not implied by a passing test suite. `NEXT_ACTION.md`
  continues to name A2/S1-G2 as the single active milestone; this report
  does not supersede that.
- **Not a claim about EURUSD or XAUUSD** — all data used here is GBPUSD
  only, for the same reasons documented in `R18_CLOSURE_REPORT.md`.

## Governance state (unchanged)

A2 remains in progress. A3 remains blocked. No governance file
(`PROJECT_STATUS.md`, `OWNER_DECISION_LOG.md`, `NEXT_ACTION.md`,
`governance/st_c3_stage_status.yaml`) was modified to produce this report.
The parallel v1.0.6 line remains quarantined, unverified, and unused here.
