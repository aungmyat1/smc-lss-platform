"""Synthetic unit tests for `validation.st_c3.a3_replay_engine._simulate_lifecycle`.

Authorized under A3's opened scope (owner decision, 2026-07-26). Requested
because the one real A3 replay run to date (`A3_REPLAY_RESULTS.md`)
produced zero TradePlans, leaving the lifecycle-simulation code entirely
untested against either real or synthetic data — a real gap flagged in
that report.

Tests `_simulate_lifecycle` directly rather than the full `run_a3_replay`
loop, since it is the actual unit of new post-S13 behavior this module
adds (`build_evidence_bundle`/`run_kernel` already have their own
golden/negative-case coverage in `test_golden_cases.py`/`test_negative_cases.py`
at the `run_kernel` level — the same pattern this file follows one level
up the call stack).

Correction against the originally proposed test plan: ST-C3's TP1/TP2/TP3
exits are **partial** (30%/30%/40%, per `ST-C3_BACKTEST_SPEC.md` section
9), not full closes — hitting only TP1 realizes `0.30 * tp1_rr`, not
`tp1_rr` itself. Expected values below reflect that.

Not covered here (out of scope for lifecycle testing, not an oversight):
- Entry-window timing (`EntryWindowEvidence`) is a pre-entry S11 guard,
  already covered by `test_golden_cases.py`/`test_negative_cases.py` — it
  has no role in post-entry lifecycle simulation.
- Chain-frequency counters (sweep->reclaim->BOS, OB/FVG interaction rates)
  are not implemented anywhere yet (see `ST-C3_A3_METRICS_SPEC.md` section
  2.2/6) — there is nothing to test.
"""
from __future__ import annotations

import pytest

from validation.st_c3.a3_replay_engine import _simulate_lifecycle
from validation.st_c3.trade_plan import TradePlan


def _candle(time: str, o: float, h: float, l: float, c: float) -> dict:
    return {"time": time, "open": o, "high": h, "low": l, "close": c}


def _short_history(n: int = 3) -> list[dict]:
    """Deliberately too short for `_htf_bias`'s `2*SWING_K+2=6` floor, so
    `HTFBiasEvidence.valid` is always False and BIAS_FLIP never fires —
    isolates the SL/TP branches in the TP/SL-focused tests below."""
    return [_candle(f"2026-01-01 00:{i:02d}", 1.0, 1.0, 1.0, 1.0) for i in range(n)]


def _long_trade_plan() -> TradePlan:
    return TradePlan(
        strategy_id="ST-C3", direction="LONG",
        context={"htf_bias_id": "HTF_BIAS-TEST"},
        entry={"entry_price": 1.1000, "entry_window_id": "EW-TEST"},
        risk={"sl_price": 1.0950, "risk_per_trade_pct": 0.5, "min_rr_required": 3.0, "computed_rr": 5.0},
        targets={
            "tp1": {"target_id": "TP1-TEST", "target_type": "TP1_INTERNAL", "price": 1.1050, "rr": 1.0},
            "tp2": {"target_id": "TP2-TEST", "target_type": "TP2_EXTERNAL", "price": 1.1150, "rr": 3.0},
            "tp3": {"target_id": "TP3-TEST", "target_type": "TP3_HTF", "price": 1.1250, "rr": 5.0},
        },
        expiry={"rules": ("BIAS_FLIP", "ENTRY_WINDOW", "SL_BREAK", "SUPERSEDED"), "expiry_evidence_id": None},
        evidence_chain=(), status={"state": "VALID", "code": None, "reason": None},
        meta={"tf_stack": ("H4", "M15", "M3", "M1"), "session": "LONDON", "provenance": "TEST"},
    )


