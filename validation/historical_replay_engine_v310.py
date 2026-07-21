#!/usr/bin/env python3
"""Deterministic historical replay engine for ST-C1 v3.10 ("Reversal Capture").

Wires src/signal_v310.py (H4 bias-divergence-gated E1/E2/E3 reversal
detection) into the same, already-validated cost/fill/trade-management
machinery reused by validation/historical_replay_engine_v39.py (itself
reused from validation/historical_replay_engine.py). The only new plumbing
here is H4 window bounding, since no prior spec version in this repo used
a fourth timeframe.

Point-in-time discipline: identical posture to the v3.9 replay engine — all
windows (M5/H1/D1/H4) are bounded by calendar time relative to the decision
timestamp, never by raw list length, so no bar after the decision point is
ever visible.

Never imports or calls a broker-order path. Research-only.
"""
from __future__ import annotations

import datetime as dt
import sys
from bisect import bisect_right
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import smc_engine as e  # noqa: E402
import signal_v310 as v310  # noqa: E402
from symbol_metadata import resolve_symbol, symbol_snapshot  # noqa: E402

from validation.historical_replay_engine import (  # noqa: E402
    CandidateRecord,
    SignalRecord,
    TradeRecord,
    ReplayResult,
    _assert_chronological,
    _load_cost_profile,
    _lookup_cost_profile,
    _parse_time,
    _window,
)
from validation.performance_metrics import compute_metrics  # noqa: E402

TIMEFRAME_DELTA_V310 = {
    "M5": dt.timedelta(minutes=5),
    "H1": dt.timedelta(hours=1),
    "H4": dt.timedelta(hours=4),
    "D1": dt.timedelta(days=1),
}


