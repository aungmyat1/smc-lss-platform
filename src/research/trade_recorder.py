"""Trade recording helpers for research artifacts."""
from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable


def trade_rows(result: Any, experiment_id: str | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for trade in getattr(result, "trades", []):
        row = asdict(trade)
        row["experiment_id"] = experiment_id
        row["strategy_id"] = getattr(result, "symbol", None)
        row["strategy_version"] = result.assumptions.get("strategy_version") if hasattr(result, "assumptions") else None
        rows.append(row)
    return rows


def event_rows(result: Any, experiment_id: str | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for event in getattr(result, "management_events", []):
        rows.append({"experiment_id": experiment_id, **dict(event)})
    return rows


def candidate_rows(result: Any, experiment_id: str | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in getattr(result, "rejected_candidates", []):
        row = asdict(item) if hasattr(item, "__dataclass_fields__") else dict(item)
        row["experiment_id"] = experiment_id
        rows.append(row)
    return rows


def write_csv(path: str | Path, rows: Iterable[dict[str, Any]]) -> str:
    rows = list(rows)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = sorted({key for row in rows for key in row.keys()}) if rows else []
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return str(target)

