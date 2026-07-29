"""Approved ST-C3 market dataset loader and validator."""
from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

MANIFEST_NAME = "DATASET_MANIFEST_ST_C3.yaml"
REQUIRED_COLUMNS = ("time", "open", "high", "low", "close", "volume")
OPTIONAL_BOOLEAN_COLUMNS = ("news_flag",)
OPTIONAL_ENUM_COLUMNS = {"session": {"LONDON", "NY", "OTHER", ""}}
EXPECTED_SYMBOLS = frozenset({"EURUSD", "GBPUSD"})
EXPECTED_TIMEFRAMES = frozenset({"H4", "M15", "M3"})
EXPECTED_SYMBOL_METADATA = {
    "EURUSD": {"point_size": 0.0001, "quote_currency": "USD"},
    "GBPUSD": {"point_size": 0.0001, "quote_currency": "USD"},
}
EXPECTED_SESSIONS = {
    "london_window_utc": "07:00-10:00 UTC",
    "ny_window_utc": "13:00-16:00 UTC",
}
TIMEFRAME_DELTAS = {
    "M1": timedelta(minutes=1),
    "M3": timedelta(minutes=3),
    "M5": timedelta(minutes=5),
    "M15": timedelta(minutes=15),
    "H1": timedelta(hours=1),
    "H4": timedelta(hours=4),
    "D1": timedelta(days=1),
}


@dataclass(frozen=True)
class DatasetFileSummary:
    symbol: str
    timeframe: str
    path: str
    sha256: str
    rows: int
    first_timestamp: str
    last_timestamp: str


@dataclass(frozen=True)
class ApprovedDataset:
    data_dir: str
    manifest_path: str
    manifest: Mapping[str, Any]
    files: tuple[DatasetFileSummary, ...]

    def to_meta(self) -> dict[str, Any]:
        return {
            "approved_data_dir": self.data_dir,
            "approval_manifest": self.manifest_path,
            "dataset_approved": bool(self.manifest.get("approved")),
            "dataset_files": [item.__dict__ for item in self.files],
        }


def load_approved_dataset(
    data_dir: str | Path,
    *,
    symbols: Iterable[str],
    timeframes: Iterable[str],
    date_from: str,
    date_to: str,
    spec_version: str,
) -> ApprovedDataset:
    root = Path(data_dir)
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing ST-C3 dataset manifest: {manifest_path}")
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, Mapping):
        raise ValueError("dataset manifest must be a mapping")
    _validate_required_manifest_fields(manifest)
    if manifest.get("strategy") != "ST-C3":
        raise ValueError("dataset manifest strategy must be ST-C3")
    if str(manifest.get("spec_version")) != spec_version:
        raise ValueError(f"dataset manifest spec_version must be {spec_version}")
    if manifest.get("approved") is not True:
        raise ValueError("dataset manifest is not approved; set approved: true only after owner approval")

    requested_symbols = set(symbols)
    requested_timeframes = set(timeframes)
    manifest_symbols = set(manifest.get("symbols") or [])
    manifest_timeframes = set(manifest.get("timeframes") or [])
    if manifest_symbols != EXPECTED_SYMBOLS:
        raise ValueError(f"manifest symbols must be exactly {sorted(EXPECTED_SYMBOLS)}")
    if manifest_timeframes != EXPECTED_TIMEFRAMES:
        raise ValueError(f"manifest timeframes must be exactly {sorted(EXPECTED_TIMEFRAMES)}")
    if requested_symbols != EXPECTED_SYMBOLS:
        raise ValueError(f"requested symbols must be exactly {sorted(EXPECTED_SYMBOLS)}")
    if requested_timeframes != EXPECTED_TIMEFRAMES:
        raise ValueError(f"requested timeframes must be exactly {sorted(EXPECTED_TIMEFRAMES)}")
    _validate_coverage(manifest.get("coverage") or {}, date_from, date_to)
    _validate_sessions(manifest.get("sessions") or {})
    _validate_symbol_metadata(manifest.get("symbol_metadata") or {}, requested_symbols)

    files = _normalize_files(manifest.get("files"))

    selected: list[DatasetFileSummary] = []
    by_key = {(item.get("symbol"), item.get("timeframe")): item for item in files if isinstance(item, Mapping)}
    for symbol in sorted(requested_symbols):
        for timeframe in sorted(requested_timeframes):
            entry = by_key.get((symbol, timeframe))
            if entry is None:
                raise ValueError(f"manifest missing file entry for {symbol} {timeframe}")
            selected.append(_validate_dataset_entry(root, entry))
    return ApprovedDataset(
        data_dir=str(root),
        manifest_path=str(manifest_path),
        manifest=manifest,
        files=tuple(selected),
    )


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_dataset_entry(root: Path, entry: Mapping[str, Any]) -> DatasetFileSummary:
    raw_path = entry.get("path")
    if not raw_path:
        raise ValueError("dataset entry missing path")
    path = (root / str(raw_path)).resolve()
    if not path.exists():
        raise FileNotFoundError(f"dataset file missing: {path}")
    digest = sha256_file(path)
    expected = entry.get("sha256")
    if expected and str(expected).lower() != digest:
        raise ValueError(f"sha256 mismatch for {path}")
    summary = _validate_csv(path, timeframe=str(entry["timeframe"]))
    return DatasetFileSummary(
        symbol=str(entry["symbol"]),
        timeframe=str(entry["timeframe"]),
        path=str(path),
        sha256=digest,
        rows=summary["rows"],
        first_timestamp=summary["first_timestamp"],
        last_timestamp=summary["last_timestamp"],
    )


