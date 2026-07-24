"""Diagnose ST-C2 v1.2 GBPUSD S1-G2 R1 liquidity failures.

Stage 1 research tooling only. This script reads local CSV data and writes a
Markdown diagnostic report. It never imports broker or execution paths.
"""
from __future__ import annotations

import bisect
import datetime as dt
from collections import Counter
from pathlib import Path
from typing import Any

from src import smc_engine as e
from validation import st_c2_reference as stc2


REPORT_PATH = Path("reports/ST-C2_V1.2_GBPUSD_R1_DIAGNOSTIC.md")
EXPECTED_MINUTES = {"htf": 240, "mf": 15, "ltf": 3}


def _parse_time(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y-%m-%d %H:%M")


def _pip(symbol: str) -> float:
    return 0.01 if symbol.endswith("JPY") else 0.0001


def _data_profile(name: str, candles: list[dict[str, Any]]) -> dict[str, Any]:
    times = [_parse_time(c["time"]) for c in candles]
    duplicates = len(times) - len(set(times))
    expected = dt.timedelta(minutes=EXPECTED_MINUTES[name])
    gaps = []
    weekend_bars = 0
    flat = 0
    bad_ohlc = 0
    for i, candle in enumerate(candles):
        if times[i].weekday() >= 5:
            weekend_bars += 1
        if candle["open"] == candle["high"] == candle["low"] == candle["close"]:
            flat += 1
        if not (candle["low"] <= min(candle["open"], candle["close"]) <= max(candle["open"], candle["close"]) <= candle["high"]):
            bad_ohlc += 1
        if i > 0:
            delta = times[i] - times[i - 1]
            if delta != expected:
                gaps.append((candles[i - 1]["time"], candle["time"], int(delta.total_seconds() / 60)))
    return {
        "bars": len(candles),
        "start": candles[0]["time"] if candles else None,
        "end": candles[-1]["time"] if candles else None,
        "duplicates": duplicates,
        "flat": flat,
        "bad_ohlc": bad_ohlc,
        "weekend_bars": weekend_bars,
        "gap_count": len(gaps),
        "gap_examples": gaps[:10],
    }


def _window(candles: list[dict[str, Any]], times: list[dt.datetime], asof: dt.datetime, lookback: int) -> list[dict[str, Any]]:
    end = bisect.bisect_right(times, asof)
    if end < lookback:
        return []
    return candles[end - lookback:end]


def _liquidity_population(candles: list[dict[str, Any]], spec: dict[str, Any]) -> dict[str, Any]:
    k = int(spec["pipeline"]["htf_structure"]["htf_swing_fractal_k_h4"])
    wick = float(spec["pipeline"]["liquidity_stage"]["detect_sweep"]["wick_ratio_min"])
    tol = float(spec["pipeline"]["liquidity_stage"]["detect_external_liquidity"]["equal_highs_tolerance_pips"]) * _pip("GBPUSD")
    sweeps = e.liquidity_sweeps(candles, k=k, min_wick_ratio=wick)
    pools = e.liquidity_pools(candles, k=k, tol=tol)
    highs, lows = e.swings(candles, k=k)
    return {
        "swing_highs": len(highs),
        "swing_lows": len(lows),
        "liquidity_pools": len(pools),
        "sweeps": len(sweeps),
        "bull_sweeps": sum(1 for s in sweeps if s["dir"] == "bull"),
        "bear_sweeps": sum(1 for s in sweeps if s["dir"] == "bear"),
        "last_sweeps": sweeps[-10:],
    }


def _sweep_sensitivity(candles: list[dict[str, Any]], spec: dict[str, Any]) -> list[tuple[float, int]]:
    k = int(spec["pipeline"]["htf_structure"]["htf_swing_fractal_k_h4"])
    return [(wick, len(e.liquidity_sweeps(candles, k=k, min_wick_ratio=wick))) for wick in (0.2, 0.3, 0.4, 0.5, 0.6)]


def _rolling_rejections(candles: dict[str, list[dict[str, Any]]], spec: dict[str, Any]) -> dict[str, Any]:
    htf_lookback = int(spec["pipeline"]["liquidity_stage"]["detect_external_liquidity"]["lookback_bars_htf"])
    mf_lookback = max(96, int(spec["pipeline"]["fvg_stage"]["mf_fvg"]["max_distance_pips"]) * 10)
    ltf_lookback = max(80, int(spec["pipeline"]["ltf_confirmation_stage"]["stronger_choch"]["max_setup_bars"]) * 4)
    max_age = int(spec["pipeline"]["liquidity_stage"]["detect_sweep"]["max_sweep_age_bars_htf"])
    wick = float(spec["pipeline"]["liquidity_stage"]["detect_sweep"]["wick_ratio_min"])
    k = int(spec["pipeline"]["htf_structure"]["htf_swing_fractal_k_h4"])

    htf_times = [_parse_time(c["time"]) for c in candles["htf"]]
    mf_times = [_parse_time(c["time"]) for c in candles["mf"]]
    ltf_times = [_parse_time(c["time"]) for c in candles["ltf"]]
    rejections = Counter()
    sweep_counts = Counter()
    sweep_ages = []
    samples = []
    checked = 0
    start = min(len(candles["ltf"]), ltf_lookback)
    for end in range(start, len(candles["ltf"]) + 1):
        asof = ltf_times[end - 1]
        htf = _window(candles["htf"], htf_times, asof, htf_lookback)
        mf = _window(candles["mf"], mf_times, asof, mf_lookback)
        ltf = candles["ltf"][end - ltf_lookback:end]
        if not htf or not mf:
            continue
        checked += 1
        sweeps = e.liquidity_sweeps(htf, k=k, min_wick_ratio=wick)
        recent = [s for s in sweeps if len(htf) - 1 - int(s["i"]) <= max_age]
        sweep_counts[(len(sweeps), len(recent))] += 1
        if sweeps:
            sweep_ages.append(len(htf) - 1 - int(sweeps[-1]["i"]))
        result = stc2.analyze_windows(htf, mf, ltf, spec=spec)
        rejections[result.rejection_code or result.decision] += 1
        if result.rejection_code == "R1" and len(samples) < 10:
            samples.append({
                "asof": candles["ltf"][end - 1]["time"],
                "htf_start": htf[0]["time"],
                "htf_end": htf[-1]["time"],
                "htf_bars": len(htf),
                "sweeps_in_window": len(sweeps),
                "recent_sweeps": len(recent),
                "last_sweep_age_h4": (len(htf) - 1 - int(sweeps[-1]["i"])) if sweeps else None,
                "last_sweep": sweeps[-1] if sweeps else None,
            })
    return {
        "checked": checked,
        "rejections": dict(rejections),
        "sweep_count_shapes": dict(sweep_counts),
        "min_last_sweep_age": min(sweep_ages) if sweep_ages else None,
        "median_last_sweep_age": sorted(sweep_ages)[len(sweep_ages) // 2] if sweep_ages else None,
        "max_last_sweep_age": max(sweep_ages) if sweep_ages else None,
        "samples": samples,
    }


def build_report() -> str:
    spec = stc2.load_spec()
    candles = stc2.load_required_candles()
    profiles = {name: _data_profile(name, rows) for name, rows in candles.items()}
    liquidity = _liquidity_population(candles["htf"], spec)
    sensitivity = _sweep_sensitivity(candles["htf"], spec)
    rolling = _rolling_rejections(candles, spec)

    data_flags = []
    for name, profile in profiles.items():
        if profile["duplicates"] or profile["bad_ohlc"] or profile["flat"]:
            data_flags.append(name)
    classification = "LIQUIDITY_DETECTOR_OR_RULE_SET"
    scope_note = "S1-G2 diagnostic after existence-scan liquidity failure."
    if data_flags:
        classification = "DATA_QUALITY_REVIEW_REQUIRED"
    elif liquidity["sweeps"] == 0:
        classification = "LIQUIDITY_DETECTOR_FIDELITY_OR_RULE_SET_MISMATCH"
    if rolling["rejections"].get("SIGNAL", 0) > 0:
        classification = "DATA_COVERAGE_CAUSE_CONFIRMED"
        scope_note = "S1-G2 diagnostic after the initial short M3 history produced a false zero-signal result."

    lines = [
        "# ST-C2 v1.2 GBPUSD R1 Liquidity Diagnostic",
        "",
        f"**Scope:** {scope_note}",
        "",
        "## Classification",
        "",
        f"**{classification}**",
        "",
        "The initial existence scan failed at R1 when only about nine days of M3 history were available. After extending the M1-derived M3 coverage, qualifying GBPUSD signals appear.",
        "",
        "## Data Coverage",
        "",
        "| TF | Bars | Range | Duplicates | Flat | Bad OHLC | Weekend Bars | Gap Count |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for name, profile in profiles.items():
        lines.append(
            f"| {name} | {profile['bars']} | {profile['start']} -> {profile['end']} | "
            f"{profile['duplicates']} | {profile['flat']} | {profile['bad_ohlc']} | "
            f"{profile['weekend_bars']} | {profile['gap_count']} |"
        )
    lines += ["", "### Gap Examples", ""]
    for name, profile in profiles.items():
        lines.append(f"**{name}:**")
        if profile["gap_examples"]:
            for prev_time, next_time, minutes in profile["gap_examples"]:
                lines.append(f"- `{prev_time}` -> `{next_time}` = {minutes} minutes")
        else:
            lines.append("- none")
        lines.append("")

    lines += [
        "## Liquidity-Only Scan",
        "",
        f"- H4 swing highs: `{liquidity['swing_highs']}`",
        f"- H4 swing lows: `{liquidity['swing_lows']}`",
        f"- H4 equal high/low pools at 5 pips tolerance: `{liquidity['liquidity_pools']}`",
        f"- H4 sweeps at wick ratio 0.6: `{liquidity['sweeps']}`",
        f"- Bull sweeps: `{liquidity['bull_sweeps']}`",
        f"- Bear sweeps: `{liquidity['bear_sweeps']}`",
        "",
        "### Wick-Ratio Sensitivity",
        "",
        "| Wick ratio | Sweep count |",
        "|---:|---:|",
    ]
    for wick, count in sensitivity:
        lines.append(f"| {wick:.1f} | {count} |")

    lines += [
        "",
        "## Rolling R1 Evidence",
        "",
        f"- Checked windows: `{rolling['checked']}`",
        f"- Rejection counts: `{rolling['rejections']}`",
        f"- Last-sweep age range in H4 bars: `{rolling['min_last_sweep_age']}` / `{rolling['median_last_sweep_age']}` / `{rolling['max_last_sweep_age']}`",
        "",
        "## Ten Rejected Window Samples",
        "",
    ]
    for sample in rolling["samples"]:
        lines += [
            f"### `{sample['asof']}`",
            "",
            f"- H4 range: `{sample['htf_start']}` -> `{sample['htf_end']}` ({sample['htf_bars']} bars)",
            f"- Sweeps in 300-bar H4 window: `{sample['sweeps_in_window']}`",
            f"- Recent sweeps within max age: `{sample['recent_sweeps']}`",
            f"- Last sweep age H4 bars: `{sample['last_sweep_age_h4']}`",
            f"- Last sweep: `{sample['last_sweep']}`",
            "",
        ]

    lines += [
        "## Governance Decision",
        "",
        "Do not advance to S1-G3. The next action is to review the R1 evidence and decide whether to repair data coverage, improve detector fidelity inside the frozen spec, or open a new candidate/RCR for GBPUSD rule-set calibration.",
        "",
        "Execution, demo, live, broker, and production authority remain blocked.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(REPORT_PATH)


if __name__ == "__main__":
    print(build_report())
