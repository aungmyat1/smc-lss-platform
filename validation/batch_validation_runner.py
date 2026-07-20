#!/usr/bin/env python3
"""Batch runner for resumable ST-C1 real-data replay validation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import time
import tempfile
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from validation.historical_replay_engine import (
    HistoricalReplayEngine,
    ReplayResult,
    SignalRecord,
    TradeRecord,
    CandidateRecord,
)
from validation.performance_metrics import compute_metrics
from validation.statistical_validation import build_stability_summary
from symbol_metadata import resolve_symbol


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT_PATH = ROOT / "strategies" / "candidates" / "ST-C1_v1.yaml"
DEFAULT_REPORT_PATH = ROOT / "reports" / "ST-C1_REAL_DATA_STATISTICAL_VALIDATION.md"
DEFAULT_CACHE_DIR = ROOT / "validation" / "cache"
CACHE_SCHEMA_VERSION = 2


@dataclass(frozen=True)
class ValidationTarget:
    symbol: str
    timeframe: str
    m5_path: str
    h1_path: str | None = None
    d1_path: str | None = None
    source_symbol: str | None = None

    @property
    def display_symbol(self) -> str:
        return self.symbol


@dataclass(frozen=True)
class ValidationProgress:
    symbol: str
    timeframe: str
    candles_processed: int
    total_candles: int
    signals_detected: int
    trades_generated: int
    elapsed_seconds: float
    phase: str


@dataclass(frozen=True)
class BatchValidationResult:
    target: ValidationTarget
    cache_path: str
    dataset_hash: str
    runner_fingerprint: str
    strategy_version: str
    execution_params: dict[str, Any]
    result: ReplayResult
    candles_processed: int
    signals_detected: int
    trades_generated: int
    elapsed_seconds: float
    resumed: bool
    cache_hit: bool
    complete: bool


def _sha256_file(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _combine_hashes(parts: Sequence[str]) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(part.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def _signal_to_dict(signal: SignalRecord) -> dict[str, Any]:
    return {
        "index": signal.index,
        "time": signal.time,
        "direction": signal.direction,
        "entry": signal.entry,
        "stop": signal.stop,
        "target": signal.target,
        "structure_key": signal.structure_key,
        "reason_codes": list(signal.reason_codes),
        "structure_identity": signal.structure_identity,
        "canonical_symbol": signal.canonical_symbol,
        "source_symbol": signal.source_symbol,
        "sweep_time": signal.sweep_time,
        "sweep_level": signal.sweep_level,
        "poi_type": signal.poi_type,
        "poi_time": signal.poi_time,
        "poi_low": signal.poi_low,
        "poi_high": signal.poi_high,
        "confirmation_time": signal.confirmation_time,
        "choch_time": signal.choch_time,
        "choch_direction": signal.choch_direction,
        "choch_break_level": signal.choch_break_level,
        "choch_reason": signal.choch_reason,
    }


def _trade_to_dict(trade: TradeRecord) -> dict[str, Any]:
    return {
        "signal_index": trade.signal_index,
        "signal_time": trade.signal_time,
        "entry_index": trade.entry_index,
        "entry_time": trade.entry_time,
        "exit_index": trade.exit_index,
        "exit_time": trade.exit_time,
        "direction": trade.direction,
        "entry": trade.entry,
        "stop": trade.stop,
        "target": trade.target,
        "exit_price": trade.exit_price,
        "gross_r": trade.gross_r,
        "cost_r": trade.cost_r,
        "net_r": trade.net_r,
        "outcome": trade.outcome,
        "structure_key": trade.structure_key,
        "symbol_metadata_version": trade.symbol_metadata_version,
        "spread_price": trade.spread_price,
        "spread_points": trade.spread_points,
        "spread_pips": trade.spread_pips,
        "entry_slippage_price": trade.entry_slippage_price,
        "exit_slippage_price": trade.exit_slippage_price,
        "slippage_price_round_trip": trade.slippage_price_round_trip,
        "commission_usd_round_turn": trade.commission_usd_round_turn,
        "commission": trade.commission,
        "spread_r": trade.spread_r,
        "slippage_r": trade.slippage_r,
        "commission_r": trade.commission_r,
        "swap_r": trade.swap_r,
        "price_cost_round_trip": trade.price_cost_round_trip,
        "total_cost": trade.total_cost,
        "total_cost_r": trade.total_cost_r,
        "partial_taken": trade.partial_taken,
        "break_even_activated": trade.break_even_activated,
        "ambiguous_bar": trade.ambiguous_bar,
        "unresolved_open_position": trade.unresolved_open_position,
        "management_events": list(trade.management_events),
    }


def _signal_from_dict(payload: dict[str, Any]) -> SignalRecord:
    return SignalRecord(
        index=int(payload["index"]),
        time=str(payload["time"]),
        direction=str(payload["direction"]),
        entry=float(payload["entry"]),
        stop=float(payload["stop"]),
        target=float(payload["target"]),
        structure_key=str(payload["structure_key"]),
        reason_codes=tuple(str(item) for item in payload.get("reason_codes", [])),
        structure_identity=str(payload.get("structure_identity", "")),
        canonical_symbol=str(payload.get("canonical_symbol", "")),
        source_symbol=str(payload.get("source_symbol", "")),
        sweep_time=str(payload.get("sweep_time", "")),
        sweep_level=float(payload.get("sweep_level", 0.0)),
        poi_type=str(payload.get("poi_type", "")),
        poi_time=str(payload.get("poi_time", "")),
        poi_low=float(payload.get("poi_low", 0.0)),
        poi_high=float(payload.get("poi_high", 0.0)),
        confirmation_time=str(payload.get("confirmation_time", "")),
        choch_time=str(payload.get("choch_time", "")),
        choch_direction=str(payload.get("choch_direction", "")),
        choch_break_level=float(payload.get("choch_break_level", 0.0)),
        choch_reason=str(payload.get("choch_reason", "")),
    )


def _trade_from_dict(payload: dict[str, Any]) -> TradeRecord:
    return TradeRecord(
        signal_index=int(payload["signal_index"]),
        signal_time=str(payload["signal_time"]),
        entry_index=int(payload["entry_index"]),
        entry_time=str(payload["entry_time"]),
        exit_index=int(payload["exit_index"]),
        exit_time=str(payload["exit_time"]),
        direction=str(payload["direction"]),
        entry=float(payload["entry"]),
        stop=float(payload["stop"]),
        target=float(payload["target"]),
        exit_price=float(payload["exit_price"]),
        gross_r=float(payload["gross_r"]),
        cost_r=float(payload["cost_r"]),
        net_r=float(payload["net_r"]),
        outcome=str(payload["outcome"]),
        structure_key=str(payload["structure_key"]),
        symbol_metadata_version=str(payload.get("symbol_metadata_version", "symbol-metadata-v1")),
        spread_price=float(payload.get("spread_price", 0.0)),
        spread_points=float(payload.get("spread_points", 0.0)),
        spread_pips=float(payload.get("spread_pips", 0.0)),
        entry_slippage_price=float(payload.get("entry_slippage_price", 0.0)),
        exit_slippage_price=float(payload.get("exit_slippage_price", 0.0)),
        slippage_price_round_trip=float(payload.get("slippage_price_round_trip", 0.0)),
        commission_usd_round_turn=float(payload.get("commission_usd_round_turn", payload.get("commission", 0.0))),
        commission=float(payload.get("commission", 0.0)),
        spread_r=float(payload.get("spread_r", 0.0)),
        slippage_r=float(payload.get("slippage_r", 0.0)),
        commission_r=float(payload.get("commission_r", 0.0)),
        swap_r=float(payload.get("swap_r", 0.0)),
        price_cost_round_trip=float(payload.get("price_cost_round_trip", payload.get("total_cost", 0.0))),
        total_cost=float(payload.get("total_cost", 0.0)),
        total_cost_r=float(payload.get("total_cost_r", 0.0)),
        partial_taken=bool(payload.get("partial_taken", False)),
        break_even_activated=bool(payload.get("break_even_activated", False)),
        ambiguous_bar=bool(payload.get("ambiguous_bar", False)),
        unresolved_open_position=bool(payload.get("unresolved_open_position", False)),
        management_events=tuple(dict(item) for item in payload.get("management_events", [])),
    )


def _result_to_dict(result: ReplayResult) -> dict[str, Any]:
    return {
        "contract_path": result.contract_path,
        "symbol": result.symbol,
        "status": result.status,
        "caveat": result.caveat,
        "signals": [_signal_to_dict(signal) for signal in result.signals],
        "trades": [_trade_to_dict(trade) for trade in result.trades],
        "rejected_candidates": [asdict(item) for item in result.rejected_candidates],
        "management_events": list(result.management_events),
        "funnel_counts": dict(getattr(result, "funnel_counts", {})),
        "metrics": dict(result.metrics),
        "assumptions": dict(result.assumptions),
        "symbol_metadata": dict(result.symbol_metadata),
    }


def _result_from_dict(payload: dict[str, Any]) -> ReplayResult:
    return ReplayResult(
        contract_path=str(payload["contract_path"]),
        symbol=str(payload["symbol"]),
        status=str(payload["status"]),
        caveat=payload.get("caveat"),
        signals=tuple(_signal_from_dict(item) for item in payload.get("signals", [])),
        trades=tuple(_trade_from_dict(item) for item in payload.get("trades", [])),
        rejected_candidates=tuple(CandidateRecord(**item) for item in payload.get("rejected_candidates", [])),
        management_events=tuple(dict(item) for item in payload.get("management_events", [])),
        funnel_counts=dict(payload.get("funnel_counts", {})),
        metrics=dict(payload.get("metrics", {})),
        assumptions=dict(payload.get("assumptions", {})),
        symbol_metadata=dict(payload.get("symbol_metadata", {})),
    )


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        tmp_path.replace(path)
    except PermissionError:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def _format_seconds(value: float) -> str:
    return f"{value:.1f}s"


def _default_progress_sink(progress: ValidationProgress) -> None:
    print(
        f"[{progress.symbol} {progress.timeframe}] "
        f"candles={progress.candles_processed}/{progress.total_candles} "
        f"signals={progress.signals_detected} "
        f"trades={progress.trades_generated} "
        f"elapsed={_format_seconds(progress.elapsed_seconds)} "
        f"phase={progress.phase}",
        flush=True,
    )


def _default_funnel_counts() -> dict[str, int]:
    return {
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
        "censored_end_of_data": 0,
        "rejected_session": 0,
        "rejected_signal": 0,
        "rejected_bias": 0,
        "rejected_sweep": 0,
        "rejected_poi": 0,
        "rejected_risk": 0,
        "rejected_target": 0,
    }


@dataclass
class _RuntimeState:
    next_index: int
    consumed: set[str] = field(default_factory=set)
    signals: list[SignalRecord] = field(default_factory=list)
    trades: list[TradeRecord] = field(default_factory=list)
    rejected_candidates: list[CandidateRecord] = field(default_factory=list)
    funnel_counts: dict[str, int] = field(default_factory=dict)
    candles_processed: int = 0
    signals_detected: int = 0
    trades_generated: int = 0
    elapsed_seconds: float = 0.0
    complete: bool = False


class BatchValidationRunner:
    def __init__(
        self,
        contract_path: str | os.PathLike[str] = DEFAULT_CONTRACT_PATH,
        cache_dir: str | os.PathLike[str] = DEFAULT_CACHE_DIR,
        report_path: str | os.PathLike[str] = DEFAULT_REPORT_PATH,
        *,
        spread_points: float = 25.0,
        slippage_points: float = 3.0,
        commission_r: float = 0.0,
        point_size: float = 0.0001,
        stop_buffer_atr_mult: float = 0.15,
        warmup_bars: int = 40,
        progress_every: int = 1000,
        progress_sink: Callable[[ValidationProgress], None] | None = None,
    ) -> None:
        self.contract_path = str(contract_path)
        self.cache_dir = Path(cache_dir)
        self.report_path = Path(report_path)
        self.cost_profile_path = ROOT / "config" / "research_costs.yaml"
        self.progress_every = max(1, int(progress_every))
        self.progress_sink = progress_sink or _default_progress_sink
        self.engine = HistoricalReplayEngine(
            contract_path=self.contract_path,
            spread_points=spread_points,
            slippage_points=slippage_points,
            commission_r=commission_r,
            point_size=point_size,
            stop_buffer_atr_mult=stop_buffer_atr_mult,
            warmup_bars=warmup_bars,
        )
        self.execution_params = {
            "spread_points": spread_points,
            "slippage_points": slippage_points,
            "commission_r": commission_r,
            "point_size": point_size,
            "stop_buffer_atr_mult": stop_buffer_atr_mult,
            "warmup_bars": warmup_bars,
        }
        self.strategy_version = self._strategy_version()
        self.runner_fingerprint = self._runner_fingerprint()

    def _strategy_version(self) -> str:
        contract = self.engine.contract
        strategy = contract.get("strategy", {}) if isinstance(contract, dict) else {}
        version = strategy.get("version")
        digest = _sha256_file(self.contract_path)
        if version:
            return f"{version}:{digest[:16]}"
        return digest

    def _dataset_hash(self, target: ValidationTarget) -> str:
        paths = [target.m5_path]
        if target.h1_path:
            paths.append(target.h1_path)
        if target.d1_path:
            paths.append(target.d1_path)
        return _combine_hashes(_sha256_file(path) for path in paths)

    def _runner_fingerprint(self) -> str:
        components = [
            _sha256_file(Path(__file__).resolve()),
            _sha256_file(ROOT / "validation" / "historical_replay_engine.py"),
            _sha256_file(ROOT / "validation" / "performance_metrics.py"),
            _sha256_file(ROOT / "src" / "smc_engine.py"),
            _sha256_file(self.contract_path),
            _sha256_file(self.cost_profile_path) if self.cost_profile_path.exists() else "missing",
        ]
        return _combine_hashes(components)

    def _cache_path(self, target: ValidationTarget, dataset_hash: str) -> Path:
        safe_symbol = target.display_symbol.replace("/", "_")
        safe_tf = target.timeframe.replace("/", "_")
        source_symbol = target.source_symbol or target.display_symbol
        canonical_symbol = resolve_symbol(source_symbol).canonical_symbol if source_symbol else target.display_symbol
        metadata = self.engine._metadata_for_symbol(source_symbol)
        cache_parts = [
            self.runner_fingerprint,
            _stable_json(self.execution_params),
            self.strategy_version,
            dataset_hash,
            source_symbol,
            canonical_symbol,
            getattr(metadata, "version", "unknown"),
            _stable_json(self.engine.assumptions if hasattr(self.engine, "assumptions") else {}),
        ]
        exec_hash = _combine_hashes(cache_parts)
        return self.cache_dir / f"{safe_symbol}_{safe_tf}_{exec_hash[:24]}.json"

    def _load_state(self, cache_path: Path) -> dict[str, Any] | None:
        return _load_json(cache_path)

    def _save_state(self, cache_path: Path, payload: dict[str, Any]) -> None:
        _atomic_write_json(cache_path, payload)

    def _build_state_payload(
        self,
        target: ValidationTarget,
        dataset_hash: str,
        cache_path: Path,
        state: _RuntimeState,
        *,
        complete: bool,
        result: ReplayResult | None = None,
        elapsed_seconds: float | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": CACHE_SCHEMA_VERSION,
            "complete": complete,
            "target": asdict(target),
            "dataset_hash": dataset_hash,
            "runner_fingerprint": self.runner_fingerprint,
            "strategy_version": self.strategy_version,
            "execution_params": dict(self.execution_params),
            "cache_path": str(cache_path),
            "next_index": state.next_index,
            "candles_processed": state.candles_processed,
            "signals_detected": state.signals_detected,
            "trades_generated": state.trades_generated,
            "elapsed_seconds": elapsed_seconds if elapsed_seconds is not None else state.elapsed_seconds,
            "consumed": sorted(state.consumed),
            "signals": [_signal_to_dict(signal) for signal in state.signals],
            "trades": [_trade_to_dict(trade) for trade in state.trades],
            "rejected_candidates": [asdict(item) for item in state.rejected_candidates],
            "funnel_counts": dict(state.funnel_counts),
        }
        if result is not None:
            payload["result"] = _result_to_dict(result)
        return payload

    def _cache_is_compatible(self, payload: dict[str, Any], dataset_hash: str) -> bool:
        return (
            int(payload.get("schema_version", 0)) == CACHE_SCHEMA_VERSION
            and payload.get("dataset_hash") == dataset_hash
            and payload.get("runner_fingerprint") == self.runner_fingerprint
            and payload.get("strategy_version") == self.strategy_version
            and payload.get("execution_params") == dict(self.execution_params)
        )

    def _state_from_payload(self, payload: dict[str, Any]) -> _RuntimeState:
        state = _RuntimeState(
            next_index=int(payload.get("next_index", self.engine.warmup_bars)),
            consumed=set(str(item) for item in payload.get("consumed", [])),
            signals=[_signal_from_dict(item) for item in payload.get("signals", [])],
            trades=[_trade_from_dict(item) for item in payload.get("trades", [])],
            rejected_candidates=[CandidateRecord(**item) for item in payload.get("rejected_candidates", [])],
            funnel_counts={str(key): int(value) for key, value in payload.get("funnel_counts", {}).items()},
            candles_processed=int(payload.get("candles_processed", 0)),
            signals_detected=int(payload.get("signals_detected", 0)),
            trades_generated=int(payload.get("trades_generated", 0)),
            elapsed_seconds=float(payload.get("elapsed_seconds", 0.0)),
            complete=bool(payload.get("complete", False)),
        )
        return state

    def _normalize_signal(self, signal: SignalRecord, target: ValidationTarget) -> SignalRecord:
        canonical_symbol = self.engine._metadata_for_symbol(target.source_symbol or target.display_symbol).canonical_symbol
        source_symbol = target.source_symbol or target.display_symbol
        structure_identity = signal.structure_identity or signal.structure_key
        return replace(
            signal,
            canonical_symbol=signal.canonical_symbol or canonical_symbol,
            source_symbol=signal.source_symbol or source_symbol,
            structure_identity=structure_identity,
        )

    def _emit_progress(self, target: ValidationTarget, state: _RuntimeState, total_candles: int, start_time: float, phase: str) -> None:
        progress = ValidationProgress(
            symbol=target.display_symbol,
            timeframe=target.timeframe,
            candles_processed=state.candles_processed,
            total_candles=total_candles,
            signals_detected=state.signals_detected,
            trades_generated=state.trades_generated,
            elapsed_seconds=time.perf_counter() - start_time,
            phase=phase,
        )
        self.progress_sink(progress)

    def _final_result(self, target: ValidationTarget, state: _RuntimeState, cache_path: Path, start_time: float) -> BatchValidationResult:
        funnel_counts = dict(state.funnel_counts)
        funnel_counts["executed_trade"] = int(funnel_counts.get("executed_trade", len(state.trades)))
        funnel_counts["duplicate_structure"] = int(funnel_counts.get("duplicate_structure", 0))
        funnel_counts["skipped_open_trade"] = int(funnel_counts.get("skipped_open_trade", 0))
        result = ReplayResult(
            contract_path=self.contract_path,
            symbol=target.display_symbol,
            status="READY_FOR_STATISTICAL_VALIDATION",
            caveat=None if state.trades else "No trades were generated on the supplied replay data.",
            signals=tuple(state.signals),
            trades=tuple(state.trades),
            rejected_candidates=tuple(state.rejected_candidates),
            management_events=tuple(event for trade in state.trades for event in trade.management_events),
            funnel_counts=funnel_counts,
            metrics=compute_metrics([trade.net_r for trade in state.trades]),
            assumptions={
                "entry": "next candle after signal",
                "exit": "contract-defined SL/TP with stop-first conservative fills",
                "strategy_id": str(self.engine.contract.get("strategy", {}).get("strategy_id", "ST-C1")) if isinstance(self.engine.contract, dict) else "ST-C1",
                "strategy_version": self.strategy_version,
                "costs": {
                    **dict(self.execution_params),
                    "slippage_points_per_side": float(self.execution_params["slippage_points"]),
                    "slippage_points_round_trip": float(self.execution_params["slippage_points"]) * 2.0,
                },
                "dataset_hash": self._dataset_hash(target),
                "source_symbol": target.source_symbol or target.display_symbol,
                "runner_fingerprint": self.runner_fingerprint,
            },
            symbol_metadata=self.engine._metadata_for_symbol(target.source_symbol or target.display_symbol).snapshot(),
        )
        elapsed = time.perf_counter() - start_time
        payload = self._build_state_payload(target, result.assumptions["dataset_hash"], cache_path, state, complete=True, result=result, elapsed_seconds=elapsed)
        self._save_state(cache_path, payload)
        return BatchValidationResult(
            target=target,
            cache_path=str(cache_path),
            dataset_hash=str(result.assumptions["dataset_hash"]),
            runner_fingerprint=self.runner_fingerprint,
            strategy_version=self.strategy_version,
            execution_params=dict(self.execution_params),
            result=result,
            candles_processed=state.candles_processed,
            signals_detected=state.signals_detected,
            trades_generated=state.trades_generated,
            elapsed_seconds=elapsed,
            resumed=False,
            cache_hit=False,
            complete=True,
        )

    def run_job(
        self,
        target: ValidationTarget,
        *,
        resume: bool = True,
    ) -> BatchValidationResult:
        dataset_hash = self._dataset_hash(target)
        cache_path = self._cache_path(target, dataset_hash)
        cached = self._load_state(cache_path) if resume else None
        if cached and cached.get("complete") and self._cache_is_compatible(cached, dataset_hash):
            result = _result_from_dict(cached["result"])
            return BatchValidationResult(
                target=target,
                cache_path=str(cache_path),
                dataset_hash=dataset_hash,
                runner_fingerprint=str(cached.get("runner_fingerprint", self.runner_fingerprint)),
                strategy_version=self.strategy_version,
                execution_params=dict(self.execution_params),
                result=result,
                candles_processed=int(cached.get("candles_processed", 0)),
                signals_detected=int(cached.get("signals_detected", len(result.signals))),
                trades_generated=int(cached.get("trades_generated", len(result.trades))),
                elapsed_seconds=float(cached.get("elapsed_seconds", 0.0)),
                resumed=False,
                cache_hit=True,
                complete=True,
            )

        m5, h1, d1 = self.engine.load_series(target.m5_path, h1_path=target.h1_path, d1_path=target.d1_path)
        state = self._state_from_payload(cached) if cached and self._cache_is_compatible(cached, dataset_hash) else _RuntimeState(next_index=self.engine.warmup_bars)
        if state.next_index < self.engine.warmup_bars:
            state.next_index = self.engine.warmup_bars
        state.complete = False
        start_time = time.perf_counter()
        resumed = bool(cached) and bool(cached.get("complete") is False)
        next_checkpoint = max(state.next_index, self.engine.warmup_bars) + self.progress_every

        self._emit_progress(target, state, len(m5), start_time, phase="resume" if resumed else "start")
        state.funnel_counts = {**_default_funnel_counts(), **state.funnel_counts}
        i = state.next_index
        while i < len(m5) - 1:
            previous_trade_count = state.trades_generated
            signal = self.engine.generate_signal(
                i,
                m5,
                h1=h1,
                d1=d1,
                symbol=target.source_symbol or target.display_symbol,
                rejected_candidates=state.rejected_candidates,
                funnel_counts=state.funnel_counts,
            )
            if signal is None:
                i += 1
                state.candles_processed = i
            else:
                if signal.structure_key in state.consumed:
                    state.funnel_counts["duplicate_structure"] = int(state.funnel_counts.get("duplicate_structure", 0)) + 1
                    i += 1
                    state.candles_processed = i
                else:
                    signal = self._normalize_signal(signal, target)
                    state.consumed.add(signal.structure_key)
                    state.signals.append(signal)
                    state.signals_detected += 1
                    trade = self.engine.simulate_trade(signal, m5, entry_index=i + 1, symbol=target.source_symbol or target.display_symbol)
                    state.trades.append(trade)
                    state.trades_generated += 1
                    state.funnel_counts["executed_trade"] = int(state.funnel_counts.get("executed_trade", 0)) + 1
                    if trade.unresolved_open_position:
                        state.funnel_counts["skipped_open_trade"] = int(state.funnel_counts.get("skipped_open_trade", 0)) + 1
                    if trade.outcome == "CENSORED_END_OF_DATA":
                        state.funnel_counts["censored_end_of_data"] = int(state.funnel_counts.get("censored_end_of_data", 0)) + 1
                    i = max(trade.exit_index + 1, i + 1)
                    state.candles_processed = i
            state.next_index = i
            state.elapsed_seconds = time.perf_counter() - start_time

            should_checkpoint = state.candles_processed >= next_checkpoint or state.trades_generated > previous_trade_count
            if should_checkpoint:
                payload = self._build_state_payload(target, dataset_hash, cache_path, state, complete=False, elapsed_seconds=state.elapsed_seconds)
                self._save_state(cache_path, payload)
                self._emit_progress(target, state, len(m5), start_time, phase="running")
                next_checkpoint = state.candles_processed + self.progress_every

        state.complete = True
        state.funnel_counts = {**_default_funnel_counts(), **state.funnel_counts}
        assert int(state.funnel_counts.get("executed_trade", len(state.trades))) == len(state.trades)
        result = ReplayResult(
            contract_path=self.contract_path,
            symbol=target.display_symbol,
            status="READY_FOR_STATISTICAL_VALIDATION",
            caveat=None if state.trades else "No trades were generated on the supplied replay data.",
            signals=tuple(state.signals),
            trades=tuple(state.trades),
            rejected_candidates=tuple(state.rejected_candidates),
            management_events=tuple(event for trade in state.trades for event in trade.management_events),
            funnel_counts=dict(state.funnel_counts),
            metrics=compute_metrics([trade.net_r for trade in state.trades]),
            assumptions={
                "entry": "next candle after signal",
                "exit": "contract-defined SL/TP with stop-first conservative fills",
                "strategy_id": str(self.engine.contract.get("strategy", {}).get("strategy_id", "ST-C1")) if isinstance(self.engine.contract, dict) else "ST-C1",
                "strategy_version": self.strategy_version,
                "costs": {
                    **dict(self.execution_params),
                    "slippage_points_per_side": float(self.execution_params["slippage_points"]),
                    "slippage_points_round_trip": float(self.execution_params["slippage_points"]) * 2.0,
                },
                "dataset_hash": dataset_hash,
                "source_symbol": target.source_symbol or target.display_symbol,
                "runner_fingerprint": self.runner_fingerprint,
            },
            symbol_metadata=self.engine._metadata_for_symbol(target.source_symbol or target.display_symbol).snapshot(),
        )
        payload = self._build_state_payload(target, dataset_hash, cache_path, state, complete=True, result=result, elapsed_seconds=time.perf_counter() - start_time)
        self._save_state(cache_path, payload)
        self._emit_progress(target, state, len(m5), start_time, phase="complete")
        return BatchValidationResult(
            target=target,
            cache_path=str(cache_path),
            dataset_hash=dataset_hash,
            runner_fingerprint=self.runner_fingerprint,
            strategy_version=self.strategy_version,
            execution_params=dict(self.execution_params),
            result=result,
            candles_processed=state.candles_processed,
            signals_detected=state.signals_detected,
            trades_generated=state.trades_generated,
            elapsed_seconds=state.elapsed_seconds,
            resumed=resumed,
            cache_hit=False,
            complete=True,
        )

    def run_all(self, targets: Iterable[ValidationTarget], *, resume: bool = True) -> tuple[BatchValidationResult, ...]:
        results = [self.run_job(target, resume=resume) for target in targets]
        self.write_report(results)
        return tuple(results)

    def write_report(self, results: Sequence[BatchValidationResult], path: str | os.PathLike[str] | None = None) -> str:
        report_path = Path(path) if path is not None else self.report_path
        completed = [item for item in results if item.complete]
        replay_results = [item.result for item in completed]
        combined_metrics = compute_metrics([trade.net_r for result in replay_results for trade in result.trades])
        trade_breakdown = {
            "trade_count": sum(len(result.trades) for result in replay_results),
            "gross_r": round(sum(float(trade.gross_r) for result in replay_results for trade in result.trades), 6),
            "net_r": round(sum(float(trade.net_r) for result in replay_results for trade in result.trades), 6),
            "spread_r": round(sum(float(trade.spread_r) for result in replay_results for trade in result.trades), 6),
            "slippage_r": round(sum(float(trade.slippage_r) for result in replay_results for trade in result.trades), 6),
            "commission_r": round(sum(float(trade.commission_r) for result in replay_results for trade in result.trades), 6),
            "swap_r": round(sum(float(trade.swap_r) for result in replay_results for trade in result.trades), 6),
            "total_cost_drag_r": round(sum(float(trade.cost_r) for result in replay_results for trade in result.trades), 6),
        }
        stability = build_stability_summary(replay_results, session_windows=self.engine.session_windows)
        total_trades = int(combined_metrics.get("total_trades") or 0)
        ready = bool(completed) and len(completed) == len(results) and total_trades > 0
        funnel_totals: dict[str, int] = {}
        for item in replay_results:
            for key, value in getattr(item, "funnel_counts", {}).items():
                funnel_totals[key] = funnel_totals.get(key, 0) + int(value)
        funnel_totals["executed_trade"] = total_trades
        assert funnel_totals["executed_trade"] == total_trades
        lines = [
            "# ST-C1 Real Data Statistical Validation Report",
            "",
            f"- Contract: `{self.contract_path}`",
            f"- Strategy version: `{self.strategy_version}`",
            f"- Runner fingerprint: `{self.runner_fingerprint}`",
            f"- Status: `{ 'READY_FOR_ROBUSTNESS_VALIDATION' if ready else 'BLOCKED' }`",
            f"- Replay jobs completed: `{len(completed)}/{len(results)}`",
            "",
            "## Dataset",
            "",
        ]
        for item in completed:
            source = item.target.source_symbol or item.target.display_symbol
            lines.append(f"- {item.target.display_symbol} {item.target.timeframe}: `{source}`")
            lines.append(f"  - Dataset hash: `{item.dataset_hash}`")
            lines.append(f"  - Cache: `{item.cache_path}`")
            lines.append(f"  - Candles processed: `{item.candles_processed}`")
            lines.append(f"  - Signals detected: `{item.signals_detected}`")
            lines.append(f"  - Trades generated: `{item.trades_generated}`")
            lines.append(f"  - Elapsed: `{_format_seconds(item.elapsed_seconds)}`")
        lines.extend(
            [
                "",
                "## Performance",
                "",
                "| Symbol | Timeframe | Trades | Win% | PF | Expectancy | Sharpe | Max DD | Resumed | Cache Hit |",
                "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
            ]
        )
        for item in completed:
            metrics = item.result.metrics
            lines.append(
                "| {symbol} | {timeframe} | {trades} | {win} | {pf} | {exp} | {sharpe} | {dd} | {resumed} | {cache_hit} |".format(
                    symbol=item.target.display_symbol,
                    timeframe=item.target.timeframe,
                    trades=metrics.get("total_trades"),
                    win=_format_metric(metrics.get("win_rate_pct")),
                    pf=_format_metric(metrics.get("profit_factor")),
                    exp=_format_metric(metrics.get("expectancy_r")),
                    sharpe=_format_metric(metrics.get("sharpe_ratio")),
                    dd=_format_metric(metrics.get("maximum_drawdown_r")),
                    resumed=str(item.resumed),
                    cache_hit=str(item.cache_hit),
                )
            )
        lines.extend(
            [
                "",
                "### Combined Metrics",
                "",
            ]
        )
        for key in ("total_trades", "win_rate_pct", "profit_factor", "expectancy_r", "average_r", "maximum_drawdown_r", "sharpe_ratio"):
            lines.append(f"- {key}: `{_format_metric(combined_metrics.get(key))}`")
        lines.extend(
            [
                "",
                "### R Breakdown",
                "",
            ]
        )
        for key in ("trade_count", "gross_r", "net_r", "spread_r", "slippage_r", "commission_r", "swap_r", "total_cost_drag_r"):
            lines.append(f"- {key}: `{_format_metric(trade_breakdown.get(key))}`")
        lines.extend(
            [
                "",
                "### Funnel",
                "",
            ]
        )
        for key in ("candidate_ready", "duplicate_structure", "skipped_open_trade", "executed_trade"):
            lines.append(f"- {key}: `{funnel_totals.get(key, 0)}`")
        lines.extend(
            [
                "",
                "## Stability",
                "",
                "### Monthly",
                "",
            ]
        )
        lines.extend(_write_summary_table(stability.monthly))
        lines.extend(["### Yearly", ""])
        lines.extend(_write_summary_table(stability.yearly))
        lines.extend(["### Session", ""])
        lines.extend(_write_summary_table(stability.session))
        lines.extend(["### Symbol", ""])
        lines.extend(_write_summary_table(stability.symbol))
        lines.extend(["### Long/Short", ""])
        lines.extend(_write_summary_table(stability.direction))
        lines.extend(
            [
                "",
                "## Assumptions",
                "",
            ]
        )
        for item in completed:
            lines.append(f"- {item.target.display_symbol}: `{_stable_json(item.result.assumptions)}`")
        lines.extend(
            [
                "",
                "## Status",
                "",
                "READY_FOR_ROBUSTNESS_VALIDATION" if ready else "BLOCKED",
            ]
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return str(report_path)


def _format_metric(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _write_summary_table(summaries: Sequence[Any]) -> list[str]:
    lines = ["| Label | Trades | PF | Sharpe | Max DD | Expectancy |", "|---|---:|---:|---:|---:|---:|"]
    if not summaries:
        lines.append("| None | 0 | None | None | None | None |")
        lines.append("")
        return lines
    for summary in summaries:
        lines.append(
            "| {label} | {trades} | {pf} | {sharpe} | {dd} | {exp} |".format(
                label=summary.label,
                trades=summary.trades,
                pf=_format_metric(summary.metrics.get("profit_factor")),
                sharpe=_format_metric(summary.metrics.get("sharpe_ratio")),
                dd=_format_metric(summary.metrics.get("maximum_drawdown_r")),
                exp=_format_metric(summary.metrics.get("expectancy_r")),
            )
        )
    lines.append("")
    return lines


def default_targets() -> tuple[ValidationTarget, ...]:
    return (
        ValidationTarget(
            symbol="EURUSD",
            timeframe="M5",
            m5_path=str(ROOT / "data" / "EURUSD_M5.csv"),
            h1_path=str(ROOT / "data" / "EURUSD_H1.csv"),
            d1_path=str(ROOT / "data" / "EURUSD_D1.csv"),
            source_symbol="EURUSD",
        ),
        ValidationTarget(
            symbol="XAUUSD",
            timeframe="M5",
            m5_path=str(ROOT / "data" / "XAUUSD-VIP_M5.csv"),
            h1_path=str(ROOT / "data" / "XAUUSD-VIP_H1.csv"),
            d1_path=str(ROOT / "data" / "XAUUSD-VIP_D1.csv"),
            source_symbol="XAUUSD-VIP",
        ),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run resumable ST-C1 real-data replay validation.")
    parser.add_argument("--report", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE_DIR))
    parser.add_argument("--progress-every", type=int, default=1000)
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    runner = BatchValidationRunner(
        cache_dir=args.cache_dir,
        report_path=args.report,
        progress_every=args.progress_every,
    )
    results = runner.run_all(default_targets(), resume=not args.no_resume)
    print(runner.write_report(results, path=args.report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
