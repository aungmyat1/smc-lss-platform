# Production Readiness — SMC Trading Platform (re-run 2)
Generated: 2026-07-16 | Scores reflect verified reality incl. live demo execution.

## Production Readiness Score
| Category | Score | Basis |
|---|---|---|
| Skills | 85% | 18/18 + 5 orchestrators; 23/23 valid; engine-backed |
| MCP | 65% | MT5 read+write VERIFIED LIVE on demo; infra MCPs absent; plugin MCPs need auth |
| Integration | 82% | full chain proven incl. live order round trip |
| Automation | 60% | trigger-on-match verified; no autonomous loop |
| Reliability | 58% | smoke 3/3; deterministic engine; live order retcodes handled; no fault-injection harness |
| Documentation | 92% | README, INSTALL, 9 reports, journal store |
| Security | 62% | demo used for execution tests; real account still exists on connector; order tools gated |
| Maintainability | 82% | modular engine, tests, clean structure |
| **Overall readiness** | **≈73%** | up from ~66% — execution path now proven |

## Resolved since last run
- **P0 demo execution** — RESOLVED for testing: live place→modify→verify→close→journal on VTMarkets demo 1144985 (round-trip P/L -0.13).
- **Journal store** — wired (data/journal.csv).

## Remaining blockers
| # | Issue | Impact | Fix | Priority | Effort |
|---|---|---|---|---|---|
| 1 | Backtest not conclusive | no proven edge | run load_history.py (bulk) then validate.py --all | **P1** | Med |
| 2 | OB/FVG/liquidity detectors spec-only | validator determinism partial | code detectors in smc_engine.py | **P1** | Med |
| 3 | Connector also holds a REAL account | mislabel risk | keep terminal on demo; label clarity | **P2** | Low |
| 4 | git index.lock (user side) | commits blocked from sandbox | clear lock; commit on host | **P2** | Trivial |
| 5 | Infra MCPs absent | those integrations impossible | install only if needed | **P3** | Varies |

## Honest verdict
The platform now executes a **full live loop on a demo account** and all 18 required
skills exist and validate. It is a **~73% foundation** — the remaining gap to
"production" is a statistically conclusive backtest (bulk data) and coding the
remaining SMC detectors. No results fabricated; the one order was 0.01 lot, closed
immediately, P/L -0.13.
