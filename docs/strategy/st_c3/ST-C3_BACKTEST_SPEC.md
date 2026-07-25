# ST-C3 Backtest Specification

**Strategy ID:** ST-C3
**Version:** v1.0.0
**Status:** A3 planning specification; backtesting not authorized

This specification defines the deterministic, evidence-driven, session-aware
backtest harness requirements for ST-C3. It is designed for future Python,
MQL5, or multi-agent implementation after the required governance gates
authorize backtesting.

This document does not authorize implementation, reference-kernel work,
historical backtesting, broker integration, demo trading, live trading, or
production.

---

## 1. Backtest Identity

| Field | Value |
|---|---|
| Strategy | ST-C3 |
| Version | v1.0.0 |
| Mode | Deterministic, evidence-driven, session-aware |
| Purpose | Validate ST-C3 behavior across historical data without deviation from architecture or state machine |

---

## 2. Instruments And Pairs

ST-C3 is designed for high-liquidity, session-reactive instruments.

Primary pairs:

- XAUUSD
- GBPUSD
- EURUSD
- NAS100, optional

Secondary pairs, optional:

- USDJPY
- US30
- SPX500

Each instrument must be tested independently.

---

## 3. Timeframes

The backtest engine must support synchronized multi-timeframe replay:

- H4: bias and sweep context.
- M15: sweep, displacement, BOS, OTE, FVG/OB.
- M3/M1: LTF CHoCH, entry window, invalidation swing.

---

## 4. Sessions

ST-C3 only trades inside:

- London: `07:00-10:00 UTC`
- New York: `13:00-16:00 UTC`

Session enforcement:

```text
if timestamp NOT IN session_window:
    no trades allowed
```

---

## 5. Data Requirements

Minimum data quality:

- Tick or 1-second data preferred.
- M1 minimum.
- No missing candles.
- Accurate session timestamps.
- Accurate spread data.
- Accurate volume if available.

Required fields:

- `open`
- `high`
- `low`
- `close`
- `timestamp`
- `spread`
- `volume`, optional

---

## 6. Funnel Completion Requirement

A trade is only allowed if all 12 pre-entry funnel stages complete:

- HTF bias.
- Sweep.
- Sweep reclaim.
- Displacement.
- BOS.
- BOS extreme lock.
- Dealing range.
- OTE.
- FVG/OB confluence.
- LTF confirmation.
- Session gatekeeper.
- Entry window.

If any stage fails, no trade is allowed.

---

## 7. Evidence Chain Requirement

Every trade must include a full `evidence_chain[]`.

The backtest engine must store:

- Evidence IDs.
- Evidence values.
- Timestamps.
- Validity flags.
- Rejection codes, if any.
- ERR codes, if any.

---

## 8. Entry Logic

Entry must occur:

- Inside entry zone, FVG or OB.
- Inside `MAX_ENTRY_BARS`.
- Inside session window.
- After valid LTF CHoCH.

Entry type:

- Market or limit, depending on the trade plan.

---

## 9. SL/TP Logic

Stop loss:

- SL equals invalidation swing on M3/M1.

Targets:

- TP1 equals internal liquidity.
- TP2 equals external liquidity.
- TP3 equals HTF objective.

Partial exits:

- TP1 closes 30%.
- TP2 closes 30%.
- TP3 closes 40%.

---

## 10. Expiry Logic

The backtest engine must terminate trades using only these ERR-codes:

- `ERR_HTF_BIAS_FLIP`
- `ERR_ENTRY_WINDOW_EXPIRED`
- `ERR_SL_INVALIDATION`
- `ERR_SUPERSEDED_SETUP`

No other termination reasons are allowed.

---

## 11. Metrics To Compute

Core metrics:

- Win rate.
- RR distribution.
- Average RR.
- Max RR.
- Drawdown.
- Max consecutive losses.
- Session distribution.
- Regime distribution: trend, consolidation.

Advanced metrics:

- Evidence validity frequency.
- Funnel completion rate.
- Rejection code distribution.
- ERR termination distribution.
- Average time in trade.
- Average bars to entry.
- Spread impact.
- Slippage impact.

---

## 12. Backtest Duration

Minimum recommended duration:

- FX: 3 years.
- Indices: 5 years.
- XAUUSD: 10 years if data is available.

---

## 13. Backtest Output Format

Each trade must produce:

- `TRADE_ID`
- `TRADE_PLAN_ID`
- `direction`
- `entry_price`
- `sl_price`
- `tp1_price`
- `tp2_price`
- `tp3_price`
- `rr`
- `session`
- `evidence_chain[]`
- `rejection_code`, if any
- `termination_code`, if any
- `timestamps`: entry, TP1, TP2, TP3, SL, expiry

---

## 14. Backtest Validation Rules

A backtest is valid only if:

- No trades occur outside session windows.
- No trades occur without full funnel completion.
- No trades are missing `evidence_chain`.
- No trades are missing SL/TP.
- No trades are missing RR.
- No trades are missing termination codes where termination occurs.
- No trades are missing timestamps.
- No trades are missing session tags.
- No trades are missing trade-plan IDs.

If any rule fails, the backtest is invalid.

---

## 15. Backtest Reports

A completed, authorized backtest must produce:

- `ST-C3_BACKTEST_REPORT.md`
- `ST-C3_BACKTEST_EVIDENCE_LOG.json`
- `ST-C3_BACKTEST_TRADE_LOG.json`
- `ST-C3_BACKTEST_SUMMARY.md`
