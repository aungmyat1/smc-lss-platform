# R-18 Partial-Funnel Signal-Rate Study — GBPUSD, v1.0.5 Only

**Date:** 2026-07-26
**Spec:** `specs/st-c3_v1.0.5.yaml` (deliberately not v1.0.6 — see scope note)
**Script:** `scripts/r18_partial_funnel_gbpusd.py`
**Symbol/timeframe:** GBPUSD H4/M15 only (EURUSD's H4/M15 CSVs have only
19-21 rows; XAUUSD excluded per R-02)

**Status: this is NOT a complete R-18 answer.** It is a diagnostic over the
six funnel stages that have real detection code
(`validation/st_c3/detection.py`), reported independently because running
them through the actual `EvidenceBundle`/`run_kernel()` with stubbed
always-invalid evidence for the unimplemented stages would produce a
trivially-uninformative `signal_rate=0.0` — every bar would reject at
S3 (the first unimplemented stage) regardless of what the real, implemented
stages show. See "Why this is partial, not a full run" below.

---

## Scope note: why v1.0.5, not v1.0.6

A separate, already-committed line of work (`specs/st-c3_v1.0.6.yaml`,
`validation/st_c3/evidence_builder.py`) exists in this repo claiming a full
R-18 resolution and an A2/S1-G2 "PASSED" declaration. That work has not
been independently verified end-to-end as of this report — an audit found
it used the OTE band (`ote_band_min=0.62`/`ote_band_max=0.79`) despite
`specs/st-c3_v1.0.6.yaml` itself still marking those fields provisional,
which is inconsistent with that same work's own claim that "every field
... is resolved." Per explicit instruction, this study stays on the
v1.0.5 line and does not use or depend on any v1.0.6 material, the other
session's evidence builder, or its A2/A3 status claims.

## Results

**S1 — HTF bias** (single current-context check, end of H4 series):
valid=True, bias=BEARISH.

**S2 — raw sweep** (sampled every 3rd M15 bar, indices 500-2500, R-04/R-05/
R-06 thresholds): **11/667 valid (1.6%)**.

**S4/S5/S6/S8 — chained per BOS candidate** (first 5,000 M15 bars, sampled
every 5th of 1,741 raw BOS candidates -> 349 evaluated; each stage requires
all prior stages in this chain to also pass):

| Stage | Parameters | Pass count | Rate |
|---|---|---|---|
| S4 displacement+BOS | body_ratio>=0.50, ATR floor=1.0x, N=2 confirmation bars | 83/349 | 23.8% |
| S5 BOS extreme lock | pullback depth>=0.30x ATR(1) | 66/349 | 18.9% |
| S6 dealing range | derived geometry, k=2 | 66/349 | 18.9% |
| S8 FVG/OB confluence | FVG gap>=0.15x MF_ATR(1), OB via `smc_engine.order_blocks()` | 66/349 | 18.9% |

**Joint S4+S5+S6+S8 pass rate: 66/349 (18.9%).** S6 and S8 add no further
filtering beyond S5 in this sample — once a BOS candidate clears
displacement/confirmation and the extreme-lock depth check, a dealing range
and an FVG/OB zone are almost always present too, at least over this
5,000-bar window.

## Why this is partial, not a full run

S1/S2 are reported independently of the S4-S8 chain because they anchor
differently: S2 (sweep) is evaluated per-bar, while S4-S8 are evaluated
per-BOS-candidate (a different, sparser index set). A real S0-S13 run would
need S3 (sweep reclaim) to bridge sweep detection into the BOS/displacement
chain, and S7 (OTE), S9 (LTF confirmation), S10 (session gate), S11 (entry
window), S12 (risk/SL/TP) to carry a qualifying setup the rest of the way
to `TRADE_PLAN_EMIT` — none of which have real detection code on the
v1.0.5 line (see `R18_DETECTION_MODULE_REPORT.md` for why each is blocked).

**Rough combined-rate sanity check** (not a rigorous joint probability,
since the samples aren't from identical windows): S1 valid, S2 ~1.6%, and
the S4-S8 chain ~18.9% multiply to roughly 0.3% of bars/candidates jointly
clearing just these six stages — before the still-missing S3/S7/S9-S12
gates would filter further. This is directionally consistent with the
separately-committed (not verified here) v1.0.6 existence-check's headline
result of `signal_rate=0.0` over a real 7-week window: a strict funnel with
these parameter values produces very few qualifying setups, which is a
plausible, non-alarming outcome for a multi-gate SMC funnel, not evidence
of an implementation bug in either line of work.

## What this does and does not mean

- **Does not** answer R-18. A complete answer needs S3, S7, S9, S10, S11,
  S12 implemented (or their blocking fields ratified) and a real S0-S13
  run, which this deliberately avoids doing with fabricated stub evidence.
- **Does** confirm the six implemented stages produce internally sensible,
  monotonic, spec-conformant behavior against real GBPUSD data — consistent
  with `tests/st_c3/test_detection.py`'s assertions.
- **Does not** touch governance files, `specs/st-c3_v1.0.5.yaml`, or any
  v1.0.6 material. No A2/A3 status claim is made or implied by this report.
