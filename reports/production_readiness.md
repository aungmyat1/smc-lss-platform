# Production Readiness — SMC Trading Platform (Cowork)
Generated: 2026-07-16 | Scores reflect verified reality, NOT aspirational targets.

## Production Readiness Score
| Category | Score | Basis |
|---|---|---|
| Skills | 55% | 5 installed & active; 3/18 spec skills standalone, ~55% functional coverage |
| MCP | 55% | MT5 live & verified; infra MCPs absent; plugin MCPs need auth |
| Integration | 55% | Read/decision path works; backtest & execution paths incomplete |
| Automation | 50% | Trigger-on-match works; no scheduled/autonomous loop |
| Reliability | 38% | No retry/timeout/recovery testing possible; single live account |
| Documentation | 78% | Skills + README + this report set |
| Security | 35% | REAL account exposed to order tools; no demo isolation |
| Maintainability | 72% | Clean skill structure, valid frontmatter |
| **Overall readiness** | **≈54%** | **NOT production-ready** |

## Critical blockers (STOP — remediate before "production")
| # | Issue | Root cause | Impact | Fix | Priority | Effort |
|---|---|---|---|---|---|---|
| 1 | No demo isolation — REAL account reachable by order tools | Bridge points at live account | A bad/test order risks real capital | Create MT5 **demo** account; bind MCP to it for all testing | **P0** | Low (30 min) |
| 2 | Repo-level phases can't run | No repository connected | Env/config/CI audit impossible | If a codebase exists, connect the folder; else scope = Cowork | **P0** | Low |
| 3 | backtest-researcher non-operational | No historical data source/engine | No expectancy proof → not quant | Wire MT5 history export / CSV / data API + Python engine | **P1** | Med (1–2 days) |
| 4 | Skills store not writable from session | Cowork security model | Cannot auto-install missing skills | Author `.skill` files; install via Settings → Customize | **P1** | Low per skill |
| 5 | 13–15 of 18 spec skills not standalone | Consolidated design | Not "institutional-granular" | Decide consolidated vs granular; author the rest if granular | **P2** | Med |
| 6 | risk-manager pip value hardcoded | $10/lot assumption | Wrong sizing on XAU/JPY/crosses | Pull per-symbol tick_value before sizing | **P2** | Low |
| 7 | Infra MCPs (Docker/Redis/Postgres/WS) absent | Not installed | Those integrations impossible | Install only if architecture truly needs them | **P3** | Varies |

## Prioritized remediation plan
- **Now (P0):** demo MT5 account + confirm target environment (repo vs Cowork).
- **This week (P1):** historical data feed for backtesting; install any missing skills as `.skill` files; wire a journal store (xlsx in outputs).
- **Next (P2):** symbol-generic sizing; decide/author granular skills; add deterministic SMC detectors.
- **Later (P3):** infra MCPs, reliability/retry harness, autonomous scheduled validation.

## Honest verdict
Per the source spec's success criteria, the task is **NOT complete**: required
skills are only partially present, the execution path is unproven (no demo), and
backtesting is non-operational. This is a **solid ~54% foundation** — a live MT5
read/decision pipeline with active governance skills — not a production system.
No results were fabricated; blocked items are marked NOT IMPLEMENTED with reasons.
