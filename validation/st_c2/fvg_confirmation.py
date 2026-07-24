"""ST-C2 GC3 FVG-chain and LTF confirmation evidence."""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Sequence

from src import smc_engine as e
from validation.st_c2.identifiers import confirmation_id, fvg_id
from validation.st_c2.schemas import ConfirmationEvent, FVGEvent
from validation.st_c2.symbols import SymbolMetadata, points_to_price

Candle = dict[str, Any]


def _price(value: Any) -> Decimal:
    return Decimal(str(value))


def _body_ratio(candle: Candle) -> Decimal:
    high = _price(candle["high"])
    low = _price(candle["low"])
    if high <= low:
        return Decimal("0")
    return abs(_price(candle["close"]) - _price(candle["open"])) / (high - low)


def _direction_to_fvg(direction: str) -> str:
    return "bull" if direction == "long" else "bear"


def _overlaps(a_low: Decimal, a_high: Decimal, b_low: Decimal, b_high: Decimal) -> bool:
    return max(a_low, b_low) <= min(a_high, b_high)


def detect_fvg_events(
    candles: Sequence[Candle],
    *,
    timeframe: str,
    direction: str,
    spec: dict[str, Any],
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
    min_gap_points: Decimal | int | str | None = None,
    max_age_bars: int | None = None,
) -> tuple[FVGEvent, ...]:
    """Emit fixed three-candle wick-to-wick FVG evidence in setup direction."""
    if not candles:
        return ()
    want = _direction_to_fvg(direction)
    gap_points = Decimal(str(min_gap_points if min_gap_points is not None else 0))
    min_gap = float(points_to_price(gap_points, symbol_metadata))
    raw = [f for f in e.fvgs(list(candles), min_gap=min_gap) if f["dir"] == want]
    events: list[FVGEvent] = []
    latest_index = len(candles) - 1
    for fvg in raw:
        age = latest_index - int(fvg["i"])
        status = "confirmed"
        reason = None
        if max_age_bars is not None and age > max_age_bars:
            status = "expired"
            reason = "FVG_EXPIRED"
        lower = _price(fvg["lower"])
        upper = _price(fvg["upper"])
        attrs = {
            "symbol": symbol_metadata.symbol,
            "timeframe": timeframe,
            "direction": direction,
            "index": int(fvg["i"]),
            "timestamp": str(candles[int(fvg["i"])]["time"]),
            "lower": str(lower),
            "upper": str(upper),
            "causal_cutoff": causal_cutoff,
        }
        events.append(
            FVGEvent(
                event_id=fvg_id(attrs),
                strategy_id="ST-C2",
                strategy_version="1.2.0",
                symbol=symbol_metadata.symbol,
                timeframe=timeframe,
                rule_id="STC2-FVG-006",
                event_type="FVG",
                direction=direction,  # type: ignore[arg-type]
                source_indices=(int(fvg["i"]) - 2, int(fvg["i"])),
                source_timestamps=(str(candles[int(fvg["i"]) - 2]["time"]), str(candles[int(fvg["i"])]["time"])),
                confirmation_timestamp=str(candles[int(fvg["i"])]["time"]),
                causal_cutoff=causal_cutoff,
                reference_levels={"lower": str(lower), "upper": str(upper)},
                status=status,  # type: ignore[arg-type]
                invalidation_reason=reason,
                metadata={
                    "geometry_mode": "fixed_three_candle",
                    "boundary_formula": "wick_to_wick_displacement",
                    "gap_points_min": str(gap_points),
                    "age_bars": age,
                },
            )
        )
    return tuple(sorted(events, key=lambda ev: (ev.confirmation_timestamp or "", ev.event_id)))


