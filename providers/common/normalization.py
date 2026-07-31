from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Any

from .adapter import NormalizedBar


def canonical_session(timestamp: str) -> str:
    value = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    minutes = value.hour * 60 + value.minute
    if 7 * 60 <= minutes < 10 * 60:
        return "LONDON"
    if 13 * 60 <= minutes < 16 * 60:
        return "NY"
    return "OTHER"


def normalize_rows(rows: Iterable[dict[str, Any]], *, provider: str, timezone: str = "UTC") -> list[NormalizedBar]:
    normalized: list[NormalizedBar] = []
    for row in rows:
        timestamp = str(row["timestamp"])
        normalized.append(
            NormalizedBar(
                timestamp=timestamp,
                symbol=str(row["symbol"]),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                tick_volume=float(row.get("tick_volume", row.get("volume", 0))),
                spread=None if row.get("spread") in {None, ""} else float(row["spread"]),
                provider=provider,
                timezone=timezone,
                session=str(row.get("session") or canonical_session(timestamp)),
            )
        )
    return normalized


def validate_normalized_rows(rows: list[NormalizedBar]) -> dict[str, Any]:
    duplicates = 0
    ordering_errors = 0
    seen: set[tuple[str, str]] = set()
    previous: tuple[str, str] | None = None
    for row in rows:
        key = (row.symbol, row.timestamp)
        if key in seen:
            duplicates += 1
        seen.add(key)
        if previous and row.symbol == previous[0] and row.timestamp < previous[1]:
            ordering_errors += 1
        previous = key
    return {
        "rows": len(rows),
        "duplicates": duplicates,
        "ordering_errors": ordering_errors,
        "schema_version": "st-c4.1-normalized-v1",
        "status": "PASS" if duplicates == 0 and ordering_errors == 0 else "FAIL",
    }
