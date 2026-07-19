"""Tests for the ST-C1 statistical validation scaffold."""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from validation.historical_replay_engine import ReplayResult, SignalRecord, TradeRecord  # noqa: E402
from validation.statistical_validation import (  # noqa: E402
    DatasetSplitResult,
    GroupedTradeSummary,
    StatisticalValidationResult,
    StabilitySummary,
    WalkForwardWindowResult,
    build_stability_summary,
    evaluate_validation_gate,
    run_statistical_validation_from_paths,
    summarize_returns,
    write_statistical_validation_report,
)


CONTRACT_PATH = os.path.join(ROOT, "strategies", "candidates", "ST-C1_v1.yaml")


def _iso(value: datetime) -> str:
    return value.replace(microsecond=0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def _make_trade(
    index: int,
    signal_time: datetime,
    direction: str,
    net_r: float,
    symbol: str,
    outcome: str | None = None,
) -> tuple[SignalRecord, TradeRecord]:
    entry_time = signal_time + timedelta(minutes=5)
    exit_time = entry_time + timedelta(minutes=5)
    entry = 100.0 + index
    risk = 1.0
    if direction == "long":
        stop = entry - risk
        target = entry + 2.0 * risk
        gross_r = net_r + 0.1
        exit_price = entry + gross_r * risk
    else:
        stop = entry + risk
        target = entry - 2.0 * risk
        gross_r = net_r + 0.1
        exit_price = entry - gross_r * risk
    signal = SignalRecord(
        index=index,
        time=_iso(signal_time),
        direction=direction,
        entry=round(entry, 5),
        stop=round(stop, 5),
        target=round(target, 5),
        structure_key=f"{symbol}:{index}",
        reason_codes=("TEST",),
    )
    trade = TradeRecord(
        signal_index=index,
        signal_time=_iso(signal_time),
        entry_index=index + 1,
        entry_time=_iso(entry_time),
        exit_index=index + 2,
        exit_time=_iso(exit_time),
        direction=direction,
        entry=round(entry, 5),
        stop=round(stop, 5),
        target=round(target, 5),
        exit_price=round(exit_price, 5),
        gross_r=round(gross_r, 4),
        cost_r=0.1,
        net_r=round(net_r, 4),
        outcome=outcome or ("TARGET" if net_r >= 0 else "STOP"),
        structure_key=f"{symbol}:{index}",
    )
    return signal, trade


def _make_result(symbol: str, rows: list[tuple[datetime, str, float]], status: str = "READY_FOR_STATISTICAL_VALIDATION") -> ReplayResult:
    signals: list[SignalRecord] = []
    trades: list[TradeRecord] = []
    for index, (signal_time, direction, net_r) in enumerate(rows):
        signal, trade = _make_trade(index, signal_time, direction, net_r, symbol)
        signals.append(signal)
        trades.append(trade)
    return ReplayResult(
        contract_path=CONTRACT_PATH,
        symbol=symbol,
        status=status,
        caveat=None,
        signals=tuple(signals),
        trades=tuple(trades),
        metrics={},
        assumptions={"entry": "next candle after signal"},
    )


def _attach_metrics(result: ReplayResult) -> ReplayResult:
    from validation.performance_metrics import compute_metrics

    return ReplayResult(
        contract_path=result.contract_path,
        symbol=result.symbol,
        status=result.status,
        caveat=result.caveat,
        signals=result.signals,
        trades=result.trades,
        metrics=compute_metrics([trade.net_r for trade in result.trades]),
        assumptions=dict(result.assumptions),
    )


def test_statistical_summaries_cover_all_required_axes(tmp_path):
    eur_rows = [
        (datetime(2025, 12, 2, 6, 5), "long", 1.4),
        (datetime(2025, 12, 3, 12, 35), "short", 0.9),
        (datetime(2025, 12, 10, 6, 10), "long", -1.1),
        (datetime(2026, 1, 4, 11, 45), "long", 1.6),
        (datetime(2026, 1, 10, 6, 20), "short", 1.2),
        (datetime(2026, 1, 15, 12, 0), "long", 0.8),
    ]
    xau_rows = [
        (datetime(2026, 6, 3, 6, 15), "long", 1.5),
        (datetime(2026, 6, 5, 12, 15), "short", 1.1),
        (datetime(2026, 6, 12, 6, 45), "long", -0.9),
        (datetime(2026, 7, 2, 12, 30), "short", 1.8),
        (datetime(2026, 7, 6, 6, 10), "long", 1.0),
        (datetime(2026, 7, 15, 12, 40), "short", 0.7),
    ]
    eur = _attach_metrics(_make_result("EURUSD", eur_rows))
    xau = _attach_metrics(_make_result("XAUUSD", xau_rows))

    stability = build_stability_summary([eur, xau])
    assert len(stability.monthly) >= 4
    assert len(stability.yearly) == 2
    assert {item.label for item in stability.session} >= {"London", "NewYork"}
    assert {item.label for item in stability.symbol} == {"EURUSD", "XAUUSD"}
    assert {item.label for item in stability.direction} == {"long", "short"}

    summary = summarize_returns(eur.trade_rs + xau.trade_rs)
    assert summary["count"] == 12
    assert summary["median"] is not None
    assert summary["p25"] is not None


def test_statistical_validation_gate_and_report(tmp_path):
    eur_rows = [
        (datetime(2025, 12, 2, 6, 5), "long", 1.4),
        (datetime(2025, 12, 3, 12, 35), "short", 0.9),
        (datetime(2025, 12, 10, 6, 10), "long", -1.1),
        (datetime(2026, 1, 4, 11, 45), "long", 1.6),
        (datetime(2026, 1, 10, 6, 20), "short", 1.2),
        (datetime(2026, 1, 15, 12, 0), "long", 0.8),
    ]
    xau_rows = [
        (datetime(2026, 6, 3, 6, 15), "long", 1.5),
        (datetime(2026, 6, 5, 12, 15), "short", 1.1),
        (datetime(2026, 6, 12, 6, 45), "long", -0.9),
        (datetime(2026, 7, 2, 12, 30), "short", 1.8),
        (datetime(2026, 7, 6, 6, 10), "long", 1.0),
        (datetime(2026, 7, 15, 12, 40), "short", 0.7),
    ]
    full_result = _attach_metrics(_make_result("COMBINED", eur_rows + xau_rows))
    in_sample = _attach_metrics(_make_result("EURUSD", eur_rows))
    out_of_sample = _attach_metrics(_make_result("XAUUSD", xau_rows))

    walk_forward = (
        WalkForwardWindowResult(
            fold=1,
            train_start="2025-12-01T00:00:00Z",
            train_end="2025-12-31T23:55:00Z",
            test_start="2026-06-01T00:00:00Z",
            test_end="2026-06-15T23:55:00Z",
            result=_attach_metrics(_make_result("XAUUSD", xau_rows[:2])),
        ),
        WalkForwardWindowResult(
            fold=2,
            train_start="2025-12-01T00:00:00Z",
            train_end="2026-06-15T23:55:00Z",
            test_start="2026-06-16T00:00:00Z",
            test_end="2026-07-05T23:55:00Z",
            result=_attach_metrics(_make_result("XAUUSD", xau_rows[2:4])),
        ),
        WalkForwardWindowResult(
            fold=3,
            train_start="2025-12-01T00:00:00Z",
            train_end="2026-07-05T23:55:00Z",
            test_start="2026-07-06T00:00:00Z",
            test_end="2026-07-31T23:55:00Z",
            result=_attach_metrics(_make_result("XAUUSD", xau_rows[4:])),
        ),
    )
    split = DatasetSplitResult(
        split_ratio=0.5,
        split_time="2026-06-03T06:15:00Z",
        in_sample=in_sample,
        out_of_sample=out_of_sample,
    )
    stability = build_stability_summary([in_sample, out_of_sample])
    status, reasons = evaluate_validation_gate(
        out_of_sample,
        walk_forward,
        min_oos_trades=4,
        min_walk_forward_windows=2,
        min_positive_window_ratio=0.5,
    )

    result = StatisticalValidationResult(
        contract_path=CONTRACT_PATH,
        status=status,
        caveat=None,
        full_result=full_result,
        split=split,
        walk_forward=walk_forward,
        stability=stability,
        overall_metrics=full_result.metrics,
        return_distribution=summarize_returns(full_result.trade_rs),
        bootstrap_expectancy_ci=(0.5, 1.2),
        gate_reasons=reasons,
        assumptions={"split_ratio": 0.5},
    )

    report_path = tmp_path / "ST-C1_STATISTICAL_VALIDATION_REPORT.md"
    write_statistical_validation_report(result, path=str(report_path))

    text = report_path.read_text(encoding="utf-8")
    assert "ST-C1 Statistical Validation Report" in text
    assert "READY_FOR_ROBUSTNESS_VALIDATION" in text
    assert "Data Split Validation" in text
    assert "Walk Forward Validation" in text
    assert "Stability Tests" in text
    assert "EURUSD" in text
    assert "XAUUSD" in text


def test_statistical_validation_blocks_on_insufficient_evidence(tmp_path):
    tiny_rows = [
        (datetime(2026, 6, 3, 6, 15), "long", 0.4),
    ]
    tiny_result = _attach_metrics(_make_result("EURUSD", tiny_rows))
    walk_forward = (
        WalkForwardWindowResult(
            fold=1,
            train_start="2026-06-01T00:00:00Z",
            train_end="2026-06-02T00:00:00Z",
            test_start="2026-06-03T00:00:00Z",
            test_end="2026-06-04T00:00:00Z",
            result=tiny_result,
        ),
    )

    status, reasons = evaluate_validation_gate(
        tiny_result,
        walk_forward,
        min_oos_trades=5,
        min_walk_forward_windows=2,
        min_positive_window_ratio=0.5,
    )

    assert status == "BLOCKED"
    assert any("out-of-sample trades below minimum" in reason for reason in reasons)
    assert any("insufficient walk-forward windows" in reason for reason in reasons)


def test_run_statistical_validation_from_paths_smoke(tmp_path):
    m5_path = tmp_path / "sample_m5.csv"
    h1_path = tmp_path / "sample_h1.csv"

    def write_series(path: Path, start: datetime, step_minutes: int, closes: list[float]) -> None:
        rows = []
        current = start
        prev_close = closes[0]
        for index, close in enumerate(closes):
            open_ = prev_close if index else close
            high = max(open_, close) + 0.2
            low = min(open_, close) - 0.2
            rows.append([_iso(current), round(open_, 5), round(high, 5), round(low, 5), round(close, 5)])
            prev_close = close
            current += timedelta(minutes=step_minutes)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write("time,open,high,low,close\n")
            for row in rows:
                fh.write(",".join(map(str, row)) + "\n")

    write_series(
        m5_path,
        datetime(2026, 7, 17, 6, 0),
        5,
        [95.0, 94.8, 94.6, 94.4, 94.2, 94.1, 94.0, 94.2, 94.4, 94.6, 94.8, 95.0, 95.2, 95.4, 95.6, 95.8],
    )
    write_series(
        h1_path,
        datetime(2026, 7, 17, 6, 0),
        60,
        [95.0, 95.5, 96.0],
    )

    result = run_statistical_validation_from_paths(
        contract_path=CONTRACT_PATH,
        m5_path=str(m5_path),
        h1_path=str(h1_path),
        symbol="EURUSD",
        split_ratio=0.5,
        train_bars=6,
        test_bars=4,
        step_bars=4,
        min_oos_trades=1,
        min_walk_forward_windows=1,
        min_positive_window_ratio=0.0,
        bootstrap_resamples=50,
    )
    report_path = tmp_path / "ST-C1_STATISTICAL_VALIDATION_REPORT.md"
    write_statistical_validation_report(result, path=str(report_path))

    assert report_path.exists()
    assert result.status in {"READY_FOR_ROBUSTNESS_VALIDATION", "BLOCKED"}
    assert "ST-C1 Statistical Validation Report" in report_path.read_text(encoding="utf-8")
