# RCR-ST-C3-v1.0.4 — Revision Report

**Type:** Owner decision (instrument tie-breaking rule). Not a research/
backtest RCR under `docs/RESEARCH-CHARTER.md` — no tunable strategy
detection behavior was tested or changed.
**From:** `specs/st-c3_v1.0.3.yaml` **To:** `specs/st-c3_v1.0.4.yaml`
**Date:** 2026-07-26
**Directive:** owner chat directive resolving R-22, following the v1.0.3
correction that identified R-22 as still unresolved.

---

## Why

v1.0.3's RCR report flagged that a submission labeled "R-22" had actually
revised R-02 (instrument scope), and that R-22 itself
(`instrument.selection_logic`) remained genuinely unresolved. The owner
supplied the actual R-22 rule in a follow-up directive.

## The decision

When both R-02 instruments (EURUSD, GBPUSD) qualify concurrently near the
position cap (`risk.max_positions`=2, `risk.max_positions_per_instrument`=1):

```
IF computed_rr(EURUSD) > computed_rr(GBPUSD) THEN select EURUSD
ELIF computed_rr(GBPUSD) > computed_rr(EURUSD) THEN select GBPUSD
ELSE select EURUSD (fixed-priority fallback)
```

Owner-stated rationale, recorded as-given (risk-appetite/architecture
judgment, not independently re-derived — same treatment as R-05/R-21):
`computed_rr` is already a frozen `trade_plan.schema.risk` field, so this
introduces no new metric; deterministic with no randomness; EURUSD wins
ties for lower volatility/tighter spreads near the position cap, consistent
with R-02's own XAUUSD-exclusion rationale.

## Verification performed before folding in

- Confirmed `computed_rr` is an existing frozen field
  (`trade_plan.schema.risk.computed_rr`), not a new concept — no fabricated
  field introduced.
- Confirmed this is genuinely R-22 (cross-instrument tie-breaking), not
  another mislabeled submission — it addresses "which pair wins when both
  qualify," matching R-22's tracked definition exactly, unlike the prior
  submission that supplied an R-02 change under the "R-22" label.
- Confirmed this doesn't touch Stage A: `RESOLUTION_MATRIX.md` already notes
  R-22 is "Low for Stage A (state machine/golden cases run per-instrument
  independently); relevant later ... at Stage B" — so recording the rule as
  spec content does not require or imply any change to
  `validation/st_c3/kernel.py`'s S0-S13 logic, and no Stage B execution code
  was written (none is authorized).

## What changed in `specs/st-c3_v1.0.4.yaml`

Added `risk.instrument_tie_breaking_rule` (new field — R-22 was previously
untracked in any spec version, only in `OWNER_DECISION_LOG.md`):

```yaml
instrument_tie_breaking_rule:
  primary_metric: computed_rr
  comparison: higher_wins
  fallback_on_exact_tie: EURUSD
  rule: >
    IF computed_rr(EURUSD) > computed_rr(GBPUSD) THEN select EURUSD
    ELIF computed_rr(GBPUSD) > computed_rr(EURUSD) THEN select GBPUSD
    ELSE select EURUSD (fixed-priority fallback)
```

Nothing else changed — no evidence object, state, transition, guard,
rejection/termination code, or other spec field.

## What did NOT happen

- No execution, optimization, backtesting, demo, live, or A3 logic added.
- No Stage B arbitration code implemented — this is a decided rule recorded
  in the frozen spec for a future execution agent to consume, not an
  active portfolio-selection mechanism today (no execution agent exists).
- No change to `validation/st_c3/kernel.py` or `tests/st_c3/` behavior —
  the state machine remains per-instrument, unaffected by this field.

## Updated governance state

- **Decided (24 of 26):** R-01, R-02 (revised), R-03, R-04, R-05, R-06,
  R-07, R-08 (value only), R-09, R-10, R-12, R-13, R-14, R-15, R-16, R-17,
  R-19, R-20, R-21, R-22, R-23, R-24, R-25, R-26.
- **Pending (1 of 26):** R-18 (`existence_check_floor`) — the only field
  remaining unresolved.
- **Ruled out of v1.x scope (4 items, unchanged):** break-even/trailing,
  TP2/TP3 redefinition, session-close forced-exit, dual-timeframe bias
  confirmation.
- **Superseded (1, unchanged):** R-11 (`per_trade_risk_pct`).

## Deliverables

- `specs/st-c3_v1.0.4.yaml`.
- `reports/validation/st_c3/OWNER_DECISION_LOG.md` — R-22 row filled in,
  top status updated to 24/26 decided, 1 pending.
- `reports/validation/st_c3/RESOLUTION_MATRIX.md` — R-22 row and priority
  summary updated.
- `governance/st_c3_stage_status.yaml` — `spec`/`version` bumped to v1.0.4,
  `v1_0_4_revision` metadata block added.
- `docs/strategy/st_c3/ST-C3_CHANGELOG.md` — v1.0.4 entry added.
- `validation/st_c3/evidence.py` — `SPEC_PATH` repointed to
  `specs/st-c3_v1.0.4.yaml`; `tests/st_c3/` re-verified passing (unaffected
  by this field, as expected).
- This report.

## Next steps

R-18 (existence-check floor) is now the only unresolved field of the 26
tracked. It requires building real price-level SMC detection modules
against the thresholds v1.0.2/v1.0.3 froze, then running them over real
candle data via `tools/existence_check.py` + `tools/power_planning.py` — a
distinct, not-yet-started engineering task within the existing A2/S1-G2
scoped authorization.
