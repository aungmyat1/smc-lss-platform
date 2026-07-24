"""Symbol metadata and price-normalization utilities for ST-C2 conformance."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

import yaml


METADATA_PATH = Path("specs/st_c2/symbol_metadata.yaml")


@dataclass(frozen=True)
class SymbolMetadata:
    symbol: str
    digits: int
    point_size: Decimal
    pip_size: Decimal
    points_per_pip: Decimal
    price_rounding_digits: int
    volume_step: Decimal | None
    timezone_basis: str
    rounding_mode: str = "ROUND_HALF_UP"

    @property
    def quantum(self) -> Decimal:
        return Decimal(1).scaleb(-self.price_rounding_digits)


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def load_symbol_metadata(symbol: str = "GBPUSD", path: Path | str = METADATA_PATH) -> SymbolMetadata:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    raw = data["symbols"][symbol]
    return SymbolMetadata(
        symbol=raw["symbol"],
        digits=int(raw["digits"]),
        point_size=_decimal(raw["point_size"]),
        pip_size=_decimal(raw["pip_size"]),
        points_per_pip=_decimal(raw["points_per_pip"]),
        price_rounding_digits=int(raw["price_rounding_digits"]),
        volume_step=None if raw.get("volume_step") is None else _decimal(raw["volume_step"]),
        timezone_basis=str(raw["timezone_basis"]),
        rounding_mode=str(raw.get("rounding_mode", "ROUND_HALF_UP")),
    )


def _rounding_mode(meta: SymbolMetadata) -> str:
    if meta.rounding_mode != "ROUND_HALF_UP":
        raise ValueError(f"unsupported rounding mode: {meta.rounding_mode}")
    return ROUND_HALF_UP


def points_to_price(points: Decimal | int | float | str, meta: SymbolMetadata) -> Decimal:
    return _decimal(points) * meta.point_size


def price_to_points(price_distance: Decimal | int | float | str, meta: SymbolMetadata) -> Decimal:
    return _decimal(price_distance) / meta.point_size


def pips_to_price(pips: Decimal | int | float | str, meta: SymbolMetadata) -> Decimal:
    return _decimal(pips) * meta.pip_size


def normalize_price(price: Decimal | int | float | str, meta: SymbolMetadata) -> Decimal:
    return _decimal(price).quantize(meta.quantum, rounding=_rounding_mode(meta))


def normalize_distance(distance: Decimal | int | float | str, meta: SymbolMetadata) -> Decimal:
    return abs(_decimal(distance)).quantize(meta.quantum, rounding=_rounding_mode(meta))


def compare_price_with_tolerance(
    left: Decimal | int | float | str,
    right: Decimal | int | float | str,
    tolerance_points: Decimal | int | float | str,
    meta: SymbolMetadata,
) -> bool:
    tolerance = points_to_price(tolerance_points, meta)
    return abs(_decimal(left) - _decimal(right)) <= tolerance
