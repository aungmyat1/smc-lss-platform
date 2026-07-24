"""Typed structural interfaces for later ST-C2 S1-G2 slices.

These functions intentionally define contracts without implementing detector
semantics in GC1.
"""
from __future__ import annotations

from typing import Sequence

from validation.st_c2.schemas import (
    ConfirmationEvent,
    FVGEvent,
    LiquidityPool,
    LiquiditySweep,
    LogicalTradePlan,
    SignalCandidate,
    StateTransition,
    StructuralEvent,
)
from validation.st_c2.symbols import SymbolMetadata

Candle = dict[str, float | str]


def detect_htf_structure(
    htf_candles: Sequence[Candle],
    *,
    spec: dict,
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
) -> tuple[StructuralEvent, ...]:
    """H4 input; consumes htf_structure params; returns structural events."""
    raise NotImplementedError("planned slice: S1-G2-GC2")


def classify_htf_bias(
    structure_events: Sequence[StructuralEvent],
    *,
    spec: dict,
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
) -> StructuralEvent:
    """Consumes HTF BOS/CHoCH events only; returns one bias event or rejection."""
    raise NotImplementedError("planned slice: S1-G2-GC2")


def select_liquidity_pool(
    htf_candles: Sequence[Candle],
    *,
    spec: dict,
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
) -> LiquidityPool:
    """H4 input; consumes liquidity pool priority and stable-ID tie-break rules."""
    raise NotImplementedError("planned slice: S1-G2-GC2")


def detect_sweep_and_reclaim(
    htf_candles: Sequence[Candle],
    pool: LiquidityPool,
    *,
    spec: dict,
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
) -> LiquiditySweep:
    """H4 input; consumes sweep wick, reclaim, and max-age parameters."""
    raise NotImplementedError("planned slice: S1-G2-GC2")


def select_structural_dealing_range(
    structure_events: Sequence[StructuralEvent],
    sweep: LiquiditySweep,
    *,
    spec: dict,
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
) -> StructuralEvent:
    """Selects and freezes the external swing range tied to triggering liquidity."""
    raise NotImplementedError("planned slice: S1-G2-GC2")


def evaluate_ote_location(
    mf_candles: Sequence[Candle],
    dealing_range: StructuralEvent,
    *,
    spec: dict,
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
) -> StructuralEvent:
    """M15 input; consumes OTE/equilibrium/range invalidation rules."""
    raise NotImplementedError("planned slice: S1-G2-GC3")


def detect_fvg_chain(
    htf_candles: Sequence[Candle],
    mf_candles: Sequence[Candle],
    ltf_candles: Sequence[Candle],
    *,
    spec: dict,
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
) -> tuple[FVGEvent, ...]:
    """H4/M15/M3 input; consumes FVG geometry, confluence, age, and invalidation."""
    raise NotImplementedError("planned slice: S1-G2-GC3")


def detect_ltf_confirmation(
    ltf_candles: Sequence[Candle],
    *,
    spec: dict,
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
) -> ConfirmationEvent:
    """M3 input; consumes internal BOS, CHoCH, first-bar, and max-setup rules."""
    raise NotImplementedError("planned slice: S1-G2-GC3")


def advance_strategy_state(
    previous_state: str,
    event: StructuralEvent | LiquidityPool | LiquiditySweep | FVGEvent | ConfirmationEvent,
    *,
    spec: dict,
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
) -> StateTransition:
    """Consumes sequencing, invalidation, expiry, duplicate, and rejection rules."""
    raise NotImplementedError("planned slice: S1-G2-GC4")


def build_logical_trade_plan(
    signal: SignalCandidate,
    source_events: Sequence[StructuralEvent | LiquidityPool | LiquiditySweep | FVGEvent | ConfirmationEvent],
    *,
    spec: dict,
    symbol_metadata: SymbolMetadata,
    causal_cutoff: str,
) -> LogicalTradePlan:
    """Builds research-only logical entry/SL/TP/RR package; no broker behavior."""
    raise NotImplementedError("planned slice: S1-G2-GC4")
