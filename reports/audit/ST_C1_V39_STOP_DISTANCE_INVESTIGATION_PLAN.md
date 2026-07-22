# Research Plan: v3.9 Stop-Distance Investigation

Date: 2026-07-22
Status: Active (Phase 2 — research/validation, per `NEXT_ACTION.md`)
Owner: Aung Myat

## Objective

Determine why ST-C1 v3.9 trades are cost-dominated, specifically whether
stop-distance inflation is caused by:

- structural SL placement rules,
- liquidity-mapping errors,
- session-window mismatches,
- symbol-specific volatility,
- or detection-logic drift between v3.8 -> v3.9.

This directly answers the open question in `NEXT_ACTION.md` "After this
milestone": whether the ATR*0.15 stop buffer convention is wrong for this
preset, or whether E2/E3's zeroed wick-ratio filter admits zones too tight
to trade net of cost.

## Scope (Phase 2 only)

This investigation does **not** modify detection logic. It produces
analysis only. Any change to `specs/*.yaml` or detection logic that this
analysis motivates requires a full six-question RCR per
`docs/RESEARCH-CHARTER.md`, logged to `reports/research_log.md`, before any
backtest is run against it.

## Tasks

### 1. Extract v3.9 stop-distance distribution
- Pull all v3.9 completed/rejected trades from the existing backtest/replay
  output (per `reports/audit/ST_C1_V39_POPULATION_ABLATION_SPEC.md`).
- Compute: SL distance (points/pips), RR distribution, cost-adjusted RR,
  session-tagged SL distances, symbol-tagged SL distances.

### 2. Compare v3.8 vs v3.9 SL anchors
- Identify structural pivot differences.
- Identify liquidity-mapping differences.
- Identify CHoCH vs displacement confirmation differences.
- Determine whether v3.9 anchors are systematically farther.

### 3. Session-window correlation
- Tag trades by London AM / London PM / NY AM / NY PM.
- Determine whether SL inflation correlates with session windows, and
  cross-check against the already-flagged `specs/v3.9.yaml` vs
  `config/watchlist.yaml` session-window mismatch.

### 4. Symbol-specific volatility analysis
- Compare EURUSD, GBPUSD, XAUUSD (the symbols already populated per the
  ablation spec).
- Compute ATR at entry, SL/ATR ratio, volatility-adjusted RR.

### 5. Produce findings
- Summary, tables, and a recommendation on whether an RCR is warranted.

## Deliverables

- `reports/audit/ST_C1_V39_STOP_DISTANCE_ANALYSIS.md`
- Supporting data/plots under `reports/audit/` (naming TBD at analysis time)
- RCR proposal per `docs/RESEARCH-CHARTER.md` — only if findings justify a
  detection-logic change

## Constraints

- No code changes.
- No spec changes.
- No ADR changes.
- No conformance-kernel or scenario-binding modules.
- Research only.

## Expected outcome

A clear, evidence-backed explanation of why v3.9 trades are cost-dominated,
and whether a future RCR should propose a detection-logic adjustment.
