#!/usr/bin/env python3
"""B0 control run for the ST-C1 v3.9 population-feasibility ablation:
v3.6 (signal_v35.py) unchanged, wired into the same replay wrapper
machinery as HistoricalReplayEngineV39, so the ONLY difference from the
B1 (v3.9) run is the detection module itself (E1 enabled, wick-ratio
filters at v3.6 defaults, ATR-gated displacement).

signal_v35.py is treated as an immutable historical control per the RCR
(reports/audit/ST_C1_V39_CLEAN_SMC_RCR.md) and is not modified here or
anywhere in this task -- including not adding a min_rr passthrough to its
analyze()/generate_signal() call path. This means v3.6's own historical
min_rr default (2.0, baked into signal_v35.generate_signal's default
argument) is used for this control, NOT v3.9's 3.0 floor. That is a real,
disclosed asymmetry between B0 and B1 beyond the three named relaxations --
reported as such in reports/audit/ST_C1_V39_POPULATION_ABLATION_SPEC.md,
not hidden -- since changing it would require editing the immutable
control file.

Usage: python validation/run_v36_control_ablation.py SYMBOL M5_CSV H1_CSV OUT_JSON
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import smc_engine as e  # noqa: E402
import signal_v35 as v35  # noqa: E402
from validation.historical_replay_engine_v39 import HistoricalReplayEngineV39  # noqa: E402
from validation.historical_replay_engine import CandidateRecord, SignalRecord  # noqa: E402


class HistoricalReplayEngineV36Control(HistoricalReplayEngineV39):
    def generate_signal(self, index, m5, h1=None, *, symbol=None,
                        rejected_candidates=None, funnel_counts=None):
        if index < self.warmup_bars:
            return None
        symbol_name = symbol or self._metadata_for_symbol(None).canonical_symbol

        def bump(key, amount=1):
            if funnel_counts is not None:
                funnel_counts[key] = int(funnel_counts.get(key, 0)) + amount

        def reject(stage, reason):
            bump(f"rejected_{stage}")
            if rejected_candidates is not None:
                rejected_candidates.append(CandidateRecord(
                    signal_time=m5[index]["time"], stage=stage, direction="unknown",
                    structure_key=None, rejection_reason=reason, symbol=symbol_name, metadata={},
                ))

        bump("evaluated")
        m5_window = m5[max(0, index - 300 + 1): index + 1]
        asof_time = m5[index + 1]["time"] if index + 1 < len(m5) else m5_window[-1]["time"]
        h1_lookback = max(v35.E2_POI_MAX_AGE_H1_BARS, v35.E3_RANGE_LOOKBACK_H1_BARS,
                          v35.E1_GAP_MAX_AGE_D1_BARS * 24) + 5
        h1_window = self._bounded_context_window(h1, "H1", asof_time, h1_lookback) if h1 else None
        d1_window = None  # E1 rarely reachable without D1 data in this control; matches B1's no-D1 posture

        result = v35.analyze(symbol_name, m5_window, h1=h1_window, d1=d1_window)
        if result.get("decision") != "SIGNAL":
            reject("signal", str(result.get("reason", result.get("decision", "no signal"))))
            return None
        bump("signal_pass")
        direction = "long" if result["direction"] == "BUY" else "short"
        entry = m5[index + 1]["open"] if index + 1 < len(m5) else None
        if entry is None:
            reject("fill", "no next bar")
            return None
        stop = result["stop"]
        target = result["primary_tp"]
        if target is None:
            reject("target", "REJECT_NO_TARGET")
            return None
        risk = abs(entry - stop)
        if risk <= 0:
            reject("risk", "zero or negative risk")
            return None
        bump("candidate_ready")
        structure_key = str(result.get("structure_key"))
        return SignalRecord(
            index=index, time=m5_window[-1]["time"], direction=direction,
            entry=round(entry, 5), stop=round(stop, 5), target=round(target, 5),
            structure_key=structure_key, reason_codes=(f"E_TRIGGER_{result['e_trigger']}", f"M_MODEL_{result['m_model']}"),
            canonical_symbol=self._metadata_for_symbol(symbol_name).canonical_symbol,
            source_symbol=symbol_name,
        )


def run_symbol(symbol: str, m5_path: str, h1_path: str, out_path: str) -> None:
    m5 = e.load_candles(m5_path)
    h1 = e.load_candles(h1_path)
    engine = HistoricalReplayEngineV36Control()
    t0 = time.time()
    result = engine.replay(m5, h1=h1, symbol=symbol)
    elapsed = time.time() - t0
    payload = {
        "symbol": symbol, "cell": "B0_v36_control",
        "elapsed_seconds": round(elapsed, 1),
        "m5_bars": len(m5), "h1_bars": len(h1),
        "funnel_counts": result.funnel_counts,
        "num_signals": len(result.signals), "num_trades": len(result.trades),
        "metrics": result.metrics,
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    print(symbol, "elapsed", elapsed, "trades", len(result.trades))


if __name__ == "__main__":
    run_symbol(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
