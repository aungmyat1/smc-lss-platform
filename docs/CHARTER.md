# SMC-LSS Platform — Project Charter

## Objective
Operate a disciplined, semi-autonomous Smart Money Concepts (SMC-LSS) trading
system that Claude Cowork runs on a schedule: on each run it analyzes a preset
watchlist with a locked deterministic strategy, and — when every hard gate passes
— **executes automatically on a verified demo account**, or **prepares a
confirmation-gated intent for the live account**. The system never improvises: it
follows one versioned rulebook, sizes to fixed risk, and journals every outcome.

## Vision (end state)
A hands-off daily loop where the human sets policy (symbols, risk, promotion) and
reviews results, while Claude executes the mechanical work: fetch data → analyze →
verify environment → size → execute (demo) / propose (live) → manage → journal →
report. Live trading is unlocked only after the demo track meets published
qualification gates.

## Operating policy

### Autonomy
| Environment | Behavior on a GO signal |
|---|---|
| **Demo** (verified) + engine implements spec | **Auto-execute** — place + set SL/TP, then journal. |
| **Demo** (verified), engine NOT yet spec-complete | **Propose-mode** — analyze, size, journal the intent; hold for review (current state). |
| **Live** | **Blocked** — v3.5 is `RESEARCH_CANDIDATE`; no live orders until it is promoted out of research AND demo gates pass. |
| **Unverified / not demo** | **Blocked** — no order; alert only (fail-safe). |

**Safety interlock:** demo auto-execution is enabled only when
`specs/v3.5.yaml: implementation_status.engine_implements_spec == true`. Until the
v3.5 nine-variant `generate_signal()` engine is implemented and backtested, the
loop runs in **propose-mode** — it never blind-fires orders from code that does
not yet implement the strategy of record. `promote_to_live` stays `false`
regardless, until the demo qualification gates below are met.

### Watchlist (tiered) → v3.5 variant mapping
| Symbol | Tier | Primary v3.5 variant(s) | Bias |
|---|---|---|---|
| EURUSD | Active | E1M3, E3M3 | SELL-side |
| XAUUSD | Active | E1M1 | SELL-side |
| GBPUSD | Pending | major analog to E2M1/E3M1 family | both |
| BTCUSD | Pending | E2M3 | SELL-side |

Pending symbols enable only after owner confirmation. Any symbol still requires a
live-confirmed variant on closed candles — the mapping is the expected cell, not a forced trade.

### Cadence (derived from strategy)
v3.5 signals form on **closed candles** with an H1 E-trigger and M5 confirmation;
horizons range INTRADAY→INTRAWEEK. The loop scans **twice per weekday** at the
main session windows, then holds positions per their frozen horizon:
- London window — **07:00 UTC** (13:30 Asia/Yangon)
- New York window — **12:00 UTC** (18:30 Asia/Yangon)

Timeframes: E-trigger **H1** (context D1) · confirmation **M5** · management by horizon.

### Risk envelope (hard gates)
- Risk/trade: **0.5%** demo, **1.0%** live
- Daily loss stop: **3%** · Max open positions: **3** · Portfolio heat: **4%**
- Minimum reward:risk **2.0** · Never widen a stop · Stops only tighten

## Safety gates (every run, in order)
1. **Environment verification** — resolve login → server name; demo-safe only when
   the server contains "Demo" (never the connector `account_type` field). Unverified → treat as live/blocked.
2. **Strategy gates (v3.5)** — Stage 1 E-trigger (E1/E2/E3, HTF cause + bias) →
   Stage 2 M-model (M1/M2/M3, M5 confirmation + entry anchor) → Stage 3 direction/SL/TP/horizon.
   Both stages must confirm on closed candles or → NO-GO. (Legacy v1 pipeline retained for reference only.)
3. **Risk gate** — position sizing + all limits; lots rounded down; REFUSE on any breach.
4. **Execution gate** — demo auto-sends; live requires human confirmation; every order carries a stop.
5. **Journaling** — every GO, NO-GO, fill, and reject is logged immutably.

## Demo → Live promotion gates
Flip `promote_to_live: true` only when ALL hold on the demo track:
- ≥ 40 journaled trades under the locked spec version
- Positive expectancy (≥ +0.2R) and profit factor ≥ 1.3
- Max drawdown ≤ 15%; rule-adherence ≥ 95% (no un-journaled or off-spec trades)
- Walk-forward / out-of-sample validation passed (`validation` + `backtest-researcher`)
- Two consecutive clean weekly reviews with no critical mistakes

## Success metrics (KPIs)
Expectancy (R), profit factor, win%, max drawdown, rule-adherence %, average
R:R realized, and uptime of the scheduled loop (runs completed vs scheduled).

## Scope
**In:** scheduled analysis, demo auto-execution, live intent preparation, sizing,
trade management, journaling, reporting, backtest/validation of rule changes.
**Out (for now):** live auto-execution without confirmation, discretionary
overrides, non-watchlist symbols, news-driven or fundamental trading, martingale/
averaging-down, any stop-widening.

## Roadmap
- **M0 — Foundation (done):** repo cleaned, 22 skills, demo-safe env gate, pushed to GitHub.
- **M1 — Daily loop wired (this pass):** charter, v3.5 spec, watchlist config, multi-symbol
  runner, runbook, and scheduled London+NY weekday runs in **propose-mode** on demo.
- **M1.5 — v3.5 engine:** implement `generate_signal(e_trigger, m_model, instrument_profile)`
  with fixtures from the ruleset §4 table; backtest; flip `engine_implements_spec: true` → demo auto-execution activates.
- **M2 — Evidence:** accumulate ≥ 40 demo trades; weekly reviews; tune only via `backtest-researcher`.
- **M3 — Validation:** pass walk-forward/OOS gates; expand to GBPUSD + BTCUSD.
- **M4 — Live pilot:** on meeting promotion gates, enable live with confirm-required at reduced size.
- **M5 — Scale:** raise size/symbols incrementally under the same gates; add CI smoke checks.

## Key risks & mitigations
- **Broker/data outage mid-run** → env + connection preflight; skip symbol, log, alert.
- **Mis-sized non-USD symbols (XAUUSD/BTCUSD)** → pull live tick value per symbol; config specs are fallback only.
- **Environment misread (demo vs live)** → server-name gate + attestation; fail-safe to blocked.
- **Over-optimization** → rule changes only through backtest/validation with locked out-of-sample data.
- **Schedule drift / DST** → cadence anchored to UTC killzones; local times documented.

_Strategy version of record: **`specs/v3.5.yaml`** (RESEARCH_CANDIDATE), sourced from
`docs/strategy/SMC-LSS-v3.5-SIGNAL-RULESET.md`. `specs/v1.yaml` is retained as the
legacy reference engine. Change the spec only via the `backtest-researcher` →
`validation` path, never ad hoc._
