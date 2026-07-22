#!/usr/bin/env python3
"""Runner for the ST-C1 v3.10 net-of-cost read.

Produces the JSON evidence for the "next step" recorded in
reports/audit/ST_C1_V310_REVERSAL_CAPTURE_RCR.md and NEXT_ACTION.md: the
existence check (367 trades total) already passed, but no gross_r/net_r/
profit-factor read had been computed. This reuses the same cost model and
trade-record schema already validated for v3.9
(validation/run_v39_population_ablation.py), against
HistoricalReplayEngineV310. H4 is derived from H1 via smc_engine.resample()
per the RCR addendum's documented data-gap fix (native H4 is
missing/too-short for all three symbols) -- not fabricated data.

Research-only: no broker import, no execution side effect.

Usage: python validation/run_v310_net_of_cost.py SYMBOL M5_CSV H1_CSV D1_CSV OUT_JSON
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
from validation.historical_replay_engine_v310 import HistoricalReplayEngineV310  # noqa: E402

H4_RESAMPLE_FACTOR = 4  # 4 H1 bars -> 1 H4 bar, matching the RCR addendum's fix


def run_symbol(symbol: str, m5_path: str, h1_path: str, d1_path: str, out_path: str) -> None:
    m5 = e.load_candles(m5_path)
    h1 = e.load_candles(h1_path)
    d1 = e.load_candles(d1_path)
    h4 = e.resample(h1, H4_RESAMPLE_FACTOR)
    engine = HistoricalReplayEngineV310()
    t0 = time.time()
    result = engine.replay(m5, h1=h1, d1=d1, h4=h4, symbol=symbol)
    elapsed = time.time() - t0
    payload = {
        "symbol": symbol,
        "cell": "v310_candidate_net_of_cost",
        "elapsed_seconds": round(elapsed, 1),
        "m5_bars": len(m5),
        "h1_bars": len(h1),
        "d1_bars": len(d1),
        "h4_bars_resampled": len(h4),
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
    run_symbol(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
