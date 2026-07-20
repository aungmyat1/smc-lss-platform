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
    drawdown_duration = 0
    longest_drawdown_duration = 0
    for r in trades:
        equity += r
        peak = max(peak, equity)
        if equity < peak:
            drawdown_duration += 1
            longest_drawdown_duration = max(longest_drawdown_duration, drawdown_duration)
        else:
            drawdown_duration = 0
        max_drawdown = min(max_drawdown, equity - peak)

    if total_trades >= 2:
        spread = pstdev(trades)
        sharpe = (mean(trades) / spread) if spread > 0 else None
        downside = [r for r in trades if r < 0]
        sortino = (mean(trades) / pstdev(downside)) if len(downside) >= 2 and pstdev(downside) > 0 else None
    else:
        sharpe = None
        sortino = None

    recovery_factor = (equity / abs(max_drawdown)) if max_drawdown < 0 else (math.inf if equity > 0 else None)
    payoff_ratio = (mean(wins) / abs(mean(losses))) if wins and losses else None

    return {
        "total_trades": total_trades,
        "wins": len(wins),
        "losses": len(losses),
        "win_rate_pct": round(win_rate, 2) if win_rate is not None else None,
        "profit_factor": round(profit_factor, 4) if isinstance(profit_factor, float) and math.isfinite(profit_factor) else profit_factor,
        "expectancy_r": round(expectancy_r, 4) if expectancy_r is not None else None,
        "average_r": round(average_r, 4) if average_r is not None else None,
        "gross_profit_r": round(gross_profit, 4),
        "gross_loss_r": round(gross_loss, 4),
        "net_profit_r": round(equity, 4),
        "maximum_drawdown_r": round(max_drawdown, 4),
        "drawdown_duration_trades": longest_drawdown_duration or None,
        "sharpe_ratio": round(sharpe, 4) if sharpe is not None else None,
        "sortino_ratio": round(sortino, 4) if sortino is not None else None,
        "recovery_factor": round(recovery_factor, 4) if isinstance(recovery_factor, float) and math.isfinite(recovery_factor) else recovery_factor,
        "payoff_ratio": round(payoff_ratio, 4) if payoff_ratio is not None else None,
        "total_R": round(equity, 4),
        "longest_win_streak": _longest_streak(trades, positive=True),
        "longest_loss_streak": _longest_streak(trades, positive=False),
        "trade_count_adequacy_warning": total_trades < 30,
        "mae_distribution": None,
        "mfe_distribution": None,
        "cost_drag_r": None,
    }


def _longest_streak(trades: Sequence[float], positive: bool) -> int | None:
    if not trades:
        return None
    longest = current = 0
    for r in trades:
        if (r > 0) == positive:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest
