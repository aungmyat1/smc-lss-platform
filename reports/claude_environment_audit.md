# Claude Environment Audit — SMC Trading Platform (re-run)
Generated: 2026-07-17 | Environment: connected repo `D:\ddev\smc-lss-platform\smc-lss-platform` | Method: on-disk inspection + execution

## Executive summary
Unlike the first pass (no repo connected), this audit ran against a **real, connected,
git-initialized repository**. Findings are evidence-based (files inspected, tests executed).

## Component checklist
| Component | Status | Evidence |
|---|---|---|
| Repository connected | **PASS** | mounted; 22 skills + src + tests on disk |
| `.claude/settings.json` | **PASS** | parses as valid JSON |
| `.claude/skills/` | **PASS** | 22 skill directories on disk |
| `.mcp.json` | **PASS (template)** | valid JSON; MT5 demo creds are placeholders |
| MCP runtime (MetaTrader) | **PASS** | live-verified `get_account_info` |
| VS Code / workspace settings | **NOT PRESENT** | not required; add `.vscode/` only if desired |
| Claude Code configuration | **N/A (Cowork)** | `.claude/` present and valid |
| git history | **PASS** | multiple commits; `.git/index.lock` absent on 2026-07-17 |

## Missing / incorrect / duplicate / deprecated
- Missing: bulk historical data; optional infra MCPs.
- Incorrect: none (configs valid).
- Duplicate: none. Two naming layers by design — 18 atomic + 5 orchestrators.
- Deprecated: none.

## Recommended fixes
1. **P1** Add/load bulk history into `data/` for conclusive backtests.
2. **P1** Harden v3.5 detectors before enabling scheduled demo auto-execution.
3. **P2** Authorize plugin MCPs (GitHub, etc.) only if used.
4. **P3** Optional double-nested path flatten (`...\smc-lss-platform\smc-lss-platform`).

## Verdict
Environment is **valid, connected, and operational** for research/decision workflows.
Execution-on-demo has been smoke-tested once; conclusive backtesting remains open
(see production_readiness.md).
