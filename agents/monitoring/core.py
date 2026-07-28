from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class EvidenceBuilderAgent:
    def write(self, payload: dict[str, Any], out_path: Path) -> str:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        return str(out_path)


class JournalEngineAgent:
    def summarize(self, stage: str, result: dict[str, Any]) -> dict[str, Any]:
        return {
            "stage": stage,
            "status": result.get("status", "unknown"),
            "summary": result.get("summary", ""),
        }


class ReconciliationEngineAgent:
    def sync(self) -> dict[str, str]:
        return {
            "status": "not_run",
            "reason": "Reconciliation is only meaningful once execution or demo events exist.",
        }
