"""ST-C3 real price-level detection (A2/S1-G2 scoped, R-18 precursor).

Produces spec-conformant `Evidence` objects (via `validation.st_c3.evidence.
make_evidence`) from real candle data, for the funnel stages fully specified
by the frozen parameters in `specs/st-c3_v1.0.5.yaml` (R-04, R-05, R-06,
R-07, R-23, R-24, R-27, R-28, R-29, R-30). These Evidence objects are meant
to be assembled into a `validation.st_c3.kernel.EvidenceBundle` and run
through the existing, already-tested `run_kernel()` — this module does not
duplicate or bypass the kernel.

Reuses only existing generic `src.smc_engine` primitives (`swings`, `atr`,
`fvgs`, `order_blocks`) — no ST-C3-specific detection algorithm is invented
beyond translating already-decided spec parameters into calls against those
primitives, mirroring the discipline established in
`scripts/research_r27_r30_gbpusd.py`.

**Scope — what this module does NOT cover, and why:** several fields
remain `PROVISIONAL`/never ratified in `specs/st-c3_v1.0.5.yaml`, blocking
real detection for the corresponding stages until an owner decides them:

- `S3_SWEEP_RECLAIM` — `sweep_reclaim_max_bars` (`liquidity_sweep_stage`)
- `S7_OTE` — `ote_band_min`/`ote_band_max`/`equilibrium_boundary` (`ote_stage`)
- `S9_LTF_CONFIRMATION` — no owner-ratified M3/M1 CHoCH parameters exist
- `S10_SESSION_GATEKEEPER` — `london_window_utc`/`ny_window_utc` (`sessions`)
- `S11_ENTRY_WINDOW` — `entry_window_bars` (`entry_window_stage`)
- `S12_RISK_SLTP` — `buffer_points_atr_multiplier`'s guard *direction*
  formulation is flagged unconfirmed in `OWNER_DECISION_LOG.md` (R-08)

This module implements **S1 (HTF bias), S2 (raw sweep, not reclaim), S4
(displacement+BOS), S5 (BOS extreme lock), S6 (dealing range), and S8
(FVG/OB)** — the stages fully specified by what is frozen today.

**S2 simplification, noted explicitly:** sweep detection here uses the
single nearest prior confirmed swing level as the liquidity target, not a
clustered equal-highs/lows pool. R-05's `equal_highs_lows_tolerance` is
applied (levels within tolerance are treated as the same pool for sweep-age
purposes), but full pool selection/ranking (as `validation/st_c2/structure.
py` does for ST-C2) is out of scope for this pass — a further scoping
choice, not a spec gap.
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
    "S3_SWEEP_RECLAIM",
    "S7_OTE",
    "S9_LTF_CONFIRMATION",
    "S10_SESSION_GATEKEEPER",
    "S11_ENTRY_WINDOW",
    "S12_RISK_SLTP",
)


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
