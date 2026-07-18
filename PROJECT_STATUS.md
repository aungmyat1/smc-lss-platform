# PROJECT_STATUS.md — SMC-LSS Platform

**Audit date:** 2026-07-18 (re-audit — supersedes the same-day 14:42 audit, which
had gone stale within hours: 4 more commits landed after it, building an entire
v3.5 signal/backtest track it never mentions)
**Auditor:** AI Technical Lead (Phase 1 repository re-audit)
**Repo root:** `D:\ddev\smc-lss-platform\smc-lss-platform`
**Objective under audit:** reach a stable, deterministic **MT5 Demo Trading** system.

> Every status below is grounded in files actually read, tests actually run, and
> `git log`/`git status` actually checked during this audit. Nothing is assumed.

---

## 1. Executive summary

There are **two live signal-engine tracks** in this repo right now, and the previous
audit only knew about one of them:

- **v1 (`smc_engine.py`)** — the original deterministic primitives library. Still
  what `live_signal.py` and `smc_master.py` actually use to produce the order
  payload today.
- **v3.5 (`signal_v35.py` + `backtest_v35.py`)** — `docs/CHARTER.md`'s declared
  **version of record**, built out today across 4 commits (formula layer, tests,
  backtest harness, daily-runner integration). Status: **`RESEARCH_CANDIDATE`**,
  not yet wired into the live decision path. `daily_runner.py` already calls it in
  parallel, propose-only, gated by `config/watchlist.yaml`'s
  `autonomy.engine_implements_spec` interlock — so there is no execution-safety
  gap today, only a documentation one.
- **v3.6 (`specs/v3.6.yaml`)** — a further research spec (IFVG detection),
  `engine_implements_spec: false`, no code consumes it yet. Research-only.

**Overall readiness to "stable Demo Trading": ~50%** (revised down slightly from the
prior 55% — the automation spine (execution module, runner loop, risk guards,
journal writer) is unchanged and still missing; what changed is *where* signal
research effort went, not how close the demo-trading spine is).

| Phase | Area | Status | Confidence |
|---|---|---|---|
| 1 | Project Audit | ✅ Complete (this doc) | High |
| 2 | Signal Engine | 🟡 v1 ~90% deterministic, but not version-of-record; v3.5 formula layer done + backtested (single/mixed-symbol evidence), not yet promoted; v3.6 research-only | High |
| 3 | Risk Engine | 🟡 ~60% — sizing done; daily-loss-limit/spread-filter/session-validation guards still missing | High |
| 4 | MT5 Demo Execution | 🔴 ~25% — proven by hand, **no module** | High |
| 5 | Trade Manager | 🟡 ~50% — BE/partial/target; no trail/timeout/emergency | High |
| 6 | Journal | 🟡 ~40% — CSV exists; no auto-writer module | High |
| 7 | Daily Validation | 🟡 ~50% — walk-forward works; needs multi-symbol data + report | High |

---

## 2. What exists and works (verified this session)

**v1 signal engine — `src/smc_engine.py`.** Unchanged since prior audit: pure,
deterministic, no look-ahead. Still what `live_signal.py`/`smc_master.py` run on.

**v3.5 signal engine — `src/signal_v35.py` (formula layer) + `src/backtest_v35.py`
(harness).** Implements the nine-variant E×M model per
`docs/strategy/SMC-LSS-v3.5-SIGNAL-RULESET.md`. 28 unit tests pass (invariants,
determinism, RR gate, structure detection). Backtest evidence so far is **mixed
across symbols**, not yet a clean pass:
  - XAUUSD-VIP: 44 trades, 70.5% win rate, expectancy **+0.135R**, PF 1.59 (`reports/backtest_v35_XAUUSD-VIP.json`, generated 2026-07-18T12:39Z).
  - BTCUSD (per uncommitted `run_baseline.py` re-run): 231 trades, 10.0% win rate, expectancy **−0.182R**.
  - `specs/v3.5.yaml`'s own `implementation_status.engine_implements_spec` still
    reads `false` — i.e. the spec's own safety interlock has **not** been flipped
    despite this backtest evidence existing, which is the correct conservative
    default given the mixed cross-symbol result.

**`daily_runner.py` (new).** Multi-symbol scan over `config/watchlist.yaml`. Runs
v1 (`smc_master`) as the actual decision path and v3.5 (`signal_v35.analyze`) in
parallel for comparison. Everything is forced to `mode=propose` while
`engine_implements_spec` is false — **no execution risk**, this is read-only
research output (`reports/daily_signals.json`).

**Backtest — `src/backtest.py` (v1) and `src/backtest_v35.py` (v3.5).** Both
deterministic, stop-first fills, per-file + aggregate metrics.

**Walk-forward validation — `src/validate.py`.** Unchanged; still gated at 30-trade
minimum, still `INCONCLUSIVE` on thin data for the v1 track. Not yet run against v3.5.

**Live signal orchestrator — `src/live_signal.py`.** Unchanged: v1-based, GO/NO-GO +
two-step MCP order payload, **does not transmit**.

**Trade management rules — `src/trade_manager.py`.** Unchanged: `manage()` →
breakeven at +1R, 50% partial, target-hit close. Stops only tighten.

**MT5 demo execution — proven live, twice** (unchanged from prior audit).
Environment gate confirmed: **login 1144985 / VTMarkets-Demo / DEMO_VERIFIED**.

**Config specs.** `specs/v1.yaml` (legacy, 214 bytes, minimal), `specs/v3.5.yaml`
(version of record per CHARTER.md, 3954 bytes), `specs/v3.6.yaml` (research-only IFVG
spec, 6010 bytes, unimplemented). None of the three is read by `src/config.py` —
**that module does not exist.**

