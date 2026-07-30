#!/usr/bin/env python3
"""Investigate exact sparse ST-C3 source minutes without changing dataset gates."""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

from tools.st_c3_acquire_dukascopy_dataset import RAW_CACHE, _cache_path, _dukascopy_url, _format_time
from tools.st_c3_verify_dukascopy_provider import Tick, _parse_bi5_ticks

HISTDATA_CACHE = Path("data/market/raw/histdata/st_c3")
REPORT = Path("reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_INVESTIGATION.json")
MARKDOWN_REPORT = Path("reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_INVESTIGATION.md")
GUARDRAIL = "Source integrity investigation does not approve data, fill candles, open replay, or change validation rules."


@dataclass(frozen=True)
class Probe:
    symbol: str
    timestamp: datetime


DEFAULT_PROBES = (
    Probe("EURUSD", datetime(2021, 1, 4, 22, 45, tzinfo=UTC)),
    Probe("EURUSD", datetime(2021, 1, 4, 22, 46, tzinfo=UTC)),
    Probe("GBPUSD", datetime(2021, 1, 4, 22, 19, tzinfo=UTC)),
)


def investigate_source_integrity(
    *,
    probes: Iterable[Probe] = DEFAULT_PROBES,
    dukascopy_cache: str | Path = RAW_CACHE,
    histdata_cache: str | Path = HISTDATA_CACHE,
    fresh_download: bool = True,
    write_report: bool = True,
) -> dict[str, Any]:
    rows = [
        _investigate_probe(
            probe,
            dukascopy_cache=Path(dukascopy_cache),
            histdata_cache=Path(histdata_cache),
            fresh_download=fresh_download,
        )
        for probe in probes
    ]
    parser_ok = all(item["dukascopy_cached"]["parse_status"] == "PASS" for item in rows)
    fresh_ok = all(
        item["dukascopy_fresh"]["status"] in {"MATCHED_CACHE", "SKIPPED"}
        for item in rows
    )
    histdata_has_reference = any(item["histdata_reference"]["present"] for item in rows)
    all_cached_missing = all(not item["dukascopy_cached"]["minute_present"] for item in rows)
    status = "BLOCKED"
    reason = _reason(rows, parser_ok=parser_ok, fresh_ok=fresh_ok, histdata_has_reference=histdata_has_reference, all_cached_missing=all_cached_missing)
    result = {
        "stage": "source_integrity_investigation",
        "status": status,
        "reason": reason,
        "next_action": _next_action(histdata_has_reference=histdata_has_reference, all_cached_missing=all_cached_missing, fresh_ok=fresh_ok),
        "details": {
            "probes": rows,
            "parser_audit": "PASS" if parser_ok else "BLOCKED",
            "fresh_download_audit": "PASS" if fresh_ok else "BLOCKED",
            "cross_source_reference": "PRESENT" if histdata_has_reference else "ABSENT",
            "policy_question": "Does the ST-C3 Dataset Contract require candles for zero-tick market-open minutes, or only minutes with at least one source tick?",
        },
        "guardrail": GUARDRAIL,
        "recommendation": "INVESTIGATE_SOURCE_INTEGRITY",
    }
    if write_report:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        MARKDOWN_REPORT.write_text(_markdown(result), encoding="utf-8")
    return result


def _investigate_probe(probe: Probe, *, dukascopy_cache: Path, histdata_cache: Path, fresh_download: bool) -> dict[str, Any]:
    hour = probe.timestamp.replace(minute=0, second=0, microsecond=0)
    cached = _inspect_dukascopy_payload(probe, _cache_path(dukascopy_cache, probe.symbol, hour))
    fresh = _fresh_dukascopy_audit(probe, cached, fresh_download=fresh_download)
    histdata = _histdata_reference(probe, histdata_cache)
    return {
        "symbol": probe.symbol,
        "timestamp_utc": _format_time(probe.timestamp.replace(tzinfo=None)),
        "dukascopy_cached": cached,
        "dukascopy_fresh": fresh,
        "histdata_reference": histdata,
        "verdict": _probe_verdict(cached, fresh, histdata),
    }


