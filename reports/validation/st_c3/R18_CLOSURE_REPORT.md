# R-18 Closure Report — v1.0.7 Line

**Date:** 2026-07-26, updated 2026-07-27 (S3/S10/S11 implemented; spec line
advanced v1.0.5 -> v1.0.7)
**Status: R-18 (`existence_check_floor`) remains OPEN / UNRESOLVED.** This
report documents engineering progress made against it — it is not a
closure or resolution, despite the filename. "Closure" here means "closing
out this round of work," not "R-18 is closed."

**A2 remains in progress. A3 remains blocked.** No governance escalation
is implied by this report. The parallel v1.0.6 line
(`specs/st-c3_v1.0.6.yaml`, `validation/st_c3/evidence_builder.py`, and its
"A2/S1-G2 PASSED"/"A3 OPENED" claims) remains quarantined — unverified, not
relied upon, not merged, not adopted — per
`reports/governance/v1.0.6_RECONCILIATION_AUDIT.md`, which found it used
the OTE band despite that same work's own spec revision marking it
provisional.

---

## What is implemented (`validation/st_c3/detection.py`)

Real, tested price-level detection against real GBPUSD H4/M15 data, using
only frozen `specs/st-c3_v1.0.7.yaml` parameters:

| Stage | Frozen parameters |
|---|---|
| S1_HTF_BIAS | R-27 swing/fractal `k=2` |
| S2_SWEEP (raw pierce) | R-04 `wick_ratio_min=0.50`, R-05 `equal_tolerance=0.10x MF_ATR(1)`, R-06 `max_age=15` |
| S3_SWEEP_RECLAIM | R-31 `sweep_reclaim_max_bars=2` |
| S4_DISPLACEMENT_BOS | R-07 `body_ratio_min=0.50` + ATR floor `1.0x`, R-28 `N=2` confirmation bars |
| S5_BOS_EXTREME_LOCK | R-30 pullback depth `0.30x ATR(1)` |
| S6_DEALING_RANGE | derived geometry from R-27's `k`, no independent threshold |
| S8_FVG_OB_CONFLUENCE | R-29 FVG min gap `0.15x MF_ATR(1)`, R-23/R-24 freshness (OB<=3, FVG<=1 MF swings) |
| S10_SESSION_GATEKEEPER | R-33 session UTC windows (London 07:00-10:00, NY 13:00-16:00) |
| S11_ENTRY_WINDOW (check mechanism) | R-32 `entry_window_bars=4` — see S11 caveat below |

Reuses only existing generic `src.smc_engine` primitives (`swings`, `atr`,
`fvgs`, `order_blocks`) — no invented or ST-C2-inherited detection
algorithm. `tests/st_c3/test_detection.py` and
`tests/st_c3/test_detection_structural_conformance.py` (24 tests combined)
assert determinism, causal invariance, spec-conformant `Evidence` shape,
and correct threshold behavior against real data.

**S11 caveat:** `entry_window_evidence_for()` implements R-32's window
check (bars-since-LTF-CHoCH vs. `max_allowed_bars=4`) as real, tested
logic — but it takes `bars_since_ltf_choch` as an input rather than
deriving it from raw candles, since that derivation is S9 (LTF CHoCH
detection), which remains blocked. The comparison itself is not a stub;
it just cannot run end-to-end without S9 supplying its input.

## What is still blocked (why R-18 cannot close)

| Stage | Blocked on | Status |
|---|---|---|
| S7_OTE | `ote_band_min`/`ote_band_max`/`equilibrium_boundary` | Reference-doc provisional since v1.0.0; never owner-ratified. The quarantined v1.0.6/evidence_builder work used these values anyway ("still spec-marked provisional but numerically usable") — that is exactly the implementation-before-freeze violation this line avoids; not adopted here. |
| S9_LTF_CONFIRMATION | No ratified M3/M1 CHoCH detection parameters exist at all |
| S12_RISK_SLTP | `buffer_points_atr_multiplier`'s guard *direction* formulation flagged unconfirmed (R-08, `OWNER_DECISION_LOG.md`) |