def test_tp1_only_hit_partial_close_open_at_end():
    plan = _long_trade_plan()
    mf = [
        _candle("2026-01-01 07:00", 1.1000, 1.1000, 1.1000, 1.1000),  # entry bar, i=0
        _candle("2026-01-01 07:15", 1.1000, 1.1055, 1.1000, 1.1050),  # TP1 touched (high>=1.1050)
        _candle("2026-01-01 07:30", 1.1050, 1.1050, 1.1050, 1.1050),  # flat, data ends here
    ]
    result = _simulate_lifecycle(plan, mf, _short_history(), _short_history(), spec=None,
                                  entry_index=0, max_hold_bars=10)

    assert result.termination == "OPEN_AT_DATA_END"
    assert [h.target for h in result.hits] == ["TP1"]
    assert result.remaining_fraction == pytest.approx(0.70)
    assert result.realized_rr == pytest.approx(0.30 * 1.0)
    assert result.unrealized_rr == pytest.approx(0.70 * 1.0)  # (1.1050-1.1000)/0.0050 = 1.0
    assert not result.sl_hit
    assert result.bias_flip_index is None


def test_all_targets_hit_full_closure():
    plan = _long_trade_plan()
    mf = [
        _candle("2026-01-01 07:00", 1.1000, 1.1000, 1.1000, 1.1000),
        _candle("2026-01-01 07:15", 1.1000, 1.1055, 1.1000, 1.1050),  # TP1
        _candle("2026-01-01 07:30", 1.1050, 1.1155, 1.1050, 1.1140),  # TP2
        _candle("2026-01-01 07:45", 1.1140, 1.1255, 1.1140, 1.1200),  # TP3
    ]
    result = _simulate_lifecycle(plan, mf, _short_history(), _short_history(), spec=None,
                                  entry_index=0, max_hold_bars=10)

    assert result.termination == "ALL_TARGETS_HIT"
    assert [h.target for h in result.hits] == ["TP1", "TP2", "TP3"]
    assert result.remaining_fraction == pytest.approx(0.0, abs=1e-9)
    assert result.realized_rr == pytest.approx(0.30 * 1.0 + 0.30 * 3.0 + 0.40 * 5.0)  # 3.2
    assert result.bars_held == 3
    assert not result.sl_hit


def test_sl_hit_immediately_no_targets():
    plan = _long_trade_plan()
    mf = [
        _candle("2026-01-01 07:00", 1.1000, 1.1000, 1.1000, 1.1000),
        _candle("2026-01-01 07:15", 1.1000, 1.1010, 1.0940, 1.0945),  # low<=SL (1.0950)
    ]
    result = _simulate_lifecycle(plan, mf, _short_history(), _short_history(), spec=None,
                                  entry_index=0, max_hold_bars=10)

    assert result.termination == "SL_HIT"
    assert result.sl_hit
    assert result.sl_hit_index == 1
    assert result.hits == ()
    assert result.remaining_fraction == 0.0
    assert result.realized_rr == -1.0


def test_partial_tp1_then_sl_hit():
    plan = _long_trade_plan()
    mf = [
        _candle("2026-01-01 07:00", 1.1000, 1.1000, 1.1000, 1.1000),
        _candle("2026-01-01 07:15", 1.1000, 1.1055, 1.1000, 1.1050),  # TP1 hit, 30% closed
        _candle("2026-01-01 07:30", 1.1050, 1.1060, 1.0940, 1.0945),  # remaining 70% stopped out
    ]
    result = _simulate_lifecycle(plan, mf, _short_history(), _short_history(), spec=None,
                                  entry_index=0, max_hold_bars=10)

    assert result.termination == "SL_HIT"
    assert [h.target for h in result.hits] == ["TP1"]
    assert result.remaining_fraction == pytest.approx(0.0, abs=1e-9)
    assert result.realized_rr == pytest.approx(0.30 * 1.0 - 0.70)  # 0.3 - 0.7 = -0.4


