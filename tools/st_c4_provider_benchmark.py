#!/usr/bin/env python3
"""Build ST-C4 provider benchmark artifacts.

This sprint prepares provider evidence for a future ST-C3 run. It does not
approve any dataset, unlock replay, or modify ST-C3 validation thresholds.
"""
from __future__ import annotations

import argparse
import csv
import json
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

REPORT_DIR = Path("reports/st_c4")
DOC_PATH = Path("docs/data/CANONICAL_DATA_SPECIFICATION.md")
RESEARCH_ROOT = Path("research_data")
QUALITY_JSON = REPORT_DIR / "provider_quality_statistics.json"
BENCHMARK_CSV = REPORT_DIR / "provider_benchmark.csv"
BENCHMARK_XLSX_REQUIRED = REPORT_DIR / "provider_benchmark.xlsx"
BENCHMARK_XLSX = REPORT_DIR / "provider_benchmark_matrix.xlsx"
BENCHMARK_MD = REPORT_DIR / "provider_benchmark.md"
BUILD_REPORT = REPORT_DIR / "DATASET_BUILD_REPORT.md"
READINESS_REPORT = REPORT_DIR / "ST_C3_READINESS_REPORT.md"
SELECTION_REPORT = REPORT_DIR / "CANONICAL_PROVIDER_SELECTION.md"
GUARDRAIL = "ST-C4 benchmark only; rejected ST-C3 data remains immutable and replay remains blocked."
ACCEPTANCE_SCORE = 80.0
ACCEPTANCE_MISSING_RATE = 0.001


WEIGHTS = {
    "historical_completeness": 0.30,
    "continuity": 0.25,
    "timestamp_accuracy": 0.20,
    "automation": 0.10,
    "documentation": 0.05,
    "cost": 0.05,
    "licensing": 0.05,
}


@dataclass(frozen=True)
class ProviderCandidate:
    provider: str
    status: str
    historical_coverage: str
    timestamp_precision: str
    timezone_policy: str
    sample_status: str
    missing_rate: float | None
    duplicate_rate: float | None
    longest_gap_minutes: int | None
    unexpected_gap_pct: float | None
    historical_completeness: float
    continuity: float
    timestamp_accuracy: float
    automation: float
    documentation: float
    cost: float
    licensing: float
    evidence: str
    blocker: str
    source_url: str


def run_st_c4_benchmark(output_dir: str | Path = REPORT_DIR) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    _ensure_research_layout()
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(_canonical_spec(), encoding="utf-8")
    providers = _provider_candidates()
    rows = [_provider_row(provider) for provider in providers]
    _write_csv(output / "provider_benchmark.csv", rows)
    _write_xlsx(output / "provider_benchmark_matrix.xlsx", rows)
    _write_xlsx(output / "provider_benchmark.xlsx", rows)
    _write_markdown(output / "provider_benchmark.md", _benchmark_markdown(providers))
    quality = _quality_statistics(providers)
    (output / "provider_quality_statistics.json").write_text(json.dumps(quality, indent=2, sort_keys=True), encoding="utf-8")
    selection = _selection(quality)
    (output / "CANONICAL_PROVIDER_SELECTION.md").write_text(_selection_markdown(selection, quality), encoding="utf-8")
    (output / "DATASET_BUILD_REPORT.md").write_text(_dataset_build_report(selection), encoding="utf-8")
    (output / "ST_C3_READINESS_REPORT.md").write_text(_readiness_report(selection, quality), encoding="utf-8")
    (RESEARCH_ROOT / "metadata" / "ST_C4_SAMPLE_INDEX.json").write_text(json.dumps(_sample_index(), indent=2, sort_keys=True), encoding="utf-8")
    return {
        "stage": "st_c4_provider_benchmark",
        "status": "COMPLETE",
        "guardrail": GUARDRAIL,
        "candidate_count": len(providers),
        "selection": selection,
        "recommendation": selection["st_c3_readiness"],
    }


def quality_score(candidate: ProviderCandidate) -> float:
    return round(
        candidate.historical_completeness * WEIGHTS["historical_completeness"]
        + candidate.continuity * WEIGHTS["continuity"]
        + candidate.timestamp_accuracy * WEIGHTS["timestamp_accuracy"]
        + candidate.automation * WEIGHTS["automation"]
        + candidate.documentation * WEIGHTS["documentation"]
        + candidate.cost * WEIGHTS["cost"]
        + candidate.licensing * WEIGHTS["licensing"],
        2,
    )


