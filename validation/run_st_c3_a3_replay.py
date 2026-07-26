#!/usr/bin/env python3
"""A3 replay runner: real GBPUSD H4/M15/M3 data through the frozen v1.0.6
ST-C3 funnel via `validation.st_c3.a3_replay_engine`, producing behavioral
and statistical metrics (signal rate, TradePlan lifecycle, RR distribution,
rejection distribution, session distribution).

Authorized by owner decision, 2026-07-26 ("A3 statistical validation —
OPENED" entry in `reports/validation/st_c3/OWNER_DECISION_LOG.md`).
Research tool only — no broker integration, demo, live trading, or Stage B
execution exists here or is authorized by this run.

EURUSD is excluded for the same reason as the R-18 existence check: its
H4/M15 CSVs cover only a few hours, far too little for replay (see
`reports/validation/st_c3/R27_R30_RESEARCH_REPORT.md`).
"""
from __future__ import annotations

import json
from pathlib import Path

from src import smc_engine as engine
from validation.st_c3.a3_replay_engine import run_a3_replay


def main() -> None:
    htf = engine.load_candles("data/GBPUSD_H4.csv")
    mf = engine.load_candles("data/GBPUSD_M15.csv")
    ltf = engine.load_candles("data/GBPUSD_M3.csv")

    result = run_a3_replay(symbol="GBPUSD", htf_candles=htf, mf_candles=mf, ltf_candles=ltf)
    metrics = result["metrics"]

    out_dir = Path("reports/a3")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ST-C3_v1.0.6_GBPUSD_M15_a3_replay.json"
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")

    print(f"Scanned {metrics['bar_count']} M15 bars ({mf[metrics['warmup_bars']]['time']} -> {mf[-1]['time']})")
    print(f"Signals: {metrics['signal_count']} (rate={metrics['signal_rate']:.6f})")
    print(f"TradePlans: {metrics['tradeplan_count']}, closed: {metrics['closed_trade_count']}, "
          f"open-at-end: {metrics['open_at_end_count']}, bias-flip: {metrics['bias_flip_count']}")
    print(f"Win rate: {metrics['win_rate']}, avg RR: {metrics['avg_rr']}")
    print(f"Rejections by code: {metrics['rejections_by_code']}")
    print(f"Session bar counts: {metrics['session_counts']}")
    print(f"Report written to {out_path}")


if __name__ == "__main__":
    main()