class HistoricalReplayEngineV310:
    """Point-in-time replay for specs/v3.10.yaml / ST-C1_v1.3.0.yaml."""

    def __init__(
        self,
        contract_path: str = "strategies/candidates/ST-C1_v1.3.0.yaml",
        min_rr: float = 3.0,
        warmup_bars: int = 350,
        cost_profile_path: str | None = None,
    ) -> None:
        self.contract_path = contract_path
        self.min_rr = min_rr
        self.warmup_bars = warmup_bars
        self.cost_profile = _load_cost_profile(cost_profile_path)
        self.metadata_snapshot = symbol_snapshot()
        self._timeline_cache: dict[int, Any] = {}
        self._e_trigger_cache: dict[tuple, Any] = {}

    def _build_timeline(self, candles: list[dict[str, Any]], timeframe: str):
        delta = TIMEFRAME_DELTA_V310.get(timeframe.upper())
        if delta is None:
            raise ValueError(f"unsupported timeframe: {timeframe}")
        times = tuple(_parse_time(c["time"]) for c in candles)
        return tuple(t + delta for t in times)

    def _available_index(self, candles: list[dict[str, Any]], timeframe: str, asof: str) -> int:
        key = id(candles)
        close_times = self._timeline_cache.get(key)
        if close_times is None:
            close_times = self._build_timeline(candles, timeframe)
            self._timeline_cache[key] = close_times
        cutoff = _parse_time(asof)
        idx = bisect_right(close_times, cutoff) - 1
        return min(idx, len(close_times) - 1)

    def _bounded_context_window(self, candles, timeframe, asof, lookback_bars):
        if not candles:
            return []
        available = self._available_index(candles, timeframe, asof)
        if available < 0:
            return []
        start = max(0, available - max(1, lookback_bars) + 1)
        return candles[start: available + 1]

    def _metadata_for_symbol(self, symbol: str | None):
        if not symbol:
            return resolve_symbol("EURUSD")
        try:
            return resolve_symbol(symbol)
        except KeyError:
            return resolve_symbol("EURUSD")

    def _cost_to_r(self, symbol, entry, stop):
        meta = self._metadata_for_symbol(symbol)
        profile = _lookup_cost_profile(symbol or meta.canonical_symbol, meta.asset_class, self.cost_profile)
        risk = abs(entry - stop)
        if risk <= 0:
            raise ValueError("invalid zero-risk trade")
        point_size = float(meta.point_size)
        pip_size = float(meta.pip_size)
        spread_points = float(profile.get("spread_points", 25.0))
        slippage_points = float(profile.get("slippage_points", 3.0))
        commission_usd_round_turn = float(profile.get("commission_per_lot_usd_round_turn", 0.0))
        spread_price = spread_points * point_size
        slippage_price_per_side = slippage_points * point_size
        slippage_price_round_trip = slippage_price_per_side * 2.0
        spread_r = spread_price / risk
        slippage_r = slippage_price_round_trip / risk
        commission_r = commission_usd_round_turn / (risk * meta.contract_size) if meta.contract_size > 0 else 0.0
        price_cost_round_trip = spread_price + slippage_price_round_trip
        total_cost_r = spread_r + slippage_r + commission_r
        return meta, {
            "spread_price": round(spread_price, 10), "spread_points": spread_points,
            "spread_pips": round(spread_price / pip_size, 10) if pip_size else 0.0,
            "entry_slippage_price": round(slippage_price_per_side, 10),
            "exit_slippage_price": round(slippage_price_per_side, 10),
            "slippage_price_round_trip": round(slippage_price_round_trip, 10),
            "commission_usd_round_turn": round(commission_usd_round_turn, 10),
            "commission": round(commission_usd_round_turn, 10),
            "spread_r": round(spread_r, 10), "slippage_r": round(slippage_r, 10),
            "commission_r": round(commission_r, 10), "swap_r": 0.0,
            "price_cost_round_trip": round(price_cost_round_trip, 10),
            "total_cost": round(price_cost_round_trip, 10), "total_cost_r": round(total_cost_r, 10),
        }

    def generate_signal(
        self, index, m5, h1=None, d1=None, h4=None, *,
        symbol=None, rejected_candidates=None, funnel_counts=None,
    ):
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
        m5_window = _window(m5, index, 300)
        asof_time = m5[index + 1]["time"] if index + 1 < len(m5) else m5_window[-1]["time"]
        h1_lookback = max(v310.E2_POI_MAX_AGE_H1_BARS, v310.E3_RANGE_LOOKBACK_H1_BARS,
                          v310.E1_REACTION_WINDOW_H1_BARS) + 5
        d1_lookback = v310.E1_GAP_MAX_AGE_D1_BARS + 5
        h4_lookback = v310.TREND_BIAS_H4_BARS + 5

        h1_available_idx = self._available_index(h1, "H1", asof_time) if h1 else -1
        cache_key = (h1_available_idx,)
        if h1 is not None:
            if cache_key not in self._e_trigger_cache:
                h1_win = self._bounded_context_window(h1, "H1", asof_time, h1_lookback)
                d1_win = self._bounded_context_window(d1, "D1", asof_time, d1_lookback) if d1 else None
                h4_win = self._bounded_context_window(h4, "H4", asof_time, h4_lookback) if h4 else None
                self._e_trigger_cache[cache_key] = (
                    v310.detect_e_trigger(h1_win, d1=d1_win, h4=h4_win) if h1_win else None
                )
            if self._e_trigger_cache[cache_key] is None:
                reject("signal", "no qualifying reversal E-trigger")
                return None
            h1_window = self._bounded_context_window(h1, "H1", asof_time, h1_lookback)
            d1_window = self._bounded_context_window(d1, "D1", asof_time, d1_lookback) if d1 else None
            h4_window = self._bounded_context_window(h4, "H4", asof_time, h4_lookback) if h4 else None
        else:
            h1_window = d1_window = h4_window = None

        result = v310.analyze(symbol_name, m5_window, h1=h1_window, d1=d1_window, h4=h4_window, min_rr=self.min_rr)
        if result.get("decision") != "SIGNAL":
            reject("signal", str(result.get("reason", result.get("decision", "no signal"))))
            return None
        bump("signal_pass")

        direction = "long" if result["direction"] == "BUY" else "short"
        entry = m5[index + 1]["open"] if index + 1 < len(m5) else None
        if entry is None:
            reject("fill", "no next bar available for next-bar-open entry")
            return None
        stop = result["stop"]
        target = result["primary_tp"]
        if target is None:
            reject("target", "REJECT_NO_TARGET")
            return None
        risk = abs(entry - stop)
        if risk <= 0:
            reject("risk", "zero or negative risk at actual fill price")
            return None
        bump("candidate_ready")

        structure_key = str(result.get("structure_key"))
        return SignalRecord(
            index=index, time=m5_window[-1]["time"], direction=direction,
            entry=round(entry, 5), stop=round(stop, 5), target=round(target, 5),
            structure_key=structure_key,
            reason_codes=(f"E_TRIGGER_{result['e_trigger']}", f"M_MODEL_{result['m_model']}", "H4_DIVERGENCE_OK"),
            canonical_symbol=self._metadata_for_symbol(symbol_name).canonical_symbol,
            source_symbol=symbol_name,
        )

    def _crosses_weekend_gap(self, ts, next_ts):
        d1 = _parse_time(ts).date()
        d2 = _parse_time(next_ts).date()
        return (d2 - d1).days >= 2

    def simulate_trade(self, signal, m5, entry_index, symbol=None):
        forward = m5[entry_index:]
        if not forward:
            raise ValueError("no forward candles available for trade simulation")
        direction = signal.direction
        risk = abs(signal.entry - signal.stop)
        if risk <= 0:
            raise ValueError("invalid zero-risk trade")
        meta, cost = self._cost_to_r(symbol, signal.entry, signal.stop)
        exit_price = forward[-1]["close"]
        exit_index = len(m5) - 1
        outcome = "TIMEOUT"
        partial_taken = False
        break_even_activated = False
        ambiguous_bar = False
        unresolved_open_position = False
        management_events: list[dict[str, Any]] = []
        one_r_level = signal.entry + risk if direction == "long" else signal.entry - risk
        current_stop = signal.stop

        for offset, candle in enumerate(forward):
            hit_stop = candle["low"] <= current_stop if direction == "long" else candle["high"] >= current_stop
            hit_target = candle["high"] >= signal.target if direction == "long" else candle["low"] <= signal.target
            hit_one_r = candle["high"] >= one_r_level if direction == "long" else candle["low"] <= one_r_level
            if hit_stop and hit_target:
                ambiguous_bar = True
                exit_price, exit_index, outcome = current_stop, entry_index + offset, "STOP"
                break
            if hit_stop:
                exit_price, exit_index, outcome = current_stop, entry_index + offset, "STOP"
                break
            if hit_target:
                exit_price, exit_index, outcome = signal.target, entry_index + offset, "TARGET"
                break
            if offset + 1 < len(forward) and self._crosses_weekend_gap(candle["time"], forward[offset + 1]["time"]):
                exit_price, exit_index, outcome = candle["close"], entry_index + offset, "WEEKEND_EXIT"
                management_events.append({"event": "WEEKEND_EXIT", "bar": offset})
                break
            if hit_one_r and not partial_taken:
                partial_taken = True
                break_even_activated = True
                current_stop = signal.entry
                management_events.append({"event": "+1R_REACHED", "bar": offset})
                management_events.append({"event": "PARTIAL_TAKEN", "fraction": 0.5, "bar": offset})
                management_events.append({"event": "BREAK_EVEN_ACTIVATED", "new_stop": round(signal.entry, 5), "bar": offset})
        else:
            unresolved_open_position = True
            outcome = "CENSORED_END_OF_DATA"
            management_events.append({"event": "CENSORED_END_OF_DATA", "bar": len(forward) - 1})

        final_leg_r = ((exit_price - signal.entry) / risk) if direction == "long" else ((signal.entry - exit_price) / risk)
        gross_r = (0.5 * 1.0 + 0.5 * final_leg_r) if partial_taken else final_leg_r
        net_r = gross_r - cost["total_cost_r"]
        return TradeRecord(
            signal_index=signal.index, signal_time=signal.time,
            entry_index=entry_index, entry_time=m5[entry_index]["time"],
            exit_index=exit_index, exit_time=m5[exit_index]["time"],
            direction=direction, entry=round(signal.entry, 5), stop=round(signal.stop, 5),
            target=round(signal.target, 5), exit_price=round(exit_price, 5),
            gross_r=round(gross_r, 6), cost_r=round(cost["total_cost_r"], 6), net_r=round(net_r, 6),
            outcome=outcome, structure_key=signal.structure_key, symbol_metadata_version=meta.version,
            partial_taken=partial_taken, break_even_activated=break_even_activated,
            ambiguous_bar=ambiguous_bar, unresolved_open_position=unresolved_open_position,
            management_events=tuple(management_events), **cost,
        )

    def replay(self, m5, h1=None, d1=None, h4=None, symbol="ST-C1"):
        _assert_chronological(m5, "<m5>")
        if h1:
            _assert_chronological(h1, "<h1>")
        if d1:
            _assert_chronological(d1, "<d1>")
        if h4:
            _assert_chronological(h4, "<h4>")

        signals: list[SignalRecord] = []
        trades: list[TradeRecord] = []
        rejected_candidates: list[CandidateRecord] = []
        funnel_counts: dict[str, int] = {
            "evaluated": 0, "signal_pass": 0, "candidate_ready": 0,
            "duplicate_structure": 0, "executed_trade": 0,
        }
        consumed: set[str] = set()
        i = self.warmup_bars
        while i < len(m5) - 1:
            signal = self.generate_signal(
                i, m5, h1=h1, d1=d1, h4=h4, symbol=symbol,
                rejected_candidates=rejected_candidates, funnel_counts=funnel_counts,
            )
            if signal is None:
                i += 1
                continue
            if signal.structure_key in consumed:
                funnel_counts["duplicate_structure"] = int(funnel_counts.get("duplicate_structure", 0)) + 1
                i += 1
                continue
            consumed.add(signal.structure_key)
            signals.append(signal)
            trade = self.simulate_trade(signal, m5, entry_index=i + 1, symbol=symbol)
            trades.append(trade)
            funnel_counts["executed_trade"] = int(funnel_counts.get("executed_trade", 0)) + 1
            i = max(trade.exit_index + 1, i + 1)

        assert funnel_counts["executed_trade"] == len(trades)
        return ReplayResult(
            contract_path=self.contract_path, symbol=symbol,
            status="READY_FOR_STATISTICAL_VALIDATION",
            caveat=None if trades else "No trades were generated on the supplied replay data.",
            signals=tuple(signals), trades=tuple(trades),
            rejected_candidates=tuple(rejected_candidates),
            management_events=tuple(ev for trade in trades for ev in trade.management_events),
            funnel_counts=dict(funnel_counts), metrics=compute_metrics([t.net_r for t in trades]),
            assumptions={
                "entry": "next candle after signal (confirmation_close_next_bar_open)",
                "exit": "stop-first conservative fills, +1R partial/break-even, weekend force-exit",
                "strategy_id": "ST-C1", "strategy_version": "1.3.0", "spec_version": "3.10",
            },
            symbol_metadata=self._metadata_for_symbol(symbol).snapshot(),
        )

    def run_from_paths(self, m5_path, h1_path=None, d1_path=None, h4_path=None, symbol="ST-C1"):
        m5 = e.load_candles(m5_path)
        h1 = e.load_candles(h1_path) if h1_path else None
        d1 = e.load_candles(d1_path) if d1_path else None
        h4 = e.load_candles(h4_path) if h4_path else None
        return self.replay(m5, h1=h1, d1=d1, h4=h4, symbol=symbol)
