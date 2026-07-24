from dataclasses import FrozenInstanceError

import pytest

from validation.st_c2.identifiers import liquidity_pool_id, stable_id, sweep_id
from validation.st_c2.schemas import LiquiditySweep


def _attrs():
    return {
        "strategy_id": "ST-C2",
        "strategy_version": "1.2.0",
        "symbol": "GBPUSD",
        "timeframe": "H4",
        "rule_id": "STC2-LIQ-003",
        "timestamp": "2026-06-10 16:00",
        "price": "1.34760",
        "direction": "bear",
        "metadata": {"diagnostic": "ignored"},
    }


def test_stable_id_repeatability():
    assert liquidity_pool_id(_attrs()) == liquidity_pool_id(_attrs())


def test_stable_id_defining_field_mutation_changes_id():
    original = _attrs()
    changed = {**original, "price": "1.34761"}
    assert liquidity_pool_id(original) != liquidity_pool_id(changed)


def test_stable_id_non_defining_metadata_invariance():
    original = _attrs()
    changed = {**original, "metadata": {"diagnostic": "changed"}}
    assert liquidity_pool_id(original) == liquidity_pool_id(changed)


def test_stable_id_collision_sanity_across_object_types():
    attrs = _attrs()
    assert liquidity_pool_id(attrs) != sweep_id(attrs)


def test_schema_immutability_and_serialization():
    sweep = LiquiditySweep(
        event_id=stable_id("sweep", _attrs()),
        strategy_id="ST-C2",
        strategy_version="1.2.0",
        symbol="GBPUSD",
        timeframe="H4",
        rule_id="STC2-LIQ-003",
        event_type="liquidity_sweep",
        direction="short",
        source_indices=(10, 12),
        source_timestamps=("2026-06-10 12:00", "2026-06-10 16:00"),
        confirmation_timestamp="2026-06-10 16:00",
        causal_cutoff="2026-06-10 16:00",
        reference_levels={"sweep_level": "1.34760"},
        status="confirmed",
    )
    assert sweep.to_dict()["event_id"].startswith("SWEEP-")
    with pytest.raises(FrozenInstanceError):
        sweep.status = "invalidated"  # type: ignore[misc]
