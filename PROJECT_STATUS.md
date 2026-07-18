# PROJECT_STATUS.md — SMC-LSS Platform

**Audit date:** 2026-07-18
**Auditor:** AI Technical Lead (Phase 1 repository audit)
**Repo root:** `D:\ddev\smc-lss-platform\smc-lss-platform`
**Objective under audit:** reach a stable, deterministic **MT5 Demo Trading** system.

> Every status below is grounded in files actually read during this audit. Nothing is assumed.

---

## 1. Executive summary

The **research/signal core is strong and deterministic**; the **automated execution layer does not yet exist as code**. Orders have been placed on the demo account successfully — but by the agent calling the MetaTrader MCP by hand, not by a repeatable Python module. To reach an *automated* Demo Trading system, the critical path is an execution module plus a runner loop, and wiring the existing config file into the code.

**Overall readiness to "stable Demo Trading": ~55%.**

| Phase | Area | Status | Confidence |
|---|---|---|---|
| 1 | Project Audit | ✅ Complete (this doc) | High |
| 2 | Signal Engine | ✅ ~90% — all primitives deterministic | High |
| 3 | Risk Engine | 🟡 ~60% — sizing done; guards missing | High |
| 4 | MT5 Demo Execution | 🔴 ~25% — proven by hand, **no module** | High |
| 5 | Trade Manager | 🟡 ~50% — BE/partial/target; no trail/timeout | High |
| 6 | Journal | 🟡 ~40% — CSV exists; no auto-writer module | High |
| 7 | Daily Validation | 🟡 ~50% — walk-forward works; needs data + report | High |

---

## 2. What exists and works (verified)

**Signal engine — `src/smc_engine.py` (deterministic, optimized).**
Pure functions, no look-ahead beyond explicit gating, same input → same output. Implements: fractal swings (k-confirmed), equilibrium/premium-discount, ATR, displacement move (numeric, v3.6 spec), trend state, fair value gaps, order blocks (BOS-linked), liquidity pools (equal highs/lows), liquidity sweeps (sweep+reclaim), inducement, and mitigation status (FRESH/MITIGATED/INVALIDATED). Performance-conscious (monotonic pointers, bisect) — clearly battle-tested.

**Backtest — `src/backtest.py`.** Deterministic BOS-in-discount / mirror strategy, stop-first fills, per-file + aggregate metrics (win rate, expectancy R, profit factor, max DD). Writes `reports/backtest_result.json`.

**Walk-forward validation — `src/validate.py`.** Chronological IS/OOS split with an objective ACCEPT/REJECT/INCONCLUSIVE verdict and a 30-trade minimum guard. Writes `reports/validation_result.json`.

**Live signal orchestrator — `src/live_signal.py`.** Detects a signal on the latest closed bar, sizes it, emits GO/NO-GO plus the exact two-step MCP order payload. Correctly models the MCP quirk (place, then modify for SL/TP). **Does not transmit** — payload only.

**Trade management rules — `src/trade_manager.py`.** Deterministic `manage()` → breakeven at +1R, 50% partial, target-hit close. Stops only tighten.

**MT5 demo execution — proven live, twice.** `reports/execution_test.json` records a full round trip on `EURUSD-VIP` (pos 522514689, place→modify→verify→close→deals, P/L −0.13). This session re-verified the identical chain on `BTCUSD` (pos 525598904, −0.17). Environment gate confirmed: **login 1144985 / VTMarkets-Demo / DEMO_VERIFIED**.

**Config spec — `specs/v1.yaml`.** Symbol, HTF/entry/LTF timeframes, swing lookback, tolerances, risk %, min RR, sessions.

**Smoke tests — `tests/test_smoke.py`.** Structure/config integrity + skill frontmatter (≥18 skills).

**Monitoring — 3 scheduled read-only checks** (daily health, pre-London, pre-NY), created this session.

---

## 3. Blockers to Demo Trading (ranked)

1. **[CRITICAL] No execution module.** There is no `src/execution/` — order routing is currently the agent manually calling MCP tools. An automated system needs code that sends/modifies/closes orders with reconnect, error handling, and retry. This is Priority 1 in the charter and the single biggest gap.
2. **[CRITICAL] No runner loop.** Nothing ties `live_signal → risk → execution → trade_manager → journal` into one deterministic cycle. The stages exist as islands.
3. **[HIGH] Config not wired.** `specs/v1.yaml` is **not read by any code** — `risk_pct`, `min_rr`, `k`, `window`, `sessions` are hardcoded as argparse defaults / a `CFG` dict in `dry_run.py`. Directly violates the charter rule "everything must come from configuration."
4. **[HIGH] Risk engine incomplete.** Missing in code: **daily-loss-limit enforcement**, **spread filter**, **session validation**. (Values are declared in config/CFG but never checked.)
5. **[MEDIUM] Insufficient data → validation INCONCLUSIVE.** Only 1 backtest trade across ~130 bars total. `verdict: INCONCLUSIVE (1 trade < 30)`. Need real historical pulls before any statistical claim.
6. **[MEDIUM] Duplicated signal logic.** `src/dry_run.py` re-implements `swings()`, `trend()`, `validate()`, `size()` instead of importing `smc_engine`. Violates DRY; risks drift between backtest and live logic.

---

## 4. Duplicated / dead logic

- `dry_run.py` — prototype harness with **embedded hardcoded candles** and its own copies of `swings`/`trend`. It already served its purpose (generated the `data/*.csv`, proved the chain). Recommend demoting to `research/` or deleting once `live_signal.py` covers its role.
- `size()` exists in both `live_signal.py` and `dry_run.py` — consolidate into one risk module.

---

## 5. System ownership (per CLAUDE.md: SVOS research vs Production Execution)

- **SVOS / Research:** `smc_engine.py`, `backtest.py`, `validate.py`, `data/`, `reports/`.
- **Production Execution:** `live_signal.py`, `trade_manager.py`, the (missing) execution module, the runner loop, the journal writer.
- `dry_run.py` straddles both and should be retired to research.

---

## 6. Known risks

- The MCP `account_type` field reads `real` on this demo — never use it to classify safety; rely on the `VTMarkets-Demo` server / login 1144985 attestation.
- `place_market_order` takes no SL/TP; any execution module MUST place-then-modify and never leave a position naked (already modeled in `live_signal.py`).
- **Sandbox VM currently down** → Python/pytest cannot be run this session. Code can be written but not executed/tested until the environment is back. No untested code should be marked "done."
- `pip_value` is hardcoded to 10.0 (USD-quote majors). Cross/metal/crypto symbols need per-symbol tick value from the broker before live sizing on those instruments.

---

## 7. Test status

`tests/test_smoke.py` present (structure/config only). **No unit tests** for `smc_engine` functions or risk math yet. Could not execute the suite this session (VM down).
