"""ST-C2 GC2 structural bias, liquidity, and dealing-range conformance."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Sequence

from src import smc_engine as e
from validation.st_c2.identifiers import (
    liquidity_pool_id,
    stable_id,
    structure_id,
    sweep_id,
)
from validation.st_c2.schemas import LiquidityPool, LiquiditySweep, StructuralEvent
from validation.st_c2.symbols import SymbolMetadata, load_symbol_metadata

Candle = dict[str, Any]


@dataclass(frozen=True)
class BiasEvidence:
    direction: str
    bias_event_id: str | None
    bias_evidence_timestamp: str | None
    bias_evidence_type: str | None
    protected_level_id: str | None
    classification_rule_id: str
    causal_cutoff: str
    reason: str


@dataclass(frozen=True)
class DealingRange:
    range_id: str
    direction: str
    anchor_high_event_id: str
    anchor_low_event_id: str
    high: Decimal
    low: Decimal
    equilibrium: Decimal
    creation_timestamp: str
    confirmation_timestamp: str
    age_bars: int
    status: str
    invalidation_reason: str | None
    causal_cutoff: str


@dataclass(frozen=True)
class OTEEvidence:
    range_id: str
    candidate_price: Decimal
    normalized_position: Decimal
    zone: str
    ote_eligible: bool
    fib_lower: Decimal
    fib_upper: Decimal
    rule_id: str
    causal_cutoff: str
    rejection_detail: str | None = None


def _price(value: Any) -> Decimal:
    return Decimal(str(value))


def _mk_struct_event(
    *,
    event_type: str,
    direction: str,
    rule_id: str,
    symbol: str,
    timeframe: str,
    index: int,
    timestamp: str,
    price: Decimal,
    confirmation_index: int,
    confirmation_timestamp: str,
    causal_cutoff: str,
    metadata: dict[str, Any] | None = None,
) -> StructuralEvent:
    attrs = {
        "strategy_id": "ST-C2",
        "strategy_version": "1.2.0",
        "symbol": symbol,
        "timeframe": timeframe,
        "event_type": event_type,
        "direction": direction,
        "swing_price": str(price),
        "swing_index": index,
        "swing_timestamp": timestamp,
        "confirmation_index": confirmation_index,
        "confirmation_timestamp": confirmation_timestamp,
        "causal_cutoff": causal_cutoff,
    }
    event_id = structure_id(attrs)
    return StructuralEvent(
        event_id=event_id,
        strategy_id="ST-C2",
        strategy_version="1.2.0",
        symbol=symbol,
        timeframe=timeframe,
        rule_id=rule_id,
        event_type=event_type,
        direction=direction,  # type: ignore[arg-type]
        source_indices=(index, confirmation_index),
        source_timestamps=(timestamp, confirmation_timestamp),
        confirmation_timestamp=confirmation_timestamp,
        causal_cutoff=causal_cutoff,
        reference_levels={"price": str(price)},
        status="confirmed",
        metadata=metadata or {},
    )


def _body_ratio(candle: Candle) -> Decimal:
    high = _price(candle["high"])
    low = _price(candle["low"])
    if high <= low:
        return Decimal("0")
    return abs(_price(candle["close"]) - _price(candle["open"])) / (high - low)


def detect_htf_structure(
    htf_candles: Sequence[Candle],
    *,
    spec: dict[str, Any],
    symbol_metadata: SymbolMetadata | None = None,
    causal_cutoff: str | None = None,
    symbol: str = "GBPUSD",
) -> tuple[StructuralEvent, ...]:
    """Detect H4 swings, closed-candle BOS/CHoCH, and protected-level events."""
    del symbol_metadata
    if not htf_candles:
        return ()
    cutoff = causal_cutoff or str(htf_candles[-1]["time"])
    k = int(spec["pipeline"]["htf_structure"]["htf_swing_fractal_k_h4"])
    confirmation_bars = int(spec["pipeline"]["htf_bias_stage"]["bos"]["confirmation_bars"])
    highs, lows = e.swings(list(htf_candles), k=k)
    events: list[StructuralEvent] = []
    confirmed_highs: list[tuple[int, Decimal, StructuralEvent]] = []
    confirmed_lows: list[tuple[int, Decimal, StructuralEvent]] = []

    for idx, value in highs:
        confirm_i = idx + k
        if confirm_i >= len(htf_candles):
            continue
        event = _mk_struct_event(
            event_type="SWING_HIGH",
            direction="none",
            rule_id="STC2-STRUCT-001",
            symbol=symbol,
            timeframe="H4",
            index=idx,
            timestamp=str(htf_candles[idx]["time"]),
            price=_price(value),
            confirmation_index=confirm_i,
            confirmation_timestamp=str(htf_candles[confirm_i]["time"]),
            causal_cutoff=cutoff,
            metadata={"swing_type": "external_candidate", "confirmation_bars": k},
        )
        events.append(event)
        confirmed_highs.append((idx, _price(value), event))
    for idx, value in lows:
        confirm_i = idx + k
        if confirm_i >= len(htf_candles):
            continue
        event = _mk_struct_event(
            event_type="SWING_LOW",
            direction="none",
            rule_id="STC2-STRUCT-001",
            symbol=symbol,
            timeframe="H4",
            index=idx,
            timestamp=str(htf_candles[idx]["time"]),
            price=_price(value),
            confirmation_index=confirm_i,
            confirmation_timestamp=str(htf_candles[confirm_i]["time"]),
            causal_cutoff=cutoff,
            metadata={"swing_type": "external_candidate", "confirmation_bars": k},
        )
        events.append(event)
        confirmed_lows.append((idx, _price(value), event))

    confirmed_highs.sort(key=lambda x: x[0])
    confirmed_lows.sort(key=lambda x: x[0])
    hi_ptr = 0
    lo_ptr = 0
    active_bias = "none"
    protected: StructuralEvent | None = None
    choch_count = 0

    for i, candle in enumerate(htf_candles):
        while hi_ptr < len(confirmed_highs) and confirmed_highs[hi_ptr][0] + k <= i - confirmation_bars:
            hi_ptr += 1
        while lo_ptr < len(confirmed_lows) and confirmed_lows[lo_ptr][0] + k <= i - confirmation_bars:
            lo_ptr += 1
        last_high = confirmed_highs[hi_ptr - 1] if hi_ptr else None
        last_low = confirmed_lows[lo_ptr - 1] if lo_ptr else None
        close = _price(candle["close"])
        break_dir = None
        level = None
        source_event = None
        if last_high and close > last_high[1]:
            break_dir = "long"
            level = last_high[1]
            source_event = last_high[2]
        elif last_low and close < last_low[1]:
            break_dir = "short"
            level = last_low[1]
            source_event = last_low[2]
        if break_dir is None or level is None or source_event is None:
            continue
        bias_before = active_bias
        displacement_score = _body_ratio(candle)
        if active_bias == "none":
            event_type = "BULLISH_BOS" if break_dir == "long" else "BEARISH_BOS"
            rule_id = "STC2-BIAS-003"
            active_bias = break_dir
        elif active_bias != break_dir:
            choch_count += 1
            min_displacement = Decimal(str(spec["pipeline"]["htf_bias_stage"]["choch"]["displacement_body_ratio_min"]))
            if displacement_score < min_displacement:
                events.append(
                    _mk_struct_event(
                        event_type="CHOCH_REJECTED",
                        direction=break_dir,
                        rule_id="STC2-BIAS-004",
                        symbol=symbol,
                        timeframe="H4",
                        index=int(source_event.source_indices[0]),
                        timestamp=source_event.source_timestamps[0],
                        price=level,
                        confirmation_index=i,
                        confirmation_timestamp=str(candle["time"]),
                        causal_cutoff=cutoff,
                        metadata={
                            "close": str(close),
                            "source_structure_id": source_event.event_id,
                            "bias_before": bias_before,
                            "bias_after": bias_before,
                            "displacement_score": str(displacement_score),
                            "min_displacement": str(min_displacement),
                            "rejection_code": "INSUFFICIENT_CHOCH_DISPLACEMENT",
                        },
                    )
                )
                continue
            event_type = "BULLISH_CHOCH" if break_dir == "long" else "BEARISH_CHOCH"
            rule_id = "STC2-BIAS-004"
            if protected is not None:
                invalidated = _mk_struct_event(
                    event_type="PROTECTED_LEVEL_INVALIDATED",
                    direction=break_dir,
                    rule_id="STC2-STRUCT-005",
                    symbol=symbol,
                    timeframe="H4",
                    index=i,
                    timestamp=str(candle["time"]),
                    price=level,
                    confirmation_index=i,
                    confirmation_timestamp=str(candle["time"]),
                    causal_cutoff=cutoff,
                    metadata={"invalidated_event_id": protected.event_id},
                )
                events.append(invalidated)
            active_bias = break_dir
            protected_source = last_low[2] if break_dir == "long" and last_low else last_high[2] if break_dir == "short" and last_high else source_event
            protected_type = "PROTECTED_LOW_CREATED" if break_dir == "long" else "PROTECTED_HIGH_CREATED"
            protected_price = _price(protected_source.reference_levels["price"])
            protected = _mk_struct_event(
                event_type=protected_type,
                direction=break_dir,
                rule_id="STC2-STRUCT-004",
                symbol=symbol,
                timeframe="H4",
                index=int(protected_source.source_indices[0]),
                timestamp=protected_source.source_timestamps[0],
                price=protected_price,
                confirmation_index=i,
                confirmation_timestamp=str(candle["time"]),
                causal_cutoff=cutoff,
                metadata={"created_by_choch_count": choch_count},
            )
            events.append(protected)
        else:
            event_type = "BULLISH_BOS" if break_dir == "long" else "BEARISH_BOS"
            rule_id = "STC2-BIAS-003"
        if protected is None and active_bias != "none":
            protected_source = last_low[2] if break_dir == "long" and last_low else last_high[2] if break_dir == "short" and last_high else source_event
            protected_type = "PROTECTED_LOW_CREATED" if break_dir == "long" else "PROTECTED_HIGH_CREATED"
            protected_price = _price(protected_source.reference_levels["price"])
            protected = _mk_struct_event(
                event_type=protected_type,
                direction=break_dir,
                rule_id="STC2-STRUCT-004",
                symbol=symbol,
                timeframe="H4",
                index=int(protected_source.source_indices[0]),
                timestamp=protected_source.source_timestamps[0],
                price=protected_price,
                confirmation_index=i,
                confirmation_timestamp=str(candle["time"]),
                causal_cutoff=cutoff,
                metadata={"created_by_initial_bias": event_type},
            )
            events.append(protected)
        events.append(
            _mk_struct_event(
                event_type=event_type,
                direction=break_dir,
                rule_id=rule_id,
                symbol=symbol,
                timeframe="H4",
                index=int(source_event.source_indices[0]),
                timestamp=source_event.source_timestamps[0],
                price=level,
                confirmation_index=i,
                confirmation_timestamp=str(candle["time"]),
                causal_cutoff=cutoff,
                metadata={
                    "close": str(close),
                    "source_structure_id": source_event.event_id,
                    "broken_swing_id": source_event.event_id,
                    "swing_classification": "external",
                    "bias_before": bias_before,
                    "bias_after": active_bias,
                    "displacement_score": str(displacement_score),
                    "choch_count": choch_count,
                    "classification": "choch" if "CHOCH" in event_type else "bos",
                },
            )
        )
    return tuple(sorted(events, key=lambda ev: (ev.confirmation_timestamp or "", ev.event_id)))


def classify_htf_bias(
    structure_events: Sequence[StructuralEvent],
    *,
    spec: dict[str, Any],
    symbol_metadata: SymbolMetadata | None = None,
    causal_cutoff: str | None = None,
) -> BiasEvidence:
    del spec, symbol_metadata
    cutoff = causal_cutoff or (structure_events[-1].causal_cutoff if structure_events else "")
    bias_events = [
        ev
        for ev in structure_events
        if ev.event_type in {"BULLISH_BOS", "BEARISH_BOS", "BULLISH_CHOCH", "BEARISH_CHOCH"}
    ]
    if not bias_events:
        return BiasEvidence("none", None, None, None, None, "STC2-BIAS-001", cutoff, "NO_STRUCTURAL_BIAS_EVENT")
    latest = sorted(bias_events, key=lambda ev: (ev.confirmation_timestamp or "", ev.event_id))[-1]
    protected = [
        ev
        for ev in structure_events
        if ev.event_type in {"PROTECTED_HIGH_CREATED", "PROTECTED_LOW_CREATED"}
        and ev.direction == latest.direction
        and (ev.confirmation_timestamp or "") <= (latest.confirmation_timestamp or "")
    ]
    protected_id = sorted(protected, key=lambda ev: (ev.confirmation_timestamp or "", ev.event_id))[-1].event_id if protected else None
    return BiasEvidence(
        direction=latest.direction,
        bias_event_id=latest.event_id,
        bias_evidence_timestamp=latest.confirmation_timestamp,
        bias_evidence_type="CHOCH" if "CHOCH" in latest.event_type else "BOS",
        protected_level_id=protected_id,
        classification_rule_id="STC2-BIAS-001",
        causal_cutoff=cutoff,
        reason=latest.event_type,
    )


def build_liquidity_pools(
    structure_events: Sequence[StructuralEvent],
    *,
    spec: dict[str, Any],
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
    current_index: int | None = None,
) -> tuple[LiquidityPool, ...]:
    tol_pips = Decimal(str(spec["pipeline"]["liquidity_stage"]["detect_external_liquidity"]["equal_highs_tolerance_pips"]))
    pools: list[LiquidityPool] = []
    swing_events = [ev for ev in structure_events if ev.event_type in {"SWING_HIGH", "SWING_LOW"}]
    for ev in swing_events:
        price = ev.reference_levels["price"]
        pool_type = "BUY_SIDE" if ev.event_type == "SWING_HIGH" else "SELL_SIDE"
        direction = "short" if pool_type == "BUY_SIDE" else "long"
        attrs = {
            "symbol": ev.symbol,
            "timeframe": ev.timeframe,
            "pool_type": pool_type,
            "price_level": price,
            "source_structure_ids": (ev.event_id,),
            "confirmation_timestamp": ev.confirmation_timestamp,
            "causal_cutoff": causal_cutoff,
        }
        age_bars = 0
        if current_index is not None:
            age_bars = max(0, current_index - int(ev.source_indices[0]))
        pool_id = liquidity_pool_id(attrs)
        pools.append(
            LiquidityPool(
                event_id=pool_id,
                strategy_id="ST-C2",
                strategy_version="1.2.0",
                symbol=ev.symbol,
                timeframe=ev.timeframe,
                rule_id="STC2-LIQ-002",
                event_type="LIQUIDITY_POOL",
                direction=direction,  # type: ignore[arg-type]
                source_indices=ev.source_indices,
                source_timestamps=ev.source_timestamps,
                confirmation_timestamp=ev.confirmation_timestamp,
                causal_cutoff=causal_cutoff,
                reference_levels={"price_level": price},
                status="confirmed",
                metadata={
                    "pool_type": pool_type,
                    "source_structure_ids": (ev.event_id,),
                    "age_bars": age_bars,
                    "eligibility_status": "eligible",
                    "tie_break_attributes": attrs,
                    "equal_tolerance_pips": str(tol_pips),
                    "equal_tolerance_price": str(symbol_metadata.pip_size * tol_pips),
                },
            )
        )
    return tuple(sorted(pools, key=lambda p: (p.confirmation_timestamp or "", p.event_id)))


def select_liquidity_pool(
    pools: Sequence[LiquidityPool],
    *,
    current_price: Decimal,
    direction: str,
) -> LiquidityPool | None:
    eligible = [p for p in pools if p.direction == direction and p.status == "confirmed"]
    if not eligible:
        return None
    return sorted(
        eligible,
        key=lambda p: (
            abs(_price(p.reference_levels["price_level"]) - current_price),
            p.confirmation_timestamp or "",
            p.event_id,
        ),
    )[0]


def detect_sweep_and_reclaim(
    htf_candles: Sequence[Candle],
    pool: LiquidityPool,
    *,
    spec: dict[str, Any],
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
) -> LiquiditySweep | None:
    params = spec["pipeline"]["liquidity_stage"]["detect_sweep"]
    wick_min = Decimal(str(params["wick_ratio_min"]))
    max_age = int(params["max_sweep_age_bars_htf"])
    pool_level = _price(pool.reference_levels["price_level"])
    start_i = max(pool.source_indices) + 1
    found: list[LiquiditySweep] = []
    for i in range(start_i, len(htf_candles)):
        candle = htf_candles[i]
        high = _price(candle["high"])
        low = _price(candle["low"])
        open_ = _price(candle["open"])
        close = _price(candle["close"])
        rng = high - low
        if rng <= 0:
            continue
        if pool.metadata["pool_type"] == "BUY_SIDE":
            pierced = high > pool_level
            reclaimed = close < pool_level
            wick_ratio = (high - max(open_, close)) / rng
            direction = "short"
            wick_extreme = high
        else:
            pierced = low < pool_level
            reclaimed = close > pool_level
            wick_ratio = (min(open_, close) - low) / rng
            direction = "long"
            wick_extreme = low
        age = i - int(pool.source_indices[0])
        if not pierced:
            continue
        reason = None
        status = "confirmed"
        if not reclaimed:
            reason = "SWEEP_NOT_RECLAIMED"
            status = "rejected"
        elif wick_ratio < wick_min:
            reason = "SWEEP_WICK_RATIO_INSUFFICIENT"
            status = "rejected"
        elif age > max_age:
            reason = "SWEEP_EXPIRED"
            status = "expired"
        attrs = {
            "pool_id": pool.event_id,
            "direction": direction,
            "sweep_bar_index": i,
            "sweep_timestamp": candle["time"],
            "pool_level": str(pool_level),
            "wick_extreme": str(wick_extreme),
            "close": str(close),
            "causal_cutoff": causal_cutoff,
        }
        found.append(
            LiquiditySweep(
                event_id=sweep_id(attrs),
                strategy_id="ST-C2",
                strategy_version="1.2.0",
                symbol=pool.symbol,
                timeframe=pool.timeframe,
                rule_id="STC2-LIQ-003",
                event_type="LIQUIDITY_SWEEP_RECLAIM",
                direction=direction,  # type: ignore[arg-type]
                source_indices=pool.source_indices + (i,),
                source_timestamps=pool.source_timestamps + (str(candle["time"]),),
                confirmation_timestamp=str(candle["time"]) if reclaimed else None,
                causal_cutoff=causal_cutoff,
                reference_levels={"pool_level": str(pool_level), "wick_extreme": str(wick_extreme), "close": str(close)},
                status=status,  # type: ignore[arg-type]
                invalidation_reason=reason,
                metadata={
                    "pool_id": pool.event_id,
                    "sweep_bar_index": i,
                    "sweep_timestamp": str(candle["time"]),
                    "wick_ratio": str(wick_ratio),
                    "reclaim_status": "reclaimed" if reclaimed else "not_reclaimed",
                    "reclaim_timestamp": str(candle["time"]) if reclaimed else None,
                    "max_age_status": "valid" if age <= max_age else "expired",
                    "age_bars": age,
                    "detail_reason": reason,
                },
            )
        )
    confirmed = [s for s in found if s.status == "confirmed"]
    if confirmed:
        return sorted(confirmed, key=lambda s: (s.confirmation_timestamp or "", s.event_id))[0]
    return sorted(found, key=lambda s: (s.source_timestamps[-1], s.event_id))[0] if found else None


def select_structural_dealing_range(
    structure_events: Sequence[StructuralEvent],
    sweep: LiquiditySweep,
    *,
    spec: dict[str, Any],
    symbol_metadata: SymbolMetadata | None = None,
    causal_cutoff: str,
) -> DealingRange | None:
    del spec, symbol_metadata
    swing_highs = [
        ev for ev in structure_events
        if ev.event_type == "SWING_HIGH" and (ev.confirmation_timestamp or "") <= (sweep.confirmation_timestamp or causal_cutoff)
    ]
    swing_lows = [
        ev for ev in structure_events
        if ev.event_type == "SWING_LOW" and (ev.confirmation_timestamp or "") <= (sweep.confirmation_timestamp or causal_cutoff)
    ]
    if not swing_highs or not swing_lows:
        return None
    high_ev = sorted(swing_highs, key=lambda ev: (ev.confirmation_timestamp or "", ev.event_id))[-1]
    low_ev = sorted(swing_lows, key=lambda ev: (ev.confirmation_timestamp or "", ev.event_id))[-1]
    high = _price(high_ev.reference_levels["price"])
    low = _price(low_ev.reference_levels["price"])
    if high <= low:
        return None
    eq = (high + low) / Decimal("2")
    attrs = {
        "direction": sweep.direction,
        "anchor_high_event_id": high_ev.event_id,
        "anchor_low_event_id": low_ev.event_id,
        "high": str(high),
        "low": str(low),
        "causal_cutoff": causal_cutoff,
    }
    return DealingRange(
        range_id=stable_id("dealing_range", attrs),
        direction=sweep.direction,
        anchor_high_event_id=high_ev.event_id,
        anchor_low_event_id=low_ev.event_id,
        high=high,
        low=low,
        equilibrium=eq,
        creation_timestamp=sweep.source_timestamps[-1],
        confirmation_timestamp=sweep.confirmation_timestamp or sweep.source_timestamps[-1],
        age_bars=0,
        status="confirmed",
        invalidation_reason=None,
        causal_cutoff=causal_cutoff,
    )


def evaluate_ote_location(
    candidate_price: Decimal,
    dealing_range: DealingRange,
    *,
    direction: str,
    spec: dict[str, Any],
    symbol_metadata: SymbolMetadata | None = None,
    causal_cutoff: str,
) -> OTEEvidence:
    del symbol_metadata
    if dealing_range.status != "confirmed" or dealing_range.high <= dealing_range.low:
        return OTEEvidence(
            dealing_range.range_id,
            candidate_price,
            Decimal("0"),
            "invalid",
            False,
            Decimal("0.5"),
            Decimal(str(spec["pipeline"]["ote_stage"]["max_retrace_pct"])),
            "STC2-OTE-001",
            causal_cutoff,
            "INVALID_RANGE",
        )
    span = dealing_range.high - dealing_range.low
    normalized = (candidate_price - dealing_range.low) / span
    eq = Decimal(str(spec["pipeline"]["ote_stage"]["equilibrium_boundary"]))
    upper = Decimal(str(spec["pipeline"]["ote_stage"]["max_retrace_pct"]))
    if normalized < eq:
        zone = "discount"
    elif normalized > eq:
        zone = "premium"
    else:
        zone = "equilibrium"
    if direction == "long":
        eligible = eq <= (Decimal("1") - normalized) <= upper and zone in {"discount", "equilibrium"}
        detail = None if eligible else "LONG_NOT_IN_DISCOUNT_OTE"
    else:
        eligible = eq <= normalized <= upper and zone in {"premium", "equilibrium"}
        detail = None if eligible else "SHORT_NOT_IN_PREMIUM_OTE"
    return OTEEvidence(
        range_id=dealing_range.range_id,
        candidate_price=candidate_price,
        normalized_position=normalized,
        zone=zone,
        ote_eligible=eligible,
        fib_lower=eq,
        fib_upper=upper,
        rule_id="STC2-OTE-002",
        causal_cutoff=causal_cutoff,
        rejection_detail=detail,
    )


def structural_context(
    htf: Sequence[Candle],
    mf: Sequence[Candle],
    *,
    spec: dict[str, Any],
    symbol: str = "GBPUSD",
) -> dict[str, Any]:
    metadata = load_symbol_metadata(symbol)
    cutoff = str(htf[-1]["time"]) if htf else ""
    events = detect_htf_structure(htf, spec=spec, symbol_metadata=metadata, causal_cutoff=cutoff, symbol=symbol)
    bias = classify_htf_bias(events, spec=spec, symbol_metadata=metadata, causal_cutoff=cutoff)
    if bias.direction == "none":
        return {"events": events, "bias": bias, "pool": None, "sweep": None, "range": None, "ote": None}
    pools = build_liquidity_pools(events, spec=spec, symbol_metadata=metadata, causal_cutoff=cutoff, current_index=len(htf) - 1)
    current_price = _price(htf[-1]["close"])
    pool = select_liquidity_pool(pools, current_price=current_price, direction=bias.direction)
    sweep = detect_sweep_and_reclaim(htf, pool, spec=spec, symbol_metadata=metadata, causal_cutoff=cutoff) if pool else None
    dealing_range = select_structural_dealing_range(events, sweep, spec=spec, symbol_metadata=metadata, causal_cutoff=cutoff) if sweep and sweep.status == "confirmed" else None
    candidate = _price(mf[-1]["close"]) if mf else current_price
    ote = evaluate_ote_location(candidate, dealing_range, direction=bias.direction, spec=spec, symbol_metadata=metadata, causal_cutoff=cutoff) if dealing_range else None
    return {"events": events, "bias": bias, "pools": pools, "pool": pool, "sweep": sweep, "range": dealing_range, "ote": ote}
