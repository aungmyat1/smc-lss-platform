# SMC-LSS Platform — Implementation Master Plan  ⚠️ DEPRECATED

> **DEPRECATED 2026-07-18.** Superseded by the root [`MASTER_PLAN.md`](../MASTER_PLAN.md)
> (Master Agent v2.1), which is the authoritative governance document. This file is
> retained for historical milestone detail (M0–M6, exit gates, Telegram/observability
> plans) only. Where this document conflicts with the root `MASTER_PLAN.md`, the root
> file wins. Do not use this as the source of phase priority or sequencing.

_Program-manager view (historical). Objective source: docs/CHARTER.md. Strategy of record:
specs/v3.5.yaml (RESEARCH_CANDIDATE). Last updated: 2026-07-17._

## 1. Objective (what "done" means)
A fully automated SMC-LSS trading system that Claude Cowork runs on schedule: it
analyzes only preset symbols with the locked preset strategy, sizes orders from
configured position/risk limits, auto-executes qualifying trades, manages open
positions, journals every event, and reports scan/trade/status updates to
Telegram. Demo automation comes first; live auto-trading is unlocked only after
v3.5 leaves RESEARCH_CANDIDATE and the demo evidence gate is met.

## 2. Status snapshot
| Area | State |
|---|---|
| Repo / CI | On GitHub (origin/master), 12/12 tests pass |
| Skills | 22 (17 atomic + 5 orchestrators), duplicates merged |
| Strategy | v3.5 ruleset registered; parameterized spec `specs/v3.5.yaml` |
| Engine | Formula layer complete + tested; detection layer first pass |
| Loop | `daily_runner` runs legacy + v3.5 read; scheduled London+NY weekdays |
| Autonomy | PROPOSE-MODE (interlock `engine_implements_spec=false`); live blocked |
| Env safety | Demo-safe gate + attestation (login 1144985 → VTMarkets-Demo) |
| Watchlist | Active: EURUSD, XAUUSD, BTCUSD · Pending: GBPUSD |
| Reporting | Telegram reporting is target-state; integration not yet implemented |

## 3. Gap analysis (propose-mode → objective)
1. **Signal fidelity** — detection layer uses FVG/OB/sweep proxies, not the ruleset's
   tick-level E-trigger / IFVG / gold-zone mechanics. Must be hardened + validated.
2. **Evidence gap** — only low-sample backtest output exists (1 trade, inconclusive);
   no statistically valid v3.5 evidence set yet.
3. **Time normalization** — broker candle timestamps ≠ UTC; killzone/session filter
   must normalize to a canonical timezone before it can be trusted.
4. **Sizing for non-USD** — XAUUSD/BTCUSD need live tick-value sizing, not fallbacks.
5. **Automation controls not yet wired** — one demo order round trip has been
   verified (place → modify SL/TP → close → journal), but scheduled execution,
   preset amount enforcement, reconciliation, and kill-switch operation still need
   implementation.
6. **Telegram reporting missing** — no Telegram bot/channel integration, message
   templates, retry policy, or delivery audit yet.
7. **Observability** — no run history, alerting, or health metrics for the loop.

## 4. Milestones, exit gates, and tasks

### M0 — Foundation ✅ DONE
Repo cleaned, 22 skills, demo-safe env gate, pushed to GitHub.

### M1 — Daily loop wired (propose-mode) ✅ DONE
Charter, v3.5 spec, watchlist, multi-symbol runner, runbook, scheduled runs.

### M1.5 — v3.5 engine ✅ (formula) / 🔄 (detection first pass)
`generate_signal` + fixtures done; `analyze()` detection wired. Detection refinement moves to M2.

### M2 — Backtest & signal validation  ⏳ NEXT  (the unlock gate)
**Objective:** prove the v3.5 engine on history before scheduled demo auto-execution.
- Build `src/backtest_v35.py`: event-driven, closed-candles-only, realistic spread/
  slippage/commission, per-symbol tick value, walk-forward split.
- Load ≥ 12 months H1+M5(+D1) history per active symbol via `load_history.py`.
- Harden detection: normalize broker→UTC time; tighten E-trigger (D1 gap / POI / sweep)
  and M3 IFVG (inversion + ≥50% retrace) to match the ruleset.
- Produce `reports/backtest_v35_<symbol>.json`: trades, expectancy(R), profit factor,
  win%, max DD, avg R:R, exposure.
**Exit gate:** each active symbol shows expectancy ≥ +0.2R and PF ≥ 1.3 out-of-sample,
max DD ≤ 15%, ≥ 30 trades. Then run the `validation` skill (walk-forward/OOS).
On pass → allow `engine_implements_spec: true` only after M2.5 automation controls
also pass.

### M2.5 — Automation controls + Telegram foundation  ⏳
**Objective:** make the fully automated loop controllable by presets before any
scheduled order sending.
- Enforce `config/watchlist.yaml` as the only source for active symbols, strategy
  spec, position amount mode (`risk_pct`, `fixed_lot`, `fixed_notional`), max
  positions, heat, daily loss, and min R:R.
- Add Telegram reporting module + templates for scan summaries, GO/NO-GO/SKIP,
  fills, modifies, closes, rejects, risk stops, and daily summaries.
- Add notification retry/delivery audit that cannot duplicate orders if Telegram
  delivery fails.
- Add order reconciliation state: every placed order must be confirmed by
  positions/deals reads, journaled once, and matched to the originating signal.
