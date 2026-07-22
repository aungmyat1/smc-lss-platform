# ST-C1 v3.9 vs v3.10 — Comparison (Corrected Data)

Date: 2026-07-22
Status: Diagnostic comparison only — no promotion, selection, or spec
change made. Uses the corrected trade populations from
`reports/audit/ST_C1_DEDUP_BUG_AND_CORRECTED_RESULTS.md`, not the original
(bugged) v3.9/v3.10 analyses.

Per `project-governance-agent`'s ruling, this comparison is run *before*
any spec-drafting decision, to determine whether the next step should be a
symbol-whitelist RCR, a detection-logic RCR, or no change.

## Net-of-cost result, side by side

| | v3.9 B1 | v3.10 |
|---|---|---|
| Total trades | 239 | 2,217 |
| Net PF (aggregate) | 0.138 | 0.469 |
| Net expectancy | -0.710R | -0.416R |
| Net win rate | 19.2% | 46.4% |
| Best symbol | XAUUSD (PF 0.382) | XAUUSD (PF 0.734) |
| Worst symbol | EURUSD (PF 0.049) | EURUSD (PF 0.309) |

**Both candidates are net-losing in aggregate and in every individual
symbol.** v3.10 is directionally less bad than v3.9 on every metric shown
(higher PF, less negative expectancy, higher win rate, both aggregate and
per-symbol) — but "less bad than a strategy with PF 0.138" is a low bar;
neither clears any promotion threshold.

## Symbol-level split — present in both, same direction

| Symbol | v3.9 net PF | v3.10 net PF |
|---|---|---|
| EURUSD | 0.049 | 0.309 |
| GBPUSD | 0.125 | 0.460 |
| XAUUSD | 0.382 | 0.734 |

The relative ranking (XAUUSD best, GBPUSD middle, EURUSD worst) is
identical in both engines, despite completely different detection logic.
This is the strongest single piece of evidence in this comparison: **the
symbol-level effect is not specific to either engine's design** — it
persists across two independently-built detection approaches, on the same
underlying cost model. That points at a structural cost/instrument-scale
mismatch (per `ST_C1_DEDUP_BUG_AND_CORRECTED_RESULTS.md` and the original
stop-distance analysis's cost-model reasoning), not a flaw unique to
either candidate's alpha logic.

## Scenario/trigger population — v3.9 vs v3.10 differ sharply

| Variant | v3.9 B1 (n=239) | v3.10 (n=2,217) |
|---|---|---|
| E1* (gap-reversal, any M-model) | 0 | **0** |
| E2M1 | 74 | 454 |
| E2M2 | 127 | 105 |
| E3M1 | 21 | 1,327 |
| E3M2 | 17 | 329 |
| E3M3 | 0 | 2 |

Two notable findings:

1. **v3.10 executed zero E1-triggered trades, in any symbol, despite E1
   (D1 gap-reversal against H4 trend) being the specific new mechanism
   this candidate was built to capture** (`ST_C1_V310_REVERSAL_CAPTURE_RCR.md`'s
   entire stated thesis). Every executed v3.10 trade is E2 or E3 — the same
   trigger families v3.9 already uses. This means v3.10's actual realized
   population, once the dedup bug is corrected, is not evidence for or
   against the reversal-capture thesis at all — it never got a single
   trade through that gate. Worth a dedicated look at why (a gate elsewhere
   filtering all E1 candidates out before they reach execution, e.g. the
   H4-divergence requirement or the 3-bar hold confirmation being far more
   restrictive than the RCR's existence check suggested) — **not
   diagnosed in this pass.**
2. v3.10 is heavily E3M1-dominated (1,327 of 2,217, ~60%) versus v3.9's
   more even E2M1/E2M2 split. Both use the same E3 sweep/reclaim family,
   but v3.10's version (internal sweeps accepted, per the RCR) fires far
   more often relative to its own population than v3.9's (external-sweep
   only) does.

## Session compliance

Both fully compliant: 0 of 239 (v3.9) and 0 of 2,217 (v3.10) trades fall
outside the `specs/v3.9.yaml`/`specs/v3.10.yaml` London (07-16 UTC) / New
York (12-21 UTC) session windows.

## Stop-distance / cost-scale comparison

Not independently re-derived here (would require the same engine
instrumentation flagged as a follow-up in the original stop-distance
analysis). The symbol-level PF ranking match above is treated as
sufficient evidence that the same cost/scale mechanism is at work in both,
without re-deriving raw SL distances per trade in this pass.

## What this determines

Per the three options `NEXT_ACTION.md`/the owner posed:

- **Symbol whitelist restriction (config-level):** the strongest-supported
  option given the evidence above — the symbol ranking is consistent
  across two independent engines, suggesting a structural, symbol-specific
  cause. But note XAUUSD itself is *still net-losing* in both corrected
  reads (PF 0.382 / 0.734) — a symbol restriction alone would not currently
  produce a profitable candidate from either engine as-is; it would only
  narrow the loss.
- **Detection-logic change:** weaker support. v3.10's E3M1-heavy,
  zero-E1 population suggests the two candidates aren't actually testing
  different alpha theses in practice (both end up trading E2/E3
  continuation-family setups) — a new detection design would need to
  address why E1 never fires, not just relabel the spec version.
- **No change:** not supported — both candidates are clearly net-losing,
  which itself is decision-relevant information, not a null result.

## Recommendation

Neither "draft v40" nor "pick a winner between v3.9/v3.10" is supported by
this comparison. Two concrete next steps, both requiring their own RCR
before implementation, are better supported than a new spec version:

1. Diagnose why v3.10 never executes an E1 trade — this is a prerequisite
   to judging the reversal-capture thesis at all, before any further
   development of that design.
2. If a symbol-restriction hypothesis is pursued, it should be framed
   explicitly as "reduces losses, does not yet produce a profitable
   candidate" — per the RESEARCH-CHARTER's evidence-first discipline, not
   oversold as a fix.

Neither is executed here; this is a diagnostic comparison only.
