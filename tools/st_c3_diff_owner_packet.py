#!/usr/bin/env python3
"""Diff two ST-C3 owner decision packet JSON files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def diff_owner_packets(old_path: str | Path, new_path: str | Path) -> dict[str, Any]:
    old = json.loads(Path(old_path).read_text(encoding="utf-8"))
    new = json.loads(Path(new_path).read_text(encoding="utf-8"))
    keys = [
        "ledger_sha256",
        "recommendation",
        "stats_summary.status",
        "robustness_matrix.status",
        "walkforward_results.status",
    ]
    changes = []
    for key in keys:
        old_value = _get_dotted(old, key)
        new_value = _get_dotted(new, key)
        if old_value != new_value:
            changes.append({"field": key, "old": old_value, "new": new_value})
    return {
        "old": str(old_path),
        "new": str(new_path),
        "changed": bool(changes),
        "changes": changes,
        "guardrail": "Diff only. Does not accept gates, open A3, or authorize execution.",
    }


def _get_dotted(payload: dict[str, Any], key: str) -> Any:
    current: Any = payload
    for part in key.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    args = parser.parse_args()
    print(json.dumps(diff_owner_packets(args.old, args.new), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
