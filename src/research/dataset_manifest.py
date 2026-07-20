"""Dataset manifest helpers for deterministic research runs."""
from __future__ import annotations

import csv
import datetime as dt
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


def _parse_time(value: str) -> dt.datetime:
    cleaned = value.replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(cleaned)
    except ValueError:
        parsed = dt.datetime.strptime(value[:16], "%Y-%m-%d %H:%M")
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt.UTC)
    return parsed.astimezone(dt.UTC)


def _bar_semantics(timeframe: str) -> str:
    label = timeframe.upper() if timeframe else "UNKNOWN"
    return f"{label} bar-open timestamp; visible only after close"


@dataclass(frozen=True)
class DatasetArtifact:
    symbol: str
    source_symbol: str
    timeframe: str
    path: str
    sha256: str
    rows: int | None = None
    first_timestamp: str | None = None
    last_timestamp: str | None = None
    timezone: str = "UTC"
    bar_semantics: str = "bar-open timestamp; visible only after close"


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
    dataset_metadata: Iterable[dict[str, Any]] | None = None,
) -> DatasetManifest:
    metadata_by_path = {
        str(item["path"]): dict(item)
        for item in (dataset_metadata or [])
        if isinstance(item, dict) and "path" in item
    }
    datasets: list[DatasetArtifact] = []
    for path in dataset_paths:
        p = Path(path)
        if not p.exists():
            continue
        meta = metadata_by_path.get(str(p), {})
        rows = meta.get("rows")
        first_timestamp = meta.get("first_timestamp")
        last_timestamp = meta.get("last_timestamp")
        if rows is None or first_timestamp is None or last_timestamp is None:
            with p.open(newline="", encoding="utf-8") as fh:
                reader = list(csv.DictReader(fh))
            rows = len(reader)
            if reader:
                first_timestamp = _parse_time(reader[0]["time"]).isoformat().replace("+00:00", "Z")
                last_timestamp = _parse_time(reader[-1]["time"]).isoformat().replace("+00:00", "Z")
        timeframe = str(meta.get("timeframe", p.stem.split("_")[-1] if "_" in p.stem else ""))
        datasets.append(
            DatasetArtifact(
                symbol=str(meta.get("symbol", "")),
                source_symbol=str(meta.get("source_symbol", meta.get("symbol", ""))),
                timeframe=timeframe,
                path=str(p),
                sha256=sha256_file(p),
                rows=int(rows) if rows is not None else None,
                first_timestamp=first_timestamp,
                last_timestamp=last_timestamp,
                timezone=str(meta.get("timezone", "UTC")),
                bar_semantics=str(meta.get("bar_semantics", _bar_semantics(timeframe))),
            )
        )
    return DatasetManifest(
        strategy_id=strategy_id,
        strategy_version=strategy_version,
        git_sha=git_sha,
        generated_utc=generated_utc,
        random_seed=random_seed,
        spec_path=str(spec_path),
        cost_profile_path=str(cost_profile_path),
        datasets=tuple(datasets),
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
