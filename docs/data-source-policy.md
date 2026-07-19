# Data Source Policy — SMC-LSS Platform

**Status:** Accepted · **Decision date:** 2026-07-18 · **Owner:** SVOS Research (data ingestion)
**Supersedes:** none · **Related:** MCP connector setup (MetaTrader 5, Alpha Vantage, FMP)

---

## Decision

**MetaTrader 5 (MT5) is the canonical OHLC source** for every instrument the strategy
prices, backtests, or executes against. Third-party feeds (Alpha Vantage, FMP) are
**context/reference sources only** and must never supply price bars that enter a
backtest series or a live signal.

No backtest series may mix a broker-close value with a third-party reference/spot value.
One canonical series per instrument.

## Source roles

| Layer | Source | Used for | Not used for |
|---|---|---|---|
| **Canonical OHLC** | MetaTrader 5 | All open/high/low/close bars — FX, metals, crypto, indices. Backtests, SMC structure (sweeps, FVG, order blocks), live execution. | — |
| **Reference / context** | Alpha Vantage | Economic indicators (CPI, NFP, rates), technical-indicator cross-checks, news sentiment, FX sanity checks. | OHLC bars in any backtest or signal. |
| **Reference / context** | FMP | Commitment of Traders (COT), economic calendar, market hours, positioning context. | OHLC bars in any backtest or signal. |

## Rationale (validated 2026-07-18)

Feed-parity check, MT5 vs Alpha Vantage, close of 2026-07-17:

| Symbol | MT5 close | Alpha Vantage | Divergence | Note |
|---|---|---|---|---|
| EURUSD | 1.14375 | 1.14390 | +0.013% | FX feeds agree to 4dp |
| GBPUSD | 1.34545 | 1.34530 | −0.011% | FX feeds agree to 4dp |
| BTCUSD | 64,110.96 | 63,894.00 | −0.34% | Normal cross-venue crypto spread; different UTC roll |
| XAUUSD | 4,018.25 | 3,984.54 | −0.84% | AV gold is a single daily **spot reference** (no OHLC) |

Key findings:
- FX parity is effectively perfect — but standardizing on MT5 avoids ever mixing conventions.
- **Alpha Vantage gold (`GOLD_SILVER_HISTORY`) returns one spot value per day, no highs/lows** —
  structurally unusable for SMC, which depends on intraday wicks. This is the primary reason
  a single canonical OHLC source is mandatory.
- Crypto diverges ~0.34% across venues and rolls at 00:00 UTC; broker-close is the reference.

## Rules for the backtesting / feature loader

1. Every price series is tagged `source = MT5` and `convention = broker-close`.
2. Reject any attempt to load OHLC from Alpha Vantage or FMP into a backtest or signal path.
3. Reference data (COT, economic calendar, indicators, news) may be joined by timestamp but
   is stored in a separate namespace from price bars.
4. Timestamps normalized to UTC; align to MT5 daily roll, not the third-party roll.

## Divergence guard (recommended, not yet implemented)

Daily check comparing MT5 close vs a reference feed per symbol. Flag before the day enters
any backtest if divergence exceeds:
- FX: **0.5%**
- Crypto / metals: **1.0%**

A flag means "investigate feed drift," not "switch source" — MT5 remains canonical.

## Symbol mapping (MT5 canonical names)

| Instrument | MT5 symbol |
|---|---|
| EURUSD | `EURUSD` |
| GBPUSD | `GBPUSD` |
| Gold | `XAUUSD-VIP` (≡ `XAUUSD.crp`, verified identical) |
| BTCUSD | `BTCUSD` |
