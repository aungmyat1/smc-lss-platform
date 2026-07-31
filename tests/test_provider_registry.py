from __future__ import annotations

from providers.common.registry import load_provider_registry


def test_provider_registry_contains_required_candidates():
    registry = load_provider_registry()

    assert registry["schema_version"] == "st-c4.1-provider-registry-v1"
    assert set(registry["providers"]) >= {"dukascopy", "truefx", "tiingo", "histdata", "darwinex", "mt5"}
    for provider in registry["providers"].values():
        assert {"status", "license", "api", "cost", "symbols", "timeframes", "evaluation_status"} <= set(provider)
