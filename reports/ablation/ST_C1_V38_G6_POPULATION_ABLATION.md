# ST-C1 v3.8 (R2.1) — Locked G6 Population Feasibility Ablation

Per `reports/audit/ST_C1_V38_G6_POPULATION_RCR.md`. Independent variable:
`poi_entry_to_sweep_max_m5_bars` only (B0=30 control, B1=72, B2=144). G4
disabled in all three cells (population diagnostics, not strategy-performance
results). All other rules, costs, models, symbol universe, sessions, and
repaired-candle policy held fixed. Data: same full local development history
per symbol used throughout this research track (not a sealed OOS partition —
see `reports/audit/ST_C1_V38_PRE_EDIT_FINDINGS.md` §6).

## Results

| Symbol | Cell | G5-qualified distinct POIs | Completed G6 sequences | Pass rate | Elapsed |
|---|---|---|---|---|---|
| EURUSD | B0 | 121 | 2 | 1.65% | 99.9s |
| EURUSD | B1 | 121 | 3 | 2.48% | 86.2s |
| EURUSD | B2 | 121 | 5 | 4.13% | 87.7s |
| GBPUSD | B0 | 117 | 3 | 2.56% | 70.3s |
| GBPUSD | B1 | 117 | 3 | 2.56% | 87.1s |
| GBPUSD | B2 | 117 | 4 | 3.42% | 72.6s |
| XAUUSD | B0 | 135 | 3 | 2.22% | 86.9s |
| XAUUSD | B1 | 135 | 5 | 3.70% | 101.4s |
| XAUUSD | B2 | 135 | 5 | 3.70% | 95.2s |
| **Total** | | **373** | **B0=8, B1=11, B2=14** | | |

Full funnel/rejection-code detail in `reports/diagnostics/ST_C1_V38_G6_LATENCY_REPORT.md`.
Raw data: `reports/ablation/st_c1_v38_g6_population_raw.json` (alias of
`reports/diagnostics/st_c1_v38_g6_population_summary.json` — see note below).

## Precommitted selection rule, applied mechanically (checked B0, then B1, then B2)

| Criterion | B0 | B1 | B2 |
|---|---|---|---|
| 1. >=30 completed sequences total | 8 — **FAIL** | 11 — **FAIL** | 14 — **FAIL** |
| 2. >=5 completed in >=2 symbols | 0 symbols — FAIL | 1 symbol (XAUUSD) — FAIL | 2 symbols (EURUSD, XAUUSD) — PASS |
| 3. Coverage across >=2 calendar years | PASS (2025+2026, all symbols) | PASS | PASS |
| 4. G6 pass rate <=10% of G5-qualified | PASS (1.65-2.56%) | PASS (2.48-3.70%) | PASS (3.42-4.13%) |
| 5. Clean == resumed | PASS (see below) | not separately re-verified (moot — B1 fails criterion 1 regardless) | PASS (see below) |
| 6. No fail-open/look-ahead test failure | PASS (`tests/test_g6_latency_diagnostics.py`, 11/11) | PASS | PASS |

**No cell satisfies all six criteria.** Criterion 1 (the primary population
floor) is not met by B0, B1, or B2 — B2, the maximum bound permitted in this
task (144 bars, 4.8x the control), still produces only 14 total completed
sequences across all three symbols over the full available history, well
short of the precommitted 30-sequence floor.

## Decision

Per the RCR's own precommitted rule: **"If neither B1 nor B2 qualifies,
reject the hypothesis and stop. Do not widen beyond 144 in this task."**

**HYPOTHESIS REJECTED** within the tested range (B0-B2). No v3.8 candidate
is created. This is not selected on profitability grounds — P&L was never
computed for this experiment, consistent with the RCR's exclusion of PF/
expectancy/Sharpe/win-rate/drawdown from the selection criteria.

## Why this is still a useful result (not merely "no")

The funnel shape shows the hypothesis was PARTIALLY correct and precisely
falsifiable: widening `poi_entry_to_sweep_max_m5_bars` sharply reduces
`REJECTED_NO_SWEEP` exactly as predicted (e.g. EURUSD 68→35→3 across
B0→B1→B2). But the population that survives is then caught by
`REJECTED_NO_DISPLACEMENT` (a fixed parameter in this experiment, not the
tested variable), which grows to dominate at B1/B2 in every symbol. The
sweep-timing bound was A real constraint, but not THE binding constraint —
the ATR-based displacement requirement immediately downstream is now the
larger bottleneck once sweep timing is relaxed. This is a concrete,
falsifiable candidate for a follow-up Research Change Request — not
something this task resolves or acts on.

## Safety

No parameters were selected or promoted. No broker orders sent. No demo/live
flags touched. Nothing committed or pushed.
