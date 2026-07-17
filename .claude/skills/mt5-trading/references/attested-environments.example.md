# Attested MT5 Environments (TEMPLATE — copy to attested-environments.md, fill, keep local)

The real file is gitignored because it contains account identifiers. Fill one row
per verified login. A DEMO_VERIFIED match here satisfies the demo-safe gate.

| Login | Account name | Broker | Server | Environment | Attested (UTC) | Method |
|---|---|---|---|---|---|---|
| <LOGIN> | <NAME> | <BROKER> | <SERVER e.g. Broker-Demo> | DEMO_VERIFIED | <YYYY-MM-DD> | <how verified> |

## Rules
- Match on login number, not the connector `account_type` field (UNVERIFIED).
- Login not listed -> UNVERIFIED -> treat as LIVE (fail-safe).
- Server not containing "Demo" -> LIVE; explicit owner approval required before any write.
