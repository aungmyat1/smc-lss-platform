#!/usr/bin/env python3
"""Performance metrics for deterministic historical replay results."""
from __future__ import annotations

import math
from statistics import mean, pstdev
from typing import Sequence


def compute_metrics(trade_rs: Sequence[float]) -> dict[str, float | int | None]:
    trades = list(trade_rs)
    total_trades = len(trades)
    wins = [r for r in trades if r > 0]
    losses = [r for r in trades if r < 0]
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    average_r = mean(trades) if trades else None
    expectancy_r = average_r
    win_rate = (len(wins) / total_trades * 100.0) if total_trades else None
    profit_factor = (gross_profit / gross_loss) if gross_loss else (math.inf if wins else None)

    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for r in trades:
        equity += r
        peak = max(peak, equity)
        max_drawdown = min(max_drawdown, equity - peak)

    if total_trades >= 2:
        spread = pstdev(trades)
        sharpe = (mean(trades) / spread) if spread > 0 else None
    else:
        sharpe = None

    return {
        "total_trades": total_trades,
        "win_rate_pct": round(win_rate, 2) if win_rate is not None else None,
        "profit_factor": round(profit_factor, 4) if isinstance(profit_factor, float) and math.isfinite(profit_factor) else profit_factor,
        "expectancy_r": round(expectancy_r, 4) if expectancy_r is not None else None,
        "average_r": round(average_r, 4) if average_r is not None else None,
        "maximum_drawdown_r": round(max_drawdown, 4),
        "sharpe_ratio": round(sharpe, 4) if sharpe is not None else None,
    }
