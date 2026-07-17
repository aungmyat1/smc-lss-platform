# Daily-Loop Runbook (scheduled Cowork procedure)

This is the exact procedure Claude Cowork follows on each scheduled run. It is the
"wiring" between the schedule and the deterministic engine. Strategy of record:
`specs/v3.5.yaml` (RESEARCH_CANDIDATE). Do not improvise — follow the steps in order
and stop at the first hard failure.

## Preconditions (fail-safe)
1. **Environment check.** Call `get_account_info`. Resolve the account to an
   environment using `.claude/skills/mt5-trading/references/attested-environments.md`
   (match by login). A login mapped `DEMO_VERIFIED` (server name contains "Demo") is
   demo-safe. **Never** trust the `account_type` field. If the login is not attested
   or the server is not a Demo server → environment is LIVE/UNVERIFIED → **do not place
   any order**; produce analysis + alert only.
2. **Autonomy check.** Read `config/watchlist.yaml`. Orders are placed only if
   `autonomy.demo == auto_on_engine_ready` AND `autonomy.engine_implements_spec == true`
   AND environment is `DEMO_VERIFIED`. Otherwise run in **propose-mode** (analyze, size,
   journal the intent, place nothing). `autonomy.live` is `blocked` while v3.5 is RESEARCH_CANDIDATE.

## Per run
For each symbol in `symbols.active` (add `symbols.pending` only after owner confirmation):

3. **Fetch closed candles** via the MetaTrader MCP and write `data/<name>_<tf>.csv`
   (columns `time,open,high,low,close`, ascending; use `src/load_history.py` format):
   - D1 (context) and H1 (E-trigger) — for bias/structure
   - M5 (confirmation) — the entry timeframe the runner reads
   Use the broker symbol from `mt5:` (e.g. `XAUUSD-VIP`, not `XAUUSD`).
4. **Run the deterministic scan:**
   `python src/daily_runner.py --equity <live_equity> --env demo`
   It writes `reports/daily_signals.json` with a decision per symbol
   (GO / PROPOSE / NO-GO / SKIP), sized order payload, and `auto_execute_enabled`.
5. **Cross-check with skills** for anything the coded engine does not yet cover
   (v3.5 E-trigger / M-model variant, DOL target selection): `strategy-validator`,
   `smc-market-structure`, `smc-liquidity-sweep`, `smc-entry-confirmation`. The trade
   must satisfy BOTH the coded gates and the v3.5 variant logic before it is actionable.
6. **Risk gate.** For each actionable symbol, run the `risk-management` skill (pull live
   per-symbol tick value; do not rely on config fallbacks). REFUSE on any limit breach
   (0.5% demo risk, 3% daily loss, 3 max positions, 4% heat, min R:R 2.0).

## Execute / propose
7. **If `auto_execute_enabled == true` and decision GO (demo only):**
   place via `mt5-trading` two-step flow — `place_market_order` then
   `modify_position` for SL/TP. Every order carries a stop. Confirm the fill by
   reconciling with `get_all_positions` before considering it done.
8. **If propose-mode or LIVE target:** do NOT place. Present the sized intent
   (symbol, side, lots, entry, SL, TP, variant, R:R) for explicit owner approval.
9. **Journal** every outcome — GO, PROPOSE, NO-GO, SKIP, fill, reject — via the
   `journaling` skill (immutable row + running metrics).

## After the run
10. Write a one-paragraph summary to `reports/` and surface it: what fired, what was
    proposed, what was skipped, and the next scheduled run. End reviews with exactly
    one concrete fix (per `journaling`).

## Open positions between runs
Manage per frozen horizon (INTRADAY/OVERNIGHT/INTRAWEEK/MULTI_HORIZON) using
`smc-trade-management` / `trade_manager.py`: move stop to breakeven at +1R, take the
partial, never widen a stop, close at the pre-selected DOL or max-hold-hours.

## Notes
- All decisions use closed candles only (no future bars).
- Auto-execution activates automatically once `engine_implements_spec` flips to `true`
  in both `specs/v3.5.yaml` and `config/watchlist.yaml` (after the v3.5 engine is built + backtested).
- If the broker/data is unavailable for a symbol: skip it, log, alert; do not retry blindly.
