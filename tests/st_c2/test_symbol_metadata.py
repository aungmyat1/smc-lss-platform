from decimal import Decimal

from validation.st_c2.symbols import (
    compare_price_with_tolerance,
    load_symbol_metadata,
    normalize_distance,
    normalize_price,
    pips_to_price,
    points_to_price,
    price_to_points,
)


def test_symbol_metadata_loading():
    meta = load_symbol_metadata("GBPUSD")
    assert meta.symbol == "GBPUSD"
    assert meta.digits == 5
    assert meta.point_size == Decimal("0.00001")
    assert meta.pip_size == Decimal("0.0001")
    assert meta.points_per_pip == Decimal("10")
    assert meta.timezone_basis == "UTC"


def test_point_and_pip_conversions_boundaries():
    meta = load_symbol_metadata("GBPUSD")
    assert points_to_price(1, meta) == Decimal("0.00001")
    assert points_to_price(Decimal("2.5"), meta) == Decimal("0.000025")
    assert points_to_price(10, meta) == Decimal("0.00010")
    assert pips_to_price(1, meta) == Decimal("0.0001")
    assert price_to_points(Decimal("0.00010"), meta) == Decimal("10")


def test_price_normalization_and_distance_behavior():
    meta = load_symbol_metadata("GBPUSD")
    assert normalize_price("1.234565", meta) == Decimal("1.23457")
    assert normalize_price("1.234564", meta) == Decimal("1.23456")
    assert normalize_distance("-0.000025", meta) == Decimal("0.00003")
    assert normalize_distance("0", meta) == Decimal("0.00000")


def test_compare_price_with_tolerance():
    meta = load_symbol_metadata("GBPUSD")
    assert compare_price_with_tolerance("1.25000", "1.25002", 2, meta)
    assert not compare_price_with_tolerance("1.25000", "1.25003", 2, meta)


def test_stop_distance_boundaries_from_provisional_gbp_spec_values():
    meta = load_symbol_metadata("GBPUSD")
    assert points_to_price(35, meta) == Decimal("0.00035")
    assert points_to_price(150, meta) == Decimal("0.00150")
