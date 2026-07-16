# Skills Inventory — SMC Trading Platform
Generated: 2026-07-16 | Verified via `list_skills` + read-only skills cache + live activation test

## Installed skills (5) — all verified present, valid frontmatter, user-created
| Skill | Purpose | Trigger (sample) | Dependencies | Status | Issues | Recommendation |
|---|---|---|---|---|---|---|
| strategy-validator | 5-check SMC entry gate (HTF bias, liquidity, MSS, confirmation, rulebook) | "validate this setup" | metatrader MCP (candles, price) | **ACTIVE — live-fired** | Checks are qualitative/subjective; no programmatic SMC detection | Add deterministic detection rules or a Python detector via bash |
| risk-manager | Position sizing, stops, R:R, daily loss limit, overtrading guard | "size this trade" | metatrader MCP (account, price, symbols) | **ACTIVE** | Pip value hardcoded ($10/lot) — wrong for metals/JPY/cross | Pull tick_value per symbol before sizing |
| trade-journal-analyst | Log trades, classify mistakes, compute expectancy | "journal my trade" | metatrader MCP (deals/orders); storage | **ACTIVE** | No persistent storage backend defined | Define xlsx/CSV journal path or DB |
| backtest-researcher | Spec → backtest → version compare → accept/reject | "backtest this" | historical data + compute | **INSTALLED, NON-OPERATIONAL** | No wired data feed or backtest engine | Provide historical data source + engine |
| trading-coach | Discipline questions, never signals | "coach me" | none | **ACTIVE** | Least production-critical (by design) | Keep as-is |

## Phase 3 — Required institutional SMC skills (18): coverage gap
Legend: ✅ standalone skill · 🟡 covered as a *check/section* inside an existing skill · ❌ missing

| Required skill | Coverage | Where |
|---|---|---|
| market-structure | 🟡 | strategy-validator check 1/3 |
| liquidity-sweep | 🟡 | strategy-validator check 2 |
| order-block | 🟡 | strategy-validator check 4 |
| fair-value-gap | 🟡 | strategy-validator check 4 |
| choch-bos | 🟡 | strategy-validator check 3 |
| premium-discount | ❌ | not implemented |
| session-filter | 🟡 | strategy-validator check 5 |
| inducement | ❌ | not implemented |
| mitigation | ❌ | not implemented |
| entry-confirmation | 🟡 | strategy-validator check 4 |
| risk-management | ✅ | risk-manager |
| trade-management | 🟡 | risk-manager (modify_position) |
| backtesting | ✅ | backtest-researcher |
| optimization | 🟡 | backtest-researcher (walk-forward) |
| validation | 🟡 | backtest-researcher / strategy-validator |
| mt5-trading | 🟡 | metatrader MCP (no skill wrapper) |
| execution | 🟡 | risk-manager (place→modify flow) |
| journaling | ✅ | trade-journal-analyst |

**Tally:** 3 fully standalone ✅ · 11 partial 🟡 · 3 missing ❌. As **18 discrete
auto-loading skills**, ~13–15 do not exist. As **functional coverage**, the 5
consolidated skills cover roughly 55% of the intended behavior.

## Recommendation
Two valid designs — pick one:
- **A) Consolidated (current):** keep 5 skills; deepen each. Simpler, fewer trigger collisions. Recommended for a solo beginner.
- **B) Granular (spec):** author the 18 discrete skills. More modular/institutional, but higher maintenance and trigger-overlap risk. Requires manual install via Settings → Customize (session cannot write to the skills store).
