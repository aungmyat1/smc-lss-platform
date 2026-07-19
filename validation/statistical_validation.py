#!/usr/bin/env python3
"""Statistical validation scaffold for ST-C1.

This layer sits on top of deterministic replay results and checks whether the
observed edge survives chronological splits, rolling windows, and basic
stability tests. It does not optimize or modify strategy rules.
"""
from __future__ import annotations

import datetime as dt
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Iterable, Sequence

from validation.historical_replay_engine import HistoricalReplayEngine, ReplayResult, TradeRecord
from validation.performance_metrics import compute_metrics


SESSION_WINDOWS_UTC: dict[str, tuple[str, str]] = {
    "London": ("06:00", "10:00"),
    "NewYork": ("11:30", "15:00"),
}


@dataclass(frozen=True)
class DatasetSplitResult:
    split_ratio: float
    split_time: str
    in_sample: ReplayResult
    out_of_sample: ReplayResult


@dataclass(frozen=True)
class WalkForwardWindowResult:
    fold: int
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    result: ReplayResult


@dataclass(frozen=True)
class GroupedTradeSummary:
    label: str
    trades: int
    metrics: dict[str, Any]
    distribution: dict[str, Any]


@dataclass(frozen=True)
class StabilitySummary:
    monthly: tuple[GroupedTradeSummary, ...] = field(default_factory=tuple)
    yearly: tuple[GroupedTradeSummary, ...] = field(default_factory=tuple)
    session: tuple[GroupedTradeSummary, ...] = field(default_factory=tuple)
    symbol: tuple[GroupedTradeSummary, ...] = field(default_factory=tuple)
    direction: tuple[GroupedTradeSummary, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class StatisticalValidationResult:
    contract_path: str
    status: str
    caveat: str | None
    full_result: ReplayResult
    split: DatasetSplitResult
    walk_forward: tuple[WalkForwardWindowResult, ...]
    stability: StabilitySummary
    overall_metrics: dict[str, Any]
    return_distribution: dict[str, Any]
    bootstrap_expectancy_ci: tuple[float | None, float | None]
    gate_reasons: tuple[str, ...] = field(default_factory=tuple)
    assumptions: dict[str, Any] = field(default_factory=dict)


def _parse_time(value: str) -> dt.datetime:
    cleaned = value.replace("Z", "+00:00")
    try:
        return dt.datetime.fromisoformat(cleaned)
    except ValueError:
        return dt.datetime.strptime(value[:16], "%Y-%m-%d %H:%M")


def _timestamp_string(value: str) -> str:
    return _parse_time(value).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _time_key(value: str) -> tuple[int, int, int, int, int, int]:
    dt_value = _parse_time(value)
    return (
        dt_value.year,
        dt_value.month,
        dt_value.day,
        dt_value.hour,
        dt_value.minute,
        dt_value.second,
    )


def _series_between(
    series: list[dict[str, Any]] | None,
    start_time: str | None = None,
    end_time: str | None = None,
    *,
    start_inclusive: bool = True,
    end_inclusive: bool = True,
) -> list[dict[str, Any]] | None:
    if not series:
        return None
    start = _parse_time(start_time) if start_time else None
    end = _parse_time(end_time) if end_time else None
    subset: list[dict[str, Any]] = []
    for candle in series:
        current = _parse_time(candle["time"])
        if start is not None:
            if start_inclusive and current < start:
                continue
            if not start_inclusive and current <= start:
                continue
        if end is not None:
            if end_inclusive and current > end:
                continue
            if not end_inclusive and current >= end:
                continue
        subset.append(candle)
    return subset


def _split_series_by_ratio(series: list[dict[str, Any]], split_ratio: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    if not 0.0 < split_ratio < 1.0:
        raise ValueError("split_ratio must be between 0 and 1")
    if len(series) < 2:
        raise ValueError("series must contain at least two candles")
    split_index = max(1, min(len(series) - 1, int(len(series) * split_ratio)))
    split_time = series[split_index]["time"]
    return series[:split_index], series[split_index:], _timestamp_string(split_time)


def _bootstrap_mean_ci(values: Sequence[float], resamples: int = 2000, alpha: float = 0.05, seed: int = 7) -> tuple[float | None, float | None]:
    sample = list(values)
    if not sample:
        return None, None
    point = mean(sample)
    if len(sample) == 1 or resamples <= 0:
        rounded = round(point, 4)
        return rounded, rounded
    rng = random.Random(seed)
    stats: list[float] = []
    for _ in range(resamples):
        draw = [sample[rng.randrange(len(sample))] for _ in range(len(sample))]
        stats.append(mean(draw))
    stats.sort()
    low_index = max(0, min(len(stats) - 1, int((alpha / 2.0) * (len(stats) - 1))))
    high_index = max(0, min(len(stats) - 1, int((1.0 - alpha / 2.0) * (len(stats) - 1))))
    return round(stats[low_index], 4), round(stats[high_index], 4)


def _percentile(sorted_values: Sequence[float], percentile: float) -> float | None:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return round(sorted_values[0], 4)
    position = (len(sorted_values) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return round(sorted_values[int(position)], 4)
    lower_value = sorted_values[lower]
    upper_value = sorted_values[upper]
    interpolated = lower_value + (upper_value - lower_value) * (position - lower)
    return round(interpolated, 4)


def summarize_returns(trade_rs: Sequence[float]) -> dict[str, Any]:
    values = list(trade_rs)
    if not values:
        return {
            "count": 0,
            "min": None,
            "p10": None,
            "p25": None,
            "median": None,
            "p75": None,
            "p90": None,
            "max": None,
            "mean": None,
            "stdev": None,
        }
    ordered = sorted(values)
    return {
        "count": len(values),
        "min": round(min(values), 4),
        "p10": _percentile(ordered, 0.10),
        "p25": _percentile(ordered, 0.25),
        "median": round(median(values), 4),
        "p75": _percentile(ordered, 0.75),
        "p90": _percentile(ordered, 0.90),
        "max": round(max(values), 4),
        "mean": round(mean(values), 4),
        "stdev": round(pstdev(values), 4) if len(values) >= 2 else None,
    }


def _session_label(time_text: str, session_windows: dict[str, tuple[str, str]] | None = None) -> str:
    windows = session_windows or SESSION_WINDOWS_UTC
    t = _parse_time(time_text)
    if t.weekday() >= 5:
        return "OFF_SESSION"
    hhmm = t.strftime("%H:%M")
    matches: list[str] = []
    for label, (start, end) in windows.items():
        if start <= hhmm <= end:
            matches.append(label)
    if not matches:
        return "OFF_SESSION"
    return "+".join(matches)


def _flatten_results(results: Sequence[ReplayResult]) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for result in results:
        for trade in result.trades:
            flattened.append(
                {
                    "symbol": result.symbol,
                    "time": trade.entry_time,
                    "signal_time": trade.signal_time,
                    "direction": trade.direction,
                    "net_r": trade.net_r,
                    "trade": trade,
                }
            )
    flattened.sort(key=lambda row: (_time_key(row["time"]), row["symbol"], row["direction"]))
    return flattened


def _summarize_group(label: str, trades: Sequence[dict[str, Any]]) -> GroupedTradeSummary:
    trade_rs = [float(row["net_r"]) for row in trades]
    return GroupedTradeSummary(
        label=label,
        trades=len(trades),
        metrics=compute_metrics(trade_rs),
        distribution=summarize_returns(trade_rs),
    )


def build_stability_summary(
    results: Sequence[ReplayResult],
    session_windows: dict[str, tuple[str, str]] | None = None,
) -> StabilitySummary:
    flattened = _flatten_results(results)
    if not flattened:
        return StabilitySummary()

    monthly_groups: dict[str, list[dict[str, Any]]] = {}
    yearly_groups: dict[str, list[dict[str, Any]]] = {}
    session_groups: dict[str, list[dict[str, Any]]] = {}
    symbol_groups: dict[str, list[dict[str, Any]]] = {}
    direction_groups: dict[str, list[dict[str, Any]]] = {}

    for row in flattened:
        time = _parse_time(row["time"])
        monthly_groups.setdefault(time.strftime("%Y-%m"), []).append(row)
        yearly_groups.setdefault(time.strftime("%Y"), []).append(row)
        session_groups.setdefault(_session_label(row["signal_time"], session_windows), []).append(row)
        symbol_groups.setdefault(str(row["symbol"]), []).append(row)
        direction_groups.setdefault(str(row["direction"]), []).append(row)

    def build(groups: dict[str, list[dict[str, Any]]]) -> tuple[GroupedTradeSummary, ...]:
        items = [
            _summarize_group(label, rows)
            for label, rows in sorted(groups.items(), key=lambda item: item[0])
        ]
        return tuple(items)

    return StabilitySummary(
        monthly=build(monthly_groups),
        yearly=build(yearly_groups),
        session=build(session_groups),
        symbol=build(symbol_groups),
        direction=build(direction_groups),
    )


def _subset_result(result: ReplayResult, start_index: int, end_index: int, label: str) -> ReplayResult:
    signals = tuple(
        signal
        for signal in result.signals
        if start_index <= signal.index <= end_index
    )
    trades = tuple(
        trade
        for trade in result.trades
        if start_index <= trade.signal_index <= end_index
    )
    caveat = result.caveat if trades else f"{label} slice produced no trades."
    return ReplayResult(
        contract_path=result.contract_path,
        symbol=result.symbol,
        status=result.status,
        caveat=caveat,
        signals=signals,
        trades=trades,
        metrics=compute_metrics([trade.net_r for trade in trades]),
        assumptions=dict(result.assumptions),
    )


def _evaluate_window_gate(
    oos_result: ReplayResult,
    walk_forward: Sequence[WalkForwardWindowResult],
    min_oos_trades: int,
    min_walk_forward_windows: int,
    min_positive_window_ratio: float,
) -> tuple[str, tuple[str, ...]]:
    reasons: list[str] = []
    oos_trades = int(oos_result.metrics.get("total_trades") or 0)
    oos_pf = oos_result.metrics.get("profit_factor")
    oos_expectancy = oos_result.metrics.get("expectancy_r")
    oos_sharpe = oos_result.metrics.get("sharpe_ratio")

    if oos_trades < min_oos_trades:
        reasons.append(f"out-of-sample trades below minimum ({oos_trades} < {min_oos_trades})")
    if oos_pf is None or (isinstance(oos_pf, (int, float)) and oos_pf <= 1.0):
        reasons.append("out-of-sample profit factor is not above 1.0")
    if oos_expectancy is None or (isinstance(oos_expectancy, (int, float)) and oos_expectancy <= 0):
        reasons.append("out-of-sample expectancy is not positive")
    if oos_sharpe is None:
        reasons.append("out-of-sample sharpe ratio is unavailable")

    if len(walk_forward) < min_walk_forward_windows:
        reasons.append(
            f"insufficient walk-forward windows ({len(walk_forward)} < {min_walk_forward_windows})"
        )
    positive_windows = [
        window
        for window in walk_forward
        if (window.result.metrics.get("expectancy_r") or 0) > 0
    ]
    if walk_forward:
        ratio = len(positive_windows) / len(walk_forward)
        if ratio < min_positive_window_ratio:
            reasons.append(
                f"positive walk-forward window ratio below minimum ({ratio:.2f} < {min_positive_window_ratio:.2f})"
            )

    status = "READY_FOR_ROBUSTNESS_VALIDATION" if not reasons else "BLOCKED"
    return status, tuple(reasons)


def evaluate_validation_gate(
    oos_result: ReplayResult,
    walk_forward: Sequence[WalkForwardWindowResult],
    min_oos_trades: int = 10,
    min_walk_forward_windows: int = 3,
    min_positive_window_ratio: float = 0.5,
) -> tuple[str, tuple[str, ...]]:
    """Public wrapper for the approval gate logic."""
    return _evaluate_window_gate(
        oos_result,
        walk_forward,
        min_oos_trades=min_oos_trades,
        min_walk_forward_windows=min_walk_forward_windows,
        min_positive_window_ratio=min_positive_window_ratio,
    )


def run_statistical_validation_from_paths(
    contract_path: str,
    m5_path: str,
    h1_path: str | None = None,
    d1_path: str | None = None,
    symbol: str = "ST-C1",
    split_ratio: float = 0.7,
    train_bars: int | None = None,
    test_bars: int | None = None,
    step_bars: int | None = None,
    min_oos_trades: int = 10,
    min_walk_forward_windows: int = 3,
    min_positive_window_ratio: float = 0.5,
    bootstrap_resamples: int = 1000,
) -> StatisticalValidationResult:
    engine = HistoricalReplayEngine(contract_path=contract_path)
    m5, h1, d1 = engine.load_series(m5_path, h1_path=h1_path, d1_path=d1_path)
    full_result = engine.replay(m5, h1=h1, d1=d1, symbol=symbol)

    m5_is, m5_oos, split_time = _split_series_by_ratio(m5, split_ratio)
    h1_is = _series_between(h1, end_time=split_time, end_inclusive=False)
    h1_oos = _series_between(h1, start_time=split_time)
    d1_is = _series_between(d1, end_time=split_time, end_inclusive=False)
    d1_oos = _series_between(d1, start_time=split_time)

    in_sample = engine.replay(m5_is, h1=h1_is, d1=d1_is, symbol=symbol)
    out_of_sample = engine.replay(m5_oos, h1=h1_oos, d1=d1_oos, symbol=symbol)
    split = DatasetSplitResult(
        split_ratio=split_ratio,
        split_time=split_time,
        in_sample=in_sample,
        out_of_sample=out_of_sample,
    )

    train_bars = train_bars or max(engine.warmup_bars * 3, len(m5) // 2)
    test_bars = test_bars or max(engine.warmup_bars, len(m5) // 5)
    step_bars = step_bars or test_bars

    walk_forward: list[WalkForwardWindowResult] = []
    fold = 1
    start = 0
    while start + train_bars + test_bars <= len(m5):
        train_start_index = start
        train_end_index = start + train_bars - 1
        test_start_index = train_end_index + 1
        test_end_index = test_start_index + test_bars - 1
        test_slice = m5[test_start_index : test_end_index + 1]
        if len(test_slice) < test_bars:
            break
        test_start_time = test_slice[0]["time"]
        test_end_time = test_slice[-1]["time"]
        h1_test = _series_between(h1, start_time=test_start_time, end_time=test_end_time)
        d1_test = _series_between(d1, start_time=test_start_time, end_time=test_end_time)
        window_result = engine.replay(test_slice, h1=h1_test, d1=d1_test, symbol=symbol)
        walk_forward.append(
            WalkForwardWindowResult(
                fold=fold,
                train_start=_timestamp_string(m5[train_start_index]["time"]),
                train_end=_timestamp_string(m5[train_end_index]["time"]),
                test_start=_timestamp_string(test_start_time),
                test_end=_timestamp_string(test_end_time),
                result=window_result,
            )
        )
        fold += 1
        start += step_bars

    stability = build_stability_summary([full_result], session_windows=engine.session_windows)
    overall_metrics = dict(full_result.metrics)
    return_distribution = summarize_returns(full_result.trade_rs)
    bootstrap_expectancy_ci = _bootstrap_mean_ci(full_result.trade_rs, resamples=bootstrap_resamples)
    status, reasons = _evaluate_window_gate(
        out_of_sample,
        walk_forward,
        min_oos_trades=min_oos_trades,
        min_walk_forward_windows=min_walk_forward_windows,
        min_positive_window_ratio=min_positive_window_ratio,
    )
    assumptions = {
        "split_ratio": split_ratio,
        "split_time": split_time,
        "train_bars": train_bars,
        "test_bars": test_bars,
        "step_bars": step_bars,
        "bootstrap_resamples": bootstrap_resamples,
        "entry": "next candle after signal",
        "execution": "closed-candle replay only",
        "no_lookahead": True,
    }
    caveat = out_of_sample.caveat or full_result.caveat
    return StatisticalValidationResult(
        contract_path=contract_path,
        status=status,
        caveat=caveat,
        full_result=full_result,
        split=split,
        walk_forward=tuple(walk_forward),
        stability=stability,
        overall_metrics=overall_metrics,
        return_distribution=return_distribution,
        bootstrap_expectancy_ci=bootstrap_expectancy_ci,
        gate_reasons=reasons,
        assumptions=assumptions,
    )


def _format_metric(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        if math.isinf(value):
            return "inf"
        return f"{value:.4f}"
    return str(value)


def _write_group_table(title: str, summaries: Sequence[GroupedTradeSummary]) -> list[str]:
    lines = [f"### {title}", "", "| Label | Trades | PF | Sharpe | Max DD | Expectancy |", "|---|---:|---:|---:|---:|---:|"]
    if not summaries:
        lines.append("| None | 0 | None | None | None | None |")
        lines.append("")
        return lines
    for summary in summaries:
        metrics = summary.metrics
        lines.append(
            "| {label} | {trades} | {pf} | {sharpe} | {dd} | {exp} |".format(
                label=summary.label,
                trades=summary.trades,
                pf=_format_metric(metrics.get("profit_factor")),
                sharpe=_format_metric(metrics.get("sharpe_ratio")),
                dd=_format_metric(metrics.get("maximum_drawdown_r")),
                exp=_format_metric(metrics.get("expectancy_r")),
            )
        )
    lines.append("")
    return lines


def write_statistical_validation_report(
    result: StatisticalValidationResult,
    path: str = "reports/ST-C1_STATISTICAL_VALIDATION_REPORT.md",
) -> str:
    split = result.split
    lines = [
        "# ST-C1 Statistical Validation Report",
        "",
        f"- Contract: `{result.contract_path}`",
        f"- Status: `{result.status}`",
        f"- Caveat: `{result.caveat or 'None'}`",
        f"- Gate reasons: `{len(result.gate_reasons)}`",
        "",
        "## Result",
        "",
        "READY_FOR_ROBUSTNESS_VALIDATION" if result.status == "READY_FOR_ROBUSTNESS_VALIDATION" else "BLOCKED",
        "",
        "## Gate Reasons",
        "",
    ]
    if result.gate_reasons:
        lines.extend(f"- {reason}" for reason in result.gate_reasons)
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Overall Metrics",
            "",
        ]
    )
    for key in ("total_trades", "win_rate_pct", "profit_factor", "expectancy_r", "average_r", "maximum_drawdown_r", "sharpe_ratio"):
        lines.append(f"- {key}: `{_format_metric(result.overall_metrics.get(key))}`")
    lines.extend(
        [
            "",
            "## Return Distribution",
            "",
        ]
    )
    for key in ("count", "min", "p10", "p25", "median", "p75", "p90", "max", "mean", "stdev"):
        lines.append(f"- {key}: `{_format_metric(result.return_distribution.get(key))}`")
    lines.extend(
        [
            "",
            "## Bootstrap Expectancy CI",
            "",
            f"- Lower: `{_format_metric(result.bootstrap_expectancy_ci[0])}`",
            f"- Upper: `{_format_metric(result.bootstrap_expectancy_ci[1])}`",
            "",
            "## Data Split Validation",
            "",
            f"- Split ratio: `{split.split_ratio}`",
            f"- Split time: `{split.split_time}`",
            "",
            "### In-Sample",
            "",
            f"- Trades: `{split.in_sample.metrics.get('total_trades')}`",
            f"- PF: `{_format_metric(split.in_sample.metrics.get('profit_factor'))}`",
            f"- Sharpe: `{_format_metric(split.in_sample.metrics.get('sharpe_ratio'))}`",
            f"- Max DD: `{_format_metric(split.in_sample.metrics.get('maximum_drawdown_r'))}`",
            f"- Expectancy: `{_format_metric(split.in_sample.metrics.get('expectancy_r'))}`",
            "",
            "### Out-of-Sample",
            "",
            f"- Trades: `{split.out_of_sample.metrics.get('total_trades')}`",
            f"- PF: `{_format_metric(split.out_of_sample.metrics.get('profit_factor'))}`",
            f"- Sharpe: `{_format_metric(split.out_of_sample.metrics.get('sharpe_ratio'))}`",
            f"- Max DD: `{_format_metric(split.out_of_sample.metrics.get('maximum_drawdown_r'))}`",
            f"- Expectancy: `{_format_metric(split.out_of_sample.metrics.get('expectancy_r'))}`",
            "",
            "## Walk Forward Validation",
            "",
        ]
    )
    lines.append("| Fold | Train Period | Test Period | Trades | PF | Sharpe | Max DD | Expectancy |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|")
    if result.walk_forward:
        for window in result.walk_forward:
            lines.append(
                "| {fold} | {train_start} -> {train_end} | {test_start} -> {test_end} | {trades} | {pf} | {sharpe} | {dd} | {exp} |".format(
                    fold=window.fold,
                    train_start=window.train_start,
                    train_end=window.train_end,
                    test_start=window.test_start,
                    test_end=window.test_end,
                    trades=window.result.metrics.get("total_trades"),
                    pf=_format_metric(window.result.metrics.get("profit_factor")),
                    sharpe=_format_metric(window.result.metrics.get("sharpe_ratio")),
                    dd=_format_metric(window.result.metrics.get("maximum_drawdown_r")),
                    exp=_format_metric(window.result.metrics.get("expectancy_r")),
                )
            )
    else:
        lines.append("| None | None | None | 0 | None | None | None | None |")
    lines.extend(
        [
            "",
            "## Stability Tests",
            "",
        ]
    )
    lines.extend(_write_group_table("Monthly", result.stability.monthly))
    lines.extend(_write_group_table("Yearly", result.stability.yearly))
    lines.extend(_write_group_table("Session", result.stability.session))
    lines.extend(_write_group_table("Symbol", result.stability.symbol))
    lines.extend(_write_group_table("Long/Short", result.stability.direction))
    lines.extend(
        [
            "## Assumptions",
            "",
        ]
    )
    for key, value in result.assumptions.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(
        [
            "",
            "## Status",
            "",
            "READY_FOR_ROBUSTNESS_VALIDATION" if result.status == "READY_FOR_ROBUSTNESS_VALIDATION" else "BLOCKED",
        ]
    )
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
