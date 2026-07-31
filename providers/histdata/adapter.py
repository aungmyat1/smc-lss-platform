from __future__ import annotations

from pathlib import Path
from typing import Any

from providers.common.adapter import HealthCheck, ProviderMetadata


class HistDataAdapter:
    name = "histdata"

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            provider="HistData",
            symbols=("EURUSD", "GBPUSD"),
            timeframes=("M1",),
            timezone="EST_NO_DST",
            license_status="free_download_terms_require_review",
        )

    def health_check(self) -> HealthCheck:
        evidence = Path("DATA_APPROVAL_ST_C3.md")
        return HealthCheck(
            provider="HistData",
            ok=evidence.exists(),
            status="AVAILABLE_REJECTED_EVIDENCE" if evidence.exists() else "MISSING_LOCAL_EVIDENCE",
            reason="Prior candidate failed integrity with missing timestamps." if evidence.exists() else "Dataset approval record missing.",
            evidence_path=str(evidence) if evidence.exists() else None,
        )

    def download_sample(self, output_dir: str | Path, *, days: int = 100) -> dict[str, Any]:
        return {"status": "SKIPPED", "reason": "Existing rejected candidate/reference evidence is reused."}

    def download_range(self, output_dir: str | Path, start: str, end: str) -> dict[str, Any]:
        return {"status": "BLOCKED", "reason": "Prior HistData candidate failed integrity."}

    def normalize(self, input_dir: str | Path, output_dir: str | Path) -> dict[str, Any]:
        return {"status": "SKIPPED", "reason": "Rejected candidate is not normalized into vNext."}

    def validate(self, normalized_dir: str | Path) -> dict[str, Any]:
        return {
            "status": "FAIL",
            "st_c3_status": "FAIL",
            "missing_minute_rate": None,
            "duplicate_rate": None,
            "reproducible_acquisition": True,
            "stable_normalization": False,
            "integrity_score": 30.0,
            "automation_score": 45.0,
            "reason": "Prior candidate failed unchanged integrity validation.",
        }
