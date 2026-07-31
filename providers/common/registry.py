from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_provider_registry(path: str | Path = "providers/provider_registry.yaml") -> dict[str, Any]:
    registry = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(registry, dict):
        raise ValueError("provider registry must be a mapping")
    providers = registry.get("providers")
    if not isinstance(providers, dict) or not providers:
        raise ValueError("provider registry must include providers")
    required = {"status", "license", "api", "cost", "symbols", "timeframes", "evaluation_status"}
    for name, provider in providers.items():
        missing = required - set(provider or {})
        if missing:
            raise ValueError(f"provider {name} missing fields: {sorted(missing)}")
    return registry
