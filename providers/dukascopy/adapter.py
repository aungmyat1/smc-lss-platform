from __future__ import annotations

from pathlib import Path
from typing import Any

from providers.common.adapter import HealthCheck, ProviderMetadata


class DukascopyAdapter:
    name = "dukascopy"

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            provider="Dukascopy",
            symbols=("EURUSD", "GBPUSD"),
            timeframes=("tick", "M1", "M3", "M15", "H4"),
            timezone="UTC",
            license_status="research_use_requires_governance_review",
        )

    def health_check(self) -> HealthCheck:
        evidence = Path("reports/validation/st_c3/root_cause/ROOT_CAUSE_DECISION.json")
        ok = evidence.exists()
        return HealthCheck(
            provider="Dukascopy",
            ok=ok,
            status="AVAILABLE_REJECTED_EVIDENCE" if ok else "MISSING_LOCAL_EVIDENCE",
            reason="Completed ST-C3 evidence exists but decision is REJECT_DATASET." if ok else "Root-cause decision artifact missing.",
            evidence_path=str(evidence) if ok else None,
        )

    def download_sample(self, output_dir: str | Path, *, days: int = 100) -> dict[str, Any]:
        return {"status": "SKIPPED", "reason": "Existing deterministic 100-day rejected evidence is reused immutably."}

    def download_range(self, output_dir: str | Path, start: str, end: str) -> dict[str, Any]:
        return {"status": "BLOCKED", "reason": "Dukascopy is rejected for ST-C3 canonical use."}

    def normalize(self, input_dir: str | Path, output_dir: str | Path) -> dict[str, Any]:
        return {"status": "SKIPPED", "reason": "Rejected evidence is not normalized into a new canonical candidate."}

    def validate(self, normalized_dir: str | Path) -> dict[str, Any]:
        return {
            "status": "FAIL",
            "st_c3_status": "FAIL",
            "missing_minute_rate": 0.004301970580072162,
            "duplicate_rate": 0.0,
            "reproducible_acquisition": True,
            "stable_normalization": False,
            "integrity_score": 35.0,
            "automation_score": 90.0,
            "reason": "Rejected by completed ST-C3 root-cause analysis.",
        }