def readiness_decision(provider_rows: list[dict[str, Any]]) -> str:
    eligible = [
        row
        for row in provider_rows
        if row["sample_status"] == "VALIDATED_SAMPLE_PASS"
        and row["missing_rate"] is not None
        and row["missing_rate"] < ACCEPTANCE_MISSING_RATE
        and row["quality_score"] >= ACCEPTANCE_SCORE
    ]
    return "READY_FOR_ST_C3" if eligible else "NOT_READY_FOR_ST_C3"


def _provider_candidates() -> list[ProviderCandidate]:
    return [
        ProviderCandidate(
            provider="Dukascopy",
            status="REJECTED_ST_C3_EVIDENCE",
            historical_coverage="Tick/bar export available; repository 100-day ST-C3 sample complete",
            timestamp_precision="tick millisecond source; normalized to minute bars",
            timezone_policy="UTC source handling with DST Friday-close mismatch evidence",
            sample_status="VALIDATED_SAMPLE_FAIL",
            missing_rate=0.004301970580072162,
            duplicate_rate=0.0,
            longest_gap_minutes=None,
            unexpected_gap_pct=630 / 1240,
            historical_completeness=95,
            continuity=35,
            timestamp_accuracy=70,
            automation=90,
            documentation=75,
            cost=95,
            licensing=60,
            evidence="Completed ST-C3 100-day evidence sample; root cause decision REJECT_DATASET",
            blocker="Effective missing rate exceeds ST-C3 threshold and unknown gaps remain",
            source_url="https://www.dukascopy.com/swiss/english/marketwatch/historical/",
        ),
        ProviderCandidate(
            provider="HistData",
            status="REJECTED_PRIOR_CANDIDATE",
            historical_coverage="Free M1 ASCII files available; repository candidate failed integrity",
            timestamp_precision="M1 bars",
            timezone_policy="EST without daylight-saving adjustments",
            sample_status="VALIDATED_SAMPLE_FAIL",
            missing_rate=None,
            duplicate_rate=None,
            longest_gap_minutes=None,
            unexpected_gap_pct=None,
            historical_completeness=70,
            continuity=30,
            timestamp_accuracy=35,
            automation=45,
            documentation=65,
            cost=95,
            licensing=50,
            evidence="Repository DATA_APPROVAL_ST_C3 records missing timestamps in every required file",
            blocker="Timezone policy and prior integrity failure",
            source_url="https://www.histdata.com/f-a-q/",
        ),
        ProviderCandidate(
            provider="TrueFX",
            status="CANDIDATE_REQUIRES_ACCOUNT_OR_COMMERCIAL_ACCESS",
            historical_coverage="Historical tick-by-tick market data advertised",
            timestamp_precision="millisecond tick detail advertised",
            timezone_policy="provider documentation review required after account access",
            sample_status="NOT_ACQUIRED_ACCESS_REQUIRED",
            missing_rate=None,
            duplicate_rate=None,
            longest_gap_minutes=None,
            unexpected_gap_pct=None,
            historical_completeness=85,
            continuity=65,
            timestamp_accuracy=80,
            automation=60,
            documentation=70,
            cost=35,
            licensing=45,
            evidence="Public download/terms pages verified; no repository credentials/session",
            blocker="Account/commercial access and licensing acceptance required before sampling",
            source_url="https://www.truefx.com/truefx-historical-downloads-2/",
        ),
        ProviderCandidate(
            provider="Darwinex",
            status="CANDIDATE_REQUIRES_LIVE_ACCOUNT_FTP",
            historical_coverage="Tick-level data from October 2017 onward advertised for clients",
            timestamp_precision="tick precision",
            timezone_policy="provider documentation review required after FTP access",
            sample_status="NOT_ACQUIRED_ACCESS_REQUIRED",
            missing_rate=None,
            duplicate_rate=None,
            longest_gap_minutes=None,
            unexpected_gap_pct=None,
            historical_completeness=75,
            continuity=65,
            timestamp_accuracy=75,
            automation=55,
            documentation=65,
            cost=55,
            licensing=55,
            evidence="Public Darwinex tick-data page verified; no FTP credentials",
            blocker="Live account/FTP access required before sampling",
            source_url="https://www.darwinex.com/tick-data",
        ),
        ProviderCandidate(
            provider="Tiingo FX",
            status="CANDIDATE_REQUIRES_API_TOKEN",
            historical_coverage="Forex API historical intraday data from 2020; 140+ pairs advertised",
            timestamp_precision="microsecond/latest quotes; OHLC intraday bars",
            timezone_policy="market hours documented as 8pm EST Sunday through 5pm EST Friday",
            sample_status="NOT_ACQUIRED_ACCESS_REQUIRED",
            missing_rate=None,
            duplicate_rate=None,
            longest_gap_minutes=None,
            unexpected_gap_pct=None,
            historical_completeness=65,
            continuity=70,
            timestamp_accuracy=70,
            automation=85,
            documentation=80,
            cost=70,
            licensing=65,
            evidence="Public API docs/product page verified; no API token configured",
            blocker="Coverage begins 2020, so 2021-2025 is plausible but must be sampled",
            source_url="https://www.tiingo.com/documentation/forex",
        ),
        ProviderCandidate(
            provider="Polygon/Massive Forex",
            status="CANDIDATE_REQUIRES_API_SUBSCRIPTION",
            historical_coverage="Historical forex aggregates available via REST",
            timestamp_precision="minute-plus aggregates; empty intervals may be omitted when no quotes occur",
            timezone_policy="Eastern Time aggregates documented",
            sample_status="NOT_ACQUIRED_ACCESS_REQUIRED",
            missing_rate=None,
            duplicate_rate=None,
            longest_gap_minutes=None,
            unexpected_gap_pct=None,
            historical_completeness=60,
            continuity=45,
            timestamp_accuracy=55,
            automation=85,
            documentation=80,
            cost=45,
            licensing=55,
            evidence="Public REST documentation verified; no subscription/API key configured",
            blocker="Documented empty intervals conflict with ST-C3 continuous-minute tolerance until sampled",
            source_url="https://massive.com/docs/rest/forex/overview",
        ),
        ProviderCandidate(
            provider="Broker MT5 Export",
            status="CANDIDATE_REQUIRES_TERMINAL_HISTORY",
            historical_coverage="Broker-dependent",
            timestamp_precision="bar timestamps from terminal",
            timezone_policy="broker-server timezone must be proven and normalized",
            sample_status="NOT_ACQUIRED_LOCAL_TERMINAL_REQUIRED",
            missing_rate=None,
            duplicate_rate=None,
            longest_gap_minutes=None,
            unexpected_gap_pct=None,
            historical_completeness=45,
            continuity=40,
            timestamp_accuracy=45,
            automation=45,
            documentation=30,
            cost=80,
            licensing=40,
            evidence="Repository MT5 acquisition tool exists; no complete validated export",
            blocker="Local terminal history is broker-specific and not independently reproducible yet",
            source_url="local-broker-export",
        ),
    ]


