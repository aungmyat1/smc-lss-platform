# ROADMAP.md — Path to Stable MT5 Demo Trading

**Authority:** organized under [`MASTER_PLAN.md`](MASTER_PLAN.md) (v2.1). Phases and
priority come from that document; this file holds the per-phase status and
acceptance criteria. **Current priority: Phase 3 — Risk Engine.**

**Guiding rule:** working system over perfect system. Ship the smallest thing that
makes the end-to-end demo loop run deterministically, then harden.

**Revision note (2026-07-18):** re-sequenced from the previous M0–M8 track into
v2.1's seven phases. Per owner ruling, the demo spine is built on the **locked v1
engine**; the v3.5 promotion track (backtest-perf fix, promotion gate) is **parked**
until the demo success gates pass. The old M0 (fix the 27-min v3.5 backtest) is
therefore no longer the next action — it is deferred with the rest of the v3.5 work.

---

## PHASE 1 — Governance · 🟡 ~80%
Deliverables: `PROJECT_STATUS.md` ✅ · `ROADMAP.md` ✅ · `NEXT_ACTION.md` ✅ ·
`MASTER_PLAN.md` ✅ · `ARCHITECTURE.md` ❌ (missing) · `KNOWN_ISSUES.md` ❌ (missing).
*Remaining:* create `ARCHITECTURE.md` (module/dataflow map) and `KNOWN_ISSUES.md`
(migrate the ranked blockers out of `PROJECT_STATUS.md`).

## PHASE 2 — Signal Engine (LOCKED) · ✅ for demo purposes
`src/smc_engine.py` (v1) is the **locked, authoritative** engine driving
`live_signal.py` / `smc_master.py`. Deterministic, no look-ahead, tested. **Do not
rewrite.** The v3.5 formula layer (`signal_v35.py`, `backtest_v35.py`) and the v3.6
spec remain **parked research** — not on the demo critical path.
*Gate:* demo trading uses v1 only until an explicit, owner-approved promotion.

## PHASE 3 — Risk Engine (HIGHEST PRIORITY) · 🟡 ~60% — CURRENT
Built on the **locked v1 engine**. Per MASTER_PLAN v2.1.1, implement in this order:

- **M1 — Configuration Loader ← NEXT.** `src/config.py`: load config, validate schema,
  reject invalid values, remove hardcoded risk values (risk %, RR, session, window,
  ATR, thresholds). *Acceptance:* configuration controls risk behavior; no strategy
  constant remains hardcoded.
- **M2 — Risk Validator.** Pure functions for max risk/trade, max daily loss, max
  exposure, max open trades, spread filter, session filter, minimum RR, margin
  validation. *Acceptance:* every signal receives APPROVED or REJECTED **with reason**;
  unit tests prove accept/refuse at each boundary.
- **M3 — Position Sizing.** Input: account balance, risk %, stop distance, symbol →
  Output: lot size. Consolidate the duplicated `size()` (`live_signal.py`, `dry_run.py`)
  into one `src/risk.py`. *Acceptance:* deterministic, tested, broker-compatible; no
  duplicate sizing logic remains.
- **M4 — Trade Approval Gate.** Single `approve()` verifying signal valid + risk
  approved + environment DEMO + stop exists + lot valid → ALLOW EXECUTION. This gate
  is the mandatory pre-check before Phase 4. *Acceptance:* deterministic GO/NO-GO with
  machine-readable reason; enforces the Execution Security Gate (no broker call bypasses it).

*Phase exit:* `python -m pytest -q` green across M1–M4.

## PHASE 4 — MT5 Execution (Demo only) · 🔴 ~25%
`src/execution/mt5_client.py`: one canonical order path — `send()` (place-then-modify
SL/TP), `modify()`, `close()`, `positions()` — plus reconnect, retry, structured
logging, error recovery, execution validation. **Demo-gated:** refuses to route
unless the environment is DEMO_VERIFIED (server name contains "Demo"; never trust the
MCP `account_type` field). Idempotent by client intent ID.
*Acceptance:* places → attaches SL/TP → closes a 0.01 test position on demo and
reconciles flat; refuses on any unverified environment.

## PHASE 5 — Trade Manager · 🟡 ~50%
Extend `trade_manager.manage()` (already does breakeven +1R, 50% partial, target
close) with trailing stop, time exit, emergency close, manual override, and position
synchronization. Keep "stops only tighten."
*Acceptance:* unit tests for each new action; monitor loop applies them via Phase 4.

## PHASE 6 — Trade Journal · 🟡 ~40%
`src/journal.py`: auto-append signal, entry, SL, TP, lot, risk, strategy, reason,
broker response, latency, profit, and validation result to `data/journal.csv`
(schema-stable). Pull fills from `get_deals` for reconciliation.
*Acceptance:* a demo round trip produces one complete, correct journal row.

## PHASE 7 — Daily Validation · 🟡 ~50%
`src/daily_report.py` (+ existing scheduled tasks): win rate, profit factor, Sharpe,
drawdown, expectancy, execution stats, risk stats, system health, recommendations.
Telegram remains the delivery channel for these reports (per CHARTER).
*Acceptance:* one automated end-of-day report file per session day.

---

## Cross-cutting requirements (every phase)
Deterministic logic only · config-driven (nothing strategy-related hardcoded) · unit
tests for new logic · update `/docs` and the Phase-1 status files · commit per
milestone · **never route on an unverified (non-demo) environment.**

## Explicitly out of scope (v2.1 non-goals)
Rewriting the signal engine · parameter optimization/tuning · v3.5 promotion work
(parked) · live-account routing · AI overlays. Revisit only after the demo loop is
stable. (Exception on record: continued **skill development** is owner-authorized.)

## ⚠ Operational blocker
Per v2.1 Definition of Done, nothing is "done" until `pytest` passes. The sandbox
**workspace VM is currently down**, so Phase 3 code cannot be validated yet. Restore
the VM before marking any Phase 3 acceptance criteria complete.
