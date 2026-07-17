---
name: smc-trading-master
description: >-
  Master orchestrator for the full SMC-LSS workflow. Coordinates the analysis,
  execution, and research skills in a fixed order, stopping immediately if any
  hard gate fails. Trigger on "analyze <SYMBOL>", "run the SMC workflow",
  "full setup check", or any end-to-end trade-decision request. Never skips steps.
version: 1.0
---

# SMC Trading Master

## Purpose
Run the complete SMC-LSS pipeline end to end and produce a single GO/NO-GO
decision with a per-stage audit trail. Orchestrates the specialized skills;
does not re-implement their logic. Backed by runnable code: `src/smc_master.py`.

## Inputs
- symbol + candle data (CSV via load_history.py, or live via metatrader MCP)
- account equity (metatrader get_account_info), risk % (default 0.5), min R:R (2.0)

## Outputs
- ordered stage report (each PASS/FAIL + evidence)
- final decision GO/NO-GO with reason
- on GO: sized two-step order payload for the execution layer

## Workflow (never skip; stop at first hard-gate FAIL)
1. session-filter        (hard, optional strict)
2. market-structure      (hard: bias must not be RANGING)
3. liquidity-sweep       (hard: aligned sweep required)
4. choch-bos             (hard: aligned structure shift)
5. order-block           (confluence, soft)
6. fair-value-gap        (confluence, soft)
7. premium-discount      (hard: correct zone for direction)
8. entry-confirmation    (hard: LTF signal present)
9. risk-management       (hard: lots>0 and R:R>=min)
10. mt5-trading          (execution: place_market_order)
11. trade-management     (execution: modify_position SL/TP, manage)
12. journaling           (record to data/journal.csv)

## Decision rules
- Hard gate FAIL -> stop, decision NO-GO, report the failing stage.
- Confluence (OB/FVG) is scored, not blocking.
- Execution stages 10-12 run ONLY on GO and ONLY on a demo account.

## Validation checklist
- [ ] stages evaluated strictly in order
- [ ] first hard FAIL halts the pipeline
- [ ] no order emitted unless stage 9 = GO
- [ ] deterministic: identical candles -> identical decision

## Failure handling
Any missing data or engine error -> NO-GO with the stage and reason. Never
guess past a failed gate. On execution error, close any partial position.

## Examples
`python src/smc_master.py --data data/EURUSD_H1.csv --equity 988.12 --risk_pct 0.5`
-> stops at "2 market-structure: RANGING" => NO-GO (correct stand-aside).

## Acceptance criteria
- [ ] Emits ordered stage report + GO/NO-GO
- [ ] Hands a sized payload to execution only on GO
- [ ] Mirrors institutional signal / execution / research separation
