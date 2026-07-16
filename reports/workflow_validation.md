# Workflow & Auto-loading Validation
Generated: 2026-07-16 | Honest PASS/FAIL/NOT IMPLEMENTED

## Auto-loading (Phase 9) — skills fire on trigger?
| Prompt | Expected skill | Result | Evidence |
|---|---|---|---|
| (activation test) invoke strategy-validator | strategy-validator loads | **PASS** | Skill loaded full instruction set from installed cache |
| "validate this EURUSD setup" | strategy-validator | **PASS (demonstrated prior turn)** | Ran 5-check gate on live data → INVALID/stand-aside |
| "size this trade, stop 24 pips" | risk-manager | **PASS (demonstrated prior turn)** | Computed 0.04 lots, refused on R:R |
| "backtest this rule" | backtest-researcher | **PARTIAL** | Skill loads, but cannot execute — no data feed |
| "journal my last trade" | trade-journal-analyst | **NOT IMPLEMENTED** | No closed trades + no store to write to |
| "coach me" | trading-coach | **PASS (design-verified)** | Loads; question flow intact |

Note: skills are **trigger-on-match**, not autonomous daemons. They activate when
a request matches — they do not monitor markets on their own. This is correct and safe.

## End-to-end workflow (Phase 11 / 13) — GBPUSD/EURUSD full chain
| Stage | Result | Reason |
|---|---|---|
| User prompt → skill selection | **PASS** | Verified (validator/risk fired) |
| Skill → tool selection → MCP read | **PASS** | Live candles/price/account |
| Risk → lot size | **PASS** | Deterministic sizing computed |
| MT5 **demo** execution | **NOT IMPLEMENTED** | No demo account; real account excluded from test orders by policy |
| Journal write | **NOT IMPLEMENTED** | No store wired |
| Logging / recovery | **NOT IMPLEMENTED** | No harness |

**Verdict:** The **analysis-and-decision half** of the workflow runs end-to-end with
no manual intervention (prompt → validate → size → decision). The **execution-and-record
half** is NOT validated and must not be claimed until a demo account and journal store exist.
