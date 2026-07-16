# Claude Environment Audit — SMC Trading Platform
Generated: 2026-07-16 | Environment: Claude **Cowork** session (not Claude Code repo) | Auditor: Cowork Systems Engineer

## Executive summary
This session is a **Cowork skills + MCP environment**, NOT a mounted Claude Code
repository. No user project folder is connected. Therefore the repository-level
checks in the source spec (`.claude/settings.json`, user `.mcp.json`, VS Code /
workspace config) have **no target to inspect** and are marked NOT APPLICABLE
rather than PASS/FAIL. What *can* be audited — installed skills and live MCP
tools — is audited truthfully below.

## Component checklist
| Expected component | Status | Evidence / Note |
|---|---|---|
| Connected repo / working folder | **NOT PRESENT** | `env: user selected folder = no`; mounts contain only `.claude` (read-only skills cache), `.remote-plugins`, `outputs`, `uploads` |
| `.claude/settings.json` (user) | **NOT APPLICABLE** | No user repo; only plugin-internal configs exist |
| `.claude/skills/` (installed) | **PASS (read-only)** | 5 SMC skills present in cache: strategy-validator, risk-manager, trade-journal-analyst, backtest-researcher, trading-coach |
| `.mcp.json` (user/trading) | **NOT PRESENT** | Only Anthropic plugin `.mcp.json` files found (finance/marketing/engineering) — not a trading repo |
| MCP configuration (runtime) | **PARTIAL** | MetaTrader MCP connected & live; many plugin MCPs require auth |
| VS Code / workspace settings | **NOT APPLICABLE** | Cowork desktop, no IDE workspace in scope |
| Claude Code configuration | **NOT APPLICABLE** | This is Cowork, not Claude Code |

## Missing / incorrect / duplicate / deprecated
- **Missing:** a connected repository (if one exists for the SMC-LSS platform, it must be mounted to run repo-level phases); backtest historical-data source; demo trading account.
- **Incorrect:** none detected in installed skills (frontmatter valid, no duplicates).
- **Duplicate:** none. (Prior stray temp files under `outputs/smc-lss-skills/` are packaging artifacts, not skills.)
- **Deprecated:** none.

## Recommended fixes (priority order)
1. **Decide the target environment.** If auditing the SMC-LSS *codebase*, connect that folder via the folder-access request so `.claude/`, `.mcp.json`, and source can be inspected. Otherwise treat scope as Cowork-only (this report).
2. **Provision a DEMO MT5 account** before any order-execution testing. The live bridge points at a REAL account (balance $988.12, 500x) — unsafe for automated test orders.
3. **Wire a historical data source** for backtesting (MT5 export / CSV / data API).
4. **Authorize needed plugin MCPs** (e.g., GitHub) via connector settings if they are part of the workflow.

## Verdict
Environment is a valid Cowork skills+MCP setup with a **live MT5 execution bridge**
and **5 installed SMC skills**, but it is **not a repository** and **not demo-isolated**.
Repository-level and demo-execution phases are BLOCKED pending the fixes above.