def _provider_row(candidate: ProviderCandidate) -> dict[str, Any]:
    return {
        "provider": candidate.provider,
        "status": candidate.status,
        "historical_coverage": candidate.historical_coverage,
        "timestamp_precision": candidate.timestamp_precision,
        "timezone_policy": candidate.timezone_policy,
        "sample_status": candidate.sample_status,
        "missing_rate": candidate.missing_rate,
        "duplicate_rate": candidate.duplicate_rate,
        "longest_gap_minutes": candidate.longest_gap_minutes,
        "unexpected_gap_pct": candidate.unexpected_gap_pct,
        "historical_completeness_score": candidate.historical_completeness,
        "continuity_score": candidate.continuity,
        "timestamp_accuracy_score": candidate.timestamp_accuracy,
        "automation_score": candidate.automation,
        "documentation_score": candidate.documentation,
        "cost_score": candidate.cost,
        "licensing_score": candidate.licensing,
        "quality_score": quality_score(candidate),
        "evidence": candidate.evidence,
        "blocker": candidate.blocker,
        "source_url": candidate.source_url,
    }


def _quality_statistics(providers: list[ProviderCandidate]) -> dict[str, Any]:
    rows = [_provider_row(provider) for provider in providers]
    ranked = sorted(rows, key=lambda row: row["quality_score"], reverse=True)
    return {
        "generated_at_utc": datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "guardrail": GUARDRAIL,
        "acceptance": {
            "minimum_quality_score": ACCEPTANCE_SCORE,
            "maximum_missing_rate": ACCEPTANCE_MISSING_RATE,
            "requires_validated_sample": True,
        },
        "weights": WEIGHTS,
        "providers": rows,
        "ranking": [{"provider": row["provider"], "quality_score": row["quality_score"], "sample_status": row["sample_status"]} for row in ranked],
        "readiness": readiness_decision(rows),
    }


