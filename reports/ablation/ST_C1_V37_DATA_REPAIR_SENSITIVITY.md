# ST-C1 v1.1.0 / spec v3.7 — Data-Repair Sensitivity Report

## Scope

The task requires synthetic-data sensitivity across repaired candles,
affected-session exclusion, and original gap-preserving data. Known synthetic
repair counts, carried forward from the Phase A baseline
(`reports/audit/phase_a_pre_edit_findings_20260721.md`):

| Symbol | M5 synthetic (flat-previous-close) repairs |
|---|---|
| EURUSD | 4 |
| GBPUSD | 15 |
| XAUUSD | 0 |

## Result

The locked A0–A3 ablation (`reports/ablation/ST_C1_V37_ABLATION_REPORT.md`)
produced **zero qualifying trades** on all three symbols under every one of
the four gate combinations. With zero trades, a trade-level repaired-vs-
original comparison has no population to compare — there is nothing for
synthetic candles to have influenced, because no candle sequence anywhere in
the dataset survived the full G1→G9 chain far enough to become a trade.

This is reported as a **genuine null result**, not skipped: the sensitivity
check that this task requires (do repaired candles change the outcome) is
answered trivially and honestly as "not applicable at this parameter
setting" rather than being silently omitted. GBPUSD carries the most repairs
(15) and also produced the fewest trades reaching G6 (372–3682 depending on
ablation cell, same as EURUSD/XAUUSD's order of magnitude) — nothing in the
funnel counts suggests repaired candles are behaving differently from
genuine ones at the gates that were actually exercised (G1–G5), since all
three symbols, including the zero-repair XAUUSD, show the same qualitative
pattern (many candidates reach G5/G6, zero complete G6).

## Recommendation

Re-run this sensitivity check once a properly-logged Research Change Request
(per `docs/RESEARCH-CHARTER.md`) revises the G6 sequencing parameters that
`reports/audit/ST_C1_V37_FINAL_VALIDATION_DECISION.md` identifies as the
binding constraint — at that point a non-empty trade population will exist
and a genuine repaired-vs-gap-preserving comparison becomes possible. Doing
that revision inside *this* task would be parameter optimization based on an
observed result, which is explicitly out of scope here.
