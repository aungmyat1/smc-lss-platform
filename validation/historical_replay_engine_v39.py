#!/usr/bin/env python3
"""Deterministic historical replay engine for ST-C1 v3.9 ("Clean SMC").

Wires src/signal_v39.py (the v3.9-parameterized E1/E2/E3+M1/M2/M3 detection
engine — NOT the parked v3.7 G1-G10 pipeline) into the existing, already-
validated cost/fill/trade-management machinery from
validation/historical_replay_engine.py, reused here rather than
reimplemented (conformance matrix: cost model / gross-vs-net RR / break-
even+partial management are VERIFIED and reusable; only v3.9-aware
*detection* was missing).

Point-in-time discipline: every window passed to signal_v39.analyze() is
bounded by _bounded_context_window()/_available_index() (imported from the
v3.6 replay engine, generic and reused as-is) so no bar after the decision
timestamp is ever visible. Entry is next-bar-open after the signal bar
closes, matching specs/v3.9.yaml's `entry.type: confirmation_close_next_bar_open`.

Adds v3.9-specific behavior absent from the v3.6 replay engine: a weekend
force-exit (specs/v3.9.yaml trade_management.weekend_exit/forced_exit are
`true`, but time_stop is disabled — per the conformance matrix's resolved
reading, the only remaining forced-exit condition is the weekend gap-risk
close, since horizon-based time-stops are explicitly off in this preset).

Never imports or calls a broker-order path. Research-only.
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import smc_engine as e  # noqa: E402
import signal_v39 as v39  # noqa: E402
from symbol_metadata import resolve_symbol, symbol_snapshot  # noqa: E402

from validation.historical_replay_engine import (  # noqa: E402
    CandidateRecord,
    SignalRecord,
    TradeRecord,
    ReplayResult,
    TIMEFRAME_DELTA,
    _assert_chronological,
    _load_cost_profile,
    _lookup_cost_profile,
    _parse_time,
    _window,
)
from validation.performance_metrics import compute_metrics  # noqa: E402
from bisect import bisect_right


class HistoricalReplayEngineV39:
    """Point-in-time replay for specs/v3.9.yaml / ST-C1_v1.2.0.yaml.

    warmup_bars only needs to cover the M5-side detection window (a fixed
    300 M5 bars, sized for M1/M2/M3's own lookbacks — see generate_signal);
    the H1 side is bounded independently by calendar time via
    _bounded_context_window/_available_index, not by warmup_bars, and this
    repo's H1 CSVs start well before the corresponding M5 CSVs for all three
    ST-C1 symbols. Default kept modest so a full-history population run
    doesn't waste evaluated bars on an unnecessarily long warmup.
    """

    def __init__(
        self,
        contract_path: str = "strategies/candidates/ST-C1_v1.2.0.yaml",
        min_rr: float = 3.0,
        warmup_bars: int = 350,
        cost_profile_path: str | None = None,
        h1_bars_per_m5_bar_ratio: int = 12,
    ) -> None:
        self.contract_path = contract_path
        self.min_rr = min_rr
        self.warmup_bars = warmup_bars
        self.cost_profile = _load_cost_profile(cost_profile_path)
        self.metadata_snapshot = symbol_snapshot()
        self._h1_per_m5 = h1_bars_per_m5_bar_ratio
        self._timeline_cache: dict[int, Any] = {}
        self._e_trigger_cache: dict[int, Any] = {}

    def _build_timeline(self, candles: list[dict[str, Any]], timeframe: str):
        delta = TIMEFRAME_DELTA.get(timeframe.upper())
        if delta is None:
            raise ValueError(f"unsupported timeframe: {timeframe}")
        times = tuple(_parse_time(c["time"]) for c in candles)
        close_times = tuple(t + delta for t in times)
        return close_times

    def _available_index(self, candles: list[dict[str, Any]], timeframe: str, asof: str) -> int:
        key = id(candles)
        close_times = self._timeline_cache.get(key)
        if close_times is None:
            close_times = self._build_timeline(candles, timeframe)
            self._timeline_cache[key] = close_times
        cutoff = _parse_time(asof)
        idx = bisect_right(close_times, cutoff) - 1
        return min(idx, len(close_times) - 1)

    def _bounded_context_window(
        self,
        candles: list[dict[str, Any]] | None,
        timeframe: str,
        asof: str,
        lookback_bars: int,
    ) -> list[dict[str, Any]]:
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

    def _cost_to_r(self, symbol: str | None, entry: float, stop: float) -> tuple[Any, dict[str, float]]:
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
            "spread_price": round(spread_price, 10),
            "spread_points": spread_points,
            "spread_pips": round(spread_price / pip_size, 10) if pip_size else 0.0,
            "entry_slippage_price": round(slippage_price_per_side, 10),
            "exit_slippage_price": round(slippage_price_per_side, 10),
            "slippage_price_round_trip": round(slippage_price_round_trip, 10),
            "commission_usd_round_turn": round(commission_usd_round_turn, 10),
            "commission": round(commission_usd_round_turn, 10),
            "spread_r": round(spread_r, 10),
            "slippage_r": round(slippage_r, 10),
            "commission_r": round(commission_r, 10),
            "swap_r": 0.0,
            "price_cost_round_trip": round(price_cost_round_trip, 10),
            "total_cost": round(price_cost_round_trip, 10),
            "total_cost_r": round(total_cost_r, 10),
        }

    def generate_signal(
        self,
        index: int,
        m5: list[dict[str, Any]],
        h1: list[dict[str, Any]] | None = None,
        *,
        symbol: str | None = None,
        rejected_candidates: list[CandidateRecord] | None = None,
        funnel_counts: dict[str, int] | None = None,
    ) -> SignalRecord | None:
        if index < self.warmup_bars:
            return None
        symbol_name = symbol or self._metadata_for_symbol(None).canonical_symbol

        def bump(key: str, amount: int = 1) -> None:
            if funnel_counts is not None:
                funnel_counts[key] = int(funnel_counts.get(key, 0)) + amount

        def reject(stage: str, reason: str) -> None:
            bump(f"rejected_{stage}")
            if rejected_candidates is not None:
                rejected_candidates.append(
                    CandidateRecord(
                        signal_time=m5[index]["time"],
                        stage=stage,
                        direction="unknown",
                        structure_key=None,
                        rejection_reason=reason,
                        symbol=symbol_name,
                        metadata={},
                    )
                )

        bump("evaluated")
        # M-model detection (M1/M2/M3) only needs a modest, M5-scaled lookback
        # (ifvg_max_age_m5_bars=20, retrace_max_bars=30, plus swing-confirmation
        # padding) -- NOT the H1 E3 lookback (60 H1 bars ~= 720 M5 bars), which
        # was being used to size this window in an earlier draft and made every
        # per-bar smc_engine scan (swings/order_blocks/fvgs/liquidity_sweeps,
        # each O(window)) ~3x more expensive than necessary for no detection
        # benefit (found via a performance probe: 8000 M5 bars did not finish
        # in 120s with the H1-scaled window).
        m5_window = _window(m5, index, 300)
        m5_window_start = max(0, index - 299)  # matches _window's own start=max(0,end-size+1)
        asof_time = m5[index + 1]["time"] if index + 1 < len(m5) else m5_window[-1]["time"]
        h1_lookback = max(v39.E2_POI_MAX_AGE_H1_BARS, v39.E3_RANGE_LOOKBACK_H1_BARS) + 5

        # Fast H1 pre-check, cached per H1 available-bar-index: many M5 bars
        # share the same closed H1 bar, so detect_e_trigger's H1-side scan
        # (swings/order_blocks/liquidity_sweeps over the H1 lookback) only
        # needs to run once per H1 bar, not once per M5 bar. Point-in-time
        # integrity is preserved: the cache key IS the bounded H1 availability
        # index, so no future H1 bar is ever consulted early.
        h1_available_idx = self._available_index(h1, "H1", asof_time) if h1 else -1
        if h1 is not None:
            if h1_available_idx not in self._e_trigger_cache:
                h1_window_for_cache = self._bounded_context_window(h1, "H1", asof_time, h1_lookback)
                self._e_trigger_cache[h1_available_idx] = (
                    v39.detect_e_trigger(h1_window_for_cache) if h1_window_for_cache else None
                )
            if self._e_trigger_cache[h1_available_idx] is None:
                reject("signal", "no qualifying E-trigger (E1 disabled in v3.9 / E2 POI / E3 external sweep)")
                return None
            h1_window = self._bounded_context_window(h1, "H1", asof_time, h1_lookback)
        else:
            h1_window = None

        result = v39.analyze(symbol_name, m5_window, h1=h1_window, index_offset=m5_window_start, min_rr=self.min_rr)
        if result.get("decision") != "SIGNAL":
            reject("signal", str(result.get("reason", result.get("decision", "no signal"))))
            return None
        bump("signal_pass")

        direction_raw = result["direction"]
        direction = "long" if direction_raw == "BUY" else "short"
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
        reason_codes = (
            f"E_TRIGGER_{result['e_trigger']}",
            f"M_MODEL_{result['m_model']}",
            "SESSION_OK",
            f"GROSS_RR_{result.get('rr_to_primary_tp_gross')}",
        )
        return SignalRecord(
            index=index,
            time=m5_window[-1]["time"],
            direction=direction,
            entry=round(entry, 5),
            stop=round(stop, 5),
            target=round(target, 5),
            structure_key=structure_key,
            reason_codes=reason_codes,
            canonical_symbol=self._metadata_for_symbol(symbol_name).canonical_symbol,
            source_symbol=symbol_name,
        )

    def _is_weekday_utc(self, ts: str) -> bool:
        return _parse_time(ts).weekday() < 5

    def _crosses_weekend_gap(self, ts: str, next_ts: str) -> bool:
        """True if `next_ts` is >=2 calendar days after `ts`. Real forex data
        has no Saturday/Sunday bars at all (Friday's last bar is directly
        followed by Monday's first) — checking whether the *next* bar falls
        on a weekend day would never fire, since that bar simply doesn't
        exist in the series. The weekend gap must be detected from the date
        jump itself."""
        d1 = _parse_time(ts).date()
        d2 = _parse_time(next_ts).date()
        return (d2 - d1).days >= 2

    def simulate_trade(
        self,
        signal: SignalRecord,
        m5: list[dict[str, Any]],
        entry_index: int,
        symbol: str | None = None,
    ) -> TradeRecord:
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
                exit_price = current_stop
                exit_index = entry_index + offset
                outcome = "STOP"
                break
            if hit_stop:
                exit_price = current_stop
                exit_index = entry_index + offset
                outcome = "STOP"
                break
            if hit_target:
                exit_price = signal.target
                exit_index = entry_index + offset
                outcome = "TARGET"
                break
            # v3.9 weekend force-exit: trade_management.weekend_exit/forced_exit
            # are true with time_stop disabled — the only forced-exit condition
            # remaining is closing flat before a weekend gap, checked only
            # after this bar's own stop/target outcome is ruled out (a Friday
            # bar that hits stop/target intrabar resolves as STOP/TARGET, not
            # a weekend exit).
            if offset + 1 < len(forward) and self._crosses_weekend_gap(candle["time"], forward[offset + 1]["time"]):
                exit_price = candle["close"]
                exit_index = entry_index + offset
                outcome = "WEEKEND_EXIT"
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
            signal_index=signal.index,
            signal_time=signal.time,
            entry_index=entry_index,
            entry_time=m5[entry_index]["time"],
            exit_index=exit_index,
            exit_time=m5[exit_index]["time"],
            direction=direction,
            entry=round(signal.entry, 5),
            stop=round(signal.stop, 5),
            target=round(signal.target, 5),
            exit_price=round(exit_price, 5),
            gross_r=round(gross_r, 6),
            cost_r=round(cost["total_cost_r"], 6),
            net_r=round(net_r, 6),
            outcome=outcome,
            structure_key=signal.structure_key,
            symbol_metadata_version=meta.version,
            partial_taken=partial_taken,
            break_even_activated=break_even_activated,
            ambiguous_bar=ambiguous_bar,
            unresolved_open_position=unresolved_open_position,
            management_events=tuple(management_events),
            **cost,
        )

    def replay(self, m5: list[dict[str, Any]], h1: list[dict[str, Any]] | None = None, symbol: str = "ST-C1") -> ReplayResult:
        _assert_chronological(m5, "<m5>")
        if h1:
            _assert_chronological(h1, "<h1>")

        signals: list[SignalRecord] = []
        trades: list[TradeRecord] = []
        rejected_candidates: list[CandidateRecord] = []
        funnel_counts: dict[str, int] = {
            "evaluated": 0,
            "signal_pass": 0,
            "candidate_ready": 0,
            "duplicate_structure": 0,
            "executed_trade": 0,
        }
        consumed: set[str] = set()
        i = self.warmup_bars
        while i < len(m5) - 1:
            signal = self.generate_signal(
                i, m5, h1=h1, symbol=symbol,
                rejected_candidates=rejected_candidates,
                funnel_counts=funnel_counts,
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
            contract_path=self.contract_path,
            symbol=symbol,
            status="READY_FOR_STATISTICAL_VALIDATION",
            caveat=None if trades else "No trades were generated on the supplied replay data.",
            signals=tuple(signals),
            trades=tuple(trades),
            rejected_candidates=tuple(rejected_candidates),
            management_events=tuple(ev for trade in trades for ev in trade.management_events),
            funnel_counts=dict(funnel_counts),
            metrics=compute_metrics([t.net_r for t in trades]),
            assumptions={
                "entry": "next candle after signal (confirmation_close_next_bar_open)",
                "exit": "stop-first conservative fills, +1R partial/break-even, weekend force-exit",
                "strategy_id": "ST-C1",
                "strategy_version": "1.2.0",
                "spec_version": "3.9",
            },
            symbol_metadata=self._metadata_for_symbol(symbol).snapshot(),
        )

    def run_from_paths(self, m5_path: str, h1_path: str | None = None, symbol: str = "ST-C1") -> ReplayResult:
        m5 = e.load_candles(m5_path)
        h1 = e.load_candles(h1_path) if h1_path else None
        return self.replay(m5, h1=h1, symbol=symbol)
