# CLAUDE.md — SMC-LSS Platform

Institutional Smart Money Concepts (SMC-LSS) trading research + execution platform.
Goal: a disciplined, config-driven MT5 demo trading loop, promoted to live only after
evidence gates pass. Full detail lives in the docs below — this file is the index and
the hard rules; don't duplicate their content here, keep it current instead.

## Document authority (v3.0.0 — higher wins; read in this order too)
This file (`CLAUDE.md`) is read **first** as the entry index, but `MASTER_PLAN.md` is
the **highest authority**. Full order:
1. [`MASTER_PLAN.md`](MASTER_PLAN.md) — **AUTHORITATIVE (v3.0.0, supersedes v2.1.x).**
   Scope, phase priority, sequencing, non-negotiable rules, Definition of Done,
   success gates. When any document conflicts with it, this file wins.
2. [`CLAUDE.md`](CLAUDE.md) — this file: entry index + the hard rules below.
3. [`docs/CHARTER.md`](docs/CHARTER.md) — trade-safety authority (subordinate to
   MASTER_PLAN): autonomy policy, risk envelope, demo→live promotion gates.
4. [`docs/RESEARCH-CHARTER.md`](docs/RESEARCH-CHARTER.md) — research discipline: no
   change to `specs/*.yaml` or detection logic without the six-question
   why/evidence/hypothesis/expected-improvement/success/rollback template, logged to
   `reports/research_log.md` before running the backtest.
5. [`PROJECT_STATUS.md`](PROJECT_STATUS.md) — last audited state, ranked blockers.
6. [`ROADMAP.md`](ROADMAP.md) — milestone sequence under MASTER_PLAN's **M1–M5**
   (M1 Strategy Contract Normalization — complete; M2 Strategy Approval & Validation
   — current, ST-C1 v3.9/v3.10 research sits here; M3 Execution Layer Skeleton;
   M4 Demo Trading Integration; M5 Live Promotion Gate).
7. [`NEXT_ACTION.md`](NEXT_ACTION.md) — the *one* milestone in flight right now.
8. Source code.

On conflict: stop, identify it, follow the higher-authority document. Never silently
override governance.

> `docs/MASTER-PLAN.md` is **DEPRECATED** — superseded by the root `MASTER_PLAN.md`.

## Owner directives (Updated 2026-07-22 — replaces 2026-07-18 text)
- **Roadmap alignment:** the prior "Risk Engine = Phase 3" directive (2026-07-18,
  drawn from `MASTER_PLAN.md` v2.1/v2.1.1) is **obsolete and removed** — `MASTER_PLAN.md`
  v3.0.0 (2026-07-19) superseded that text the next day and defines no such phase.
  Current roadmap, per `MASTER_PLAN.md` v3.0.0's Implementation Roadmap: **M1 Strategy
  Contract Normalization (complete) → M2 Strategy Approval & Validation (current — all
  ST-C1 v3.9/v3.10 research belongs here; no detection-logic change without an RCR
  through `docs/RESEARCH-CHARTER.md`) → M3 Execution Layer Skeleton (not yet
  authorized — no kernel/scenario-binding modules, audit logging, or execution-layer
  code until sequenced by `project-governance-agent`) → M4 Demo Trading Integration →
  M5 Live Promotion Gate.** The v3.5 promotion track remains **parked** until demo
  success gates pass — never wire v3.5 into live execution.
- **Skills/agents:** existing skills and agents may continue, but **orchestration
  only** — they MUST NOT replace Python modules, duplicate strategy logic, bypass
  validation, or create alternative signal engines. New skills or agent files require
  justification and, where they claim governance/enforcement authority, an Accepted
  ADR. (This refines the earlier owner authorization to continue skills.)
- Note: `MASTER_PLAN.md`'s own "CURRENT PRIORITY" line is itself stale relative to
  `ROADMAP.md`'s tracked Phase 1 ✅ / Phase 2 🟡 state — that requires an owner-approved
  `MASTER_PLAN.md` version bump, not a fix here.

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