def _normalize_files(raw_files: Any) -> list[Mapping[str, Any]]:
    if isinstance(raw_files, list):
        return [item for item in raw_files if isinstance(item, Mapping)]
    if isinstance(raw_files, Mapping):
        normalized = []
        for file_name, metadata in raw_files.items():
            if not isinstance(metadata, Mapping):
                raise ValueError(f"dataset file entry {file_name} must be a mapping")
            stem = Path(str(file_name)).stem
            parts = stem.split("_")
            if len(parts) < 2:
                raise ValueError(f"dataset file name must encode symbol and timeframe: {file_name}")
            normalized.append(
                {
                    "symbol": "_".join(parts[:-1]),
                    "timeframe": parts[-1],
                    "path": str(file_name),
                    "sha256": metadata.get("sha256"),
                }
            )
        return normalized
    raise ValueError("dataset manifest requires files as a list or mapping")


def _validate_csv(path: Path, *, timeframe: str) -> dict[str, Any]:
    expected_delta = TIMEFRAME_DELTAS.get(timeframe)
    if expected_delta is None:
        raise ValueError(f"{path}: unsupported timeframe {timeframe}")
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: missing header")
        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"{path}: missing required columns: {missing}")
        fieldnames = set(reader.fieldnames)
        previous: datetime | None = None
        rows = 0
        first: datetime | None = None
        last: datetime | None = None
        seen: set[datetime] = set()
        for row in reader:
            current = _parse_timestamp(row["time"])
            if current in seen:
                raise ValueError(f"{path}: duplicate timestamp {row['time']}")
            if previous is not None and current <= previous:
                raise ValueError(f"{path}: timestamps must be strictly increasing")
            if previous is not None and current - previous != expected_delta:
                raise ValueError(f"{path}: missing or irregular candle between {previous} and {current}")
            for column in ("open", "high", "low", "close", "volume"):
                value = float(row[column])
                if column == "volume" and value < 0:
                    raise ValueError(f"{path}: volume must be non-negative")
            _validate_optional_columns(path, row, fieldnames)
            seen.add(current)
            previous = current
            first = first or current
            last = current
            rows += 1
    if rows == 0:
        raise ValueError(f"{path}: no candle rows")
    return {
        "rows": rows,
        "first_timestamp": first.isoformat() + "Z",
        "last_timestamp": last.isoformat() + "Z",
    }


def _parse_timestamp(value: str) -> datetime:
    cleaned = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(cleaned)
    except ValueError:
        parsed = datetime.strptime(value.strip()[:16], "%Y-%m-%d %H:%M")
    return parsed.replace(tzinfo=None)


def _validate_required_manifest_fields(manifest: Mapping[str, Any]) -> None:
    required = {
        "approved",
        "approval_status",
        "approval_date",
        "approved_by",
        "spec_version",
        "symbols",
        "timeframes",
        "coverage",
        "files",
        "sessions",
        "symbol_metadata",
    }
    missing = sorted(required - set(manifest))
    if missing:
        raise ValueError(f"dataset manifest missing required fields: {missing}")
    for field in ("approval_status", "approval_date", "approved_by"):
        if not str(manifest.get(field) or "").strip():
            raise ValueError(f"dataset manifest {field} must be populated")


def _validate_coverage(coverage: Mapping[str, Any], requested_from: str, requested_to: str) -> None:
    manifest_from = str(coverage.get("from", ""))
    manifest_to = str(coverage.get("to", ""))
    if not manifest_from or not manifest_to:
        raise ValueError("manifest coverage requires from and to")
    _parse_date(manifest_from, "coverage.from")
    _parse_date(manifest_to, "coverage.to")
    _parse_date(requested_from, "requested date_from")
    _parse_date(requested_to, "requested date_to")
    if manifest_from > manifest_to:
        raise ValueError("manifest coverage.from must be <= coverage.to")
    if manifest_from > requested_from or manifest_to < requested_to:
        raise ValueError(
            f"manifest coverage {manifest_from}..{manifest_to} does not cover requested {requested_from}..{requested_to}"
        )


def _validate_sessions(sessions: Mapping[str, Any]) -> None:
    for key, expected in EXPECTED_SESSIONS.items():
        if sessions.get(key) != expected:
            raise ValueError(f"manifest sessions.{key} must be {expected}")


def _validate_symbol_metadata(metadata: Mapping[str, Any], symbols: set[str]) -> None:
    missing = sorted(symbol for symbol in symbols if symbol not in metadata)
    if missing:
        raise ValueError(f"manifest missing symbol metadata: {missing}")
    for symbol in symbols:
        entry = metadata[symbol]
        if not isinstance(entry, Mapping):
            raise ValueError(f"symbol metadata for {symbol} must be a mapping")
        expected = EXPECTED_SYMBOL_METADATA[symbol]
        for key, expected_value in expected.items():
            if entry.get(key) != expected_value:
                raise ValueError(f"symbol metadata for {symbol}.{key} must be {expected_value}")


def _validate_optional_columns(path: Path, row: Mapping[str, str], fieldnames: set[str]) -> None:
    for column in OPTIONAL_BOOLEAN_COLUMNS:
        if column in fieldnames and row[column].strip().lower() not in {"true", "false", "1", "0", "yes", "no", ""}:
            raise ValueError(f"{path}: {column} must be boolean-like")
    for column, allowed in OPTIONAL_ENUM_COLUMNS.items():
        if column in fieldnames and row[column].strip() not in allowed:
            raise ValueError(f"{path}: {column} must be one of {sorted(allowed)}")


def _parse_date(value: str, field_name: str) -> datetime:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(f"manifest {field_name} must be YYYY-MM-DD") from exc