**Test suite — `tests/` (36 tests, ran this session, all pass, `python -m pytest -v
--durations=10`):**
```
36 passed, 2 warnings in 1670.90s (0:27:50)
```
**One test dominates the runtime: `test_run_backtest_report_shape_on_real_csv`
took 1654.88s (~27.5 minutes) by itself.** See blocker #1 below — this is new
since the last audit (the prior audit couldn't run pytest at all; the sandbox VM
was down). It is a real, previously-unmeasured performance problem, not a flake.

---

## 3. Blockers to Demo Trading (ranked)

1. **[CRITICAL — NEW] `backtest_v35.py` is catastrophically slow on real data.**
   `test_run_backtest_report_shape_on_real_csv` took 27m50s for one backtest run.
   The loop is already bounded to O(n) by design (500-bar M5 lookback window per
   step, documented in `run_backtest()`'s docstring as a deliberate fix for an
   earlier O(n²) bug) — so the remaining cost is the per-step constant: calling
   `v35.analyze()` over a full 500-bar window on every single bar of a
   multi-month/year XAUUSD M5 series. At this speed, `backtest-researcher`
   iteration, walk-forward validation, and any daily/multi-symbol evidence
   gathering for the v3.5 promotion decision are impractical. This blocks
   everything downstream in the v3.5 track, independent of which spec wins.
2. **[CRITICAL] No execution module.** Still no `src/execution/` — order routing
   is still the agent manually calling MCP tools. Unchanged from prior audit.
3. **[CRITICAL] No runner loop that executes.** `daily_runner.py` now exists and
   ties `signal → risk → journal(partial)` together, but stops at propose-mode by
   design — nothing closes the loop to execution yet.
4. **[HIGH] Config not wired, and now ambiguous which spec it should wire.**
   `src/config.py` does not exist. Given v3.5 is version-of-record but v1 still
   drives the live decision path, a config loader needs to serve both during the
   transition, or the transition needs to happen first. See ROADMAP.md M1.
5. **[HIGH] Risk engine incomplete.** Missing in code: daily-loss-limit
   enforcement, spread filter, session validation. Unchanged from prior audit.
6. **[MEDIUM] `docs/RESEARCH-CHARTER.md`'s process was not followed for today's
   v3.5 work.** The charter requires a six-question research-log entry in
   `reports/research_log.md` *before* running a backtest on a rule/spec change.
   That file does not exist. Today's v3.5 backtests (XAUUSD-VIP, EURUSD, BTCUSD)
   have no logged hypothesis/evidence/rollback trail.
7. **[MEDIUM] Insufficient/mixed data → v3.5 not promotable yet.** One
   promising symbol (XAUUSD-VIP, PF 1.59) and one clearly negative symbol
   (BTCUSD, −0.182R expectancy) is not a basis to flip `engine_implements_spec`.
   Needs the research-log process (#6) and more symbols/OOS split before a
   promotion decision.
8. **[LOW] Uncommitted change in `src/run_baseline.py`.** Fixes BTCUSD's
   `broker_offset` (0 → 3, to match how `load_history.py` actually pulls candles —
   comment explains crypto gets no special-case) and removes a `⚠` character that
   would raise `UnicodeEncodeError` on a Windows `cp1252` console. Looks correct;
   not yet committed — left for you to review/commit rather than silently staged.
9. **[MEDIUM] Duplicated signal logic (unchanged).** `dry_run.py` still
   re-implements `swings()`/`trend()`/`validate()`/`size()` instead of importing
   `smc_engine`.

---

## 4. Duplicated / dead logic

- `dry_run.py` — unchanged assessment: prototype harness, recommend demoting to
  `research/` or deleting once `live_signal.py`'s role is fully covered elsewhere.
- `size()` exists in both `live_signal.py` and `dry_run.py` — consolidate into one
  risk module (`src/risk.py`, per ROADMAP M4).

---

## 5. System ownership (per CLAUDE.md: SVOS research vs Production Execution)

- **SVOS / Research:** `smc_engine.py`, `backtest.py`, `signal_v35.py`,
  `backtest_v35.py`, `features.py`, `feature_analytics.py`, `data/`, `reports/`.
- **Production Execution:** `live_signal.py`, `smc_master.py`, `trade_manager.py`,
  `daily_runner.py` (propose-only today), the (missing) execution module, the
  (missing) runner-loop execution leg, the (missing) journal writer.
- `dry_run.py` straddles both and should be retired to research.

---

## 6. Known risks

- The MCP `account_type` field reads `real` on this demo — never use it to
  classify safety; rely on the `VTMarkets-Demo` server / login 1144985 attestation.
- `place_market_order` takes no SL/TP; any execution module MUST place-then-modify
  and never leave a position naked (already modeled in `live_signal.py`).
- `pip_value` is hardcoded to 10.0 (USD-quote majors). Cross/metal/crypto symbols
  need per-symbol tick value from the broker before live sizing on those instruments.
- **New:** two signal engines producing potentially divergent decisions
  (`daily_runner.py` already surfaces both v1 and v3.5 reads per symbol) — keep
  this parallel/propose-only until the promotion decision in blocker #7 is made
  deliberately, not by drift.

---

## 7. Test status

`python -m pytest -v --durations=10` — **36/36 passed**, 1670.90s total wall time,
dominated by the 27m50s single test in blocker #1. All other tests are fast
(next slowest: 13.93s). No failures. No unit tests yet for the still-missing risk
guards (daily-loss-limit, spread filter, session validation) since that code
doesn't exist yet.
