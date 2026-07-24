# ST-C3 Execution Agent Specification

**Strategy ID:** ST-C3
**Agent ID:** EXECUTION_AGENT_STC3
**Status:** Proposed Stage B specification; no execution authority

This specification defines the future execution layer that consumes the
`TRADE_PLAN` emitted at `S13_TRADE_PLAN_EMIT` and performs deterministic,
rule-bound execution after ST-C3 has passed the required governance gates.

This document does not authorize implementation, broker integration, demo
trading, live trading, or production.

---

## Agent Identity

```yaml
agent_id: EXECUTION_AGENT_STC3
role: Execute validated ST-C3 trade-plans
mode: deterministic_rule_based_session_aware
inputs: TRADE_PLAN object from S13
outputs: execution events, order placement, lifecycle logs
```

---

## Responsibilities

- Consume validated `TRADE_PLAN` objects.
- Enforce session rules.
- Enforce expiry rules.
- Place orders only inside the entry zone.
- Respect SL/TP levels.
- Track RR, partial exits, and liquidity targets.
- Emit execution logs for governance.
- Terminate trades using ERR-codes.
- Never override validator decisions.
- Never modify evidence.
- Never modify trade-plan structure.
- Never reinterpret structure.

---

## Execution Preconditions

Execution begins only if:

```text
TRADE_PLAN.status.state == "VALID"
AND current_session IN ["LONDON", "NY"]
AND price is inside TRADE_PLAN.entry.entry_zone
```

If any precondition fails, no trade is placed.

---

## Execution Workflow

1. Load `TRADE_PLAN`: direction, entry zone, SL, TP1/TP2/TP3, RR, expiry rules,
   and evidence chain.
2. Enforce session. If session is not `LONDON` or `NY`, terminate with
   `ERR_ENTRY_WINDOW_EXPIRED`.
3. Enforce entry zone. If price is outside the entry zone, wait. If price is
   inside the entry zone, place order.
4. Place order as market or limit, depending on the trade plan.
5. Enforce SL. If price hits SL, terminate with `ERR_SL_INVALIDATION`.
6. Execute partial exits: TP1 closes 30%, TP2 closes 30%, TP3 closes 40%.
7. Enforce expiry triggers: HTF bias flip, entry-window expiration, SL break,
   and superseded setup.
8. Complete trade when TP3 is hit and emit final RR, liquidity targets hit,
   full evidence chain, and execution log.

Entry zone types:

- FVG entry.
- Order Block entry.
- Hybrid entry: OB inside FVG.

---

## YAML Specification

```yaml
execution_agent:
  id: EXECUTION_AGENT_STC3
  mode: deterministic
  authorization: blocked_until_stage_b

  preconditions:
    - TRADE_PLAN.status.state == "VALID"
    - session IN ["LONDON", "NY"]
    - price_inside_trade_plan_entry_zone

  entry_logic:
    zone_type: TRADE_PLAN.entry.entry_zone_type
    zone_id: TRADE_PLAN.entry.entry_zone_id
    entry_price: TRADE_PLAN.entry.entry_price
    max_entry_bars: TRADE_PLAN.entry.max_entry_bars
    supported_zone_types: ["FVG", "ORDERBLOCK", "HYBRID_OB_INSIDE_FVG"]

  order:
    type: ["MARKET", "LIMIT"]
    sl: TRADE_PLAN.risk.sl_price
    tp1: TRADE_PLAN.targets.tp1.price
    tp2: TRADE_PLAN.targets.tp2.price
    tp3: TRADE_PLAN.targets.tp3.price
    risk_pct: TRADE_PLAN.risk.risk_per_trade_pct

  expiry_rules:
    - BIAS_FLIP
    - ENTRY_WINDOW
    - SL_BREAK
    - SUPERSEDED

  termination_codes:
    BIAS_FLIP: ERR_HTF_BIAS_FLIP
    ENTRY_WINDOW: ERR_ENTRY_WINDOW_EXPIRED
    SL_BREAK: ERR_SL_INVALIDATION
    SUPERSEDED: ERR_SUPERSEDED_SETUP

  partial_exits:
    tp1: 0.30
    tp2: 0.30
    tp3: 0.40

  outputs:
    - execution_log
    - termination_log
    - final_rr
    - liquidity_targets_hit
```

---

## Event Model

Execution events:

- `EXEC_ENTER`
- `EXEC_EXIT_TP1`
- `EXEC_EXIT_TP2`
- `EXEC_EXIT_TP3`
- `EXEC_SL_HIT`
- `EXEC_EXPIRED`
- `EXEC_TERMINATED`
- `EXEC_COMPLETED`

Termination events:

- `ERR_HTF_BIAS_FLIP`
- `ERR_ENTRY_WINDOW_EXPIRED`
- `ERR_SL_INVALIDATION`
- `ERR_SUPERSEDED_SETUP`
