#!/usr/bin/env python3
"""G6 population-feasibility latency diagnostics (R2.1 / v3.8).

Pure research diagnostic. Traces, for every G5-qualified candidate POI, the
point-in-time bar index/timestamp of each G6 transition:

    1. POI creation -> POI touch
    2. POI touch -> first qualifying sweep
    3. Sweep -> displacement
    4. Displacement -> close-confirmed CHoCH/BOS
    5. CHoCH/BOS -> permitted retracement
    6. Retracement -> next-bar-open entry

A stage that never resolves is recorded as REJECTED (the full allowed search
window was available and exhausted) or CENSORED (the dataset ended before
the search window could elapse) — these are NOT the same thing and must not
be conflated: a REJECTED stage is evidence the gate is discriminating;
a CENSORED stage is missing information, not a negative result.

THIS MODULE MUST NEVER BE IMPORTED BY A BROKER OR EXECUTION PATH. It exists
solely to produce `reports/diagnostics/*` evidence for research/validation
decisions. It performs no order construction, no MT5 calls, no config
mutation, and asserts nothing about demo/live readiness.

DISCLOSED METHODOLOGY DIFFERENCE FROM THE PRODUCTION ENGINE (versioned here,
not a silent "optimization"): `validation/historical_replay_engine_v37.py`'s
`generate_signal` searches for a POI touch in a window of
`m5_poi_entry_search_bars` M5 bars ENDING AT the current evaluation bar
("today", scanning backward) -- a per-bar, backward-looking convention
inherited from the base engine's bar-by-bar replay loop. This diagnostic
instead traces FORWARD from each POI's own creation bar, up to
`m5_poi_entry_search_bars` bars ahead, which is the natural direction for a
causal-latency measurement (and is what this task's STEP 3 explicitly asks
for: "record ... latency for every transition"). The two are NOT the same
search and can disagree on whether a given POI is ever "touched" within the
window, depending on how far the touch bar sits from an arbitrary "today"
reference versus from the POI's own creation bar. Consequence: this
diagnostic's B0 (poi_entry_to_sweep_max_m5_bars=30) is NOT expected to
reproduce the production engine's true zero-trade B0-equivalent result
bar-for-bar -- see reports/diagnostics/ST_C1_V38_G6_LATENCY_REPORT.md for the
measured effect of this difference, disclosed rather than hidden.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import smc_engine as e  # noqa: E402
import signal_v37 as v37  # noqa: E402

from validation.historical_replay_engine_v37 import HistoricalReplayEngineV37  # noqa: E402
from validation.historical_replay_engine import _is_session_allowed, _parse_time  # noqa: E402


@dataclass(frozen=True)
class G6LatencyRecord:
    candidate_id: str
    symbol: str
    direction: str
    session: str
    year: int
    cell: str
    poi_entry_to_sweep_max_m5_bars: int
    range_id: str
    poi_origin: str
    poi_creation_time: str
    poi_creation_index: int
    poi_touch_time: str | None = None
    poi_touch_index: int | None = None
    sweep_time: str | None = None
    sweep_index: int | None = None
    displacement_start_time: str | None = None
    displacement_start_index: int | None = None
    displacement_end_time: str | None = None
    displacement_end_index: int | None = None
    choch_time: str | None = None
    choch_index: int | None = None
    retrace_time: str | None = None
    retrace_index: int | None = None
    entry_time: str | None = None
    entry_index: int | None = None
    latency_poi_creation_to_touch: int | None = None
    latency_touch_to_sweep: int | None = None
    latency_sweep_to_displacement: int | None = None
    latency_displacement_to_choch: int | None = None
    latency_choch_to_retrace: int | None = None
    latency_retrace_to_entry: int | None = None
    data_cutoff: str = ""
    strategy_version: str = "1.1.0"
    spec_version: str = "3.7"
    code_commit: str = "uncommitted"
    cost_profile_version: int = 1
    final_decision: str = "UNKNOWN"
    primary_rejection_code: str | None = None
    secondary_rejection_codes: tuple[str, ...] = field(default_factory=tuple)


_DISPLACEMENT_KW = dict(atr_period=14, atr_mult=1.5, body_ratio_min=0.5,
                        start_offset_bars=2, max_run_bars=3)
_DISPLACEMENT_TO_CHOCH_MAX = 5
_CHOCH_TO_RETRACE_MAX = 30
_SESSIONS = ["London", "NewYork"]
_SESSION_WINDOWS = {"London": ("06:00", "10:00"), "NewYork": ("11:30", "15:00")}


def _session_label(time_text: str) -> str:
    t = _parse_time(time_text)
    hhmm = t.strftime("%H:%M")
    for name, (start, end) in _SESSION_WINDOWS.items():
        if start <= hhmm <= end:
            return name
    return "OTHER"


def _year_of(time_text: str) -> int:
    return _parse_time(time_text).year


def trace_g6_candidates(
    m5: list[dict[str, Any]],
    h1: list[dict[str, Any]] | None,
    d1: list[dict[str, Any]] | None,
    symbol: str,
    cell: str,
    poi_entry_to_sweep_max_m5_bars: int,
    warmup_bars: int = 40,
    m5_poi_entry_search_bars: int = 3200,
    funnel_counts: dict[str, int] | None = None,
) -> list[G6LatencyRecord]:
    """Walk the full M5 series once, identify each distinct G5-qualified POI
    exactly once (deduped by structure identity), and trace it forward.

    Reuses the engine's own window-sizing/bounding logic (via a throwaway
    HistoricalReplayEngineV37 instance) so this diagnostic sees exactly the
    same H1/D1 context the real engine would have seen at each evaluation
    bar — no separate, drifting window-sizing logic.

    If `funnel_counts` (a dict) is supplied, it is mutated in place with
    G1-G5 walk-level counts (evaluated, rejected_session, rejected_g1,
    rejected_g2, rejected_g5, g5_qualified_distinct_poi).
    """
    def bump(key: str, amount: int = 1) -> None:
        if funnel_counts is not None:
            funnel_counts[key] = int(funnel_counts.get(key, 0)) + amount

    eng = HistoricalReplayEngineV37(
        contract_path=str(ROOT / "strategies" / "candidates" / "ST-C1_v1.1.0.yaml"),
    )
    params = dict(eng.params)
    params["_skip_g4"] = True   # population diagnostic — G4 disabled in all cells, per RCR
    k = int(params.get("swing_lookback_bars", 2))
    n = len(m5)
    seen_poi_keys: set[str] = set()
    records: list[G6LatencyRecord] = []

    data_cutoff = m5[-1]["time"]   # end of the loaded dataset -- see module docstring on data_cutoff semantics
    i = warmup_bars
    while i < n - 1:
        bump("evaluated")
        last_time = m5[i]["time"]
        if not _is_session_allowed(last_time, _SESSIONS, _SESSION_WINDOWS):
            bump("rejected_session")
            i += 1
            continue
        asof_time = m5[i + 1]["time"]
        h1_lookback = max(
            int(params.get("dealing_range_lookback_h1_bars", 40)),
            int(params.get("htf_poi_max_age_h1_bars", 60)), 120)
        d1_lookback = max(int(params.get("d1_gap_max_age_d1_bars", 10)), 20)
        h1_window = eng._bounded_context_window(h1, "H1", asof_time, h1_lookback) if h1 else None
        d1_window = eng._bounded_context_window(d1, "D1", asof_time, d1_lookback) if d1 else None
        if not h1_window or len(h1_window) < 10:
            bump("rejected_g1")
            i += 1
            continue

        g1 = v37.evaluate_g1_bias(h1_window, params)
        if g1["state"] not in ("BULLISH", "BEARISH"):
            bump("rejected_g1")
            i += 1
            continue
        direction = "long" if g1["state"] == "BULLISH" else "short"
        g2 = v37.evaluate_g2_external_structure(h1_window, params)
        if g2 is None:
            bump("rejected_g2")
            i += 1
            continue
        g5 = v37.evaluate_g5_htf_poi(h1_window, d1_window, direction, g2, params)
        if g5 is None:
            bump("rejected_g5")
            i += 1
            continue

        poi_key = f"{symbol}|{direction}|{g5['poi_origin']}|{g5['time']}|{round(g5['low'], 5)}|{round(g5['high'], 5)}"
        if poi_key in seen_poi_keys:
            bump("duplicate_poi")
            i += 1
            continue
        seen_poi_keys.add(poi_key)
        bump("g5_qualified_distinct_poi")

        record = _trace_one_poi(
            m5, i, direction, g5, g2, symbol, cell,
            poi_entry_to_sweep_max_m5_bars, m5_poi_entry_search_bars, k, data_cutoff,
        )
        records.append(record)
        bump(f"g6_{record.final_decision.lower()}")
        i += 1

    return records


def _trace_one_poi(
    m5: list[dict[str, Any]],
    origin_index: int,
    direction: str,
    poi: dict[str, Any],
    dealing_range: dict[str, Any],
    symbol: str,
    cell: str,
    poi_entry_to_sweep_max_m5_bars: int,
    m5_poi_entry_search_bars: int,
    k: int,
    data_cutoff: str,
) -> G6LatencyRecord:
    want = "bull" if direction == "long" else "bear"
    n = len(m5)
    candidate_id = f"{symbol}:{origin_index}:{poi['poi_origin']}"
    base = dict(
        candidate_id=candidate_id, symbol=symbol, direction=direction,
        session=_session_label(m5[origin_index]["time"]), year=_year_of(m5[origin_index]["time"]),
        cell=cell, poi_entry_to_sweep_max_m5_bars=poi_entry_to_sweep_max_m5_bars,
        range_id=dealing_range["range_id"], poi_origin=poi["poi_origin"],
        poi_creation_time=str(poi["time"]), poi_creation_index=origin_index,
        data_cutoff=data_cutoff,
    )

    def censored_or_rejected(search_end: int, stage: str) -> str:
        return "CENSORED_" + stage if search_end >= n - 1 else "REJECTED_" + stage

    # --- Stage 1: POI creation -> touch ---
    touch_search_end = min(origin_index + m5_poi_entry_search_bars, n - 1)
    touch_i = None
    for idx in range(origin_index, touch_search_end + 1):
        c = m5[idx]
        if c["low"] <= poi["high"] and c["high"] >= poi["low"]:
            touch_i = idx
            break
    if touch_i is None:
        decision = censored_or_rejected(touch_search_end, "NO_TOUCH")
        return G6LatencyRecord(**base, final_decision=decision, primary_rejection_code=decision)
    base["latency_poi_creation_to_touch"] = touch_i - origin_index
    base["poi_touch_time"], base["poi_touch_index"] = m5[touch_i]["time"], touch_i

    # --- Stage 2: touch -> first qualifying sweep (the tested variable) ---
    sweep_search_end = min(touch_i + poi_entry_to_sweep_max_m5_bars, n - 1)
    sweeps = [s for s in e.liquidity_sweeps(m5[: sweep_search_end + 1], k, min_wick_ratio=0.5)
              if s["dir"] == want and touch_i <= s["i"] <= sweep_search_end]
    if not sweeps:
        decision = censored_or_rejected(sweep_search_end, "NO_SWEEP")
        return G6LatencyRecord(**base, final_decision=decision, primary_rejection_code=decision)
    sweep_i = sweeps[0]["i"]
    base["latency_touch_to_sweep"] = sweep_i - touch_i
    base["sweep_time"], base["sweep_index"] = m5[sweep_i]["time"], sweep_i

    # --- Stage 3: sweep -> displacement (fixed, not the tested variable) ---
    disp_search_end = min(sweep_i + _DISPLACEMENT_KW["start_offset_bars"] + _DISPLACEMENT_KW["max_run_bars"] + 1, n - 1)
    disp = e.displacement_move(m5[: disp_search_end + 1], sweep_i, want, **_DISPLACEMENT_KW)
    if disp is None:
        decision = censored_or_rejected(disp_search_end, "NO_DISPLACEMENT")
        return G6LatencyRecord(**base, final_decision=decision, primary_rejection_code=decision)
    base["latency_sweep_to_displacement"] = disp["start"] - sweep_i
    base["displacement_start_time"] = m5[disp["start"]]["time"]
    base["displacement_start_index"] = disp["start"]
    base["displacement_end_time"] = m5[disp["end"]]["time"]
    base["displacement_end_index"] = disp["end"]

    # --- Stage 4: displacement -> close-confirmed CHoCH/BOS (fixed) ---
    choch_search_end = min(disp["end"] + 1 + _DISPLACEMENT_TO_CHOCH_MAX, n - 1)
    ref_high, ref_low = m5[disp["start"]]["high"], m5[disp["start"]]["low"]
    choch_i = None
    for j in range(disp["end"] + 1, choch_search_end + 1):
        c = m5[j]
        if want == "bull" and c["close"] > ref_high:
            choch_i = j
            break
        if want == "bear" and c["close"] < ref_low:
            choch_i = j
            break
    if choch_i is None:
        decision = censored_or_rejected(choch_search_end, "NO_CHOCH")
        return G6LatencyRecord(**base, final_decision=decision, primary_rejection_code=decision)
    base["latency_displacement_to_choch"] = choch_i - (disp["end"] + 1)
    base["choch_time"], base["choch_index"] = m5[choch_i]["time"], choch_i

    # --- Stage 5: CHoCH -> permitted retracement (first qualifying bar, fixed) ---
    retrace_search_end = min(choch_i + _CHOCH_TO_RETRACE_MAX, n - 1)
    mid = (disp["origin"] + m5[disp["end"]]["close"]) / 2.0
    retrace_i = None
    for j in range(choch_i + 1, retrace_search_end + 1):
        last_close = m5[j]["close"]
        retraced = last_close <= mid if want == "bull" else last_close >= mid
        if retraced:
            retrace_i = j
            break
    if retrace_i is None:
        decision = censored_or_rejected(retrace_search_end, "NO_RETRACE")
        return G6LatencyRecord(**base, final_decision=decision, primary_rejection_code=decision)
    base["latency_choch_to_retrace"] = retrace_i - choch_i
    base["retrace_time"], base["retrace_index"] = m5[retrace_i]["time"], retrace_i

    # --- Stage 6: retracement -> next-bar-open entry ---
    if retrace_i + 1 >= n:
        return G6LatencyRecord(**base, final_decision="CENSORED_NO_ENTRY_BAR",
                                primary_rejection_code="CENSORED_NO_ENTRY_BAR")
    entry_i = retrace_i + 1
    base["latency_retrace_to_entry"] = 1
    base["entry_time"], base["entry_index"] = m5[entry_i]["time"], entry_i

    return G6LatencyRecord(**base, final_decision="COMPLETED", primary_rejection_code=None)


def percentile(values: list[int], pct: float) -> float | None:
    if not values:
        return None
    s = sorted(values)
    idx = min(len(s) - 1, max(0, int(round(pct / 100.0 * (len(s) - 1)))))
    return float(s[idx])


def to_json_rows(records: list[G6LatencyRecord]) -> list[dict[str, Any]]:
    return [asdict(r) for r in records]
