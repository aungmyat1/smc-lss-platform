# S1-G4 Structural Consistency Across Symbols

**Date:** 2026-07-26
**Script:** `scripts/s1_g4_structural_consistency.py`
**Scope:** confirms `validation/st_c3/detection.py` is symbol-agnostic (no
hardcoded symbol logic) and establishes a reusable multi-symbol runner,
applied to R-02's active instruments (EURUSD, GBPUSD; XAUUSD excluded per
R-02's v1.0.3 revision). No governance file is modified by this report; it
does not assert S1-G4 (or any gate) is "opened" or "passed" — same
disclaimer as `S1_G3_STRUCTURAL_CONFORMANCE.md`, and for the same reason:
that remains a governance decision outside this report's authority.

---

## Data-availability check

| Symbol | H4 rows | M15 rows | Status |
|---|---|---|---|
| EURUSD | 18 | 20 | **INSUFFICIENT** (threshold: 1,000) |
| GBPUSD | 5,000 | 30,000 | SUFFICIENT |

XAUUSD is out of scope entirely — excluded from `instruments` since R-02's
v1.0.3 revision, and has no H4/M15 CSVs in `data/` at all (only H1/D1/M5).

**EURUSD placeholder:** once real EURUSD H4/M15 history is sourced (the
same blocker already documented in `R27_R30_RESEARCH_REPORT.md` and
`R18_CLOSURE_REPORT.md`), re-running `scripts/s1_g4_structural_consistency.py`
requires no code change — the script already iterates the same `SYMBOLS`
dict and calls the same symbol-agnostic functions. This is the
"structural-invariance comparison framework ready for multi-symbol
expansion": it already exists, in the form of the detection module itself
plus this runner, not a separate thing still to be built.

## Confirming symbol-agnosticism

`validation/st_c3/detection.py` contains zero hardcoded symbol strings
(`grep -i "gbpusd\|eurusd\|xauusd"` returns only a docstring reference to
an unrelated research script's filename). Every function takes a candle
list and spec-derived parameters as arguments — nothing about GBPUSD is
baked into the detection logic itself. The apparent "GBPUSD-only" scope of
prior reports (`R18_PARTIAL_FUNNEL_SIGNAL_RATE_GBPUSD.md`,
`R27_R30_RESEARCH_REPORT.md`) was a **data** limitation, not a code one.

## GBPUSD structural summary (only symbol currently runnable)

| Metric | Value |
|---|---|
| H4 bars | 5,000 |
| M15 bars | 30,000 |
| Current HTF bias (end of series) | valid=True, BEARISH |
| Raw BOS candidates (M15, k=2) | 10,417 |
| S4+S5 pass rate (sampled 500 of 10,417) | 19.0% |

Consistent with `R18_PARTIAL_FUNNEL_SIGNAL_RATE_GBPUSD.md`'s full-series
S4/S5 rate (20.3%, 2,112/10,417) — the two measurements use different
sampling but land in the same range, another cross-check that the
detection module's output isn't sampling-artifact-dependent.

## What this does NOT establish

- **Not a real cross-symbol consistency claim** — with only one symbol
  runnable, there is nothing to compare against yet. "Consistency" here
  means "the same code produces sensible output on a second symbol's data
  structure," not "GBPUSD and EURUSD produce statistically similar
  results" (unknowable until EURUSD data exists).
- **Not a gate decision.** Same disclaimer as `S1_G3_STRUCTURAL_CONFORMANCE.md`
  — this report does not open, pass, or change any gate's status.
  `NEXT_ACTION.md` continues to name A2/S1-G2 as the single active
  milestone.
- **No lifecycle, A3, or execution logic** was added or touched.

## Governance state (unchanged)

A2 remains in progress. A3 remains blocked. No governance file
(`PROJECT_STATUS.md`, `OWNER_DECISION_LOG.md`, `NEXT_ACTION.md`,
`governance/st_c3_stage_status.yaml`) was modified to produce this report.
The parallel v1.0.6 line remains quarantined, unverified, and unused here.
