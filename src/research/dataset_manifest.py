"""Dataset manifest helpers for deterministic research runs."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Iterable


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class DatasetArtifact:
    path: str
    sha256: str
    rows: int | None = None


@dataclass(frozen=True)
class DatasetManifest:
    strategy_id: str
    strategy_version: str
    git_sha: str
    generated_utc: str
    random_seed: int
    spec_path: str
    cost_profile_path: str
    datasets: tuple[DatasetArtifact, ...] = field(default_factory=tuple)
    symbols: tuple[str, ...] = field(default_factory=tuple)
    timeframes: tuple[str, ...] = field(default_factory=tuple)
    date_ranges: dict[str, Any] = field(default_factory=dict)
    execution_assumptions: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["datasets"] = [asdict(item) for item in self.datasets]
        return payload


def build_dataset_manifest(
    *,
    strategy_id: str,
    strategy_version: str,
    git_sha: str,
    generated_utc: str,
    random_seed: int,
    spec_path: str,
    cost_profile_path: str,
    dataset_paths: Iterable[str | Path],
    symbols: Iterable[str],
    timeframes: Iterable[str],
    date_ranges: dict[str, Any],
    execution_assumptions: dict[str, Any],
) -> DatasetManifest:
    datasets = tuple(DatasetArtifact(path=str(path), sha256=sha256_file(path)) for path in dataset_paths if Path(path).exists())
    return DatasetManifest(
        strategy_id=strategy_id,
        strategy_version=strategy_version,
        git_sha=git_sha,
        generated_utc=generated_utc,
        random_seed=random_seed,
        spec_path=str(spec_path),
        cost_profile_path=str(cost_profile_path),
        datasets=datasets,
        symbols=tuple(symbols),
        timeframes=tuple(timeframes),
        date_ranges=date_ranges,
        execution_assumptions=execution_assumptions,
    )


def write_manifest(path: str | Path, manifest: DatasetManifest) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(target)

