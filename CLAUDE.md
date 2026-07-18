# CLAUDE.md — SMC-LSS Platform

Institutional Smart Money Concepts (SMC-LSS) trading research + execution platform.
Goal: a disciplined, config-driven MT5 demo trading loop, promoted to live only after
evidence gates pass. Full detail lives in the docs below — this file is the index and
the hard rules; don't duplicate their content here, keep it current instead.

## Source of truth (read in this order)
1. [`docs/CHARTER.md`](docs/CHARTER.md) — operational charter: autonomy policy, risk
   envelope, safety gates, demo→live promotion gates. Governs *when the system may trade*.
2. [`docs/RESEARCH-CHARTER.md`](docs/RESEARCH-CHARTER.md) — research discipline: no
   change to `specs/*.yaml` or detection logic without the six-question
   why/evidence/hypothesis/expected-improvement/success/rollback template, logged to
   `reports/research_log.md` before running the backtest.
3. [`PROJECT_STATUS.md`](PROJECT_STATUS.md) — last audited state, ranked blockers, what's
   verified vs assumed. Re-read before claiming something works.
4. [`ROADMAP.md`](ROADMAP.md) — milestone sequence (M1–M8) and acceptance criteria.
5. [`NEXT_ACTION.md`](NEXT_ACTION.md) — the *one* milestone in flight right now.

## Hard rules
- Never hardcode strategy values (risk %, min RR, k, window, sessions) — everything
  must come from configuration. This is the reason M1 (config loader) exists.
- Stops only tighten. Never widen a stop. Every order carries a stop.
- Never route an order unless the environment is verified DEMO (server name contains
  "Demo" — never trust the MCP `account_type` field). Unverified → blocked, alert only.
- No live auto-trading until the demo→live promotion gates in `docs/CHARTER.md` are
  met. Nothing in this repo should assume live is enabled.
- One milestone at a time (`NEXT_ACTION.md`). Don't start M2 work while M1 is open.
- Nothing is "done" until `python -m pytest -q` passes. Don't mark acceptance criteria
  complete on untested code.
- Strategy/spec changes go through `backtest-researcher` → `validation`, never ad hoc.

## Open item — spec version drift
`docs/CHARTER.md` names `specs/v3.5.yaml` as the version of record and `specs/v1.yaml`
as legacy reference, but `specs/v3.6.yaml` now also exists and `ROADMAP.md`/`NEXT_ACTION.md`
still target `v1.yaml` for the M1 config loader. Resolve which spec file is canonical
before wiring `src/config.py` — don't silently pick one.

## Working conventions
- Skills autoload from `.claude/skills` (see `.claude/settings.json`). Start multi-step
  trade decisions with `smc-trading-master`; it orchestrates the atomic skills in order
  and stops on any hard-gate failure.
- `.claude/settings.json` gates `place_*`/`modify_*`/`close_*`/`cancel_*` MCP calls
  behind `confirmBeforeExecute` — do not try to bypass this.
- `.mcp.json` holds MT5 demo credentials locally; it is gitignored (see below) — never
  commit real values, and use a DEMO account only.
- System ownership split (per `PROJECT_STATUS.md` §5): SVOS/Research is
  `smc_engine.py`, `backtest.py`, `validate.py`, `data/`, `reports/`; Production
  Execution is `live_signal.py`, `trade_manager.py`, the execution module, runner loop,
  journal writer. `dry_run.py` straddles both and is slated to retire to research.
