# Research Change Request — G6 POI-Entry-to-Sweep Population Feasibility (R2.1)

Filed per `docs/RESEARCH-CHARTER.md` before any new backtest or latency scan
runs. Preregistered in full below; the selection rule is committed BEFORE
the B0/B1/B2 experiment executes.

## Change: G6 poi_entry_to_sweep_max_m5_bars population feasibility (v3.7 -> diagnostic-only, no spec bump yet)
Date: 2026-07-21
Author: Claude (research agent), R2.1 task

### Why
`reports/ablation/ST_C1_V37_ABLATION_REPORT.md`: all 12 cells of the locked
v3.7 A0-A3 ablation produced zero trades on EURUSD/GBPUSD/XAUUSD full
history. G6 saturates identically across every cell (location and net-RR
ablation flags are downstream of G6 and never get exercised). A diagnostic
example on real EURUSD data found the nearest matching M5 sweep 127 bars
after a genuine POI touch — roughly 4x the locked `poi_entry_to_sweep_max_m5_bars=30`.

### Evidence
`reports/ablation/st_c1_v37_ablation_raw.json`: `rejected_g6` (== total
G5-qualified population, since `candidate_ready=0` everywhere) ranges 372-5022
across cells/symbols, with 0 passing in every case — a 0% G6 pass rate
against a population large enough that a 0% rate is not attributable to
small-sample noise.

### Hypothesis
The 30-bar `poi_entry_to_sweep_max_m5_bars` limit is shorter than the normal
causal latency between a genuine HTF-POI touch and the M5 sweep that follows
it. A bounded increase (not unbounded — this task caps at 144 bars, roughly
4.8x the current value and roughly matching the single diagnostic latency
observation) can restore a nonzero, statistically usable G6 population
without making G6 effectively always-pass (i.e., without collapsing the gate
into a no-op). This is a **population feasibility** hypothesis, not a
profitability hypothesis — P&L is explicitly excluded from the selection
rule (see below).

### Independent variable
`poi_entry_to_sweep_max_m5_bars` ONLY. Every other rule is held fixed:
G1-G5 unchanged; `displacement_to_choch_max_m5_bars`, `choch_to_retrace_entry_max_m5_bars`,
`m5_poi_entry_search_bars=3200` unchanged; costs, fill model, target model,
management model, symbol universe, sessions, repaired-candle policy,
first-qualifying-bar behavior, and closed-candle/next-bar-open behavior all
unchanged. G4 (premium/discount) is DISABLED for these three diagnostic
cells specifically (population diagnostics, not strategy-performance
results) — the same downstream reward configuration (net reward gate, per
v3.7 defaults) is used identically in all three cells so it cannot bias the
population comparison between them.

### Locked cells
- **B0 = 30** (current v3.7 value — the control)
- **B1 = 72** (2.4x)
- **B2 = 144** (4.8x — the ceiling for this task; NOT to be widened further)

### Expected result / falsifiable numbers
If the hypothesis is correct, B1 and/or B2 will show a nonzero completed-G6-sequence
count that grows with the bound, while the G6-pass-rate-over-G5-qualified
stays well under 100% (evidence the gate is still discriminating, not merely
disabled by a large window). If B2 still shows zero or a near-zero (<30
total) completed sequences, the hypothesis is rejected within the tested
range — no further widening is performed in this task.

### Precommitted selection rule (stated before running anything)
Select the **smallest** bound (checked in order B0, B1, B2) that satisfies
ALL of:
1. At least 30 completed G6 sequences in total across all three symbols.
2. At least 5 completed sequences in at least 2 of the 3 symbols.
3. Coverage across at least 2 distinct calendar years present in the data.
4. G6 pass rate <= 10% of G5-qualified candidates (i.e., the gate must still
   reject at least 90% of what reaches it — evidence it did not degrade into
   an always-pass gate).
5. Clean and resumed runs produce identical completed-sequence counts and
   identical latency distributions (determinism / no silent state leakage).
6. No fail-open or look-ahead test failure (see STEP 4 tests).

**If B1 qualifies, B1 wins even if B2 has strictly better trade/PF/expectancy
numbers** — profitability is explicitly excluded from this selection; only
population-feasibility criteria 1-6 above are used. If only B2 qualifies, B2
is selected. If neither B1 nor B2 qualifies, the hypothesis is REJECTED (or
INCONCLUSIVE if criterion 5 or 6 fails on an otherwise-qualifying cell) and
**no v3.8 candidate is created** — this task stops at that point rather than
widening beyond 144.

### Success criteria
The six criteria above, checked mechanically against the B0/B1/B2 run
output — not PF, expectancy, Sharpe, win rate, or drawdown, all of which are
explicitly excluded from this decision by design.

### Rollback criteria
- Any cell where clean vs. resumed runs disagree -> INCONCLUSIVE for that
  cell, do not select it even if criteria 1-4 otherwise pass.
- Any fail-open (a gate defaulting to pass on missing/malformed input) or
  look-ahead (a candidate using data not yet closed as of its evaluation
  time) detected in the STEP 4 test additions -> stop, fix the engineering
  defect, re-run before any selection is made.
- If B2 does not qualify -> REJECTED/INCONCLUSIVE, full stop, no v3.8 files
  created, no further widening attempted in this task.

---
Logged to `reports/research_log.md` in date order alongside this entry, per
`docs/RESEARCH-CHARTER.md`. No backtest or latency scan was run before this
template was filed.
