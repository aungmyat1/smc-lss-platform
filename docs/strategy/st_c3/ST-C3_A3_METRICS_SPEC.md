# ST-C3 A3 Metrics Specification

**Status:** planning material, like `ST-C3_BACKTEST_SPEC.md` — non-normative,
does not itself change `specs/st-c3_v1.0.6.yaml`, detection logic, or any
tunable parameter, so it is not subject to `docs/RESEARCH-CHARTER.md`'s RCR
requirement (which governs `specs/*.yaml`/detection-logic/tunable-behavior
changes, not report/metrics definitions). Deliberately kept out of
`specs/` to avoid being mistaken for the RCR-governed strategy
specification.
**Authorized under:** A3 opening (owner decision, 2026-07-26, see
`reports/validation/st_c3/OWNER_DECISION_LOG.md`, "A3 statistical
validation — OPENED" entry). Defines what A3 should measure once enough
data exists; does not authorize execution, optimization, demo, or live.

---

## 1. Purpose

A3 evaluates **funnel behavior**, not **strategy performance**. These
metrics quantify how the real S0-S13 funnel (`validation/st_c3/kernel.py` +
`validation/st_c3/evidence_builder.py`, spec `v1.0.6`) behaves over
historical data: where it rejects, how often it reaches each state, and —
once TradePlans actually exist — how those plans resolve. They do not
judge profitability, do not propose parameter changes, and do not
authorize execution.

---

## 2. Metric Categories

### 2.1 Funnel-Level Metrics

Already implemented in `validation/st_c3/a3_replay_engine.py`'s
`run_a3_replay()` return value (`result["metrics"]`):

- **Signal rate** (`metrics["signal_rate"]`) — fraction of scanned M15
  bars where S13 (`TRADE_PLAN_EMIT`) is reached.
- **Rejection distribution** (`metrics["rejections_by_code"]`) — counts
  per actual R-code. The frozen funnel emits exactly **R1 through R8**
  (`R1_HTF_BIAS_UNCLEAR` .. `R8_INVALID_RISK_OR_TARGET`, one per guard
  state S1-S12) — not R1-R12; there is no R9 through R12 in
  `specs/st-c3_v1.0.6.yaml`'s `rejection_code_json_schema`.
- **Funnel-stage reach distribution** (`metrics["states_reached_counts"]`)
  — how many bars reached each of the 12 named guard states
  (`kernel.STATE_ORDER`), i.e. where the funnel spends its time before
  rejecting or emitting.
- **Session bar/signal counts** (`metrics["session_counts"]`,
  `metrics["session_signal_counts"]`) — LONDON/NY only, per `v1.0.6`'s
  ratified UTC bounds (R-33). There is no Asian session in this spec.

### 2.2 Evidence-Chain / Structural-Prerequisite Metrics

Derivable from `states_reached_counts` and the rejection distribution
without new code:

- **Sweep -> Reclaim -> BOS chain frequency** — bars reaching
  `S4_DISPLACEMENT_BOS` or later, as a fraction of bars reaching
  `S2_SWEEP`.
- **OB / FVG confluence frequency** — bars reaching `S8_FVG_OB_CONFLUENCE`
  as a fraction of bars reaching `S7_OTE`.
- **Entry-window availability** — bars reaching `S11_ENTRY_WINDOW`, given
  the current `_entry_window()` implementation always resolves
  `bars_since_ltf_choch=0` (documented limitation in
  `evidence_builder.py`) — this metric currently measures "LTF
  confirmation resolved," not a real bars-since-CHoCH distribution, and
  the entry window itself is measured in **M15 bars** (R-32,
  `ENTRY_WINDOW_BARS=4`), not M3 bars.

### 2.3 TradePlan Lifecycle Metrics

Only computable once TradePlans exist — `a3_replay_engine._simulate_lifecycle()`
already emits the raw fields (`hits`, `sl_hit`, `realized_rr`,
`unrealized_rr`, `termination`, `bars_held`); these are the rollups to
compute from them across a run:

- **TP1/TP2/TP3 hit rate** — fraction of TradePlans whose `hits` include
  each target.
- **SL hit rate** (`metrics["closed_trade_count"]` vs. count where
  `sl_hit=True`).
- **Realized RR distribution** — from `metrics["rr_samples"]`
  (`avg_rr`/`max_rr`/`min_rr` already computed; percentiles are a
  straightforward aggregation of the same list).
- **BIAS_FLIP rate** (`metrics["bias_flip_count"]`).
- **Lifecycle duration** — `bars_held` per closed trade.

**Current status (2026-07-27):** zero TradePlans exist in the only replay
run so far (`reports/validation/st_c3/A3_REPLAY_RESULTS.md`), so every
metric in this subsection is presently undefined (`None`/empty), not zero
or negative — that distinction matters when a report reads these numbers.

### 2.4 Session-Level Metrics

Already partially implemented (`session_counts`, `session_signal_counts`).
Extending to session-level rejection distribution and session-level RR
requires only re-running the same aggregation filtered by
`log_entry["session"]` — no new detection logic.

### 2.5 Stability / Rolling Metrics

Not implemented in the current `a3_replay_engine.py`. Rolling-window
signal rate, rejection distribution, and RR distribution (e.g. a 500-bar
window) require enough total bars for multiple non-overlapping windows to
exist — meaningless on the current ~3,300-bar single window, and are
listed here as a **future** metric category, not a current gap.

---

## 3. Required Outputs

- **`A3_REPLAY_RESULTS.md`** — raw per-run summary (exists:
  `reports/validation/st_c3/A3_REPLAY_RESULTS.md`).
- **`A3_METRICS_SUMMARY.md`** — the aggregated metrics in §2, across all
  runs to date. Not yet created — trivial once a second run (different
  data) exists to compare against; a single-run summary would just
  restate `A3_REPLAY_RESULTS.md`.
- **`A3_BEHAVIORAL_ANALYSIS.md`** — non-evaluative interpretation (e.g.
  "the funnel is bottlenecked upstream at S1/S2 on short windows"). Not
  yet created for the same reason — one data point does not support
  behavioral interpretation beyond what `A3_REPLAY_RESULTS.md` already
  states.

Creating either of the latter two now, before a second/longer data run
exists, would mean writing a report with no new content beyond
`A3_REPLAY_RESULTS.md` restated under a different filename.

---

## 4. Non-Goals (Explicit Constraints)

A3 does **not** measure or determine:

- Profitability or expectancy.
- Optimal RR targets or any parameter re-tuning.
- Execution viability, slippage, or broker-level behavior.
- Live-trading or demo-trading readiness.

These belong to Stage B (execution qualification) per `MASTER_PLAN.md`'s
active lifecycle model, which defines only A1/A2/A3 within Stage A — there
is no "A4/A5/A6" governance substage in the current model. Any future
optimization or execution work requires its own separate owner decision
and Stage B entry, not an implied continuation of A3.

---

## 5. Data Requirements

Per `specs/st-c3_v1.0.6.yaml`'s own `instruments` field comment: **minimum
3 years per instrument, preferred 5-10 years**, applying at this
statistical-validation phase (not before). The current GBPUSD dataset is
~7 weeks — sufficient to prove the replay engine's detection path is
wired correctly (which it did, reproducing R-18 exactly), but far short of
what's needed for any of the §2.3-2.5 metrics to produce a meaningful
distribution. EURUSD's current CSVs (~20 rows) are unusable for this
purpose (see `reports/validation/st_c3/R27_R30_RESEARCH_REPORT.md`).

---

## 6. Implementation Status

`validation/st_c3/a3_replay_engine.py`'s `run_a3_replay()` already returns
a `metrics` dict covering all of §2.1, §2.3 (schema-ready, empty until
TradePlans exist), and §2.4 (bar-level; session-filtered rollups not yet
separately computed). §2.2's chain-frequency ratios and §2.5's rolling
metrics are not yet implemented — both are straightforward aggregations
over existing `states_reached_counts`/`logs` data, not new detection code,
and are natural candidates for a future small extension once there is
enough data to make them meaningful.
