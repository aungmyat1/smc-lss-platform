#!/usr/bin/env python3
"""Pre-registered sample-size / power planning helpers (Lever B).

Given a target expectancy and the observed signal rate from an existence
check (`tools.existence_check`), estimate how many trades and how many bars
of history would be needed to have a reasonable chance of detecting that
edge — before committing to a full A3 statistical-validation run. This
operationalizes `docs/RESEARCH-CHARTER.md`'s pre-registration discipline:
state the expected scale of evidence needed *before* looking at whether a
candidate "worked."

The trade-count estimate is a one-sample z-test power calculation against
R-multiple outcomes (mean R == 0 vs. mean R == target_expectancy_r) — meant
to catch "this candidate can never accumulate enough trades to matter" cheaply,
not to replace the `validation` skill's OOS/walk-forward gates or any Monte
Carlo robustness work.
"""
from __future__ import annotations

import math
from statistics import NormalDist


def estimate_required_trades(
    target_expectancy_r: float,
    *,
    outcome_stdev_r: float = 1.0,
    alpha: float = 0.05,
    power: float = 0.80,
) -> int:
    """Minimum trade count for a one-sample test of H0: mean R == 0 vs.
    H1: mean R == target_expectancy_r, at the given two-sided alpha/power.

    `outcome_stdev_r` is the assumed standard deviation of per-trade R
    outcomes; 1.0R is a conservative default for R-multiple systems with a
    hard stop and no partials. Supply the actual observed stdev from a prior
    candidate's trade log when available instead of the default.
    """
    if target_expectancy_r <= 0:
        raise ValueError("target_expectancy_r must be > 0 to estimate a required sample size")
    if not (0 < alpha < 1) or not (0 < power < 1):
        raise ValueError("alpha and power must both be in (0, 1)")
    dist = NormalDist()
    z_alpha = dist.inv_cdf(1 - alpha / 2)  # two-sided
    z_power = dist.inv_cdf(power)
    n = ((z_alpha + z_power) * outcome_stdev_r / target_expectancy_r) ** 2
    return math.ceil(n)


def estimate_required_bars(trades_needed: int, signals_per_bar: float) -> int:
    """Bars of history needed to accumulate `trades_needed` signals, given the
    observed `signals_per_bar` rate from an existence check
    (`ExistenceCheckResult.to_dict()["signal_rate"]`).
    """
    if trades_needed <= 0:
        raise ValueError("trades_needed must be > 0")
    if signals_per_bar <= 0:
        raise ValueError("signals_per_bar must be > 0 — spec never fires per the existence check")
    return math.ceil(trades_needed / signals_per_bar)


def power_plan(
    target_expectancy_r: float,
    signals_per_bar: float,
    *,
    outcome_stdev_r: float = 1.0,
    alpha: float = 0.05,
    power: float = 0.80,
) -> dict:
    """Convenience wrapper combining both estimates into one report dict,
    matching the shape recorded in a candidate's RCR pre-registration entry.
    """
    required_trades = estimate_required_trades(
        target_expectancy_r,
        outcome_stdev_r=outcome_stdev_r,
        alpha=alpha,
        power=power,
    )
    required_bars = estimate_required_bars(required_trades, signals_per_bar)
    return {
        "target_expectancy_r": target_expectancy_r,
        "outcome_stdev_r": outcome_stdev_r,
        "alpha": alpha,
        "power": power,
        "signals_per_bar": signals_per_bar,
        "required_trades": required_trades,
        "required_bars": required_bars,
    }