def detect_fvg_chain(
    htf_candles: Sequence[Candle],
    mf_candles: Sequence[Candle],
    ltf_candles: Sequence[Candle],
    *,
    direction: str,
    spec: dict[str, Any],
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
) -> tuple[FVGEvent, ...]:
    """Detect HTF/MF/LTF FVG evidence and chain overlap where data permits."""
    htf_params = spec["pipeline"]["fvg_stage"]["htf_fvg"]
    ltf_params = spec["pipeline"]["fvg_stage"]["ltf_fvg"]
    htf_events = detect_fvg_events(
        htf_candles,
        timeframe="H4",
        direction=direction,
        spec=spec,
        symbol_metadata=symbol_metadata,
        causal_cutoff=causal_cutoff,
        min_gap_points=0,
        max_age_bars=int(htf_params["max_age_bars"]),
    )
    mf_events = detect_fvg_events(
        mf_candles,
        timeframe="M15",
        direction=direction,
        spec=spec,
        symbol_metadata=symbol_metadata,
        causal_cutoff=causal_cutoff,
        min_gap_points=spec["pipeline"]["liquidity_stage"]["poi_gap_reaction"]["gap_min_points"],
        max_age_bars=None,
    )
    ltf_events = detect_fvg_events(
        ltf_candles,
        timeframe="M3",
        direction=direction,
        spec=spec,
        symbol_metadata=symbol_metadata,
        causal_cutoff=causal_cutoff,
        min_gap_points=0,
        max_age_bars=int(ltf_params["max_age_bars"]),
    )
    confirmed_htf = [ev for ev in htf_events if ev.status == "confirmed"]
    confirmed_mf = [ev for ev in mf_events if ev.status == "confirmed"]
    confirmed_ltf = [ev for ev in ltf_events if ev.status == "confirmed"]
    if not confirmed_mf:
        return ()
    selected_mf = confirmed_mf[-1]
    chain: list[FVGEvent] = []
    selected_htf = None
    for ev in reversed(confirmed_htf):
        if _overlaps(
            _price(ev.reference_levels["lower"]),
            _price(ev.reference_levels["upper"]),
            _price(selected_mf.reference_levels["lower"]),
            _price(selected_mf.reference_levels["upper"]),
        ):
            selected_htf = ev
            break
    selected_ltf = None
    for ev in reversed(confirmed_ltf):
        if _overlaps(
            _price(ev.reference_levels["lower"]),
            _price(ev.reference_levels["upper"]),
            _price(selected_mf.reference_levels["lower"]),
            _price(selected_mf.reference_levels["upper"]),
        ):
            selected_ltf = ev
            break
    if selected_htf is not None:
        chain.append(selected_htf)
    chain.append(selected_mf)
    if selected_ltf is not None:
        chain.append(selected_ltf)
    return tuple(chain)


def detect_ltf_confirmation(
    ltf_candles: Sequence[Candle],
    *,
    direction: str,
    spec: dict[str, Any],
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
) -> ConfirmationEvent | None:
    """Emit first qualifying M3 close-confirmed structure break evidence."""
    del symbol_metadata
    if not ltf_candles:
        return None
    k = 2
    max_setup_bars = int(spec["pipeline"]["ltf_confirmation_stage"]["stronger_choch"]["max_setup_bars"])
    min_body = Decimal(str(spec["pipeline"]["ltf_confirmation_stage"]["choch"]["displacement_body_ratio_min"]))
    highs, lows = e.swings(list(ltf_candles), k=k)
    start = max(0, len(ltf_candles) - max_setup_bars)
    for i in range(start, len(ltf_candles)):
        candle = ltf_candles[i]
        body = _body_ratio(candle)
        if body < min_body:
            continue
        if direction == "long":
            prior = [(idx, price) for idx, price in highs if idx + k < i]
            if not prior:
                continue
            break_level = _price(prior[-1][1])
            if _price(candle["close"]) <= break_level:
                continue
        else:
            prior = [(idx, price) for idx, price in lows if idx + k < i]
            if not prior:
                continue
            break_level = _price(prior[-1][1])
            if _price(candle["close"]) >= break_level:
                continue
        attrs = {
            "symbol": "GBPUSD",
            "timeframe": "M3",
            "direction": direction,
            "confirmation_index": i,
            "confirmation_timestamp": str(candle["time"]),
            "break_level": str(break_level),
            "causal_cutoff": causal_cutoff,
        }
        return ConfirmationEvent(
            event_id=confirmation_id(attrs),
            strategy_id="ST-C2",
            strategy_version="1.2.0",
            symbol="GBPUSD",
            timeframe="M3",
            rule_id="STC2-LTF-002",
            event_type="LTF_CONFIRMATION",
            direction=direction,  # type: ignore[arg-type]
            source_indices=(i,),
            source_timestamps=(str(candle["time"]),),
            confirmation_timestamp=str(candle["time"]),
            causal_cutoff=causal_cutoff,
            reference_levels={"break_level": str(break_level), "close": str(candle["close"])},
            status="confirmed",
            metadata={
                "break_structure_close_required": True,
                "body_ratio": str(body),
                "min_body_ratio": str(min_body),
                "first_qualifying_bar": True,
                "max_setup_bars": max_setup_bars,
            },
        )
    return None