- Add kill-switch checks before every send and during position management.
**Exit gate:** config-driven sizing tests pass, Telegram dry-run/delivery audit
passes, notification failure is proven non-blocking for reconciliation and
non-duplicating for order sends, and demo execution remains disabled unless both
M2 and M2.5 are green. Then flip `engine_implements_spec: true` to activate demo
auto-execution.

### M3 — Demo auto-execution + evidence  ⏳
**Objective:** run fully automated trading on demo, accumulate reviewable results.
- Full order path smoke test is complete once on demo; next step is scheduled,
  strategy-gated execution after M2 passes.
- Journal every outcome; weekly review via `journaling` (+ one fix each).
- Trade-management loop per frozen horizon (BE at +1R, partial, DOL/time exits).
- Send Telegram updates for scan summary, GO/NO-GO/SKIP decisions, fills,
  modifications, closes, rejects, risk stops, and daily summaries.
**Exit gate:** ≥ 40 journaled demo trades, rule-adherence ≥ 95%, positive expectancy
sustained, two consecutive clean weekly reviews, Telegram delivery audited.

### M4 — Hardening & expansion  ⏳
- Add observability: run-history report, failure alerts, loop uptime metric.
- Enable pending symbols (GBPUSD) after per-symbol backtest pass.
- CI smoke check (GitHub Actions running pytest on push).
- Optimize only via `backtest-researcher` → `optimization` with multiple-testing controls.
**Exit gate:** stable 4-symbol demo operation, CI green, Telegram/alerting verified.

### M5 — Live auto-trading pilot  ⏳
**Precondition:** v3.5 promoted out of RESEARCH_CANDIDATE by the owner.
- Enable fully automated live trading at reduced preset size (e.g. 0.25% risk or
  configured fixed amount per position).
- Daily reconciliation; kill-switch on daily-loss / drawdown breach.
**Exit gate:** N live auto-trades matching demo behavior, Telegram reports
delivered, no risk-gate violations.

### M6 — Scale & operate  ⏳
- Incrementally raise size/symbols under the same gates.
- Periodic re-validation; documented change process (spec bump only via backtest→validation).

## 5. Workstreams (parallel tracks)
- **Research/Strategy:** engine fidelity, backtest, validation, optimization.
- **Execution/Infra:** MT5 order path, reconciliation, runner, scheduling.
- **Risk/Safety:** sizing, limits, env gate, kill-switch, promotion governance.
- **Data:** history loading, time normalization, per-symbol specs.
- **Ops/Observability:** Telegram reporting, run history, alerting, CI, uptime.

## 5.1 Objective coverage check
| Objective requirement | Current coverage | Required plan path |
|---|---|---|
| Trade only preset symbols | `config/watchlist.yaml` active/pending lists | Enforce in M2.5 runner/executor; enable GBPUSD only after per-symbol gate |
| Use preset strategy | `specs/v3.5.yaml` is strategy of record | M2 hardens detector fidelity and validates v3.5 before interlock flip |
| Use preset position amount/risk | Config now defines risk %, fixed lot, fixed notional modes | M2.5 implements mode enforcement + tests; M5 starts at reduced live preset |
| Fully auto execute | Demo round trip proven once; scheduled loop still propose-mode | M2 + M2.5 unlock scheduled demo auto-exec; M5 unlocks live auto-exec |
| Manage open positions | `trade_manager.py` exists for stop tightening rules | M3 exercises BE/partial/DOL/time exits on demo; M5 requires reconciliation |
| Journal every event | `data/journal.csv` exists | M2.5 adds idempotent signal/order linkage; M3 requires weekly reviews |
| Report to Telegram | Config placeholders only | M2.5 implements reporter/templates/retry audit; M3/M5 require delivery evidence |
| Prevent uncontrolled automation | Interlocks and promotion flags exist | M2/M2.5/M3/M5 gates require validation, kill-switches, and audited evidence |

## 6. Risk register
| Risk | Impact | Mitigation |
|---|---|---|
| Detection ≠ ruleset mechanics | False signals | M2 harden + backtest before auto-exec |
| Overfitting in backtest | Live underperformance | Walk-forward, OOS lock, deflated Sharpe |
| Broker time ≠ UTC | Wrong killzone filtering | Normalize timestamps in M2 (session-filter) |
| Env misclassification | Live order on "demo" belief | Server-name gate + attestation; fail-safe LIVE |
| Crypto/metal mis-sizing | Oversized risk | Live tick-value sizing; config fallback only |
| App-closed at run time | Missed scan | Runs on next launch; document; consider always-on host |
| Over-automation | Unreviewed losses | Interlock + demo-first + preset limits + kill-switch + Telegram alerts |
| Telegram outage | Missed operator visibility | Log delivery failure, retry, and include in ops report; never duplicate orders |

## 7. KPIs
Expectancy (R), profit factor, win%, max drawdown, rule-adherence %, realized R:R,
loop uptime (runs completed / scheduled), signal-to-fill latency, Telegram
delivery success rate.

## 8. Immediate next actions (this week)
1. Build `backtest_v35.py` + normalize broker→UTC time (M2 core).
2. Bulk-load ≥ 12 months history for EURUSD, XAUUSD, BTCUSD.
3. Implement config-driven amount enforcement (`risk_pct`, `fixed_lot`,
   `fixed_notional`) with tests.
4. Add Telegram reporter/templates + dry-run delivery audit.
5. Run backtest; publish per-symbol metrics; decide on the interlock flip only
   after M2 and M2.5 both pass.
6. Keep the daily loop in propose-mode; review its journaled proposals.