def _inspect_dukascopy_payload(probe: Probe, path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {
            "path": str(path),
            "exists": path.exists(),
            "bytes": path.stat().st_size if path.exists() else 0,
            "sha256": None,
            "parse_status": "MISSING_FILE",
            "hour_tick_count": 0,
            "hour_minute_count": 0,
            "minute_present": False,
            "minute_tick_count": 0,
            "neighbor_tick_counts": {},
            "first_tick_after_missing_minute": None,
            "last_tick_before_missing_minute": None,
        }
    payload = path.read_bytes()
    try:
        ticks = _parse_bi5_ticks(payload, probe.timestamp.replace(minute=0, second=0, microsecond=0), probe.symbol)
    except Exception as exc:  # noqa: BLE001 - report exact parser failure.
        return {
            "path": str(path),
            "exists": True,
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "parse_status": f"BLOCKED: {type(exc).__name__}: {exc}",
            "hour_tick_count": 0,
            "hour_minute_count": 0,
            "minute_present": False,
            "minute_tick_count": 0,
            "neighbor_tick_counts": {},
            "first_tick_after_missing_minute": None,
            "last_tick_before_missing_minute": None,
        }
    target_minute = probe.timestamp.replace(second=0, microsecond=0)
    by_minute = _ticks_by_minute(ticks)
    before = [tick for tick in ticks if tick.timestamp < target_minute]
    after = [tick for tick in ticks if tick.timestamp >= target_minute + timedelta(minutes=1)]
    return {
        "path": str(path),
        "exists": True,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "parse_status": "PASS",
        "hour_tick_count": len(ticks),
        "hour_minute_count": len(by_minute),
        "minute_present": target_minute in by_minute,
        "minute_tick_count": len(by_minute.get(target_minute, [])),
        "neighbor_tick_counts": {
            _format_time((target_minute + timedelta(minutes=offset)).replace(tzinfo=None)): len(by_minute.get(target_minute + timedelta(minutes=offset), []))
            for offset in (-2, -1, 0, 1, 2)
        },
        "first_tick_after_missing_minute": _tick_payload(after[0]) if after else None,
        "last_tick_before_missing_minute": _tick_payload(before[-1]) if before else None,
    }


def _fresh_dukascopy_audit(probe: Probe, cached: dict[str, Any], *, fresh_download: bool) -> dict[str, Any]:
    if not fresh_download:
        return {"status": "SKIPPED", "reason": "fresh download disabled"}
    hour = probe.timestamp.replace(minute=0, second=0, microsecond=0)
    url = _dukascopy_url(probe.symbol, hour)
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "smc-lss-platform source integrity investigation"})
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = response.read()
    except Exception as exc:  # noqa: BLE001 - report exact download failure.
        return {"status": "BLOCKED", "url": url, "reason": f"{type(exc).__name__}: {exc}"}
    digest = hashlib.sha256(payload).hexdigest()
    matched = cached.get("sha256") == digest
    return {
        "status": "MATCHED_CACHE" if matched else "DIFFERS_FROM_CACHE",
        "url": url,
        "bytes": len(payload),
        "sha256": digest,
        "cache_sha256": cached.get("sha256"),
    }


def _histdata_reference(probe: Probe, histdata_cache: Path) -> dict[str, Any]:
    path = histdata_cache / probe.symbol / f"DAT_ASCII_{probe.symbol}_M1_{probe.timestamp.year}.zip"
    if not path.exists():
        return {"provider": "HistData.com Generic ASCII M1", "path": str(path), "present": False, "reason": "zip missing"}
    target = probe.timestamp.replace(tzinfo=None)
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not names:
            return {"provider": "HistData.com Generic ASCII M1", "path": str(path), "present": False, "reason": "csv missing from zip"}
        with archive.open(names[0]) as fh:
            for raw in fh:
                line = raw.decode("ascii", errors="strict").strip()
                if not line:
                    continue
                parts = line.split(";")
                timestamp = datetime.strptime(parts[0], "%Y%m%d %H%M%S") + timedelta(hours=5)
                if timestamp == target:
                    return {
                        "provider": "HistData.com Generic ASCII M1",
                        "path": str(path),
                        "present": True,
                        "timestamp_utc": _format_time(timestamp),
                        "open": float(parts[1]),
                        "high": float(parts[2]),
                        "low": float(parts[3]),
                        "close": float(parts[4]),
                        "volume": float(parts[5]) if len(parts) > 5 and parts[5] else 0.0,
                    }
                if timestamp > target + timedelta(minutes=5):
                    break
    return {"provider": "HistData.com Generic ASCII M1", "path": str(path), "present": False, "reason": "minute absent"}


