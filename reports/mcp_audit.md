# MCP Audit — SMC Trading Platform (re-run)
Generated: 2026-07-16 | live enumeration + connection tests

## MetaTrader — CONNECTED & LIVE ✅
- Auth valid; account REAL, $988.12, USD, 500x, 0 open positions (live-read).
- ~30 tools: account/positions/orders/deals reads; symbols/candles/price; place/modify/close/cancel (market + pending).
- Quirk encoded: `place_market_order` has no SL/TP → `modify_position` second step.
- ⚠️ Live REAL account reachable by order tools; no demo isolation.

## Platform MCPs — available
cowork, workspace(bash+web_fetch), scheduled-tasks, skills, computer-use,
claude-in-chrome, mcp-registry, session_info, plugins, visualize.

## Plugin MCPs — AUTH REQUIRED (unusable until authorized) ⚠️
github, asana, atlassian, datadog, linear, pagerduty, bigquery, ahrefs,
amplitude(+eu), canva, figma, hubspot, klaviyo, notion, slack, supermetrics.
similarweb: connecting. → Authorize via claude.ai connector settings.

## Spec-listed servers NOT present ❌ (with substitutes)
| Requested | Present | Substitute |
|---|---|---|
| Filesystem | ❌ | Read/Write + bash mount |
| Python | ❌ | bash sandbox python3 (used for backtest) |
| Terminal | ❌ | bash sandbox |
| Docker/Redis/Postgres/WebSocket | ❌ | none (SQLite possible in sandbox) |
| GitHub | 🟡 auth | github plugin |
| Browser | ✅ | claude-in-chrome |

## Config / secrets
`.mcp.json` present & valid; MT5 creds are placeholders (`<DEMO_LOGIN>` etc.).
Live MT5 credentials are connector-managed, not in-repo → good hygiene.
