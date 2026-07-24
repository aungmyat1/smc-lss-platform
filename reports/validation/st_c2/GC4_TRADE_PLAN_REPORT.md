# ST-C2 GC4 Logical Trade Plan Report

**Date:** 2026-07-24  
**Lifecycle:** Stage A / A2 / S1-G2  
**Scope:** Research-only reference evidence

## Verdict

GC4 LOGICAL TRADE PLAN: PARTIAL PASS

S1-G2 REMAINS OPEN

## Evidence

- Logical trade plans are built with `LogicalTradePlan`.
- Entry is derived from LTF FVG evidence.
- Stop is derived from liquidity sweep extreme plus frozen stop buffer.
- Target is derived from the opposite structural dealing-range extreme.
- Stop min/max and net reward/risk checks are enforced from the frozen spec and
  `config/research_costs.yaml`.
- Plans are explicitly marked `research_only` and `no_order_routing`.
- Added research-only interface hook:
  `collect_logical_trade_plan()`.

## Tests

- `tests/st_c2/test_gc4_evidence.py::test_gc4_builds_complete_state_signal_and_trade_plan`
- `tests/test_st_c2_reference.py::test_positive_golden_case_emits_signal`
- `tests/test_st_c2_reference.py::test_bearish_mirror_emits_short_signal`

## Limits

This is not an executable order plan. Partial fills, post-fill event priority,
and live order management remain blocked.
