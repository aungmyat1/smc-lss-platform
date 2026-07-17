# MCP Audit — SMC Trading Platform (re-run 3)
Generated: 2026-07-17 | live enumeration + demo execution status reconciled

## MetaTrader — CONNECTED & LIVE ✅
- Auth valid; VTMarkets demo login 1144985 verified by server/balance evidence.
- Connector `account_type` may report `real`; project policy treats server-name
  attestation as authoritative and fail-closes when not demo-attested.
- ~30 tools: account/positions/orders/deals reads; symbols/candles/price; place/modify/close/cancel (market + pending).
- Quirk encoded: `place_market_order` has no SL/TP → `modify_position` second step.
- Demo order round trip was verified once in `reports/execution_test.json`
  (place → modify SL/TP → close → journal). Scheduled auto-execution remains
  disabled while `engine_implements_spec=false`.

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
