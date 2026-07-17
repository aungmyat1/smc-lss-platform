# Claude Environment Audit — SMC Trading Platform (re-run)
Generated: 2026-07-16 | Environment: connected repo `D:\ddev\smc-lss-platform\smc-lss-platform` | Method: on-disk inspection + execution

## Executive summary
Unlike the first pass (no repo connected), this audit ran against a **real, connected,
git-initialized repository**. Findings are evidence-based (files inspected, tests executed).

## Component checklist
| Component | Status | Evidence |
|---|---|---|
| Repository connected | **PASS** | mounted; 23 skills + src + tests on disk |
| `.claude/settings.json` | **PASS** | parses as valid JSON |
| `.claude/skills/` | **PASS** | 23 SKILL.md, all valid frontmatter |
| `.mcp.json` | **PASS (template)** | valid JSON; MT5 demo creds are placeholders |
| MCP runtime (MetaTrader) | **PASS** | live-verified `get_account_info` |
| VS Code / workspace settings | **NOT PRESENT** | not required; add `.vscode/` only if desired |
| Claude Code configuration | **N/A (Cowork)** | `.claude/` present and valid |
| git history | **PASS** | multiple commits; note: user-side index.lock seen |

## Missing / incorrect / duplicate / deprecated
- Missing: DEMO account binding; bulk historical data; optional infra MCPs.
- Incorrect: none (configs valid).
- Duplicate: none. Two naming layers by design — 18 atomic + 5 orchestrators.
- Deprecated: none.

## Recommended fixes
1. **P0** Bind `.mcp.json` to a DEMO MT5 account before any order test.
2. **P1** Add a bulk history loader to `data/` for conclusive backtests.
3. **P2** Authorize plugin MCPs (GitHub, etc.) only if used.
4. **P3** Optional double-nested path flatten (`...\smc-lss-platform\smc-lss-platform`).

## Verdict
Environment is **valid, connected, and operational** for research/decision workflows.
Execution-on-demo and conclusive backtesting remain open (see production_readiness.md).
