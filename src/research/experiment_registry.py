"""Hypothesis registry loader/saver."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_registry(path: str | Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "hypotheses" in data and isinstance(data["hypotheses"], list):
        return data["hypotheses"]
    raise ValueError(f"{path}: expected a list or a mapping with 'hypotheses'")


def write_registry(path: str | Path, hypotheses: list[dict[str, Any]]) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump({"hypotheses": hypotheses, "version": 1}, sort_keys=False), encoding="utf-8")
    return str(target)

