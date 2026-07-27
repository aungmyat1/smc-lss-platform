#!/usr/bin/env python3
"""S1-G4 structural consistency across symbols -- data-availability check
plus a small structural summary for every symbol with sufficient H4/M15
data. Demonstrates validation/st_c3/detection.py is symbol-agnostic (it
takes candle lists directly, no hardcoded symbol strings) rather than
GBPUSD-specific code with GBPUSD hardcoded into it.

Only R-02's active instruments (EURUSD, GBPUSD) are in scope; XAUUSD is
excluded per R-02's v1.0.3 revision.

Usage: python scripts/s1_g4_structural_consistency.py
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

MIN_ROWS_FOR_STUDY = 1000  # below this, no distribution/structural claim is meaningful

SYMBOLS = {
    "EURUSD": {"h4": "data/EURUSD_H4.csv", "m15": "data/EURUSD_M15.csv"},
    "GBPUSD": {"h4": "data/GBPUSD_H4.csv", "m15": "data/GBPUSD_M15.csv"},
}


def row_count(path: Path) -> int:
    with open(path, encoding="utf-8") as f:
        return sum(1 for _ in f) - 1  # minus header


def structural_summary(symbol: str, h4_path: Path, m15_path: Path, spec: dict) -> dict:
    h4 = load_candles(str(h4_path))
    m15 = load_candles(str(m15_path))
    k = det.htf_bias_params(spec)["k"]

    bias_events = det.detect_htf_bias_events(h4, k=k)
    bias_ev = det.htf_bias_evidence_at(h4, bias_events, len(h4) - 1, evidence_id=f"{symbol}-BIAS")

    candidates = det.find_bos_candidates(m15, k=k)
    db = det.displacement_bos_params(spec)
    fv = det.fvg_ob_params(spec)
    sample = candidates[:: max(1, len(candidates) // 500)][:500]  # bounded sample, same discipline as R18 study

    s5_pass = 0
    for event in sample:
        disp = det.displacement_evidence_for(
            m15, event, body_ratio_min=db["body_ratio_min"],
            atr_floor_multiplier=db["atr_floor_multiplier"], evidence_id="X",
        )
        bos = det.bos_evidence_for(m15, event, confirmation_bars=db["confirmation_bars"], evidence_id="X")
        if not (disp.valid and bos.valid):
            continue
        extreme = det.bos_extreme_evidence_for(
            m15, event, pullback_depth_atr_multiplier=db["pullback_depth_atr_multiplier"],
            window=40, evidence_id="X",
        )
        if extreme.valid:
            s5_pass += 1

    return {
        "symbol": symbol,
        "h4_bars": len(h4),
        "m15_bars": len(m15),
        "htf_bias_valid": bias_ev.valid,
        "htf_bias": bias_ev.get("bias"),
        "bos_candidates": len(candidates),
        "sample_size": len(sample),
        "s4_s5_pass_rate": s5_pass / len(sample) if sample else None,
    }


def main():
    spec = load_spec()
    print("=== S1-G4 data-availability check ===\n")
    for symbol, paths in SYMBOLS.items():
        h4_rows = row_count(ROOT / paths["h4"])
        m15_rows = row_count(ROOT / paths["m15"])
        sufficient = h4_rows >= MIN_ROWS_FOR_STUDY and m15_rows >= MIN_ROWS_FOR_STUDY
        print(f"{symbol}: H4={h4_rows} rows, M15={m15_rows} rows -> "
              f"{'SUFFICIENT' if sufficient else 'INSUFFICIENT'} (threshold={MIN_ROWS_FOR_STUDY})")

    print("\n=== Structural summary (symbols with sufficient data only) ===\n")
    for symbol, paths in SYMBOLS.items():
        h4_rows = row_count(ROOT / paths["h4"])
        m15_rows = row_count(ROOT / paths["m15"])
        if h4_rows < MIN_ROWS_FOR_STUDY or m15_rows < MIN_ROWS_FOR_STUDY:
            print(f"{symbol}: SKIPPED (insufficient data)")
            continue
        result = structural_summary(symbol, ROOT / paths["h4"], ROOT / paths["m15"], spec)
        print(f"{symbol}: {result}")


if __name__ == "__main__":
    main()
