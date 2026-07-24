"""ST-C2 v1.2 GBPUSD reference kernel.

Research-only Stage 1 code. This module must not import broker/MT5 paths and
does not authorize execution. It implements the minimum deterministic detector
slice needed for golden-case tests and the first GBPUSD existence-check pass.
"""
from __future__ import annotations

import datetime as dt
import bisect
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from src import smc_engine as e
from validation.st_c2.structure import structural_context
from validation.st_c2.symbols import load_symbol_metadata, points_to_price


SPEC_PATH = Path("specs/st-c2_v1.2.0.yaml")
REQUIRED_DATA = {
    "htf": Path("data/GBPUSD_H4.csv"),
    "mf": Path("data/GBPUSD_M15.csv"),
    "ltf": Path("data/GBPUSD_M3.csv"),
}


@dataclass(frozen=True)
class StageEvidence:
    stage: str
    passed: bool
    code: str
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DetectionResult:
    decision: str
    symbol: str
    direction: str | None
    rejection_code: str | None
    stages: tuple[StageEvidence, ...]
    signal_time: str | None = None


@dataclass(frozen=True)
class ScanResult:
    decision: str
    checked_windows: int
    first_signal: DetectionResult | None
    rejection_counts: dict[str, int]


def load_spec(path: Path | str = SPEC_PATH) -> dict[str, Any]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected top-level mapping")
    return data


def enabled_symbols(spec: dict[str, Any]) -> list[str]:
    return [
        item["symbol"]
        for item in spec.get("instruments", [])
        if isinstance(item, dict) and item.get("enabled") is True
    ]


def data_availability(paths: dict[str, Path] | None = None) -> dict[str, bool]:
    selected = paths or REQUIRED_DATA
    return {name: path.exists() for name, path in selected.items()}


def missing_data(paths: dict[str, Path] | None = None) -> list[str]:
    return [name for name, exists in data_availability(paths).items() if not exists]


def load_required_candles(paths: dict[str, Path] | None = None) -> dict[str, list[dict[str, Any]]]:
    selected = paths or REQUIRED_DATA
    missing = missing_data(selected)
    if missing:
        raise FileNotFoundError(f"missing required ST-C2 data: {', '.join(missing)}")
    return {name: e.load_candles(path) for name, path in selected.items()}


