from __future__ import annotations

from typing import Any


def quality_score(metrics: dict[str, Any]) -> float:
    missing_rate = float(metrics.get("missing_minute_rate") or 1.0)
    duplicate_rate = float(metrics.get("duplicate_rate") or 0.0)
    continuity = max(0.0, 100.0 * (1.0 - missing_rate))
    duplicate_score = max(0.0, 100.0 * (1.0 - duplicate_rate))
    integrity = float(metrics.get("integrity_score", continuity))
    automation = float(metrics.get("automation_score", 0.0))
    return round((integrity * 0.45) + (continuity * 0.30) + (duplicate_score * 0.10) + (automation * 0.15), 2)


def provider_passes_st_c3(metrics: dict[str, Any], *, threshold: float = 0.001) -> bool:
    return (
        metrics.get("st_c3_status") == "PASS"
        and metrics.get("reproducible_acquisition") is True
        and metrics.get("stable_normalization") is True
        and float(metrics.get("missing_minute_rate") or 1.0) < threshold
    )