def _selection(quality: dict[str, Any]) -> dict[str, Any]:
    ranked = quality["ranking"]
    return {
        "preferred_provider": "NONE",
        "fallback_provider": "Tiingo FX paid/API pilot, contingent on token, licensing approval, and 100-day sample pass",
        "st_c3_readiness": quality["readiness"],
        "reason": "No candidate has both a passing validated 100-day sample and quality score above acceptance threshold.",
        "top_scored_provider": ranked[0]["provider"] if ranked else None,
        "top_score": ranked[0]["quality_score"] if ranked else None,
    }


def _ensure_research_layout() -> None:
    for path in [
        RESEARCH_ROOT / "raw" / "dukascopy",
        RESEARCH_ROOT / "raw" / "histdata",
        RESEARCH_ROOT / "raw" / "truefx",
        RESEARCH_ROOT / "raw" / "darwinex",
        RESEARCH_ROOT / "raw" / "tiingo",
        RESEARCH_ROOT / "raw" / "polygon",
        RESEARCH_ROOT / "raw" / "mt5",
        RESEARCH_ROOT / "normalized",
        RESEARCH_ROOT / "canonical",
        RESEARCH_ROOT / "metadata",
    ]:
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")


def _sample_index() -> dict[str, Any]:
    return {
        "guardrail": GUARDRAIL,
        "samples": [
            {
                "provider": "Dukascopy",
                "status": "available_existing_rejected_evidence",
                "path": "data/market/raw/dukascopy/st_c3",
                "notes": "100 deterministic ST-C3 sample days cached; rejected by root-cause analysis.",
            },
            {
                "provider": "HistData",
                "status": "available_existing_reference_cache",
                "path": "data/market/raw/histdata/st_c3",
                "notes": "Reference cache exists but prior canonical candidate failed integrity.",
            },
        ],
    }


def _canonical_spec() -> str:
    return """# ST-C4 Canonical Data Specification

## Scope

- Strategy family: ST-C3/ST-C4 validation data only.
- Symbols: EURUSD and GBPUSD.
- Required timeframes: M3, M15, H4, derived from a single provider.
- Historical depth: 2021-01-01 through 2025-12-31 minimum for ST-C3 replay readiness.
- Timestamp precision: source precision preserved; canonical bars use UTC minute timestamps.
- Timezone policy: all normalized data must be UTC. Source timezone conversions must be documented and reproducible.
- DST handling: provider session shifts must be explicitly encoded in metadata and validated against source documentation.
- Weekend handling: no fabricated weekend bars; market-open expectations must follow documented FX trading week.
- Holiday handling: New Year, Christmas, Good Friday/Easter, broker holidays, and provider-specific closures must be classified.
- Corporate action policy: not applicable to spot FX EURUSD/GBPUSD.
- Missing-data tolerance: effective unexplained missing-minute rate must be below 0.001 and unknown gaps must be zero before ST-C3 readiness.
- Storage format: immutable raw source files, normalized CSV/parquet-compatible schema, processed timeframe bars, metadata, and checksums.

## Canonical Schema

`timestamp,symbol,open,high,low,close,volume,spread,provider,timezone,session`

## Governance

The rejected ST-C3 Dukascopy dataset remains archived and immutable. No replay,
statistical validation, demo, or live trading stage may be unlocked by ST-C4
benchmark artifacts alone.
"""


