#!/usr/bin/env python3
"""Deterministic historical replay scaffold for ST-C1."""
from __future__ import annotations

import csv
import datetime as dt
import math
import os
import sys
from bisect import bisect_right
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import smc_engine as e  # noqa: E402
from live_signal import latest_signal  # noqa: E402
from symbol_metadata import resolve_symbol, symbol_snapshot  # noqa: E402

from validation.performance_metrics import compute_metrics


@dataclass(frozen=True)
class SignalRecord:
    index: int
    time: str
    direction: str
    entry: float
    stop: float
    target: float
    structure_key: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class TradeRecord:
    signal_index: int
    signal_time: str
    entry_index: int
    entry_time: str
    exit_index: int
    exit_time: str
    direction: str
    entry: float
    stop: float
    target: float
    exit_price: float
    gross_r: float
    cost_r: float
    net_r: float
    outcome: str
    structure_key: str
    symbol_metadata_version: str = "symbol-metadata-v1"
    spread_price: float = 0.0
    spread_points: float = 0.0
    spread_pips: float = 0.0
    entry_slippage_price: float = 0.0
    exit_slippage_price: float = 0.0
    slippage_price_round_trip: float = 0.0
    commission_usd_round_turn: float = 0.0
    commission: float = 0.0
    spread_r: float = 0.0
    slippage_r: float = 0.0
    commission_r: float = 0.0
    swap_r: float = 0.0
    price_cost_round_trip: float = 0.0
    total_cost: float = 0.0
    total_cost_r: float = 0.0
    partial_taken: bool = False
    break_even_activated: bool = False
    ambiguous_bar: bool = False
    unresolved_open_position: bool = False
    management_events: tuple[dict[str, Any], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CandidateRecord:
    signal_time: str
    stage: str
    direction: str
    structure_key: str | None
    rejection_reason: str
    symbol: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReplayResult:
    contract_path: str
    symbol: str
    status: str
    caveat: str | None
    signals: tuple[SignalRecord, ...] = field(default_factory=tuple)
    trades: tuple[TradeRecord, ...] = field(default_factory=tuple)
    rejected_candidates: tuple[CandidateRecord, ...] = field(default_factory=tuple)
    management_events: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    funnel_counts: dict[str, int] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    assumptions: dict[str, Any] = field(default_factory=dict)
    symbol_metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def trade_rs(self) -> list[float]:
        return [t.net_r for t in self.trades]


def _load_yaml(path: str) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a top-level mapping")
    return data


def _load_candles(path: str) -> list[dict[str, Any]]:
    _assert_file_chronological(path)
    candles = e.load_candles(path)
    _assert_chronological(candles, path)
    return candles


def _assert_file_chronological(path: str) -> None:
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    prev: dt.datetime | None = None
    seen: set[str] = set()
    for row in rows:
        raw = row["time"]
        if raw in seen:
            raise ValueError(f"{path}: duplicate timestamp {raw}")
        seen.add(raw)
        current = _parse_time(raw)
        if prev is not None and current < prev:
            raise ValueError(f"{path}: candles must be sorted chronologically")
        prev = current


def _assert_chronological(candles: list[dict[str, Any]], path: str) -> None:
    prev: dt.datetime | None = None
    seen: set[str] = set()
    for candle in candles:
        raw = candle["time"]
        if raw in seen:
            raise ValueError(f"{path}: duplicate timestamp {raw}")
        seen.add(raw)
        current = _parse_time(raw)
        if prev is not None and current < prev:
            raise ValueError(f"{path}: candles must be sorted chronologically")
        prev = current


def _parse_time(value: str) -> dt.datetime:
    cleaned = value.replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(cleaned)
    except ValueError:
        parsed = dt.datetime.strptime(value[:16], "%Y-%m-%d %H:%M")
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt.UTC)
    return parsed.astimezone(dt.UTC)


def _timestamp_string(value: str) -> str:
    return _parse_time(value).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _window(candles: list[dict[str, Any]], end: int, size: int) -> list[dict[str, Any]]:
    start = max(0, end - size + 1)
    return candles[start : end + 1]


TIMEFRAME_DELTA = {
    "M5": dt.timedelta(minutes=5),
    "H1": dt.timedelta(hours=1),
    "D1": dt.timedelta(days=1),
}


@dataclass(frozen=True)
class _SeriesTimeline:
    times: tuple[dt.datetime, ...]
    close_times: tuple[dt.datetime, ...]
    timeframe: str

    @property
    def last_index(self) -> int:
        return len(self.times) - 1


