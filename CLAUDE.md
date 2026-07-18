# CLAUDE.md — SMC-LSS Platform

Institutional Smart Money Concepts (SMC-LSS) trading research + execution platform.
Goal: a disciplined, config-driven MT5 demo trading loop, promoted to live only after
evidence gates pass. Full detail lives in the docs below — this file is the index and
the hard rules; don't duplicate their content here, keep it current instead.

## Document authority (v2.1.1 — higher wins; read in this order too)
This file (`CLAUDE.md`) is read **first** as the entry index, but `MASTER_PLAN.md` is
the **highest authority**. Full order:
1. [`MASTER_PLAN.md`](MASTER_PLAN.md) — **AUTHORITATIVE (v2.1.1).** Scope, phase
   priority, sequencing, non-negotiable rules, Definition of Done, success gates.
   When any document conflicts with it, this file wins.
2. [`CLAUDE.md`](CLAUDE.md) — this file: entry index + the hard rules below.
3. [`docs/CHARTER.md`](docs/CHARTER.md) — trade-safety authority (subordinate to
   MASTER_PLAN): autonomy policy, risk envelope, demo→live promotion gates.
4. [`docs/RESEARCH-CHARTER.md`](docs/RESEARCH-CHARTER.md) — research discipline: no
   change to `specs/*.yaml` or detection logic without the six-question
   why/evidence/hypothesis/expected-improvement/success/rollback template, logged to
   `reports/research_log.md` before running the backtest.
5. [`PROJECT_STATUS.md`](PROJECT_STATUS.md) — last audited state, ranked blockers.
6. [`ROADMAP.md`](ROADMAP.md) — milestone sequence under MASTER_PLAN's **Phases 1–7**
   (Risk Engine = Phase 3 = current priority; sub-milestones M1–M4).
7. [`NEXT_ACTION.md`](NEXT_ACTION.md) — the *one* milestone in flight right now.
8. Source code.

On conflict: stop, identify it, follow the higher-authority document. Never silently
override governance.

> `docs/MASTER-PLAN.md` is **DEPRECATED** — superseded by the root `MASTER_PLAN.md`.

## Owner directives (2026-07-18, override log)
- **Priority:** Risk Engine (Phase 3) is the highest priority, built on the **locked
  v1 engine** (`specs/v1.yaml`). Phase 3 sub-order: **M1 config loader → M2 risk
  validator → M3 position sizing → M4 approval gate.** The v3.5 promotion track is
  **parked** until demo success gates pass — never wire v3.5 into live execution.
- **Skills (v2.1.1):** existing skills may continue, but **orchestration only** — they
  MUST NOT replace Python modules, duplicate strategy logic, bypass validation, or
  create alternative signal engines. New skills require justification. (This refines
  the earlier owner authorization to continue skills.)

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

## Spec version status (resolved 2026-07-18 re-audit)
`specs/v3.5.yaml` is the version of record (per `docs/CHARTER.md`), backed by a
working formula layer + backtest harness (`signal_v35.py`, `backtest_v35.py`,
28 passing tests) but still `RESEARCH_CANDIDATE` — `engine_implements_spec` stays
`false` until the promotion gate in `ROADMAP.md` M1.5 is cleared with logged
evidence, not decided ad hoc. `specs/v1.yaml` is legacy — it's what
`live_signal.py`/`smc_master.py` actually execute today, and stays canonical for
that live path until v3.5 is promoted and those modules are rewired. `specs/v3.6.yaml`
is research-only (IFVG spec), unimplemented, not on the roadmap yet. `ROADMAP.md`
and `NEXT_ACTION.md` were rewritten this audit to target v3.5 going forward — see
`PROJECT_STATUS.md` §1 for the full picture of what changed and why.

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
