#!/usr/bin/env python3
"""Populate ST-C3 approved dataset manifest hashes after CSV validation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from validation.st_c3.dataset_loader import (
    EXPECTED_SYMBOLS,
    EXPECTED_TIMEFRAMES,
    MANIFEST_NAME,
    _normalize_files,
    _validate_csv,
    _validate_csv_covers_requested_range,
    sha256_file,
)


def prepare_dataset_manifest(data_dir: str | Path, *, write: bool = False) -> dict[str, Any]:
    root = Path(data_dir)
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.exists():
        return _blocked(f"missing ST-C3 dataset manifest: {manifest_path}")
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        return _blocked("dataset manifest must be a mapping")
    try:
        files = _normalize_files(manifest.get("files"))
        coverage = manifest.get("coverage") or {}
        file_updates = _validate_and_hash_files(
            root,
            files,
            date_from=str(coverage.get("from", "")),
            date_to=str(coverage.get("to", "")),
        )
    except (FileNotFoundError, ValueError) as exc:
        return _blocked(str(exc))
    if write:
        manifest["files"] = {
            item["path"]: {"sha256": item["sha256"]}
            for item in file_updates
        }
        manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return {
        "status": "PASS",
        "manifest": str(manifest_path),
        "write": write,
        "files": file_updates,
        "guardrail": "Replay run does not open A3 or imply acceptance.",
    }


def _validate_and_hash_files(
    root: Path,
    files: list[Mapping[str, Any]],
    *,
    date_from: str,
    date_to: str,
) -> list[dict[str, str]]:
    by_key = {(item.get("symbol"), item.get("timeframe")): item for item in files}
    updates: list[dict[str, str]] = []
    for symbol in sorted(EXPECTED_SYMBOLS):
        for timeframe in sorted(EXPECTED_TIMEFRAMES):
            entry = by_key.get((symbol, timeframe))
            if entry is None:
                raise ValueError(f"manifest missing file entry for {symbol} {timeframe}")
            path = root / str(entry["path"])
            if not path.exists():
                raise FileNotFoundError(f"dataset file missing: {path}")
            summary = _validate_csv(path, timeframe=timeframe)
            _validate_csv_covers_requested_range(
                path,
                summary,
                timeframe=timeframe,
                date_from=date_from,
                date_to=date_to,
            )
            updates.append(
                {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "path": str(entry["path"]),
                    "sha256": sha256_file(path),
                }
            )
    return updates


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "status": "BLOCKED",
        "reason": reason,
        "guardrail": "Replay run does not open A3 or imply acceptance.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/market/approved/st_c3"))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = prepare_dataset_manifest(args.data, write=args.write)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
