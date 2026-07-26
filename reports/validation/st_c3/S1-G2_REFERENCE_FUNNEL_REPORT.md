# ST-C3 A2/S1-G2 Reference Funnel Report

**Strategy:** ST-C3 v1.0.1
**Gate:** A2/S1-G2 (Reference Implementation Authorization, scoped)
**Authorization:** `governance/st_c3_stage_status.yaml` `a2_signal_conformance.opened`
(owner directive, 2026-07-26) — reference-funnel assembly, golden-case tests,
negative-case tests, existence-check conformance research. NOT execution,
optimization, A3 opening, demo, or live.

---

## What was built

- `validation/st_c3/evidence.py` — `Evidence` object + `make_evidence()`,
  spec-validated against `specs/st-c3_v1.0.1.yaml`'s `evidence` registry
  (§4.0) at construction time. Unknown/missing fields raise `ValueError`.
- `validation/st_c3/rejection_codes.py` — R-code/ERR-code sets loaded from
  the frozen spec's `rejection_code_json_schema`, not hardcoded.
- `validation/st_c3/kernel.py` — `run_kernel()`: the deterministic S0-S13
  guard/transition engine plus `TRADE_PLAN` emitter, matching
  `state_machine.transitions` and `state_machine.evidence_bindings` in the
  frozen spec exactly. Also `evaluate_expiry()`, a pure S14 expiry-reason ->
  ERR-code lookup (no monitoring loop, no execution).
- `validation/st_c3/trade_plan.py` — `TradePlan` dataclass matching the
  frozen spec's `trade_plan.schema` (§5).
- `validation/run_st_c3_existence_readiness.py` +
  `validation/st_c3/_readiness_bundles.py` — proves the kernel is
  wire-compatible with `tools/existence_check.py`'s `SignalFn` contract.
- `tests/st_c3/fixtures.py`, `test_golden_cases.py`,
  `test_negative_cases.py`, `test_existence_check_readiness.py` — 20 tests,
  all passing (`python -m pytest tests/st_c3 -q`).

## Scope decision: evidence-level kernel, not price-level detection

`specs/st-c3_v1.0.1.yaml` leaves several detection thresholds
`UNRESOLVED`/`PROVISIONAL` — `wick_ratio_min`, `equal_highs_lows_tolerance`,
`max_sweep_age_bars`, `displacement_body_ratio_min`, `freshness_definition`,
`buffer_points`, `entry_window_bars`, TP2/TP3 `rr_min`, and all `risk.*`
fields. `reports/validation/st_c3/OWNER_DECISION_LOG.md` and
`RESOLUTION_MATRIX.md` record owner decisions for most of these (R-04
through R-26), but **those decisions have not yet been folded into a frozen
spec revision** — the active frozen spec is still v1.0.1, unchanged since the
R-1/R-2/R-3/GR-1 rejection-code fix. Per the hard rules "Specification is the
source of truth" and "No implementation before specification freeze,"
building real price-bar SMC detection modules (sweep, displacement, FVG/OB
freshness, etc.) using RESOLUTION_MATRIX-only numbers would implement
un-frozen values — out of scope for this gate.

What v1.0.1 *does* fully specify, unconditionally, is the state machine
itself: `state_machine.transitions`, `state_machine.evidence_bindings`,
`validator_rules`, and `trade_plan.schema`. That layer's own
`validator_rules.principles.evidence_driven` explicitly describes it as
`validator_never_computes_structure` / `detection_modules_produce_evidence` —
i.e., the frozen spec already treats the validator/kernel and the raw-price
detection modules as separate concerns. This reference funnel implements the
former only. Golden/negative-case tests construct `Evidence` objects by hand
(asserting `.valid` and field values directly) rather than deriving them from
raw candles under thresholds that don't exist in the frozen spec yet.

Consequence: a genuine R-18 existence-check floor computation against real
market data remains blocked until a v1.0.2+ spec cut freezes the detection
thresholds. `validation/run_st_c3_existence_readiness.py` demonstrates
mechanical compatibility with `tools/existence_check.py` only, using a
synthetic hand-built evidence-bundle set — it is not an R-18 result.

## Golden-case coverage (Phase 3)

- `test_golden_long_reaches_trade_plan_emit` — full LONG path S0->S13,
  15-entry evidence chain, `TRADE_PLAN.status.state == VALID`.
- `test_golden_short_reaches_trade_plan_emit` — full SHORT path, NY session,
  distinct TP1/TP2/TP3 target types.
- `test_golden_cases_use_order_block_fallback_when_no_fvg` — S8's
  `(FVGEvidence.valid OR OrderBlockEvidence.valid)` OR-guard exercised via
  the OrderBlock branch.

## Negative-case coverage (Phase 4)

One test per required invalid path, each asserting the exact R-code, the
exact state at which the funnel stopped, and no `TRADE_PLAN` emission:

| Invalid path | State | Code |
|---|---|---|
| HTF bias unclear | S1_HTF_BIAS | R1_HTF_BIAS_UNCLEAR |
| No valid sweep | S2_SWEEP | R2_NO_SWEEP |
| Sweep not reclaimed | S3_SWEEP_RECLAIM | R2_NO_SWEEP |
| No displacement | S4_DISPLACEMENT_BOS | R3_NO_DISPLACEMENT_BOS |
| No valid BOS | S4_DISPLACEMENT_BOS | R3_NO_DISPLACEMENT_BOS |
| No BOS-extreme pullback lock | S5_BOS_EXTREME_LOCK | R3_NO_DISPLACEMENT_BOS |
| Invalid dealing range | S6_DEALING_RANGE | R4_NO_OTE_PULLBACK |
| Price outside OTE | S7_OTE | R4_NO_OTE_PULLBACK |
| No fresh FVG/OB confluence | S8_FVG_OB_CONFLUENCE | R5_NO_FVG_OB_CONFLUENCE |
| No LTF CHoCH/sweep confirmation | S9_LTF_CONFIRMATION | R6_NO_LTF_CONFIRMATION |
| Outside session window | S10_SESSION_GATEKEEPER | R6_NO_LTF_CONFIRMATION |
| Entry window expired | S11_ENTRY_WINDOW | R7_ENTRY_WINDOW_EXPIRED |
| Ambiguous structural stop | S12_RISK_SLTP | R8_INVALID_RISK_OR_TARGET |
| RR below MIN_RR | S12_RISK_SLTP | R8_INVALID_RISK_OR_TARGET |

Plus: `session_open=False` correctly yields `NOT_STARTED` with no code
(matching `S0`'s `failure_code: null`), and `make_evidence()` rejects both
missing and unexpected fields against the frozen spec's evidence registry.

## Result

19/19 targeted golden+negative tests pass, plus 1 existence-check
wire-compatibility test — 20/20 in `tests/st_c3/`. This satisfies the A2/S1-G2
scoped deliverables (reference-funnel assembly, golden-case tests,
negative-case tests, existence-check readiness) within the boundary the
frozen spec's own `validator_rules` and current `UNRESOLVED` field set impose.
Nothing in this work authorizes execution, optimization, A3 opening, demo, or
live trading, and none of it computes structure from real price data.

## Follow-on (not part of this gate)

- A v1.0.2 spec revision folding in the `RESOLUTION_MATRIX.md`-decided
  detection thresholds (R-04 through R-26) would need its own RCR and owner
  freeze act before price-level detection modules (mirroring
  `validation/st_c2/structure.py`'s pattern) could be built against ST-C3.
- R-18 (existence-check floor) real computation is blocked on that spec
  revision.
- R-03 (`sessions.low_liquidity_filters`) remains pending independent of this
  gate's work.