def _zigzag_candles(pivots: list[float], bars_per_leg: int, start_time: str, step_minutes: int) -> list[dict]:
    """Build a synthetic OHLC series whose only local extrema are exactly
    `pivots[1:]`, each confirmable as a swing high/low by `smc_engine.swings(k=2)`
    once a window extends `bars_per_leg` bars past it (`bars_per_leg` must be
    >= the swing-detection `k`). Legs are monotonic with no wicks, so each
    pivot bar is a strict local max/min relative to its `bars_per_leg`
    neighbors on both sides.
    """
    from datetime import datetime, timedelta

    t0 = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
    candles = [_candle(t0.strftime("%Y-%m-%d %H:%M"), pivots[0], pivots[0], pivots[0], pivots[0])]
    prev_close = pivots[0]
    bar_i = 1
    for leg_start, leg_end in zip(pivots, pivots[1:]):
        for step in range(1, bars_per_leg + 1):
            close = leg_start + (leg_end - leg_start) * (step / bars_per_leg)
            open_ = prev_close
            high, low = (close, open_) if close >= open_ else (open_, close)
            t = t0 + timedelta(minutes=step_minutes * bar_i)
            candles.append(_candle(t.strftime("%Y-%m-%d %H:%M"), open_, high, low, close))
            prev_close = close
            bar_i += 1
    return candles


def test_bias_flip_terminates_before_any_sl_tp_touch():
    """SHORT TradePlan; price never moves (flat at entry), so SL/TP are
    never touched. `htf_candles` is a zigzag engineered so `smc_engine.trend()`
    reads BEARISH/RANGING through bar 19, then BULLISH from bar 20 on —
    for a SHORT trade that is a flip, and `_simulate_lifecycle` must
    terminate there with no SL/TP interpretation.

    `htf_candles` shares `mf_candles`' exact timestamps purely so this
    test's bisect-based as-of lookup advances one-for-one with the replay
    loop's bar index — a simplification for isolating the flip-detection
    branch, not a claim about real H4/M15 cadence.
    """
    pivots = [1.2000, 1.2050, 1.1950, 1.2020, 1.1900, 1.2100, 1.2000, 1.2000]
    htf = _zigzag_candles(pivots, bars_per_leg=3, start_time="2026-01-01 00:00", step_minutes=15)
    mf = [
        _candle(htf[i]["time"], 1.5000, 1.5000, 1.5000, 1.5000) for i in range(len(htf))
    ]
    plan = TradePlan(
        strategy_id="ST-C3", direction="SHORT",
        context={"htf_bias_id": "HTF_BIAS-TEST"},
        entry={"entry_price": 1.5000, "entry_window_id": "EW-TEST"},
        risk={"sl_price": 1.5100, "risk_per_trade_pct": 0.5, "min_rr_required": 3.0, "computed_rr": 3.0},
        targets={
            "tp1": {"target_id": "TP1-TEST", "target_type": "TP1_INTERNAL", "price": 1.4900, "rr": 1.0},
            "tp2": {"target_id": "TP2-TEST", "target_type": "TP2_EXTERNAL", "price": 1.4800, "rr": 2.0},
            "tp3": {"target_id": "TP3-TEST", "target_type": "TP3_HTF", "price": 1.4700, "rr": 3.0},
        },
        expiry={"rules": ("BIAS_FLIP", "ENTRY_WINDOW", "SL_BREAK", "SUPERSEDED"), "expiry_evidence_id": None},
        evidence_chain=(), status={"state": "VALID", "code": None, "reason": None},
        meta={"tf_stack": ("H4", "M15", "M3", "M1"), "session": "NY", "provenance": "TEST"},
    )

    result = _simulate_lifecycle(plan, mf, htf, _short_history(), spec=None,
                                  entry_index=1, max_hold_bars=25)

    assert result.termination == "BIAS_FLIP"
    assert result.bias_flip_index == 20
    assert not result.sl_hit
    assert result.hits == ()
    assert result.realized_rr == 0.0
    assert result.unrealized_rr == 0.0  # price never moved from entry