Three of the original six blocked stages (S3, S10, S11's check mechanism)
are now implemented, following R-31/R-32/R-33's fresh decision
(`reports/governance/st_c3/RCR_ST-C3_v1.0.7_REPORT.md`). Three remain
blocked — S7/S9/S12 — each on a field with **no owner decision of any
kind on record**, not just an unimplemented one.

**Note on EURUSD:** all real-data work on this line runs GBPUSD-only.
`data/EURUSD_H4.csv`/`EURUSD_M15.csv` exist but contain only 19-21 rows —
insufficient for any distribution or existence-check work. XAUUSD is
excluded per R-02's revision (v1.0.3). A real multi-instrument R-18 answer
needs better EURUSD history sourced first, independent of the blocked
stages above.

## GBPUSD diagnostic results (not a full existence check)

`reports/validation/st_c3/R18_PARTIAL_FUNNEL_SIGNAL_RATE_GBPUSD.md`
(predates S3/S10/S11's implementation, still the latest quantitative
read):

- S2 (raw sweep): 0.2-1.6% pass rate, window-sensitive (R-04/R-05/R-06 thresholds)
- S4-S8 joint chain (per BOS candidate): 20.3% pass rate on the full
  30,000-bar M15 series (2,112/10,417), consistent with an initial 18.9%
  bounded sample
- Rough combined estimate: ~0.04-0.3% of bars/candidates jointly clear
  these six stages — before the remaining blocked stages would filter
  further

This is directionally consistent with (but independent of, and not relying
on) the quarantined v1.0.6 line's disputed `signal_rate=0.0` result: a
multi-gate SMC funnel with these parameter values produces few qualifying
setups, a plausible outcome rather than evidence of a bug in either line.
Re-running this diagnostic with S3/S10/S11 folded into the chain would
narrow it further and is a reasonable next step, not yet done.

## Why a real S0-S13 run still was not attempted

S7 (OTE), S9 (LTF confirmation), and S12 (risk/SL/TP) still have no
detection code. Running the actual `EvidenceBundle`/`run_kernel()`
end-to-end would still require stub `Evidence` for those three stages.
Stubbing them `valid=False` (the only honest choice) would make every bar
reject at S7 — right after the now-implemented S6 — regardless of what
S1-S6/S8/S10 show. That would produce a `signal_rate=0.0` that looks like
a real R-18 answer but actually reflects "these three stages were never
implemented," not genuine structural rarity. The partial diagnostic
remains the honest alternative until S7/S9/S12 are unblocked.

## What would actually close R-18

1. Owner ratification of the OTE band/equilibrium (S7), M3/M1 CHoCH
   parameters (S9), and R-08's guard direction (S12) — likely via the same
   empirical-research-then-ratify pattern used for R-27–R-30/R-31–R-33.
2. Real detection code for those three stages, plus a real S9-derived
   `bars_since_ltf_choch` feed into the existing S11 check mechanism.
3. A real S0-S13 run over real candle data producing an actual signal-rate
   number — ideally also with better EURUSD history so R-18 isn't
   GBPUSD-only.

None of that happened in this update. R-18 remains open, now with fewer
remaining gaps (3 of the original 6) than before.

## Governance state (unchanged by this report)

- **A2 remains in progress**, not passed.
- **A3 remains blocked**, not open.
- No owner decision authorizing either exists.
- `PROJECT_STATUS.md`, `OWNER_DECISION_LOG.md`, `NEXT_ACTION.md`,
  `governance/st_c3_stage_status.yaml` — none modified by this report
  beyond what the v1.0.7 RCR already recorded.
- The parallel v1.0.6 line remains quarantined: not deleted, not merged,
  not treated as authoritative.
