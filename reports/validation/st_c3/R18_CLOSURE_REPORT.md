# R-18 Closure Report — v1.0.5 Line

**Date:** 2026-07-26
**Status: R-18 (`existence_check_floor`) remains OPEN / UNRESOLVED.** This
report documents engineering progress made against it on the v1.0.5 line —
it is not a closure or resolution, despite the filename. "Closure" here
means "closing out this round of work," not "R-18 is closed."

**A2 remains in progress. A3 remains blocked.** No governance file is
touched by this report. The parallel v1.0.6 line (`specs/st-c3_v1.0.6.yaml`,
`validation/st_c3/evidence_builder.py`, and its "A2/S1-G2 PASSED"/"A3
OPENED" claims) remains quarantined — unverified, not relied upon, not
merged, not adopted — per the audit in this conversation that found it
used the OTE band despite that same work's own spec revision marking it
provisional.

---

## What is implemented (`validation/st_c3/detection.py`)

Real, tested price-level detection against real GBPUSD H4/M15 data, using
only frozen `specs/st-c3_v1.0.5.yaml` parameters:

| Stage | Frozen parameters |
|---|---|
| S1_HTF_BIAS | R-27 swing/fractal `k=2` |
| S2_SWEEP (raw pierce, not reclaim) | R-04 `wick_ratio_min=0.50`, R-05 `equal_tolerance=0.10x MF_ATR(1)`, R-06 `max_age=15` |
| S4_DISPLACEMENT_BOS | R-07 `body_ratio_min=0.50` + ATR floor `1.0x`, R-28 `N=2` confirmation bars |
| S5_BOS_EXTREME_LOCK | R-30 pullback depth `0.30x ATR(1)` |
| S6_DEALING_RANGE | derived geometry from R-27's `k`, no independent threshold |
| S8_FVG_OB_CONFLUENCE | R-29 FVG min gap `0.15x MF_ATR(1)`, R-23/R-24 freshness (OB<=3, FVG<=1 MF swings) |

Reuses only existing generic `src.smc_engine` primitives (`swings`, `atr`,
`fvgs`, `order_blocks`) — no invented or ST-C2-inherited detection
algorithm. `tests/st_c3/test_detection.py` (16 tests) assert determinism,
spec-conformant `Evidence` shape, and monotonic threshold behavior against
real data.

## What is blocked (why R-18 cannot close)

| Stage | Blocked on | Status |
|---|---|---|
| S3_SWEEP_RECLAIM | `sweep_reclaim_max_bars` | `PROVISIONAL_1_TO_3` in v1.0.5, never ratified on this line |
| S7_OTE | `ote_band_min`/`ote_band_max`/`equilibrium_boundary` | Reference-doc provisional since v1.0.0; never owner-ratified. The parallel v1.0.6/evidence_builder work used these values anyway ("still spec-marked provisional but numerically usable") — that is exactly the implementation-before-freeze violation this v1.0.5 line avoids; not adopted here. |
| S9_LTF_CONFIRMATION | No ratified M3/M1 CHoCH detection parameters exist at all |
| S10_SESSION_GATEKEEPER | `london_window_utc`/`ny_window_utc` | `PROVISIONAL_*` in v1.0.5, never ratified on this line |
| S11_ENTRY_WINDOW | `entry_window_bars` | `PROVISIONAL_3_TO_5_M3_BARS` in v1.0.5, never ratified on this line |
| S12_RISK_SLTP | `buffer_points_atr_multiplier`'s guard *direction* formulation flagged unconfirmed (R-08, `OWNER_DECISION_LOG.md`) |

**Note on EURUSD:** all real-data work on this line runs GBPUSD-only.
`data/EURUSD_H4.csv`/`EURUSD_M15.csv` exist but contain only 19-21 rows —
insufficient for any distribution or existence-check work. XAUUSD is
excluded per R-02's revision (v1.0.3). A real multi-instrument R-18 answer
needs better EURUSD history sourced first, independent of the six blocked
stages above.

## GBPUSD diagnostic results (not a full existence check)

`reports/validation/st_c3/R18_PARTIAL_FUNNEL_SIGNAL_RATE_GBPUSD.md`:

- S2 (raw sweep): 0.2-1.6% pass rate, window-sensitive (R-04/R-05/R-06 thresholds)
- S4-S8 joint chain (per BOS candidate): 20.3% pass rate on the full
  30,000-bar M15 series (2,112/10,417), consistent with an initial 18.9%
  bounded sample
- Rough combined estimate: ~0.04-0.3% of bars/candidates jointly clear
  these six stages — before the six still-blocked stages would filter
  further

This is directionally consistent with (but independent of, and not relying
on) the quarantined v1.0.6 line's disputed `signal_rate=0.0` result: a
multi-gate SMC funnel with these parameter values produces few qualifying
setups, a plausible outcome rather than evidence of a bug in either line.

## Why a real S0-S13 run was not attempted

Running the actual `EvidenceBundle`/`run_kernel()` end-to-end would require
stub `Evidence` for the six blocked stages. Stubbing them `valid=False`
(the only honest choice, since no ratified threshold exists to decide
otherwise) would make every bar reject at S3 — immediately after S2 —
regardless of what the five implemented downstream stages (S4-S8) show.
That would produce a `signal_rate=0.0` that looks like a real R-18 answer
but actually reflects "this stage was never implemented," not genuine
structural rarity. The partial, stage-by-stage diagnostic above is the
honest alternative.

## What would actually close R-18

1. Owner ratification of `sweep_reclaim_max_bars` (S3), the OTE band/
   equilibrium (S7), M3/M1 CHoCH parameters (S9), session windows (S10),
   `entry_window_bars` (S11), and R-08's guard direction (S12) — likely via
   the same empirical-research-then-ratify pattern used for R-27–R-30.
2. Real detection code for those six stages, built against whatever gets
   ratified.
3. A real S0-S13 run over real candle data producing an actual signal-rate
   number — ideally also with better EURUSD history so R-18 isn't
   GBPUSD-only.

None of that happened in this report. R-18 remains open.

## Governance state (unchanged by this report)

- **A2 remains in progress**, not passed.
- **A3 remains blocked**, not open.
- No owner decision authorizing either exists on the v1.0.5 line.
- `PROJECT_STATUS.md`, `OWNER_DECISION_LOG.md`, `NEXT_ACTION.md`,
  `governance/st_c3_stage_status.yaml` — none modified by this report.
- The parallel v1.0.6 line remains quarantined: not deleted, not merged,
  not treated as authoritative, pending explicit re-audit.
