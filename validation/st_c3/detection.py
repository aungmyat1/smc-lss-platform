"""ST-C3 real price-level detection (A2/S1-G2 scoped, R-18 precursor).

Produces spec-conformant `Evidence` objects (via `validation.st_c3.evidence.
make_evidence`) from real candle data, for the funnel stages fully specified
by the frozen parameters in `specs/st-c3_v1.0.7.yaml` (R-04, R-05, R-06,
R-07, R-23, R-24, R-27, R-28, R-29, R-30, R-31, R-32, R-33). These Evidence
objects are meant to be assembled into a `validation.st_c3.kernel.
EvidenceBundle` and run through the existing, already-tested `run_kernel()`
— this module does not duplicate or bypass the kernel.

Reuses only existing generic `src.smc_engine` primitives (`swings`, `atr`,
`fvgs`, `order_blocks`) — no ST-C3-specific detection algorithm is invented
beyond translating already-decided spec parameters into calls against those
primitives, mirroring the discipline established in
`scripts/research_r27_r30_gbpusd.py`.

**Scope — what this module does NOT cover, and why:** three fields remain
`PROVISIONAL`/never decided at all in `specs/st-c3_v1.0.7.yaml`, blocking
real detection for the corresponding stages until an owner decides them:

- `S7_OTE` — `ote_band_min`/`ote_band_max`/`equilibrium_boundary` (`ote_stage`)
- `S9_LTF_CONFIRMATION` — no owner-ratified M3/M1 CHoCH parameters exist
- `S12_RISK_SLTP` — `buffer_points_atr_multiplier`'s guard *direction*
  formulation is flagged unconfirmed in `OWNER_DECISION_LOG.md` (R-08)

This module implements **S1 (HTF bias), S2 (raw sweep), S3 (sweep reclaim,
R-31), S4 (displacement+BOS), S5 (BOS extreme lock), S6 (dealing range), S8
(FVG/OB), S10 (session gatekeeper, R-33), and S11 (entry-window check,
R-32)** — every stage whose numeric parameters are frozen.

**S2 simplification, noted explicitly:** sweep detection here uses the
single nearest prior confirmed swing level as the liquidity target, not a
clustered equal-highs/lows pool. R-05's `equal_highs_lows_tolerance` is
applied (levels within tolerance are treated as the same pool for sweep-age
purposes), but full pool selection/ranking (as `validation/st_c2/structure.
py` does for ST-C2) is out of scope for this pass — a further scoping
choice, not a spec gap.

**S11 simplification, noted explicitly:** `entry_window_evidence_for()`
evaluates the R-32 window-check mechanism (bars-since-LTF-CHoCH vs. the
frozen `max_allowed_bars=4`), but it takes `bars_since_ltf_choch` as an
input parameter rather than deriving it from raw candles — real LTF CHoCH
detection is S9, which remains blocked (no owner-ratified parameters
exist). This is real, tested logic for the comparison itself, not a stub,
but it cannot run end-to-end without S9.

**S10 timestamp assumption, noted explicitly:** candle `time` fields (e.g.
`"2026-07-13 20:00"`) carry no explicit timezone marker in the source CSVs;
treated as UTC throughout this project (matching how `R27_R30_RESEARCH_REPORT.md`
and every prior script handled timestamps), consistent with the spec's own
session windows being defined in UTC.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from smc_engine import atr as _atr  # noqa: E402
from smc_engine import fvgs as _fvgs  # noqa: E402
from smc_engine import order_blocks as _order_blocks  # noqa: E402
from smc_engine import swings as _swings  # noqa: E402

from validation.st_c3.evidence import Evidence, load_spec, make_evidence  # noqa: E402

Candle = dict[str, Any]

NOT_YET_SUPPORTED = (
    "S7_OTE",
    "S9_LTF_CONFIRMATION",
    "S12_RISK_SLTP",
)

LONDON_WINDOW_UTC = (7, 10)   # R-33, decided 2026-07-27
NY_WINDOW_UTC = (13, 16)      # R-33, decided 2026-07-27


def sweep_reclaim_params(spec: dict) -> dict:
    stage = spec["pipeline"]["liquidity_sweep_stage"]
    return {"max_allowed_bars": int(stage["sweep_reclaim_max_bars"])}


def entry_window_params(spec: dict) -> dict:
    stage = spec["pipeline"]["entry_window_stage"]
    return {"max_allowed_bars": int(stage["entry_window_bars"])}


def _parse_atr_multiplier(expr: str) -> float:
    """Parse a spec string like '0.10 * MF_ATR(1)' -> 0.10."""
    match = re.match(r"\s*([0-9.]+)\s*\*", expr)
    if not match:
        raise ValueError(f"Cannot parse ATR-multiplier expression: {expr!r}")
    return float(match.group(1))


def htf_bias_params(spec: dict) -> dict:
    stage = spec["pipeline"]["htf_bias_stage"]
    return {"k": int(stage["swing_fractal_lookback_k"])}


def sweep_params(spec: dict) -> dict:
    stage = spec["pipeline"]["liquidity_sweep_stage"]
    return {
        "wick_ratio_min": float(stage["wick_ratio_min"]),
        "equal_tolerance_atr_mult": _parse_atr_multiplier(stage["equal_highs_lows_tolerance"]),
        "max_sweep_age_bars": int(stage["max_sweep_age_bars"]),
    }


def displacement_bos_params(spec: dict) -> dict:
    stage = spec["pipeline"]["displacement_bos_stage"]
    return {
        "body_ratio_min": float(stage["displacement_body_ratio_min"]),
        "atr_floor_multiplier": float(stage["displacement_atr_floor_multiplier"]),
        "confirmation_bars": int(stage["bos_confirmation_bars"]),
        "pullback_depth_atr_multiplier": float(stage["pullback_depth_atr_multiplier"]),
    }


def fvg_ob_params(spec: dict) -> dict:
    stage = spec["pipeline"]["fvg_ob_confluence_stage"]
    return {
        "fvg_min_gap_atr_multiplier": float(stage["fvg_min_gap_atr_multiplier"]),
        "ob_freshness_max_mf_swings": int(stage["ob_freshness_max_mf_swings"]),
        "fvg_freshness_max_mf_swings": int(stage["fvg_freshness_max_mf_swings"]),
    }


# ---------------------------------------------------------------------
# S1_HTF_BIAS
# ---------------------------------------------------------------------
def detect_htf_bias_events(h4_candles: Sequence[Candle], *, k: int) -> list[dict]:
    """Bias-flip events on H4: body-close break of the last confirmed
    opposite-direction swing. The first break establishes bias (BOS); a
    later opposite-direction break flips it (CHoCH). No separate
    CHoCH-displacement threshold is applied here -- ST-C3's
    `htf_bias_stage` specifies none (distinct from ST-C2's own, unrelated
    CHoCH-displacement rule, which does not apply here per ADR-0004).
    """
    candles = list(h4_candles)
    hi_all, lo_all = _swings(candles, k=k)
    hi_ptr = lo_ptr = 0
    n_hi, n_lo = len(hi_all), len(lo_all)
    events: list[dict] = []
    bias = "NONE"
    for i in range(k + 1, len(candles)):
        while hi_ptr < n_hi and hi_all[hi_ptr][0] + k <= i:
            hi_ptr += 1
        while lo_ptr < n_lo and lo_all[lo_ptr][0] + k <= i:
            lo_ptr += 1
        hi_last = hi_all[hi_ptr - 1][1] if hi_ptr else None
        lo_last = lo_all[lo_ptr - 1][1] if lo_ptr else None
        close = candles[i]["close"]
        new_bias = None
        if hi_last is not None and close > hi_last:
            new_bias = "BULLISH"
        elif lo_last is not None and close < lo_last:
            new_bias = "BEARISH"
        if new_bias and new_bias != bias:
            events.append({"i": i, "bias": new_bias, "kind": "BOS" if bias == "NONE" else "CHOCH"})
            bias = new_bias
    return events


def htf_bias_evidence_at(h4_candles: Sequence[Candle], events: list[dict], i: int, *, evidence_id: str) -> Evidence:
    """HTFBiasEvidence as of candle index i (only events with index <= i count)."""
    prior = [e for e in events if e["i"] <= i]
    if not prior:
        return make_evidence(
            "HTFBiasEvidence", id=evidence_id, tf="H4", valid=False,
            reason="h4_structure_ambiguous", timestamp=str(h4_candles[i]["time"]),
            structure="UNCLEAR", bias="NONE",
        )
    latest = prior[-1]
    structure = "HHHL" if latest["bias"] == "BULLISH" else "LHLL"
    return make_evidence(
        "HTFBiasEvidence", id=evidence_id, tf="H4", valid=True,
        reason=f"{latest['kind'].lower()}_confirmed", timestamp=str(h4_candles[latest['i']]["time"]),
        structure=structure, bias=latest["bias"],
    )


# ---------------------------------------------------------------------
# S2_SWEEP (raw sweep only -- reclaim confirmation is S3, out of scope)
# ---------------------------------------------------------------------
def detect_sweep_at(
    candles: Sequence[Candle], i: int, *, k: int, wick_ratio_min: float,
    equal_tolerance_atr_mult: float, max_sweep_age_bars: int, evidence_id: str,
) -> Evidence:
    """SweepEvidence for candle i: did it pierce the nearest prior confirmed
    swing level with sufficient wick ratio, within the sweep-age window?
    Uses the single nearest confirmed swing as the liquidity level -- see
    module docstring's S2 simplification note re: equal-highs/lows pooling.
    """
    candles = list(candles)
    hi_all, lo_all = _swings(candles[: i + 1], k=k)
    tol = equal_tolerance_atr_mult * _atr(candles, max(0, i - 1), n=1)
    high, low = candles[i]["high"], candles[i]["low"]
    open_, close = candles[i]["open"], candles[i]["close"]
    rng = high - low
    if rng <= 0:
        return make_evidence(
            "SweepEvidence", id=evidence_id, tf=["H4", "M15"], valid=False,
            reason="no_external_liquidity_sweep", timestamp=str(candles[i]["time"]),
            sweep_type="SELL_SIDE", wick_penetration=False, level=0.0,
        )

    def _nearest(levels, ref):
        candidates = [(idx, lvl) for idx, lvl in levels if idx + k <= i]
        if not candidates:
            return None
        return min(candidates, key=lambda t: (abs(t[1] - ref), -t[0]))

    sell_side = _nearest(hi_all, high)  # buy-side stops rest above highs; sweeping them = SELL_SIDE liquidity taken
    buy_side = _nearest(lo_all, low)    # sell-side stops rest below lows; sweeping them = BUY_SIDE liquidity taken

    best = None
    if sell_side is not None:
        idx, lvl = sell_side
        pierced = high > lvl + tol
        wick_ratio = (high - max(open_, close)) / rng
        age = i - idx
        if pierced:
            best = ("SELL_SIDE", lvl, wick_ratio, age)
    if buy_side is not None:
        idx, lvl = buy_side
        pierced = low < lvl - tol
        wick_ratio = (min(open_, close) - low) / rng
        age = i - idx
        if pierced and (best is None or wick_ratio > best[2]):
            best = ("BUY_SIDE", lvl, wick_ratio, age)

    if best is None:
        return make_evidence(
            "SweepEvidence", id=evidence_id, tf=["H4", "M15"], valid=False,
            reason="no_external_liquidity_sweep", timestamp=str(candles[i]["time"]),
            sweep_type="SELL_SIDE", wick_penetration=False, level=0.0,
        )
    sweep_type, level, wick_ratio, age = best
    if age > max_sweep_age_bars:
        return make_evidence(
            "SweepEvidence", id=evidence_id, tf=["H4", "M15"], valid=False,
            reason="sweep_reclaim_exceeds_n_sweep", timestamp=str(candles[i]["time"]),
            sweep_type=sweep_type, wick_penetration=True, level=level,
        )
    if wick_ratio < wick_ratio_min:
        return make_evidence(
            "SweepEvidence", id=evidence_id, tf=["H4", "M15"], valid=False,
            reason="sweep_wick_does_not_penetrate_level", timestamp=str(candles[i]["time"]),
            sweep_type=sweep_type, wick_penetration=False, level=level,
        )
    return make_evidence(
        "SweepEvidence", id=evidence_id, tf=["H4", "M15"], valid=True,
        reason="sell_side_liquidity_swept" if sweep_type == "SELL_SIDE" else "buy_side_liquidity_swept",
        timestamp=str(candles[i]["time"]), sweep_type=sweep_type, wick_penetration=True, level=level,
    )


# ---------------------------------------------------------------------
# S4_DISPLACEMENT_BOS
# ---------------------------------------------------------------------
def find_bos_candidates(candles: Sequence[Candle], *, k: int) -> list[dict]:
    candles = list(candles)
    hi_all, lo_all = _swings(candles, k=k)
    hi_ptr = lo_ptr = 0
    n_hi, n_lo = len(hi_all), len(lo_all)
    out = []
    for i in range(k + 1, len(candles)):
        while hi_ptr < n_hi and hi_all[hi_ptr][0] + k <= i:
            hi_ptr += 1
        while lo_ptr < n_lo and lo_all[lo_ptr][0] + k <= i:
            lo_ptr += 1
        hi_last = hi_all[hi_ptr - 1][1] if hi_ptr else None
        lo_last = lo_all[lo_ptr - 1][1] if lo_ptr else None
        close = candles[i]["close"]
        if hi_last is not None and close > hi_last:
            out.append({"i": i, "dir": "UP", "level": hi_last})
        elif lo_last is not None and close < lo_last:
            out.append({"i": i, "dir": "DOWN", "level": lo_last})
    return out


def bos_confirmed(candles: Sequence[Candle], event: dict, *, confirmation_bars: int) -> bool:
    """True if price does not close back across the broken level within
    `confirmation_bars` following bars (R-28)."""
    candles = list(candles)
    i, direction, level = event["i"], event["dir"], event["level"]
    for j in range(i + 1, min(i + 1 + confirmation_bars, len(candles))):
        close = candles[j]["close"]
        if (direction == "UP" and close < level) or (direction == "DOWN" and close > level):
            return False
    return True


def displacement_evidence_for(candles: Sequence[Candle], event: dict, *, body_ratio_min: float, atr_floor_multiplier: float, evidence_id: str) -> Evidence:
    candles = list(candles)
    i = event["i"]
    candle = candles[i]
    rng = candle["high"] - candle["low"]
    body_ratio = abs(candle["close"] - candle["open"]) / rng if rng > 0 else 0.0
    ref_atr = _atr(candles, max(0, i - 1), n=1)
    threshold = atr_floor_multiplier * ref_atr
    valid = body_ratio >= body_ratio_min and rng >= threshold
    return make_evidence(
        "DisplacementEvidence", id=evidence_id, tf="M15", valid=valid,
        reason="impulsive_move_confirmed" if valid else "no_impulsive_move_after_sweep",
        timestamp=str(candle["time"]), impulse_strength=body_ratio, threshold=body_ratio_min,
    )


def bos_evidence_for(candles: Sequence[Candle], event: dict, *, confirmation_bars: int, evidence_id: str) -> Evidence:
    candles = list(candles)
    i, direction, level = event["i"], event["dir"], event["level"]
    confirmed = bos_confirmed(candles, event, confirmation_bars=confirmation_bars)
    return make_evidence(
        "BOSEvidence", id=evidence_id, tf="M15", valid=confirmed,
        reason="body_close_break_confirmed" if confirmed else "bos_no_body_close_break",
        timestamp=str(candles[i]["time"]), bos_direction=direction, body_close_break=True, level=level,
    )


# ---------------------------------------------------------------------
# S5_BOS_EXTREME_LOCK
# ---------------------------------------------------------------------
def bos_extreme_evidence_for(candles: Sequence[Candle], event: dict, *, pullback_depth_atr_multiplier: float, window: int, evidence_id: str) -> Evidence:
    """Locks the BOS extreme once price retraces >= pullback_depth_atr_multiplier
    x ATR(1) against the BOS direction, within `window` bars (R-30)."""
    candles = list(candles)
    i, direction = event["i"], event["dir"]
    bos_close = candles[i]["close"]
    provisional_extreme = candles[i]["high"] if direction == "UP" else candles[i]["low"]
    ref_atr = _atr(candles, i, n=1)
    for j in range(i + 1, min(i + 1 + window, len(candles))):
        close = candles[j]["close"]
        depth = (bos_close - close) if direction == "UP" else (close - bos_close)
        extreme = max(provisional_extreme, candles[j]["high"]) if direction == "UP" else min(provisional_extreme, candles[j]["low"])
        provisional_extreme = extreme
        if ref_atr > 0 and depth / ref_atr >= pullback_depth_atr_multiplier:
            return make_evidence(
                "BOSExtremeEvidence", id=evidence_id, tf="M15", valid=True,
                reason="extreme_locked_after_pullback", timestamp=str(candles[j]["time"]),
                provisional_extreme=provisional_extreme, locked_extreme=provisional_extreme, pullback_detected=True,
            )
    return make_evidence(
        "BOSExtremeEvidence", id=evidence_id, tf="M15", valid=False,
        reason="bos_extreme_pullback_not_detected", timestamp=str(candles[i]["time"]),
        provisional_extreme=provisional_extreme, locked_extreme=provisional_extreme, pullback_detected=False,
    )


# ---------------------------------------------------------------------
# S6_DEALING_RANGE (purely derived from swing/BOS geometry, no threshold needed)
# ---------------------------------------------------------------------
def dealing_range_evidence_for(candles: Sequence[Candle], event: dict, *, k: int, evidence_id: str) -> Evidence:
    candles = list(candles)
    i, direction = event["i"], event["dir"]
    hi_all, lo_all = _swings(candles[: i + 1], k=k)
    if direction == "UP":
        if not lo_all:
            return make_evidence(
                "DealingRangeEvidence", id=evidence_id, tf="M15", valid=False,
                reason="dealing_range_invalid_or_undefined", timestamp=str(candles[i]["time"]),
                origin=0.0, bos_extreme=0.0, range_size=0.0,
            )
        origin = lo_all[-1][1]
        bos_extreme = candles[i]["high"]
    else:
        if not hi_all:
            return make_evidence(
                "DealingRangeEvidence", id=evidence_id, tf="M15", valid=False,
                reason="dealing_range_invalid_or_undefined", timestamp=str(candles[i]["time"]),
                origin=0.0, bos_extreme=0.0, range_size=0.0,
            )
        origin = hi_all[-1][1]
        bos_extreme = candles[i]["low"]
    range_size = abs(bos_extreme - origin)
    return make_evidence(
        "DealingRangeEvidence", id=evidence_id, tf="M15", valid=range_size > 0,
        reason="range_defined_origin_to_extreme" if range_size > 0 else "dealing_range_invalid_or_undefined",
        timestamp=str(candles[i]["time"]), origin=origin, bos_extreme=bos_extreme, range_size=range_size,
    )


# ---------------------------------------------------------------------
# S8_FVG_OB_CONFLUENCE
# ---------------------------------------------------------------------
def _mf_swing_index_series(candles: Sequence[Candle], *, k: int) -> list[int]:
    """Chronologically-sorted confirmed-swing bar indices (highs and lows
    combined) -- the "MF swing index" R-23/R-24 count against, not a bar
    count. Position in this list at a given bar index is the cumulative
    swing count up to that bar."""
    hi, lo = _swings(list(candles), k=k)
    return sorted(idx for idx, _ in hi) + sorted(idx for idx, _ in lo)


def _swings_between(swing_indices: Sequence[int], start: int, end: int) -> int:
    return sum(1 for idx in swing_indices if start < idx <= end)


def fvg_evidence_near(candles: Sequence[Candle], i: int, *, min_gap_atr_multiplier: float, freshness_max_mf_swings: int, k: int, evidence_id: str) -> Evidence:
    candles = list(candles)
    gaps = _fvgs(candles[: i + 1], min_gap=0.0)
    ref_atr = _atr(candles, max(0, i - 1), n=1)
    swing_indices = sorted(_mf_swing_index_series(candles[: i + 1], k=k))
    for gap in reversed(gaps):
        size = gap["upper"] - gap["lower"]
        if ref_atr <= 0 or size / ref_atr < min_gap_atr_multiplier:
            continue
        swings_since = _swings_between(swing_indices, gap["i"], i)
        fresh = swings_since <= freshness_max_mf_swings
        return make_evidence(
            "FVGEvidence", id=evidence_id, tf=["H4", "M15"], valid=fresh,
            reason="fresh_fvg_inside_ote" if fresh else "no_fresh_fvg_or_ob_inside_ote",
            timestamp=str(candles[i]["time"]), gap_top=gap["upper"], gap_bottom=gap["lower"],
            fresh=fresh, inside_ote=False,  # OTE gate is NOT_YET_SUPPORTED -- always False here, see module docstring
        )
    return make_evidence(
        "FVGEvidence", id=evidence_id, tf=["H4", "M15"], valid=False,
        reason="no_fresh_fvg_or_ob_inside_ote", timestamp=str(candles[i]["time"]),
        gap_top=0.0, gap_bottom=0.0, fresh=False, inside_ote=False,
    )


def order_block_evidence_near(candles: Sequence[Candle], i: int, *, k: int, freshness_max_mf_swings: int, evidence_id: str) -> Evidence:
    candles = list(candles)
    obs = _order_blocks(candles[: i + 1], k=k)
    if not obs:
        return make_evidence(
            "OrderBlockEvidence", id=evidence_id, tf=["H4", "M15"], valid=False,
            reason="no_fresh_fvg_or_ob_inside_ote", timestamp=str(candles[i]["time"]),
            ob_high=0.0, ob_low=0.0, fresh=False, inside_ote=False,
        )
    ob = obs[-1]
    swing_indices = sorted(_mf_swing_index_series(candles[: i + 1], k=k))
    swings_since = _swings_between(swing_indices, ob["i"], i)
    fresh = swings_since <= freshness_max_mf_swings
    return make_evidence(
        "OrderBlockEvidence", id=evidence_id, tf=["H4", "M15"], valid=fresh,
        reason="fresh_ob_inside_ote" if fresh else "no_fresh_fvg_or_ob_inside_ote",
        timestamp=str(candles[i]["time"]), ob_high=ob["high"], ob_low=ob["low"], fresh=fresh, inside_ote=False,
        # inside_ote False -- OTE gate is NOT_YET_SUPPORTED, see module docstring
    )


# ---------------------------------------------------------------------
# S3_SWEEP_RECLAIM
# ---------------------------------------------------------------------
def sweep_reclaim_evidence_for(
    candles: Sequence[Candle], sweep_i: int, sweep_type: str, level: float, *,
    max_allowed_bars: int, evidence_id: str,
) -> Evidence:
    """Did price reclaim (close back inside the range past) the swept level
    within `max_allowed_bars` of the sweep bar (R-31)? SELL_SIDE sweeps
    (a prior high swept) reclaim on a close back below `level`; BUY_SIDE
    sweeps (a prior low swept) reclaim on a close back above `level`.
    """
    candles = list(candles)
    for offset in range(1, max_allowed_bars + 1):
        j = sweep_i + offset
        if j >= len(candles):
            break
        close = candles[j]["close"]
        reclaimed = (close < level) if sweep_type == "SELL_SIDE" else (close > level)
        if reclaimed:
            return make_evidence(
                "SweepReclaimEvidence", id=evidence_id, tf=["H4", "M15"], valid=True,
                reason="reclaimed_within_window", timestamp=str(candles[j]["time"]),
                reclaim_within_bars=offset, max_allowed_bars=max_allowed_bars, reclaimed=True,
            )
    return make_evidence(
        "SweepReclaimEvidence", id=evidence_id, tf=["H4", "M15"], valid=False,
        reason="sweep_reclaim_exceeds_n_sweep", timestamp=str(candles[sweep_i]["time"]),
        reclaim_within_bars=max_allowed_bars + 1, max_allowed_bars=max_allowed_bars, reclaimed=False,
    )


# ---------------------------------------------------------------------
# S10_SESSION_GATEKEEPER
# ---------------------------------------------------------------------
def session_window_evidence_for(candle: Candle, *, evidence_id: str) -> Evidence:
    """Which session (LONDON/NY/INVALID) does this candle's timestamp fall
    in, per R-33's frozen UTC windows? Candle `time` values are treated as
    UTC (see module docstring)."""
    time_str = str(candle["time"])
    hour = int(time_str.split(" ")[1].split(":")[0])
    if LONDON_WINDOW_UTC[0] <= hour < LONDON_WINDOW_UTC[1]:
        session = "LONDON"
    elif NY_WINDOW_UTC[0] <= hour < NY_WINDOW_UTC[1]:
        session = "NY"
    else:
        session = "INVALID"
    valid = session in ("LONDON", "NY")
    return make_evidence(
        "SessionWindowEvidence", id=evidence_id, tf=["M3", "M1"], valid=valid,
        reason="inside_allowed_session" if valid else "choch_outside_allowed_sessions",
        timestamp=time_str, session=session,
    )


# ---------------------------------------------------------------------
# S11_ENTRY_WINDOW (window-check mechanism only -- see module docstring's
# S11 simplification note re: bars_since_ltf_choch as an input, not derived)
# ---------------------------------------------------------------------
def entry_window_evidence_for(
    bars_since_ltf_choch: int, *, max_allowed_bars: int, timestamp: str, evidence_id: str,
) -> Evidence:
    """R-32's frozen window check: is `bars_since_ltf_choch` still within
    `max_allowed_bars`?"""
    inside_window = bars_since_ltf_choch <= max_allowed_bars
    return make_evidence(
        "EntryWindowEvidence", id=evidence_id, tf=["M3", "M1"], valid=inside_window,
        reason="within_max_entry_bars" if inside_window else "max_entry_bars_exceeded",
        timestamp=timestamp, bars_since_ltf_choch=bars_since_ltf_choch,
        max_allowed_bars=max_allowed_bars, inside_window=inside_window,
    )


# ---------------------------------------------------------------------
# S1-G3 primitives -- pure arithmetic, no owner decision or spec threshold
# involved. Added for S1-G3 (Primitive and Indicator Conformance)
# evidence, per MASTER_PLAN.md's required-evidence list.
# ---------------------------------------------------------------------
def compute_rr(entry: float, stop: float, target: float, direction: str) -> float:
    """Reward-to-risk ratio for a LONG/SHORT setup: reward / risk, where
    risk = |entry - stop| and reward = |target - entry|. Matches the
    frozen trade_plan.schema.risk.computed_rr field's meaning -- this is
    the arithmetic that field represents, not a new strategy rule.
    """
    risk = abs(entry - stop)
    if risk == 0:
        raise ValueError("compute_rr: entry and stop cannot be equal (zero risk)")
    if direction == "LONG":
        reward = target - entry
    elif direction == "SHORT":
        reward = entry - target
    else:
        raise ValueError(f"compute_rr: direction must be LONG or SHORT, got {direction!r}")
    return reward / risk


def premium_discount_zone(price: float, range_low: float, range_high: float) -> str:
    """Bare midpoint classification of `price` within [range_low, range_high]
    -- "premium" (upper half), "discount" (lower half), or "equilibrium"
    (exactly the midpoint). This is arithmetic (the midpoint of an
    interval), not the S7_OTE gate: it does not use, reference, or depend
    on `ote_band_min`/`ote_band_max`/`equilibrium_boundary`, which remain
    provisional and out of v1.x scope per the 2026-07-27 funnel-freeze
    decision. Provided for S1-G3 primitive-conformance evidence only --
    not wired into any funnel stage.
    """
    if range_high <= range_low:
        raise ValueError("premium_discount_zone: range_high must exceed range_low")
    midpoint = (range_low + range_high) / 2
    if price > midpoint:
        return "premium"
    if price < midpoint:
        return "discount"
    return "equilibrium"
