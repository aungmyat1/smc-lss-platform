# ST-C1 v3.8 (R2.1) — G6 Latency Diagnostic Report

Instrumentation: `validation/g6_latency_diagnostics.py` (research-diagnostic
only — never imported by any broker/execution path). Raw per-candidate
records: `reports/diagnostics/st_c1_v38_g6_latency_raw.json`. Per-cell
summary: `reports/diagnostics/st_c1_v38_g6_population_summary.json`.

## Methodology note (disclosed, not a silent optimization)

This tracer walks FORWARD from each POI's own creation bar to find its touch,
sweep, displacement, CHoCH, and retrace — the natural direction for a
causal-latency measurement. The production engine
(`historical_replay_engine_v37.py`) instead searches BACKWARD from "today"
over the last `m5_poi_entry_search_bars` bars on every evaluation call. The
two methodologies are not identical and can disagree on which POIs are
"touched" within the window. This means the population counts below are
**not** a bar-for-bar reproduction of the production engine's behavior —
they are the correct basis for a latency/population-feasibility diagnostic,
which is what this task requires, but the difference is recorded here so it
is never mistaken for "the production engine now finds trades."

## G5-qualified population (distinct POIs, deduplicated) — same across all 3 cells per symbol, since G1/G2/G5 are held fixed

| Symbol | G5-qualified distinct POIs |
|---|---|
| EURUSD | 121 |
| GBPUSD | 117 |
| XAUUSD | 135 |

## Completed G6 sequences by cell

| Symbol | B0 (30) | B1 (72) | B2 (144) |
|---|---|---|---|
| EURUSD | 2 | 3 | 5 |
| GBPUSD | 3 | 3 | 4 |
| XAUUSD | 3 | 5 | 5 |
| **Total** | **8** | **11** | **14** |

## G6 pass rate (completed / G5-qualified)

| Symbol | B0 | B1 | B2 |
|---|---|---|---|
| EURUSD | 1.65% | 2.48% | 4.13% |
| GBPUSD | 2.56% | 2.56% | 3.42% |
| XAUUSD | 2.22% | 3.70% | 3.70% |

All well under the 10% ceiling in every cell — the gate is not degenerating
into an always-pass rule as the bound widens.

## Where rejections concentrate as the bound widens (funnel shape)

| Symbol | Cell | REJECTED_NO_TOUCH | REJECTED_NO_SWEEP | REJECTED_NO_DISPLACEMENT | REJECTED_NO_CHOCH | REJECTED_NO_RETRACE | CENSORED_NO_TOUCH |
|---|---|---|---|---|---|---|---|
| EURUSD | B0 | 13 | 68 | 37 | 0 | 0 | 1 |
| EURUSD | B1 | 13 | 35 | 68 | 0 | 1 | 1 |
| EURUSD | B2 | 13 | 3 | 95 | 0 | 4 | 1 |
| GBPUSD | B0 | 17 | 53 | 40 | 1 | 1 | 2 |
| GBPUSD | B1 | 17 | 26 | 63 | 3 | 3 | 2 |
| GBPUSD | B2 | 17 | 9 | 79 | 3 | 3 | 2 |
| XAUUSD | B0 | 17 | 64 | 49 | 0 | 1 | 1 |
| XAUUSD | B1 | 17 | 27 | 81 | 2 | 2 | 1 |
| XAUUSD | B2 | 17 | 6 | 101 | 2 | 3 | 1 |

**Widening `poi_entry_to_sweep_max_m5_bars` does exactly what the
hypothesis predicted at the sweep stage**: `REJECTED_NO_SWEEP` drops sharply
(EURUSD 68→35→3, GBPUSD 53→26→9, XAUUSD 64→27→6) as the bound widens from 30
to 144. But the population that survives the sweep stage is now caught by a
**different, fixed** gate: `REJECTED_NO_DISPLACEMENT` grows to become the
dominant rejection reason at B1/B2 in every symbol (e.g. EURUSD 37→68→95).
`displacement_atr_mult=1.5` / `body_ratio_min=0.5` are NOT the independent
variable in this experiment and were correctly held fixed — but this is the
concrete, falsifiable candidate for a follow-up RCR (see final validation
decision).

## Latency percentiles (bars), COMPLETED sequences only — small-n caveat

Sample sizes are 2-5 per cell/symbol; percentiles below are reported exactly
as computed but should not be read as precise population statistics at this
sample size — they are directional only.

| Symbol | Cell | touch_to_sweep p50 | p90 | n |
|---|---|---|---|---|
| EURUSD | B0 | 0 | 13 | 2 |
| EURUSD | B1 | 13 | 57 | 3 |
| EURUSD | B2 | 57 | 139 | 5 |
| GBPUSD | B0 | 0 | 13 | 3 |
| GBPUSD | B1 | 0 | 13 | 3 |
| GBPUSD | B2 | 13 | 136 | 4 |
| XAUUSD | B0 | 12 | 26 | 3 |
| XAUUSD | B1 | 26 | 64 | 5 |
| XAUUSD | B2 | 26 | 64 | 5 |

Full latency distributions (poi_creation→touch, touch→sweep, sweep→
displacement, displacement→CHoCH, CHoCH→retrace) for every cell/symbol are in
`st_c1_v38_g6_population_summary.json`; per-candidate raw traces (including
every REJECTED/CENSORED candidate, not just COMPLETED ones) are in
`st_c1_v38_g6_latency_raw.json`.

## Session / year / direction coverage of COMPLETED sequences

All cells show coverage across both 2025 and 2026, both London and New York
sessions, and (from B2 onward) both directions in EURUSD/GBPUSD/XAUUSD —
criterion 3 of the RCR's selection rule (>=2 distinct years) is satisfied at
every bound tested. Full breakdown in the summary JSON.

## Censoring vs. rejection

`CENSORED_NO_TOUCH` (1-2 per symbol, stable across cells) represents POIs
created too close to the end of the loaded dataset for the touch-search
window to fully elapse — genuinely unknown, not a negative result. All other
non-completions are ordinary REJECTED outcomes: the full allowed search
window was available and no qualifying event was found within it.
