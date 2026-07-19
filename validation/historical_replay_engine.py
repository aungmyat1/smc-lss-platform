#!/usr/bin/env python3
"""Deterministic historical replay scaffold for ST-C1."""
from __future__ import annotations

import csv
import datetime as dt
import os
import sys
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


@dataclass(frozen=True)
class ReplayResult:
    contract_path: str
    symbol: str
    status: str
    caveat: str | None
    signals: tuple[SignalRecord, ...] = field(default_factory=tuple)
    trades: tuple[TradeRecord, ...] = field(default_factory=tuple)
    metrics: dict[str, Any] = field(default_factory=dict)
    assumptions: dict[str, Any] = field(default_factory=dict)

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
        return dt.datetime.fromisoformat(cleaned)
    except ValueError:
        return dt.datetime.strptime(value[:16], "%Y-%m-%d %H:%M")


def _timestamp_string(value: str) -> str:
    return _parse_time(value).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _window(candles: list[dict[str, Any]], end: int, size: int) -> list[dict[str, Any]]:
    start = max(0, end - size + 1)
    return candles[start : end + 1]


def _context_window(series: list[dict[str, Any]] | None, current_time: str) -> list[dict[str, Any]]:
    if not series:
        return []
    current = _parse_time(current_time)
    cutoff = 0
    while cutoff < len(series) and _parse_time(series[cutoff]["time"]) <= current:
        cutoff += 1
    return series[:cutoff]


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


class HistoricalReplayEngine:
    def __init__(
        self,
        contract: dict[str, Any] | None = None,
        contract_path: str = "strategies/candidates/ST-C1_v1.yaml",
        spread_points: float = 25.0,
        slippage_points: float = 3.0,
        commission_r: float = 0.0,
        point_size: float = 0.0001,
        stop_buffer_atr_mult: float = 0.15,
        warmup_bars: int = 40,
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
        return m5, h1, d1

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
    ) -> SignalRecord | None:
        k = int(self.params.get("swing_lookback_bars", 2))
        if index < max(self.warmup_bars, 3 * k + 2):
            return None

        m5_window = _window(m5, index, max(60, self.warmup_bars))
        h1_window = _context_window(h1, m5_window[-1]["time"]) if h1 else None
        d1_window = _context_window(d1, m5_window[-1]["time"]) if d1 else None
        features = self.evaluate_features(m5_window, h1_window, d1_window)

        if not features["session_allowed"]:
            return None
        signal = features["signal"]
        if not signal:
            return None
        direction = signal["dir"]
        if direction == "long" and features["bias"] != "BULLISH":
            return None
        if direction == "short" and features["bias"] != "BEARISH":
            return None

        sweep_dir = "bull" if direction == "long" else "bear"
        if not any(s["dir"] == sweep_dir for s in features["sweeps"][-3:]):
            return None

        poi_dir = sweep_dir
        has_ob = any(o["dir"] == poi_dir for o in features["order_blocks"])
        has_fvg = any(f["dir"] == poi_dir for f in features["fvgs"])
        if not (has_ob or has_fvg):
            return None

        entry = m5[index + 1]["open"]
        stop = self._determine_stop(direction, m5_window, features, entry)
        if stop is None:
            return None
        risk = abs(entry - stop)
        if risk <= 0:
            return None
        target = self._determine_target(direction, m5_window, features, entry, stop)
        if target is None:
            return None

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

    def simulate_trade(
        self,
        signal: SignalRecord,
        m5: list[dict[str, Any]],
        entry_index: int,
        exit_search_start: int | None = None,
    ) -> TradeRecord:
        start = exit_search_start if exit_search_start is not None else entry_index
        forward = m5[start:]
        if not forward:
            raise ValueError("no forward candles available for trade simulation")
        direction = signal.direction
        risk = abs(signal.entry - signal.stop)
        if risk <= 0:
            raise ValueError("invalid zero-risk trade")
        exit_price = forward[-1]["close"]
        exit_index = len(m5) - 1
        outcome = "TIMEOUT"
        for offset, candle in enumerate(forward):
            hit_stop = candle["low"] <= signal.stop if direction == "long" else candle["high"] >= signal.stop
            hit_target = candle["high"] >= signal.target if direction == "long" else candle["low"] <= signal.target
            if hit_stop:
                exit_price = signal.stop
                exit_index = start + offset
                outcome = "STOP"
                break
            if hit_target:
                exit_price = signal.target
                exit_index = start + offset
                outcome = "TARGET"
                break
        gross_r = ((exit_price - signal.entry) / risk) if direction == "long" else ((signal.entry - exit_price) / risk)
        cost_r = self._cost_to_r(risk)
        net_r = gross_r - cost_r
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
            gross_r=round(gross_r, 4),
            cost_r=round(cost_r, 4),
            net_r=round(net_r, 4),
            outcome=outcome,
            structure_key=signal.structure_key,
        )

    def _cost_to_r(self, risk: float) -> float:
        if risk <= 0:
            return 0.0
        round_trip_price = (self.spread_points + self.slippage_points) * self.point_size
        return round_trip_price / risk + self.commission_r

    def replay(self, m5: list[dict[str, Any]], h1: list[dict[str, Any]] | None = None, d1: list[dict[str, Any]] | None = None, symbol: str = "ST-C1") -> ReplayResult:
        _assert_chronological(m5, "<m5>")
        if h1:
            _assert_chronological(h1, "<h1>")
        if d1:
            _assert_chronological(d1, "<d1>")

        signals: list[SignalRecord] = []
        trades: list[TradeRecord] = []
        consumed: set[str] = set()
        i = self.warmup_bars
        while i < len(m5) - 1:
            signal = self.generate_signal(i, m5, h1=h1, d1=d1)
            if signal is None:
                i += 1
                continue
            if signal.structure_key in consumed:
                i += 1
                continue
            consumed.add(signal.structure_key)
            signals.append(signal)
            trade = self.simulate_trade(signal, m5, entry_index=i + 1)
            trades.append(trade)
            i = max(trade.exit_index + 1, i + 1)

        result = ReplayResult(
            contract_path=self.contract_path,
            symbol=symbol,
            status="READY_FOR_STATISTICAL_VALIDATION",
            caveat=None if trades else "No trades were generated on the supplied replay data.",
            signals=tuple(signals),
            trades=tuple(trades),
            metrics=compute_metrics([t.net_r for t in trades]),
            assumptions={
                "entry": "next candle after signal",
                "exit": "contract-defined SL/TP with stop-first conservative fills",
                "costs": {
                    "spread_points": self.spread_points,
                    "slippage_points": self.slippage_points,
                    "commission_r": self.commission_r,
                },
            },
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
