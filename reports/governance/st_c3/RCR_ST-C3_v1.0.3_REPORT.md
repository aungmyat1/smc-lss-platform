# RCR-ST-C3-v1.0.3 — Revision Report

**Type:** Owner decision (fixed-lot value) + spec-value revision (instrument
scope). Not a research/backtest RCR under `docs/RESEARCH-CHARTER.md` — no
tunable strategy detection behavior was tested or changed.
**From:** `specs/st-c3_v1.0.2.yaml` **To:** `specs/st-c3_v1.0.3.yaml`
**Date:** 2026-07-26
**Directive:** owner chat directive resolving R-21 and (mislabeled) "R-22".

---

## Why

The owner supplied two new decisions in the same directive: a fixed-lot
size value (R-21, previously deferred), and a narrowed instrument scope
(submitted as "R-22"). Before folding these into the spec, both were
checked against the real governance files.

## Correction: R-02 vs. R-22

R-21 checked out cleanly — it is genuinely R-21 (`risk.fixed_lot_size`),
previously `DEFERRED`, now a legitimate owner risk-appetite decision.

The second decision did not. `OWNER_DECISION_LOG.md` records R-02
(`instruments`) as already **decided and frozen** in v1.0.2 —
`[EURUSD, GBPUSD, XAUUSD]`, approved 2026-07-25. R-22
(`instrument.selection_logic`) is a different, still-`DEFERRED` field:
cross-instrument tie-breaking logic for when multiple symbols signal
concurrently near the position cap (`risk.max_positions`=2,
`risk.max_positions_per_instrument`=1). The owner's submission ("XAUUSD
excluded because its pip-value x SL geometry violates the risk envelope
under fixed-lot sizing") supplies neither a tie-breaking rule nor anything
about *which pair takes priority* — it narrows *which instruments are
enabled at all*. That is unambiguously R-02's field, not R-22's.

This is the same category of mismatch `OWNER_DECISION_LOG.md` already
documents for other submissions (a "R-03"-labeled dual-timeframe
bias-confirmation proposal that was actually unrelated to the real R-03;
a "R-20"-labeled session-close forced-exit proposal that was actually
unrelated to the real R-20). Per that established precedent, the decision
was remapped by content, not by the submitted label, and recorded as a
**revision to R-02**. R-22 remains genuinely unresolved — no tie-breaking
rule has been supplied.

The owner's stated rationale ($1000 account capital; XAUUSD's pip-value x
SL-distance geometry exceeds the risk envelope under 0.01-lot fixed sizing)
is recorded as the owner's own risk-appetite judgment. It was not
independently re-derived (no SL-distance/pip-value computation was run to
verify "only 0.01 lot works" or "XAUUSD must be excluded") — same treatment
as R-05's directly-decided ATR tolerance in `OWNER_DECISION_LOG.md`, which
carries the same "owner decided directly, not empirically validated" caveat.

## What changed in `specs/st-c3_v1.0.3.yaml`

| Field | v1.0.2 | v1.0.3 | Source |
|---|---|---|---|
| `instruments` | `[EURUSD, GBPUSD, XAUUSD]` | `[EURUSD, GBPUSD]` | R-02 revision (mislabeled "R-22" in submission) |
| `risk.fixed_lot_size` | `DEFERRED` | `0.01` | R-21 |
| `trade_plan.schema.risk.fixed_lot_size` | `{type: float, status: DEFERRED}` | `{type: float, value: 0.01, status: decided}` | R-21 |

Nothing else changed — no evidence object, state, transition, guard,
rejection/termination code, or other spec field.

## What did NOT happen

- R-22 (`instrument.selection_logic`) was **not** resolved. It remains
  `DEFERRED`/pending — see `OWNER_DECISION_LOG.md`.
- No execution, optimization, backtesting, demo, live, or A3 logic was
  added or authorized.
- No independent verification of the $1000-capital risk math was performed
  — this is recorded as the owner's stated rationale for a risk-appetite
  decision, which does not require research validation the way a
  `Research required` field (like R-04/R-06) would.

## Updated governance state (corrected)

- **Decided (23 of 26):** R-01, R-02 (revised), R-03, R-04, R-05, R-06,
  R-07, R-08 (value only), R-09, R-10, R-12, R-13, R-14, R-15, R-16, R-17,
  R-19, R-20, R-21, R-23, R-24, R-25, R-26.
- **Deferred / still pending (2 of 26):** R-18 (`existence_check_floor`),
  R-22 (`instrument.selection_logic`).
- **Ruled out of v1.x scope (4 items, unchanged):** break-even/trailing,
  TP2/TP3 redefinition, session-close forced-exit, dual-timeframe bias
  confirmation.
- **Superseded (1, unchanged):** R-11 (`per_trade_risk_pct`).

23 + 2 + 4-scope-items + 1-superseded accounts for all 26 tracked rows (the
4 ruled-out and 1 superseded items are bookkept separately from the 26-row
decided/deferred/pending count per `RESOLUTION_MATRIX.md`'s own convention).

## Deliverables

- `specs/st-c3_v1.0.3.yaml`.
- `reports/validation/st_c3/OWNER_DECISION_LOG.md` — R-21 row filled in,
  R-02 row annotated with the revision, R-22 row annotated with the
  mismatch explanation, top status updated.
- `reports/validation/st_c3/RESOLUTION_MATRIX.md` — R-02/R-21/R-22 rows and
  priority summary updated.
- `governance/st_c3_stage_status.yaml` — `spec`/`version` bumped to v1.0.3,
  `v1_0_3_revision` metadata block added.
- `docs/strategy/st_c3/ST-C3_CHANGELOG.md` — v1.0.3 entry added.
- `validation/st_c3/evidence.py` — `SPEC_PATH` repointed to
  `specs/st-c3_v1.0.3.yaml`; `tests/st_c3/` re-verified passing.
- This report.

## Next steps

R-18 and R-22 are the only fields left unresolved. R-18 (existence-check
floor) needs price-level SMC detection modules built against v1.0.2/v1.0.3's
now-frozen thresholds and run over real candle data — a distinct,
not-yet-started engineering task. R-22 (instrument tie-breaking) needs an
explicit owner decision on which of EURUSD/GBPUSD takes priority when both
signal concurrently near the position cap; not urgent for Stage A (golden
cases run per-instrument independently) but will matter once Stage B design
starts.