def _is_session_allowed(time_text: str, sessions: list[str], session_windows: dict[str, tuple[str, str]]) -> bool:
    t = _parse_time(time_text)
    if t.weekday() >= 5:
        return False
    hhmm = t.strftime("%H:%M")
    for session in sessions:
        window = session_windows.get(session)
        if not window:
            continue
        start, end = window
        if start <= hhmm <= end:
            return True
    return False


def _load_cost_profile(path: str | None = None) -> dict[str, Any]:
    candidate = Path(path or ROOT / "config" / "research_costs.yaml")
    if not candidate.exists():
        return {}
    data = yaml.safe_load(candidate.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _lookup_cost_profile(symbol: str, asset_class: str, profile: dict[str, Any]) -> dict[str, Any]:
    symbols = profile.get("symbols", {}) if isinstance(profile, dict) else {}
    defaults = profile.get("defaults", {}) if isinstance(profile, dict) else {}
    symbol_specific = symbols.get(symbol, {}) if isinstance(symbols, dict) else {}
    asset_specific = defaults.get(asset_class, {}) if isinstance(defaults, dict) else {}
    merged: dict[str, Any] = {}
    if isinstance(asset_specific, dict):
        merged.update(asset_specific)
    if isinstance(symbol_specific, dict):
        merged.update(symbol_specific)
    return merged


class HistoricalReplayEngine:
    def __init__(
        self,
        contract: dict[str, Any] | None = None,
        contract_path: str = "strategies/candidates/ST-C1_v1.yaml",
        spread_points: float = 25.0,
        slippage_points: float = 3.0,
        commission_r: float = 0.0,
        point_size: float | None = None,
        stop_buffer_atr_mult: float = 0.15,
        warmup_bars: int = 40,
        cost_profile_path: str | None = None,
    ) -> None:
        self.contract_path = contract_path
        self.contract = contract or _load_yaml(contract_path)
        self.params = self.contract.get("parameters", {})
        self.market = self.contract.get("market_universe", {})
        self.spread_points = spread_points
        self.slippage_points = slippage_points
        self.commission_r = commission_r
        self.point_size = point_size
        self.stop_buffer_atr_mult = stop_buffer_atr_mult
        self.warmup_bars = warmup_bars
        self.cost_profile = _load_cost_profile(cost_profile_path)
        self.metadata_snapshot = symbol_snapshot()
        self._timeline_cache: dict[int, _SeriesTimeline] = {}

    @property
    def sessions(self) -> list[str]:
        value = self.market.get("sessions", [])
        return list(value) if isinstance(value, list) else []

    @property
    def session_windows(self) -> dict[str, tuple[str, str]]:
        return {
            "London": tuple(self.params.get("london_session_utc", ["06:00", "10:00"]))[:2],
            "NewYork": tuple(self.params.get("new_york_session_utc", ["11:30", "15:00"]))[:2],
        }

    def load_series(self, m5_path: str, h1_path: str | None = None, d1_path: str | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]] | None, list[dict[str, Any]] | None]:
        m5 = _load_candles(m5_path)
        h1 = _load_candles(h1_path) if h1_path else None
        d1 = _load_candles(d1_path) if d1_path else None
        self._register_series(m5, "M5")
        if h1 is not None:
            self._register_series(h1, "H1")
        if d1 is not None:
            self._register_series(d1, "D1")
        return m5, h1, d1

    def _register_series(self, candles: list[dict[str, Any]], timeframe: str) -> None:
        self._timeline_cache[id(candles)] = self._build_timeline(candles, timeframe)

    def _build_timeline(self, candles: list[dict[str, Any]], timeframe: str) -> _SeriesTimeline:
        delta = TIMEFRAME_DELTA.get(timeframe.upper())
        if delta is None:
            raise ValueError(f"unsupported timeframe: {timeframe}")
        times = tuple(_parse_time(candle["time"]) for candle in candles)
        close_times = tuple(time + delta for time in times)
        return _SeriesTimeline(times=times, close_times=close_times, timeframe=timeframe.upper())

    def _timeline(self, candles: list[dict[str, Any]], timeframe: str) -> _SeriesTimeline:
        cached = self._timeline_cache.get(id(candles))
        if cached is not None:
            return cached
        timeline = self._build_timeline(candles, timeframe)
        self._timeline_cache[id(candles)] = timeline
        return timeline

    def _available_index(self, candles: list[dict[str, Any]], timeframe: str, asof: str) -> int:
        timeline = self._timeline(candles, timeframe)
        cutoff = _parse_time(asof)
        idx = bisect_right(timeline.close_times, cutoff) - 1
        return min(idx, timeline.last_index)

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
        return candles[start : available + 1]

    def evaluate_features(
        self,
        m5_window: list[dict[str, Any]],
        h1_window: list[dict[str, Any]] | None = None,
        d1_window: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        k = int(self.params.get("swing_lookback_bars", 2))
        eq_window = 40
        bias_window = h1_window if h1_window else m5_window
        bias = self._directional_bias(bias_window, k)
        m5_hi, m5_lo = e.swings(m5_window, k)
        m5_bias = e.trend(m5_hi, m5_lo)
        eq, _, _ = e.equilibrium(m5_window, len(m5_window) - 1, eq_window)
        sig = latest_signal(m5_window, k, eq_window)
        sweeps = e.liquidity_sweeps(m5_window, k, min_wick_ratio=float(self.params.get("e3_sweep_wick_ratio_min", 0.5)))
        obs = e.order_blocks(m5_window, k)
        fvgs = e.fvgs(m5_window)
        return {
            "bias": bias,
            "m5_bias": m5_bias,
            "equilibrium": eq,
            "signal": sig,
            "sweeps": sweeps,
            "order_blocks": obs,
            "fvgs": fvgs,
            "last_close": m5_window[-1]["close"],
            "session_allowed": _is_session_allowed(
                m5_window[-1]["time"],
                self.sessions,
                self.session_windows,
            ),
            "d1_available": bool(d1_window),
        }

    def _directional_bias(self, candles: list[dict[str, Any]], k: int) -> str:
        hi, lo = e.swings(candles, k)
        trend = e.trend(hi, lo)
        if trend != "RANGING":
            return trend
        if len(candles) >= 3:
            last3 = candles[-3:]
            highs = [c["high"] for c in last3]
            lows = [c["low"] for c in last3]
            if highs[2] > highs[1] > highs[0] and lows[2] > lows[1] > lows[0]:
                return "BULLISH"
            if highs[2] < highs[1] < highs[0] and lows[2] < lows[1] < lows[0]:
                return "BEARISH"
        return "RANGING"

    def generate_signal(
        self,
        index: int,
        m5: list[dict[str, Any]],
        h1: list[dict[str, Any]] | None = None,
        d1: list[dict[str, Any]] | None = None,
        *,
        symbol: str | None = None,
        rejected_candidates: list[CandidateRecord] | None = None,
        funnel_counts: dict[str, int] | None = None,
    ) -> SignalRecord | None:
        k = int(self.params.get("swing_lookback_bars", 2))
        if index < max(self.warmup_bars, 3 * k + 2):
            return None

        symbol_name = symbol or self._metadata_for_symbol(None).canonical_symbol

        def bump(key: str, amount: int = 1) -> None:
            if funnel_counts is not None:
                funnel_counts[key] = int(funnel_counts.get(key, 0)) + amount

        def reject(stage: str, reason: str, *, metadata: dict[str, Any] | None = None) -> None:
            bump(f"rejected_{stage}")
            if rejected_candidates is not None:
                rejected_candidates.append(
                    CandidateRecord(
                        signal_time=m5[index]["time"],
                        stage=stage,
                        direction=str(metadata.get("direction")) if metadata else "unknown",
                        structure_key=metadata.get("structure_key") if metadata else None,
                        rejection_reason=reason,
                        symbol=str(metadata.get("symbol")) if metadata and metadata.get("symbol") else symbol_name,
                        metadata=dict(metadata or {}),
                    )
                )

        bump("evaluated")
        m5_window = _window(m5, index, max(60, self.warmup_bars))
        asof_time = m5[index + 1]["time"] if index + 1 < len(m5) else m5_window[-1]["time"]
        h1_lookback = max(
            int(self.params.get("e1_reaction_window_h1_bars", 6)),
            int(self.params.get("e2_poi_max_age_h1_bars", 60)),
            int(self.params.get("e3_range_lookback_h1_bars", 40)),
            int(self.params.get("max_e_to_m_h1_bars", 12)),
            120,
        )
        d1_lookback = max(int(self.params.get("e1_gap_max_age_d1_bars", 10)), 20)
        h1_window = self._bounded_context_window(h1, "H1", asof_time, h1_lookback) if h1 else None
        d1_window = self._bounded_context_window(d1, "D1", asof_time, d1_lookback) if d1 else None
        features = self.evaluate_features(m5_window, h1_window, d1_window)

        if not features["session_allowed"]:
            reject("session", "outside allowed session", metadata={"symbol": symbol_name, "direction": "unknown"})
            return None
        bump("session_pass")
        signal = features["signal"]
        if not signal:
            reject("signal", "no qualifying signal structure")
            return None
        bump("signal_pass")
        direction = signal["dir"]
        if direction == "long" and features["bias"] != "BULLISH":
            reject("bias", "bullish alignment failed", metadata={"direction": direction, "symbol": symbol_name})
            return None
        if direction == "short" and features["bias"] != "BEARISH":
            reject("bias", "bearish alignment failed", metadata={"direction": direction, "symbol": symbol_name})
            return None
        bump("bias_pass")

        sweep_dir = "bull" if direction == "long" else "bear"
        if not any(s["dir"] == sweep_dir for s in features["sweeps"][-3:]):
            reject("sweep", "missing matching liquidity sweep", metadata={"direction": direction, "symbol": symbol_name})
            return None
        bump("sweep_pass")

        poi_dir = sweep_dir
        has_ob = any(o["dir"] == poi_dir for o in features["order_blocks"])
        has_fvg = any(f["dir"] == poi_dir for f in features["fvgs"])
        if not (has_ob or has_fvg):
            reject("poi", "missing order block or FVG confirmation", metadata={"direction": direction, "symbol": symbol_name})
            return None
        bump("poi_pass")

        entry = m5[index + 1]["open"]
        stop = self._determine_stop(direction, m5_window, features, entry)
        if stop is None:
            reject("risk", "could not determine stop", metadata={"direction": direction, "symbol": symbol_name})
            return None
        risk = abs(entry - stop)
        if risk <= 0:
            reject("risk", "zero or negative risk", metadata={"direction": direction, "symbol": symbol_name})
            return None
        target = self._determine_target(direction, m5_window, features, entry, stop)
        if target is None:
            reject("target", "could not determine target", metadata={"direction": direction, "symbol": symbol_name})
            return None
        bump("candidate_ready")

        structure_key = self._structure_key(direction, features)
        reason_codes = (
            "H1_BIAS_" + direction.upper(),
            "SESSION_OK",
            "LIQUIDITY_SWEEP_CONFIRMED",
            "POI_CONFIRMED",
            "CHoCH_CONFIRMED",
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
        )

    def _structure_key(self, direction: str, features: dict[str, Any]) -> str:
        sweep_index = features["sweeps"][-1]["i"] if features["sweeps"] else -1
        ob_index = features["order_blocks"][-1]["i"] if features["order_blocks"] else -1
        return f"{direction}:{sweep_index}:{ob_index}"

    def _determine_stop(self, direction: str, window: list[dict[str, Any]], features: dict[str, Any], entry: float) -> float | None:
        atr = e.atr(window, len(window) - 1, 14)
        buffer = atr * self.stop_buffer_atr_mult
        refs: list[float] = []
        if features["sweeps"]:
            refs.append(features["sweeps"][-1]["level"])
        if features["order_blocks"]:
            last_ob = features["order_blocks"][-1]
            refs.extend([last_ob["low"], last_ob["high"]])
        if features["fvgs"]:
            last_fvg = features["fvgs"][-1]
            refs.extend([last_fvg["lower"], last_fvg["upper"]])
        if not refs:
            return None
        if direction == "long":
            stop = min(refs) - buffer
            if stop >= entry:
                return None
            return stop
        stop = max(refs) + buffer
        if stop <= entry:
            return None
        return stop

    def _determine_target(self, direction: str, window: list[dict[str, Any]], features: dict[str, Any], entry: float, stop: float) -> float | None:
        risk = abs(entry - stop)
        min_rr = float(self.params.get("min_rr", 2.0))
        fallback = entry + risk * min_rr if direction == "long" else entry - risk * min_rr
        levels: list[float] = []
        hi, lo = e.swings(window, int(self.params.get("swing_lookback_bars", 2)))
        if direction == "long":
            levels = [price for _, price in hi if price > entry]
            target = min(levels) if levels else fallback
            return max(target, fallback)
        levels = [price for _, price in lo if price < entry]
        target = max(levels) if levels else fallback
        return min(target, fallback)

    def _metadata_for_symbol(self, symbol: str | None) -> Any:
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
        spread_points = float(profile.get("spread_points", self.spread_points))
        slippage_points = float(profile.get("slippage_points", self.slippage_points))
        commission_usd_round_turn = float(profile.get("commission_per_lot_usd_round_turn", self.commission_r))
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

    def _simulate_trade_detail(
        self,
        signal: SignalRecord,
        m5: list[dict[str, Any]],
        entry_index: int,
        exit_search_start: int | None = None,
        symbol: str | None = None,
    ) -> dict[str, Any]:
        start = exit_search_start if exit_search_start is not None else entry_index
        forward = m5[start:]
        if not forward:
            raise ValueError("no forward candles available for trade simulation")
        direction = "long" if str(signal.direction).lower() in {"long", "buy"} else "short"
        risk = abs(signal.entry - signal.stop)
        if risk <= 0:
            raise ValueError("invalid zero-risk trade")

        meta, cost = self._cost_to_r(symbol, signal.entry, signal.stop)
        exit_price = forward[-1]["close"]
        exit_index = len(m5) - 1
        outcome = "TIME_STOP"
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
                exit_index = start + offset
                outcome = "STOP"
                break
            if hit_stop:
                exit_price = current_stop
                exit_index = start + offset
                outcome = "STOP"
                break
            if hit_target:
                exit_price = signal.target
                exit_index = start + offset
                outcome = "TARGET"
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

        final_leg_r = ((exit_price - signal.entry) / risk) if direction == "long" else ((signal.entry - exit_price) / risk)
        gross_r = (0.5 * 1.0 + 0.5 * final_leg_r) if partial_taken else final_leg_r
        net_r = gross_r - cost["total_cost_r"]
        return {
            "signal_index": signal.index,
            "signal_time": signal.time,
            "entry_index": entry_index,
            "entry_time": m5[entry_index]["time"],
            "exit_index": exit_index,
            "exit_time": m5[exit_index]["time"],
            "direction": direction,
            "entry": round(signal.entry, 5),
            "stop": round(signal.stop, 5),
            "target": round(signal.target, 5),
            "exit_price": round(exit_price, 5),
            "gross_r": round(gross_r, 6),
            "cost_r": round(cost["total_cost_r"], 6),
            "net_r": round(net_r, 6),
            "outcome": outcome,
            "structure_key": signal.structure_key,
            "symbol_metadata_version": meta.version,
            "partial_taken": partial_taken,
            "break_even_activated": break_even_activated,
            "ambiguous_bar": ambiguous_bar,
            "unresolved_open_position": unresolved_open_position,
            "management_events": tuple(management_events),
            **cost,
        }

    def simulate_trade(
        self,
        signal: SignalRecord,
        m5: list[dict[str, Any]],
        entry_index: int,
        exit_search_start: int | None = None,
        symbol: str | None = None,
    ) -> TradeRecord:
        detail = self._simulate_trade_detail(signal, m5, entry_index, exit_search_start=exit_search_start, symbol=symbol)
        return TradeRecord(
            signal_index=detail["signal_index"],
            signal_time=detail["signal_time"],
            entry_index=detail["entry_index"],
            entry_time=detail["entry_time"],
            exit_index=detail["exit_index"],
            exit_time=detail["exit_time"],
            direction=detail["direction"],
            entry=detail["entry"],
            stop=detail["stop"],
            target=detail["target"],
            exit_price=detail["exit_price"],
            gross_r=detail["gross_r"],
            cost_r=detail["cost_r"],
            net_r=detail["net_r"],
            outcome=detail["outcome"],
            structure_key=detail["structure_key"],
            symbol_metadata_version=detail["symbol_metadata_version"],
            spread_price=detail["spread_price"],
            spread_points=detail["spread_points"],
            spread_pips=detail["spread_pips"],
            entry_slippage_price=detail["entry_slippage_price"],
            exit_slippage_price=detail["exit_slippage_price"],
            slippage_price_round_trip=detail["slippage_price_round_trip"],
            commission_usd_round_turn=detail["commission_usd_round_turn"],
            commission=detail["commission"],
            spread_r=detail["spread_r"],
            slippage_r=detail["slippage_r"],
            commission_r=detail["commission_r"],
            swap_r=detail["swap_r"],
            price_cost_round_trip=detail["price_cost_round_trip"],
            total_cost=detail["total_cost"],
            total_cost_r=detail["total_cost_r"],
            partial_taken=detail["partial_taken"],
            break_even_activated=detail["break_even_activated"],
            ambiguous_bar=detail["ambiguous_bar"],
            unresolved_open_position=detail["unresolved_open_position"],
            management_events=detail["management_events"],
        )

    def replay(self, m5: list[dict[str, Any]], h1: list[dict[str, Any]] | None = None, d1: list[dict[str, Any]] | None = None, symbol: str = "ST-C1") -> ReplayResult:
        _assert_chronological(m5, "<m5>")
        if h1:
            _assert_chronological(h1, "<h1>")
        if d1:
            _assert_chronological(d1, "<d1>")

        signals: list[SignalRecord] = []
        trades: list[TradeRecord] = []
        rejected_candidates: list[CandidateRecord] = []
        funnel_counts: dict[str, int] = {
            "evaluated": 0,
            "session_pass": 0,
            "signal_pass": 0,
            "bias_pass": 0,
            "sweep_pass": 0,
            "poi_pass": 0,
            "candidate_ready": 0,
            "duplicate_structure": 0,
            "skipped_open_trade": 0,
            "executed_trade": 0,
            "rejected_session": 0,
            "rejected_signal": 0,
            "rejected_bias": 0,
            "rejected_sweep": 0,
            "rejected_poi": 0,
            "rejected_risk": 0,
            "rejected_target": 0,
        }
        consumed: set[str] = set()
        i = self.warmup_bars
        while i < len(m5) - 1:
            signal = self.generate_signal(
                i,
                m5,
                h1=h1,
                d1=d1,
                symbol=symbol,
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
            if trade.unresolved_open_position:
                funnel_counts["skipped_open_trade"] = int(funnel_counts.get("skipped_open_trade", 0)) + 1
            i = max(trade.exit_index + 1, i + 1)

        assert funnel_counts["executed_trade"] == len(trades)
        result = ReplayResult(
            contract_path=self.contract_path,
            symbol=symbol,
            status="READY_FOR_STATISTICAL_VALIDATION",
            caveat=None if trades else "No trades were generated on the supplied replay data.",
            signals=tuple(signals),
            trades=tuple(trades),
            rejected_candidates=tuple(rejected_candidates),
            management_events=tuple(event for trade in trades for event in trade.management_events),
            funnel_counts=dict(funnel_counts),
            metrics=compute_metrics([t.net_r for t in trades]),
            assumptions={
                "entry": "next candle after signal",
                "exit": "next candle after signal with stop-first conservative fills, managed partials and break-even",
                "costs": {
                    "spread_points": self.spread_points,
                    "slippage_points_per_side": self.slippage_points,
                    "commission_r": self.commission_r,
                },
                "symbol_metadata": self._metadata_for_symbol(symbol).snapshot(),
                "slippage_convention": "per_side",
            },
            symbol_metadata=self._metadata_for_symbol(symbol).snapshot(),
        )
        return result

    def run_from_paths(self, m5_path: str, h1_path: str | None = None, d1_path: str | None = None, symbol: str = "ST-C1") -> ReplayResult:
        m5, h1, d1 = self.load_series(m5_path, h1_path=h1_path, d1_path=d1_path)
        return self.replay(m5, h1=h1, d1=d1, symbol=symbol)


def write_baseline_report(
    result: ReplayResult,
    path: str = "reports/ST-C1_BASELINE_BACKTEST_REPORT.md",
) -> str:
    lines = [
        "# ST-C1 Baseline Backtest Report",
        "",
        f"- Contract: `{result.contract_path}`",
        f"- Symbol: `{result.symbol}`",
        f"- Status: `{result.status}`",
        f"- Caveat: `{result.caveat or 'None'}`",
        "",
        "## Assumptions",
        "",
        f"- Entry: `{result.assumptions['entry']}`",
        f"- Exit: `{result.assumptions['exit']}`",
        f"- Spread points: `{result.assumptions['costs']['spread_points']}`",
        f"- Slippage points: `{result.assumptions['costs']['slippage_points']}`",
        f"- Commission R: `{result.assumptions['costs']['commission_r']}`",
        "",
        "## Metrics",
        "",
    ]
    for key, value in result.metrics.items():
        lines.append(f"- {key}: `{value}`")
    lines += [
        "",
        "## Counts",
        "",
        f"- Signals: `{len(result.signals)}`",
        f"- Trades: `{len(result.trades)}`",
        "",
        "## Status",
        "",
        "READY_FOR_STATISTICAL_VALIDATION" if result.status == "READY_FOR_STATISTICAL_VALIDATION" else "BLOCKED",
    ]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
