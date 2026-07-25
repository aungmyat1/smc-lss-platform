"""Tests for the pre-registered power-planning helper (tools/power_planning.py)."""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from tools.power_planning import (  # noqa: E402
    estimate_required_bars,
    estimate_required_trades,
    power_plan,
)


def test_estimate_required_trades_matches_known_power_formula():
    # z_{0.025} = 1.95996, z_{0.80} = 0.84162 for the default alpha=0.05/power=0.80.
    # n = ((1.95996 + 0.84162) * 1.0 / 0.3) ** 2 ~= 87.6 -> ceil to 88.
    n = estimate_required_trades(0.3)
    assert n == 88


def test_estimate_required_trades_rejects_non_positive_target():
    with pytest.raises(ValueError):
        estimate_required_trades(0.0)
    with pytest.raises(ValueError):
        estimate_required_trades(-0.1)


def test_estimate_required_trades_rejects_invalid_alpha_power():
    with pytest.raises(ValueError):
        estimate_required_trades(0.3, alpha=0.0)
    with pytest.raises(ValueError):
        estimate_required_trades(0.3, power=1.0)


def test_estimate_required_bars_scales_with_signal_rate():
    assert estimate_required_bars(100, 0.01) == 10000
    assert estimate_required_bars(100, 0.1) == 1000


def test_estimate_required_bars_rejects_zero_signal_rate():
    with pytest.raises(ValueError):
        estimate_required_bars(100, 0.0)


def test_power_plan_combines_both_estimates():
    plan = power_plan(target_expectancy_r=0.3, signals_per_bar=0.002)
    assert plan["required_trades"] == estimate_required_trades(0.3)
    assert plan["required_bars"] == estimate_required_bars(plan["required_trades"], 0.002)