def _ticks_by_minute(ticks: list[Tick]) -> dict[datetime, list[Tick]]:
    by_minute: dict[datetime, list[Tick]] = {}
    for tick in ticks:
        by_minute.setdefault(tick.timestamp.replace(second=0, microsecond=0), []).append(tick)
    return by_minute


def _tick_payload(tick: Tick) -> dict[str, Any]:
    return {
        "timestamp_utc": tick.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "bid": tick.bid,
        "ask": tick.ask,
        "bid_volume": tick.bid_volume,
        "ask_volume": tick.ask_volume,
    }


def _probe_verdict(cached: dict[str, Any], fresh: dict[str, Any], histdata: dict[str, Any]) -> str:
    if cached["parse_status"] != "PASS":
        return "PARSER_OR_CACHE_BLOCKED"
    if fresh["status"] == "DIFFERS_FROM_CACHE":
        return "CACHE_DIFFERS_FROM_FRESH_DUKASCOPY"
    if cached["minute_present"]:
        return "DUKASCOPY_MINUTE_PRESENT"
    if histdata["present"]:
        return "REFERENCE_HAS_MINUTE_DUKASCOPY_SPARSE"
    return "DUKASCOPY_AND_REFERENCE_ABSENT"


def _reason(
    rows: list[dict[str, Any]],
    *,
    parser_ok: bool,
    fresh_ok: bool,
    histdata_has_reference: bool,
    all_cached_missing: bool,
) -> str:
    if not parser_ok:
        return "parser or cached Dukascopy payload failed for at least one probe"
    if not fresh_ok:
        return "fresh Dukascopy download differs from cached payload or failed"
    if all_cached_missing and histdata_has_reference:
        return "Dukascopy is sparse at probed minutes while independent HistData M1 contains bars"
    if all_cached_missing:
        return "Dukascopy is sparse at probed minutes and independent reference also lacks bars"
    return "source integrity investigation completed"


def _next_action(*, histdata_has_reference: bool, all_cached_missing: bool, fresh_ok: bool) -> str:
    if not fresh_ok:
        return "Retry source download audit and repair acquisition cache only if fresh Dukascopy differs from cached data."
    if all_cached_missing and histdata_has_reference:
        return "Open Dataset Contract Review; do not continue full acquisition until sparse-minute policy/provider suitability is decided."
    if all_cached_missing:
        return "Document legitimate sparse market minutes and open Dataset Contract Review before changing policy."
    return "Continue source integrity investigation for any remaining suspect minutes."


def _markdown(result: dict[str, Any]) -> str:
    lines = [
        "# ST-C3 Source Integrity Investigation",
        "",
        f"Status: **{result['status']}**",
        "",
        f"Reason: {result['reason']}",
        "",
        f"Recommendation: **{result['recommendation']}**",
        "",
        f"Guardrail: {result['guardrail']}",
        "",
        "## Probe Summary",
        "",
        "| Symbol | Timestamp | Cached Parse | Cached Minute | Fresh Dukascopy | HistData M1 | Verdict |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in result["details"]["probes"]:
        lines.append(
            f"| `{item['symbol']}` | `{item['timestamp_utc']}` | {item['dukascopy_cached']['parse_status']} | "
            f"{item['dukascopy_cached']['minute_present']} | {item['dukascopy_fresh']['status']} | "
            f"{item['histdata_reference']['present']} | {item['verdict']} |"
        )
    lines += [
        "",
        "## Policy Question",
        "",
        result["details"]["policy_question"],
        "",
        "No candles were fabricated, interpolated, or manually inserted.",
    ]
    return "\n".join(lines) + "\n"


def _parse_probe(value: str) -> Probe:
    symbol, timestamp = value.split("=", 1)
    return Probe(symbol.upper(), datetime.fromisoformat(timestamp.replace("Z", "+00:00")).astimezone(UTC))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", action="append", type=_parse_probe, help="Probe as SYMBOL=YYYY-MM-DDTHH:MM:SSZ")
    parser.add_argument("--dukascopy-cache", type=Path, default=RAW_CACHE)
    parser.add_argument("--histdata-cache", type=Path, default=HISTDATA_CACHE)
    parser.add_argument("--no-fresh-download", action="store_true")
    parser.add_argument("--no-report", action="store_true")
    args = parser.parse_args()
    result = investigate_source_integrity(
        probes=args.probe or DEFAULT_PROBES,
        dukascopy_cache=args.dukascopy_cache,
        histdata_cache=args.histdata_cache,
        fresh_download=not args.no_fresh_download,
        write_report=not args.no_report,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] == "BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
