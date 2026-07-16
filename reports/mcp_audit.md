# MCP Audit — SMC Trading Platform
Generated: 2026-07-16 | Method: live tool enumeration + connection tests

## MetaTrader (trading MCP) — CONNECTED & LIVE ✅
- **Auth:** valid — `get_account_info` returns real data.
- **Account:** REAL, balance $988.12, equity $988.12, USD, leverage 500, 0 open positions.
- **Transport/health:** responsive; candle/price/symbol reads succeed live.
- **Tools available (~30):** get_account_info, get_all_symbols, get_symbols, get_symbol_price, get_candles_latest, get_all_positions, get_positions_by_id/symbol, get_all_pending_orders, get_pending_orders_by_id/symbol, get_orders, get_deals, place_market_order, place_pending_order, modify_position, modify_pending_order, close_position, close_all_positions(+by_symbol/profitable/losing), cancel_pending_order(+all/by_symbol).
- **Known quirk:** `place_market_order` does NOT accept SL/TP → must follow with `modify_position`. Encoded in risk-manager.
- **⚠️ RISK:** live REAL-money account is fully reachable by order tools. No demo isolation.

## Platform / infra MCPs — available
CONNECTED: cowork, workspace (bash + web_fetch), scheduled-tasks, skills, computer-use, claude-in-chrome (browser), mcp-registry, session_info, plugins, visualize.

## Plugin MCPs — require authentication (UNUSABLE until authorized) ⚠️
github, asana, atlassian, datadog, linear, pagerduty, bigquery, ahrefs, amplitude(+eu), canva, figma, hubspot, klaviyo, notion, slack, supermetrics.
similarweb: still connecting.
→ Authorize via claude.ai connector settings (or `claude mcp` / `/mcp` in an interactive session). Cannot be OAuth'd from this non-interactive session.

## Spec-listed servers NOT present ❌
| Requested | Present? | Substitute available |
|---|---|---|
| Filesystem MCP | ❌ | Read/Write tools + bash sandbox |
| Python MCP | ❌ | bash sandbox (python3 preinstalled) |
| Terminal MCP | ❌ | bash sandbox |
| Docker | ❌ | none |
| Redis | ❌ | none |
| Postgres | ❌ | none (could use SQLite in sandbox) |
| WebSocket | ❌ | none |
| GitHub | 🟡 auth-pending | github plugin (needs authorization) |
| Browser | ✅ | claude-in-chrome |

## Config / secrets / env
- No user `.mcp.json` in scope (no repo). MetaTrader credentials are managed by the connector, not visible/inspectable here → cannot audit secret hygiene from this session.
- Sandbox network access: ON, "Package managers only" allowlist (per Settings screenshot) — safe default.

## Recommendation
1. **Isolate a DEMO MT5 profile** for testing; keep the real account out of automated test loops.
2. Authorize only the plugin MCPs you actually use.
3. If Docker/Redis/Postgres/WebSocket are truly required by the architecture, they must be installed as MCP servers — none exist today. Otherwise drop them from scope.
