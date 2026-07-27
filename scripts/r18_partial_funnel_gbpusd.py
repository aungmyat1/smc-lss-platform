#!/usr/bin/env python3
"""R-18 partial-funnel signal-rate study, GBPUSD only, v1.0.5 parameters.

NOT a full R-18 existence check. Six funnel stages (S3 sweep-reclaim, S7
OTE, S9 LTF confirmation, S10 session gatekeeper, S11 entry window, S12
risk/SL/TP) have no real detection implementation -- see
validation/st_c3/detection.py's module docstring and
reports/validation/st_c3/R18_DETECTION_MODULE_REPORT.md for why. Running
those through validation.st_c3.kernel.run_kernel() with stubbed
always-invalid Evidence would produce a trivially-uninformative
signal_rate=0.0 (every bar rejected at S3 regardless of upstream reality),
not a genuine existence-check result.

Instead, this script independently measures how often the six stages that
ARE implemented (S1 HTF bias, S2 raw sweep, S4 displacement+BOS, S5 BOS
extreme lock, S6 dealing range, S8 FVG/OB) each validate, and how often
they jointly align around the same BOS candidate -- a diagnostic, not a
signal-rate answer to R-18 itself.

Usage: python scripts/r18_partial_funnel_gbpusd.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from smc_engine import load_candles  # noqa: E402

from validation.st_c3 import detection as det  # noqa: E402
from validation.st_c3.evidence import load_spec  # noqa: E402

H4_PATH = ROOT / "data" / "GBPUSD_H4.csv"
M15_PATH = ROOT / "data" / "GBPUSD_M15.csv"


def main():
    spec = load_spec()
    h4 = load_candles(str(H4_PATH))
    m15 = load_candles(str(M15_PATH))
    print(f"Loaded {len(h4)} GBPUSD H4 candles, {len(m15)} GBPUSD M15 candles\n")

    hb = det.htf_bias_params(spec)
    sw = det.sweep_params(spec)
    db = det.displacement_bos_params(spec)
    fv = det.fvg_ob_params(spec)
    k = hb["k"]

    # S1: HTF bias validity as of each M15 bar's corresponding H4 context.
    # Simplification: evaluate HTF bias once, at the end of the H4 series
    # (a single "current" bias context), since precise H4<->M15 causal
    # alignment is a separate concern from this diagnostic's scope.
    bias_events = det.detect_htf_bias_events(h4, k=k)
    htf_bias_ev = det.htf_bias_evidence_at(h4, bias_events, len(h4) - 1, evidence_id="HTF_BIAS-STUDY")
    print(f"S1 HTF bias (as of latest H4 bar): valid={htf_bias_ev.valid}, bias={htf_bias_ev.get('bias')}\n")

    # S4/S5/S6/S8 evaluated per BOS candidate on M15 (the natural anchor
    # linking displacement, extreme-lock, dealing-range, and FVG/OB).
    # Bounded to the first 5,000 M15 bars, sampled every 5th candidate:
    # detection.py's functions each recompute swings/fvgs/order_blocks over
    # the full candle prefix per call (O(n) per call), so an exhaustive
    # pass over all ~10,400 candidates against 30,000 bars is prohibitively
    # slow for a diagnostic script -- this is a bounded sample, not a
    # full-series result, and is reported as such.
    SCAN_LIMIT = 5000
    SAMPLE_STRIDE = 5
    m15_window = m15[:SCAN_LIMIT]
    all_candidates = det.find_bos_candidates(m15_window, k=k)
    candidates = all_candidates[::SAMPLE_STRIDE]
    total = len(candidates)
    print(f"{len(all_candidates)} raw BOS candidates in the first {SCAN_LIMIT} M15 bars "
          f"(k={k}); sampled every {SAMPLE_STRIDE}th -> {total} evaluated\n")

    s4_valid = s5_valid = s6_valid = s8_valid = 0
    all_four_valid = 0
    for event in candidates:
        i = event["i"]
        disp = det.displacement_evidence_for(
            m15_window, event, body_ratio_min=db["body_ratio_min"],
            atr_floor_multiplier=db["atr_floor_multiplier"], evidence_id=f"DISP-{i}",
        )
        bos = det.bos_evidence_for(m15_window, event, confirmation_bars=db["confirmation_bars"], evidence_id=f"BOS-{i}")
        s4_ok = disp.valid and bos.valid
        s4_valid += int(s4_ok)

        extreme = det.bos_extreme_evidence_for(
            m15_window, event, pullback_depth_atr_multiplier=db["pullback_depth_atr_multiplier"],
            window=40, evidence_id=f"EXT-{i}",
        )
        s5_ok = s4_ok and extreme.valid
        s5_valid += int(s5_ok)

        dr = det.dealing_range_evidence_for(m15_window, event, k=k, evidence_id=f"DR-{i}")
        s6_ok = s5_ok and dr.valid
        s6_valid += int(s6_ok)

        fvg = det.fvg_evidence_near(
            m15_window, i, min_gap_atr_multiplier=fv["fvg_min_gap_atr_multiplier"],
            freshness_max_mf_swings=fv["fvg_freshness_max_mf_swings"], k=k, evidence_id=f"FVG-{i}",
        )
        ob = det.order_block_evidence_near(
            m15_window, i, k=k, freshness_max_mf_swings=fv["ob_freshness_max_mf_swings"], evidence_id=f"OB-{i}",
        )
        s8_ok = s6_ok and (fvg.valid or ob.valid)
        s8_valid += int(s8_ok)
        all_four_valid += int(s8_ok)

    print("Per-stage pass counts (cumulative -- each requires all prior stages in this chain to also pass):")
    print(f"  S4 (displacement+BOS, N={db['confirmation_bars']}): {s4_valid}/{total} ({100*s4_valid/total:.1f}%)")
    print(f"  S5 (BOS extreme lock, depth={db['pullback_depth_atr_multiplier']}xATR): {s5_valid}/{total} ({100*s5_valid/total:.1f}%)")
    print(f"  S6 (dealing range): {s6_valid}/{total} ({100*s6_valid/total:.1f}%)")
    print(f"  S8 (FVG/OB, gap={fv['fvg_min_gap_atr_multiplier']}xATR): {s8_valid}/{total} ({100*s8_valid/total:.1f}%)")
    print(f"\nJoint S4+S5+S6+S8 pass rate: {all_four_valid}/{total} ({100*all_four_valid/total:.1f}%)")
    print("\nNOTE: S2 (raw sweep), S1 (HTF bias) not joined into the above chain --")
    print("sweep detection requires a specific bar index, not a BOS-candidate anchor;")
    print("see report for how S1/S2 pass rates are reported separately.")

    # S2: raw sweep pass rate over a sampled window (independent of BOS candidates)
    sample_start, sample_end, sample_stride = 500, 2500, 3
    sweep_valid = 0
    sample_n = 0
    for i in range(sample_start, min(sample_end, SCAN_LIMIT), sample_stride):
        sample_n += 1
        if det.detect_sweep_at(m15_window, i, k=k, evidence_id=f"SWEEP-{i}", **sw).valid:
            sweep_valid += 1
    print(f"\nS2 (raw sweep) pass rate, sampled every {sample_stride}th bar in [{sample_start}:{sample_end}]: "
          f"{sweep_valid}/{sample_n} ({100*sweep_valid/sample_n:.1f}%)")


if __name__ == "__main__":
    main()
