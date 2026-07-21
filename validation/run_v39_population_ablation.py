#!/usr/bin/env python3
"""Runner for the ST-C1 v3.9 population-feasibility ablation (B1 cell).

Produces the JSON evidence behind
reports/audit/ST_C1_V39_POPULATION_ABLATION_SPEC.md's results section.
Research-only: no broker import, no execution side effect.

Usage: python validation/run_v39_population_ablation.py SYMBOL M5_CSV H1_CSV OUT_JSON
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
from validation.historical_replay_engine_v39 import HistoricalReplayEngineV39  # noqa: E402


def run_symbol(symbol: str, m5_path: str, h1_path: str, out_path: str) -> None:
    m5 = e.load_candles(m5_path)
    h1 = e.load_candles(h1_path)
    engine = HistoricalReplayEngineV39()
    t0 = time.time()
    result = engine.replay(m5, h1=h1, symbol=symbol)
    elapsed = time.time() - t0
    payload = {
        "symbol": symbol,
        "cell": "B1_v39_candidate",
        "elapsed_seconds": round(elapsed, 1),
        "m5_bars": len(m5),
        "h1_bars": len(h1),
        "m5_range": [m5[0]["time"], m5[-1]["time"]],
        "funnel_counts": result.funnel_counts,
        "num_signals": len(result.signals),
        "num_trades": len(result.trades),
        "metrics": result.metrics,
        "trades": [
            {
                "signal_time": t.signal_time,
                "entry_time": t.entry_time,
                "exit_time": t.exit_time,
                "direction": t.direction,
                "outcome": t.outcome,
                "gross_r": t.gross_r,
                "cost_r": t.cost_r,
                "net_r": t.net_r,
                "structure_key": t.structure_key,
            }
            for t in result.trades
        ],
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    print(symbol, "elapsed", elapsed, "trades", len(result.trades), "signals", len(result.signals))


if __name__ == "__main__":
    run_symbol(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
