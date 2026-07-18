# ROADMAP.md — Path to Stable MT5 Demo Trading

**Guiding rule:** working system over perfect system. Ship the smallest thing that makes the end-to-end demo loop run deterministically, then harden.

**Definition of done (charter success criteria):** the system can generate deterministic SMC signals, validate every signal, size the position, execute on MT5 demo, monitor, close, journal every trade, and produce a daily report.

---

## Milestone sequence

### M1 — Config loader (unblocks everything) · SMALL
Wire `specs/v1.yaml` into a single `src/config.py` loader. Replace hardcoded `risk_pct`, `min_rr`, `k`, `window`, `sessions` in `live_signal.py` / `backtest.py` / `validate.py` with config reads. **No strategy value hardcoded anywhere.**
*Acceptance:* changing `v1.yaml` changes behavior in all three entrypoints; smoke test loads config.

### M2 — Execution module (Priority 1) · MEDIUM
`src/execution/mt5_client.py`: a thin, deterministic wrapper over the MetaTrader MCP with one canonical order path — `send()` (place-then-modify SL/TP), `modify()`, `close()`, `positions()`, plus reconnect, error-handling, and bounded retry. Idempotent by client intent ID. **Demo-gated:** refuses to route unless environment is DEMO_VERIFIED (login 1144985 / server contains "Demo").
*Acceptance:* module places → attaches SL/TP → closes a 0.01 test position on demo and reconciles flat; refuses on unverified environment.

### M3 — Runner loop (ties the pipeline together) · MEDIUM
`src/run_demo.py`: on each closed bar → `live_signal` → risk gate → (if GO) `execution.send` → register with `trade_manager` → journal. One deterministic cycle, config-driven, demo-only.
*Acceptance:* a dry `--paper` mode prints the full decision trail; a `--demo` mode routes through M2 on a verified account.

### M4 — Complete the risk engine · SMALL–MEDIUM
Add the three missing guards as pure functions: **daily-loss-limit** (3% start-of-day equity, refuse after breach), **spread filter** (reject if live spread > cap per symbol), **session validation** (only trade configured sessions, DST-safe). Consolidate the duplicated `size()` into `src/risk.py`.
*Acceptance:* unit tests prove each guard refuses/accepts at the boundary.

### M5 — Trade manager completion · SMALL
Add trailing stop, timeout exit, emergency close to `trade_manager.manage()`. Keep "stops only tighten."
*Acceptance:* unit tests for each new action; monitor loop applies them via M2.

### M6 — Journal writer · SMALL
`src/journal.py`: auto-append signal, entry, SL, TP, risk, result, P/L, exit reason to `data/journal.csv` (schema-stable). Pull fills from `get_deals` for reconciliation.
*Acceptance:* a demo round trip produces one complete, correct journal row.

### M7 — Data + real validation · MEDIUM
Pull real historical candles (via MCP `get_candles_latest`) to reach ≥30 trades, then re-run `validate.py`. Report is currently INCONCLUSIVE on 1 trade — this is a gate, not a formality.
*Acceptance:* validation returns ACCEPT/REJECT on a real sample (not INCONCLUSIVE).

### M8 — Daily validation report · SMALL
Extend the existing scheduled tasks / add `src/daily_report.py`: win rate, profit factor, drawdown, journal summary, errors, recommendations.
*Acceptance:* one automated end-of-day report file per session day.

---

## Sequencing rationale
M1 first because every later module should read config, not constants. M2+M3 are the Priority-1 automation spine. M4–M6 harden safety and record-keeping around that spine. M7 is the statistical gate before trusting signals. M8 closes the daily loop.

## Explicitly out of scope for now (charter: avoid gold plating)
Optimization, portfolio management, multi-symbol scaling, production/live-account routing, advanced AI overlays. Revisit only after the demo loop is stable.

## Cross-cutting requirements (apply to every milestone)
Deterministic logic only · config-driven · unit tests for new logic · update `/docs` · commit per milestone · never route on an unverified (non-demo) environment.
