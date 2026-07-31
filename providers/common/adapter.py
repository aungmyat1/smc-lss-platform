from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class HealthCheck:
    provider: str
    ok: bool
    status: str
    reason: str
    evidence_path: str | None = None


@dataclass(frozen=True)
class ProviderMetadata:
    provider: str
    symbols: tuple[str, ...]
    timeframes: tuple[str, ...]
    timezone: str
    license_status: str
    credential_env: str | None = None


@dataclass(frozen=True)
class NormalizedBar:
    timestamp: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    tick_volume: float
    spread: float | None
    provider: str
    timezone: str
    session: str
    schema_version: str = "st-c4.1-normalized-v1"


class ProviderAdapter(Protocol):
    name: str

    def metadata(self) -> ProviderMetadata:
        ...

    def health_check(self) -> HealthCheck:
        ...

    def download_sample(self, output_dir: str | Path, *, days: int = 100) -> dict[str, Any]:
        ...

    def download_range(self, output_dir: str | Path, start: str, end: str) -> dict[str, Any]:
        ...

    def normalize(self, input_dir: str | Path, output_dir: str | Path) -> dict[str, Any]:
        ...

    def validate(self, normalized_dir: str | Path) -> dict[str, Any]:
        ...
