# SMC-LSS Platform — Implementation Master Plan

_Program-manager view. Objective source: docs/CHARTER.md. Strategy of record:
specs/v3.5.yaml (RESEARCH_CANDIDATE). Last updated: 2026-07-17._

## 1. Objective (what "done" means)
A semi-autonomous SMC-LSS system that Claude Cowork runs on schedule: it analyzes a
preset watchlist with the locked v3.5 rulebook, **auto-executes on a verified demo
account**, and **prepares confirmation-gated intents for live** — with fixed risk,
full journaling, and a published demo→live promotion gate. Live is unlocked only
after v3.5 leaves RESEARCH_CANDIDATE and the demo evidence gate is met.

## 2. Status snapshot
| Area | State |
|---|---|
| Repo / CI | On GitHub (origin/master), 12/12 tests pass, clean tree |
| Skills | 22 (17 atomic + 5 orchestrators), duplicates merged |
| Strategy | v3.5 ruleset registered; parameterized spec `specs/v3.5.yaml` |
| Engine | Formula layer complete + tested; detection layer first pass |
| Loop | `daily_runner` runs legacy + v3.5 read; scheduled London+NY weekdays |
| Autonomy | PROPOSE-MODE (interlock `engine_implements_spec=false`); live blocked |
| Env safety | Demo-safe gate + attestation (login 1144985 → VTMarkets-Demo) |
| Watchlist | Active: EURUSD, XAUUSD, BTCUSD · Pending: GBPUSD |

## 3. Gap analysis (propose-mode → objective)
1. **Signal fidelity** — detection layer uses FVG/OB/sweep proxies, not the ruleset's
   tick-level E-trigger / IFVG / gold-zone mechanics. Must be hardened + validated.
2. **No evidence** — zero backtest metrics and zero journaled demo trades under v3.5.
3. **Time normalization** — broker candle timestamps ≠ UTC; killzone/session filter
   must normalize to a canonical timezone before it can be trusted.
4. **Sizing for non-USD** — XAUUSD/BTCUSD need live tick-value sizing, not fallbacks.
5. **No auto-execution path exercised** — demo order placement + reconciliation loop
   is specified in the runbook but not yet run end-to-end.
6. **Observability** — no run history, alerting, or health metrics for the loop.

## 4. Milestones, exit gates, and tasks

### M0 — Foundation ✅ DONE
Repo cleaned, 22 skills, demo-safe env gate, pushed to GitHub.

### M1 — Daily loop wired (propose-mode) ✅ DONE
Charter, v3.5 spec, watchlist, multi-symbol runner, runbook, scheduled runs.

### M1.5 — v3.5 engine ✅ (formula) / 🔄 (detection first pass)
`generate_signal` + fixtures done; `analyze()` detection wired. Detection refinement moves to M2.

### M2 — Backtest & signal validation  ⏳ NEXT  (the unlock gate)
**Objective:** prove the v3.5 engine on history before any auto-execution.
- Build `src/backtest_v35.py`: event-driven, closed-candles-only, realistic spread/
  slippage/commission, per-symbol tick value, walk-forward split.
- Load ≥ 12 months H1+M5(+D1) history per active symbol via `load_history.py`.
- Harden detection: normalize broker→UTC time; tighten E-trigger (D1 gap / POI / sweep)
  and M3 IFVG (inversion + ≥50% retrace) to match the ruleset.
- Produce `reports/backtest_v35_<symbol>.json`: trades, expectancy(R), profit factor,
  win%, max DD, avg R:R, exposure.
**Exit gate:** each active symbol shows expectancy ≥ +0.2R and PF ≥ 1.3 out-of-sample,
max DD ≤ 15%, ≥ 30 trades. Then run the `validation` skill (walk-forward/OOS).
On pass → flip `engine_implements_spec: true` → demo auto-execution activates.

### M3 — Demo auto-execution + evidence  ⏳
**Objective:** run live on demo, accumulate reviewable results.
- Exercise the full order path once (place_market_order → modify SL/TP → reconcile).
- Journal every outcome; weekly review via `journaling` (+ one fix each).
- Trade-management loop per frozen horizon (BE at +1R, partial, DOL/time exits).
**Exit gate:** ≥ 40 journaled demo trades, rule-adherence ≥ 95%, positive expectancy
sustained, two consecutive clean weekly reviews.

### M4 — Hardening & expansion  ⏳
- Add observability: run-history report, failure alerts, loop uptime metric.
- Enable pending symbols (GBPUSD) after per-symbol backtest pass.
- CI smoke check (GitHub Actions running pytest on push).
- Optimize only via `backtest-researcher` → `optimization` with multiple-testing controls.
**Exit gate:** stable 4-symbol demo operation, CI green, alerting verified.

### M5 — Live pilot (confirm-required)  ⏳
**Precondition:** v3.5 promoted out of RESEARCH_CANDIDATE by the owner.
- Enable live at reduced size (e.g. 0.25%), confirm-required on every order.
- Daily reconciliation; kill-switch on daily-loss / drawdown breach.
**Exit gate:** N live-confirmed trades matching demo behavior, no risk-gate violations.

### M6 — Scale & operate  ⏳
- Incrementally raise size/symbols under the same gates.
- Periodic re-validation; documented change process (spec bump only via backtest→validation).

## 5. Workstreams (parallel tracks)
- **Research/Strategy:** engine fidelity, backtest, validation, optimization.
- **Execution/Infra:** MT5 order path, reconciliation, runner, scheduling.
- **Risk/Safety:** sizing, limits, env gate, kill-switch, promotion governance.
- **Data:** history loading, time normalization, per-symbol specs.
- **Ops/Observability:** run history, alerting, CI, uptime.

## 6. Risk register
| Risk | Impact | Mitigation |
|---|---|---|
| Detection ≠ ruleset mechanics | False signals | M2 harden + backtest before auto-exec |
| Overfitting in backtest | Live underperformance | Walk-forward, OOS lock, deflated Sharpe |
| Broker time ≠ UTC | Wrong killzone filtering | Normalize timestamps in M2 (session-filter) |
| Env misclassification | Live order on "demo" belief | Server-name gate + attestation; fail-safe LIVE |
| Crypto/metal mis-sizing | Oversized risk | Live tick-value sizing; config fallback only |
| App-closed at run time | Missed scan | Runs on next launch; document; consider always-on host |
| Over-automation | Unreviewed losses | Interlock + demo-first + confirm-required live |

## 7. KPIs
Expectancy (R), profit factor, win%, max drawdown, rule-adherence %, realized R:R,
loop uptime (runs completed / scheduled), signal-to-fill latency.

## 8. Immediate next actions (this week)
1. Build `backtest_v35.py` + normalize broker→UTC time (M2 core).
2. Bulk-load ≥ 12 months history for EURUSD, XAUUSD, BTCUSD.
3. Run backtest; publish per-symbol metrics; decide on the interlock flip.
4. Keep the daily loop in propose-mode; review its journaled proposals.
