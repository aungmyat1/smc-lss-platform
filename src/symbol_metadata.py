"""Canonical symbol metadata for research and execution-adjacent modules.

The repository previously spread pip and point assumptions across validation
and live code. This module centralizes the canonical symbol description so
research, replay, and live sizing can resolve aliases consistently.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class SymbolMetadata:
    canonical_symbol: str
    aliases: tuple[str, ...]
    asset_class: str
    point_size: float
    pip_size: float
    tick_size: float
    tick_value: float
    contract_size: float
    min_lot: float
    max_lot: float
    lot_step: float
    price_digits: int
    spread_units: str
    commission_model: str
    default_slippage_points: float
    version: str = "symbol-metadata-v1"

    @property
    def pip_value_per_lot(self) -> float:
        if self.tick_size <= 0:
            return 0.0
        ticks_per_pip = self.pip_size / self.tick_size
        return round(self.tick_value * ticks_per_pip, 10)

    @property
    def point_value_per_lot(self) -> float:
        if self.tick_size <= 0:
            return 0.0
        ticks_per_point = self.point_size / self.tick_size
        return round(self.tick_value * ticks_per_point, 10)

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["pip_value_per_lot"] = self.pip_value_per_lot
        payload["point_value_per_lot"] = self.point_value_per_lot
        return payload


_REGISTRY: tuple[SymbolMetadata, ...] = (
    SymbolMetadata(
        canonical_symbol="EURUSD",
        aliases=("EURUSD", "EURUSD-VIP", "EURUSDm"),
        asset_class="forex",
        point_size=0.00001,
        pip_size=0.0001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        min_lot=0.01,
        max_lot=100.0,
        lot_step=0.01,
        price_digits=5,
        spread_units="points",
        commission_model="per_lot_usd_round_turn",
        default_slippage_points=3.0,
    ),
    SymbolMetadata(
        canonical_symbol="GBPUSD",
        aliases=("GBPUSD", "GBPUSD-VIP", "GBPUSDm"),
        asset_class="forex",
        point_size=0.00001,
        pip_size=0.0001,
        tick_size=0.00001,
        tick_value=1.0,
        contract_size=100000.0,
        min_lot=0.01,
        max_lot=100.0,
        lot_step=0.01,
        price_digits=5,
        spread_units="points",
        commission_model="per_lot_usd_round_turn",
        default_slippage_points=3.0,
    ),
    SymbolMetadata(
        canonical_symbol="XAUUSD",
        aliases=("XAUUSD", "XAUUSD-VIP", "GOLD"),
        asset_class="metals",
        point_size=0.01,
        pip_size=0.1,
        tick_size=0.01,
        tick_value=1.0,
        contract_size=100.0,
        min_lot=0.01,
        max_lot=50.0,
        lot_step=0.01,
        price_digits=2,
        spread_units="points",
        commission_model="per_lot_usd_round_turn",
        default_slippage_points=5.0,
    ),
    SymbolMetadata(
        canonical_symbol="BTCUSD",
        aliases=("BTCUSD", "BTCUSD-VIP", "BTCUSDm"),
        asset_class="crypto",
        point_size=0.01,
        pip_size=1.0,
        tick_size=0.01,
        tick_value=1.0,
        contract_size=1.0,
        min_lot=0.01,
        max_lot=10.0,
        lot_step=0.01,
        price_digits=2,
        spread_units="points",
        commission_model="per_lot_usd_round_turn",
        default_slippage_points=10.0,
    ),
)

_ALIASES: dict[str, SymbolMetadata] = {}
for meta in _REGISTRY:
    for alias in meta.aliases:
        _ALIASES[alias.upper()] = meta


def resolve_symbol(symbol: str) -> SymbolMetadata:
    """Return canonical metadata for a symbol or alias.

    Raises:
        KeyError: if the symbol is unknown.
    """
    key = symbol.upper().strip()
    if key not in _ALIASES:
        raise KeyError(f"unknown symbol alias: {symbol!r}")
    return _ALIASES[key]


def available_symbols() -> tuple[str, ...]:
    return tuple(meta.canonical_symbol for meta in _REGISTRY)


def symbol_snapshot() -> dict[str, dict[str, Any]]:
    return {meta.canonical_symbol: meta.snapshot() for meta in _REGISTRY}

