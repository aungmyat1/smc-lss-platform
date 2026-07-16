# SMC-LSS Platform

Institutional Smart Money Concepts research + execution environment for Claude
(Cowork / Claude Code) wired to MetaTrader 5 via MCP.

## Layout
```
.claude/
  settings.json         # project config, permissions, risk limits
  skills/               # 18 atomic SMC skills + 5 orchestrators
.mcp.json               # MetaTrader MCP config (DEMO credentials)
specs/v1.yaml           # deterministic strategy spec (versioned)
src/backtest.py         # deterministic backtest runner (skeleton)
data/                   # historical CSVs (gitignored)
tests/                  # smoke tests
reports/                # audit + validation reports
```

## Skill architecture
Atomic detectors (market-structure, liquidity-sweep, order-block, fair-value-gap,
choch-bos, premium-discount, session-filter, inducement, mitigation,
entry-confirmation) feed orchestrators (strategy-validator, risk-manager,
backtest-researcher, trade-journal-analyst, trading-coach). The validator only
passes a setup to sizing if EVERY atomic gate passes.

## Safety
- `.mcp.json` MUST use a **DEMO** account for testing. Never point tests at a live account.
- Order tools are permission-gated to require human confirmation.

## Quick start
1. Put demo credentials in `.mcp.json`.
2. Drop historical CSVs in `data/` (e.g. `EURUSD_H4.csv`).
3. `python -m pytest -q` to verify structure.
4. `python src/backtest.py --spec specs/v1.yaml --data data/EURUSD_H4.csv`.
5. Install skills into Cowork via Settings -> Customize (or use them in a Claude Code repo directly).