def _parse_time(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y-%m-%d %H:%M")


def _window_asof(candles: list[dict[str, Any]], asof: dt.datetime, lookback: int) -> list[dict[str, Any]]:
    closed = [c for c in candles if _parse_time(c["time"]) <= asof]
    return closed[-lookback:] if len(closed) >= lookback else []


def _window_asof_indexed(
    candles: list[dict[str, Any]],
    times: list[dt.datetime],
    asof: dt.datetime,
    lookback: int,
) -> list[dict[str, Any]]:
    end = bisect.bisect_right(times, asof)
    if end < lookback:
        return []
    return candles[end - lookback:end]


def _stage(stage: str, passed: bool, code: str, **detail: Any) -> StageEvidence:
    return StageEvidence(stage=stage, passed=passed, code=code, detail=detail)


def _last_sweep(htf: list[dict[str, Any]], spec: dict[str, Any]) -> dict[str, Any] | None:
    params = spec["pipeline"]["liquidity_stage"]["detect_sweep"]
    sweeps = e.liquidity_sweeps(
        htf,
        k=int(spec["pipeline"]["htf_structure"]["htf_swing_fractal_k_h4"]),
        min_wick_ratio=float(params["wick_ratio_min"]),
    )
    max_age = int(params["max_sweep_age_bars_htf"])
    last_index = len(htf) - 1
    recent = [s for s in sweeps if last_index - int(s["i"]) <= max_age]
    return recent[-1] if recent else None


def _bias_from_sweep(sweep: dict[str, Any]) -> str:
    """Deprecated compatibility shim.

    Active S1-G2-GC2 logic derives bias from HTF BOS/CHoCH structural evidence
    in `validation.st_c2.structure.classify_htf_bias`, not from sweep direction.
    """
    return "long" if sweep["dir"] == "bull" else "short"


def _in_discount_or_premium(mf: list[dict[str, Any]], direction: str) -> bool:
    """Deprecated compatibility shim for pre-GC2 tests.

    Active pipeline OTE evaluation uses structural dealing-range identity via
    `validation.st_c2.structure.evaluate_ote_location`.
    """
    high = max(c["high"] for c in mf)
    low = min(c["low"] for c in mf)
    eq = (high + low) / 2.0
    close = mf[-1]["close"]
    return close <= eq if direction == "long" else close >= eq


def _matching_mf_fvg(mf: list[dict[str, Any]], direction: str, spec: dict[str, Any]) -> dict[str, Any] | None:
    want = "bull" if direction == "long" else "bear"
    metadata = load_symbol_metadata("GBPUSD")
    gap_points = Decimal(str(spec["pipeline"]["liquidity_stage"]["poi_gap_reaction"]["gap_min_points"]))
    gap_min = float(points_to_price(gap_points, metadata))
    matches = [f for f in e.fvgs(mf, min_gap=gap_min) if f["dir"] == want]
    return matches[-1] if matches else None


def _ltf_confirmation(ltf: list[dict[str, Any]], direction: str) -> dict[str, Any] | None:
    highs, lows = e.swings(ltf, k=2)
    last = ltf[-1]
    if direction == "long":
        prior_highs = [p for i, p in highs if i < len(ltf) - 1]
        if prior_highs and last["close"] > prior_highs[-1]:
            return {"break_level": prior_highs[-1], "time": last["time"]}
    else:
        prior_lows = [p for i, p in lows if i < len(ltf) - 1]
        if prior_lows and last["close"] < prior_lows[-1]:
            return {"break_level": prior_lows[-1], "time": last["time"]}
    return None


def analyze_windows(
    htf: list[dict[str, Any]],
    mf: list[dict[str, Any]],
    ltf: list[dict[str, Any]],
    *,
    symbol: str = "GBPUSD",
    spec: dict[str, Any] | None = None,
) -> DetectionResult:
    spec = spec or load_spec()
    stages: list[StageEvidence] = []

    configured_symbols = enabled_symbols(spec)
    if configured_symbols != [symbol]:
        stages.append(_stage("config", False, "R6", enabled_symbols=configured_symbols))
        return DetectionResult("NO_SIGNAL", symbol, None, "R6", tuple(stages))

    context = structural_context(htf, mf, spec=spec, symbol=symbol)
    bias = context["bias"]
    direction = bias.direction if bias.direction in {"long", "short"} else None
    if direction is None:
        stages.append(_stage("htf_bias", False, "R2", reason=bias.reason, structural_events=len(context["events"])))
        return DetectionResult("NO_SIGNAL", symbol, None, "R2", tuple(stages))
    stages.append(
        _stage(
            "htf_bias",
            True,
            "PASS",
            direction=direction,
            bias_event_id=bias.bias_event_id,
            evidence_timestamp=bias.bias_evidence_timestamp,
            evidence_type=bias.bias_evidence_type,
            protected_level_id=bias.protected_level_id,
        )
    )

    sweep = context["sweep"]
    if sweep is None or sweep.status != "confirmed":
        reason = None if sweep is None else sweep.metadata.get("detail_reason")
        stages.append(_stage("liquidity", False, "R1", reason=reason or "NO_ELIGIBLE_LIQUIDITY_POOL"))
        return DetectionResult("NO_SIGNAL", symbol, direction, "R1", tuple(stages))
    stages.append(_stage("liquidity", True, "PASS", sweep=sweep.to_dict()))

    ote = context["ote"]
    if ote is None or not ote.ote_eligible:
        stages.append(
            _stage(
                "ote",
                False,
                "R3",
                direction=direction,
                reason=None if ote is None else ote.rejection_detail,
            )
        )
        return DetectionResult("NO_SIGNAL", symbol, direction, "R3", tuple(stages))
    stages.append(_stage("ote", True, "PASS", direction=direction, ote=ote.__dict__))

    fvg = _matching_mf_fvg(mf, direction, spec)
    if fvg is None:
        stages.append(_stage("fvg_alignment", False, "R4", direction=direction))
        return DetectionResult("NO_SIGNAL", symbol, direction, "R4", tuple(stages))
    stages.append(_stage("fvg_alignment", True, "PASS", fvg=fvg))

    confirmation = _ltf_confirmation(ltf, direction)
    if confirmation is None:
        stages.append(_stage("ltf_confirmation", False, "R5", direction=direction))
        return DetectionResult("NO_SIGNAL", symbol, direction, "R5", tuple(stages))
    stages.append(_stage("ltf_confirmation", True, "PASS", confirmation=confirmation))

    stages.append(_stage("risk", True, "PASS", provisional_thresholds=True))
    return DetectionResult("SIGNAL", symbol, direction, None, tuple(stages), signal_time=ltf[-1]["time"])


def scan_history(
    *,
    paths: dict[str, Path] | None = None,
    spec: dict[str, Any] | None = None,
    symbol: str = "GBPUSD",
    max_windows: int | None = None,
) -> ScanResult:
    spec = spec or load_spec()
    candles = load_required_candles(paths)
    htf_lookback = int(spec["pipeline"]["liquidity_stage"]["detect_external_liquidity"]["lookback_bars_htf"])
    mf_lookback = max(96, int(spec["pipeline"]["fvg_stage"]["mf_fvg"]["max_distance_pips"]) * 10)
    ltf_lookback = max(80, int(spec["pipeline"]["ltf_confirmation_stage"]["stronger_choch"]["max_setup_bars"]) * 4)
    ltf = candles["ltf"]
    htf_times = [_parse_time(c["time"]) for c in candles["htf"]]
    mf_times = [_parse_time(c["time"]) for c in candles["mf"]]
    ltf_times = [_parse_time(c["time"]) for c in ltf]
    rejection_counts: dict[str, int] = {}
    checked = 0

    start = min(len(ltf), ltf_lookback)
    for end in range(start, len(ltf) + 1):
        asof = ltf_times[end - 1]
        htf_window = _window_asof_indexed(candles["htf"], htf_times, asof, htf_lookback)
        mf_window = _window_asof_indexed(candles["mf"], mf_times, asof, mf_lookback)
        ltf_window = ltf[end - ltf_lookback:end]
        if not htf_window or not mf_window:
            continue
        result = analyze_windows(htf_window, mf_window, ltf_window, symbol=symbol, spec=spec)
        checked += 1
        if result.decision == "SIGNAL":
            return ScanResult("SIGNAL_FOUND", checked, result, rejection_counts)
        code = result.rejection_code or "NO_CODE"
        rejection_counts[code] = rejection_counts.get(code, 0) + 1
        if max_windows is not None and checked >= max_windows:
            break

    return ScanResult("NO_SIGNAL_FOUND", checked, None, rejection_counts)


def no_broker_import_guard() -> bool:
    text = Path(__file__).read_text(encoding="utf-8").lower()
    forbidden = ("meta" + "trader5", "mt" + "5.", "place" + "_order", "broker" + "_adapter")
    return not any(token in text for token in forbidden)