def _benchmark_markdown(providers: list[ProviderCandidate]) -> str:
    lines = [
        "# ST-C4 Provider Benchmark",
        "",
        f"Guardrail: {GUARDRAIL}",
        "",
        "## Sources",
        "",
        "- Dukascopy historical export: https://www.dukascopy.com/swiss/english/marketwatch/historical/",
        "- TrueFX downloads/terms: https://www.truefx.com/truefx-historical-downloads-2/ and https://www.truefx.com/truefx-terms-and-conditions/",
        "- HistData FAQ/specification: https://www.histdata.com/f-a-q/ and https://www.histdata.com/f-a-q/data-files-detailed-specification/",
        "- Darwinex tick data: https://www.darwinex.com/tick-data",
        "- Tiingo Forex API: https://www.tiingo.com/documentation/forex",
        "- Polygon/Massive Forex REST API: https://massive.com/docs/rest/forex/overview",
        "",
        "## Matrix",
        "",
        "| Provider | Status | Sample | Missing Rate | Quality Score | Blocker |",
        "|---|---|---|---:|---:|---|",
    ]
    for provider in providers:
        lines.append(
            f"| {provider.provider} | {provider.status} | {provider.sample_status} | "
            f"{provider.missing_rate if provider.missing_rate is not None else 'n/a'} | {quality_score(provider)} | {provider.blocker} |"
        )
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "No provider is selected as canonical in this sprint because no candidate has a passing validated 100-day sample under ST-C3 governance.",
            "",
        ]
    )
    return "\n".join(lines)


def _selection_markdown(selection: dict[str, Any], quality: dict[str, Any]) -> str:
    return f"""# ST-C4 Canonical Provider Selection

Preferred Provider: **{selection['preferred_provider']}**

Fallback Provider: **{selection['fallback_provider']}**

Recommendation: **{selection['st_c3_readiness']}**

Reason: {selection['reason']}

Top scored provider before validated-sample gate: `{selection['top_scored_provider']}` with score `{selection['top_score']}`.

No canonical dataset is approved or ready for ST-C3 execution by this report.
"""


def _dataset_build_report(selection: dict[str, Any]) -> str:
    return f"""# ST-C4 Dataset Build Report

Status: **NOT_BUILT**

Reason: {selection['reason']}

No Research Dataset vNext was built because no provider satisfied the validated
sample gate. Existing rejected ST-C3 evidence remains immutable. The
`research_data/` layout has been prepared for future raw, normalized,
canonical, and metadata artifacts.
"""


def _readiness_report(selection: dict[str, Any], quality: dict[str, Any]) -> str:
    return f"""# ST-C4 ST-C3 Readiness Report

Recommendation: **{selection['st_c3_readiness']}**

Provider selected: **{selection['preferred_provider']}**

Dataset version: **not assigned**

Coverage: not built.

Expected missing rate: not computable for a new provider because no new
provider sample passed acquisition and validation.

Known limitations:

- Dukascopy is rejected by completed ST-C3 evidence.
- HistData prior candidate failed integrity.
- TrueFX, Darwinex, Tiingo, Polygon/Massive, and MT5 require account/API/local
  access before representative samples can be validated.

Risk assessment: entering ST-C3 now would repeat the data-gate failure or rely
on unvalidated provider assumptions.
"""


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_markdown(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _write_xlsx(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = list(rows[0].keys())
    data = [fields] + [[row[field] for field in fields] for row in rows]
    sheet_rows = []
    for r_idx, row in enumerate(data, start=1):
        cells = []
        for c_idx, value in enumerate(row, start=1):
            ref = f"{_col(c_idx)}{r_idx}"
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape("" if value is None else str(value))}</t></is></c>')
        sheet_rows.append(f'<row r="{r_idx}">{"".join(cells)}</row>')
    sheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(sheet_rows)}</sheetData></worksheet>'
    )
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types())
        archive.writestr("_rels/.rels", _rels())
        archive.writestr("xl/workbook.xml", _workbook())
        archive.writestr("xl/_rels/workbook.xml.rels", _workbook_rels())
        archive.writestr("xl/worksheets/sheet1.xml", sheet)


def _col(index: int) -> str:
    letters = ""
    while index:
        index, rem = divmod(index - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def _content_types() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>"""


def _rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>"""


def _workbook() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="provider_benchmark" sheetId="1" r:id="rId1"/></sheets>
</workbook>"""


def _workbook_rels() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args()
    result = run_st_c4_benchmark(args.output_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["recommendation"] == "READY_FOR_ST_C3" else 1)


if __name__ == "__main__":
    main()
