#!/usr/bin/env python3
"""Acquire and construct an ST-C3 Dataset v1.0 candidate from HistData M1 bars.

This tool builds candidate data only. It does not approve the dataset, open A3,
run replay, or change ST-C3 strategy/replay/validation logic.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import urllib.parse
import urllib.request
import zipfile
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

import yaml

from tools.st_c3_data_integrity import run_integrity_check
from tools.st_c3_dataset_contract import validate_dataset_contract
from tools.st_c3_download_mt5_dataset import _format_time, _session_for
from validation.st_c3.dataset_loader import EXPECTED_SYMBOLS, EXPECTED_TIMEFRAMES, MANIFEST_NAME, TIMEFRAME_DELTAS

SOURCE = "HistData.com Generic ASCII M1"
BASE_URL = "https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes"
GET_URL = "https://www.histdata.com/get.php"
SOURCE_YEARS = tuple(range(2017, 2025))
GUARDRAIL = "Acquisition builds candidates only; approval and replay remain gated."


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


def acquire_histdata_dataset(
    data_dir: str | Path,
    *,
    cache_dir: str | Path = Path("data/market/raw/histdata/st_c3"),
    write_files: bool = False,
    validate: bool = True,
) -> dict[str, object]:
    root = Path(data_dir)
    cache = Path(cache_dir)
    manifest = _load_manifest(root)
    if manifest.get("approved") is True:
        return _blocked("dataset manifest is already approved; approved datasets are immutable")
    if str(manifest.get("spec_version")) != "1.0.7":
        return _blocked("dataset manifest spec_version must be 1.0.7")
    if set(manifest.get("symbols") or []) != EXPECTED_SYMBOLS:
        return _blocked(f"manifest symbols must be exactly {sorted(EXPECTED_SYMBOLS)}")
    if set(manifest.get("timeframes") or []) != EXPECTED_TIMEFRAMES:
        return _blocked(f"manifest timeframes must be exactly {sorted(EXPECTED_TIMEFRAMES)}")

    if not write_files:
        return {
            "stage": "market_data_acquisition",
            "status": "BLOCKED",
            "reason": "dry run only; pass --write-files to download and construct candidate CSVs",
            "next_action": "Run with --write-files after confirming HistData licensing/access is acceptable.",
            "details": _details("BLOCKED", "BLOCKED", "BLOCKED"),
            "guardrail": GUARDRAIL,
        }

    root.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    construction: list[dict[str, object]] = []
    try:
        for symbol in sorted(EXPECTED_SYMBOLS):
            source_m1 = _load_symbol_m1(symbol, cache)
            for timeframe in sorted(EXPECTED_TIMEFRAMES):
                candles = _resample(source_m1, timeframe)
                path = root / f"{symbol}_{timeframe}.csv"
                _write_csv(path, candles)
                construction.append(
                    {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "path": str(path),
                        "rows": len(candles),
                        "first_timestamp": _format_time(candles[0].timestamp) if candles else None,
                        "last_timestamp": _format_time(candles[-1].timestamp) if candles else None,
                    }
                )
    except Exception as exc:  # noqa: BLE001 - acquisition must report exact blocker.
        return {
            "stage": "market_data_acquisition",
            "status": "BLOCKED",
            "reason": f"HistData acquisition/construction failed: {exc}",
            "next_action": "Document missing coverage and select the next best authoritative provider.",
            "details": {
                **_details("BLOCKED", "BLOCKED", "BLOCKED"),
                "constructed_files": construction,
            },
            "guardrail": GUARDRAIL,
        }

    integrity_result: dict[str, object] | None = None
    contract_result: dict[str, object] | None = None
    if validate:
        integrity_result = run_integrity_check(root, recover=False, write_reports=True)
        contract_result = validate_dataset_contract(Path("contracts/DATASET_CONTRACT.yaml"), root)

    integrity_status = str(integrity_result.get("status")) if integrity_result else "NOT_RUN"
    contract_status = str(contract_result.get("status")) if contract_result else "NOT_RUN"
    status = "ACCEPTED" if integrity_status == "PASS" and contract_status in {"BLOCKED", "ACCEPTED"} else "BLOCKED"
    reason = (
        "candidate dataset constructed and passed integrity; hand off to dataset approval"
        if status == "ACCEPTED"
        else (str(integrity_result.get("reason")) if integrity_result else "candidate constructed; validation not run")
    )
    return {
        "stage": "market_data_acquisition",
        "status": status,
        "reason": reason,
        "next_action": (
            "Run dataset approval gate; do not run replay until approval succeeds."
            if status == "ACCEPTED"
            else "Stop and document missing coverage before trying the next provider."
        ),
        "details": {
            **_details(integrity_status, "BLOCKED", contract_status),
            "constructed_files": construction,
            "integrity_reason": integrity_result.get("reason") if integrity_result else None,
            "contract_reason": contract_result.get("reason") if contract_result else None,
        },
        "guardrail": GUARDRAIL,
    }


def _load_manifest(root: Path) -> dict[str, object]:
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.exists():
        raise FileNotFoundError(f"missing ST-C3 dataset manifest: {manifest_path}")
    loaded = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("dataset manifest must be a mapping")
    return loaded


def _load_symbol_m1(symbol: str, cache: Path) -> list[Candle]:
    by_time: OrderedDict[datetime, Candle] = OrderedDict()
    for year in SOURCE_YEARS:
        zip_path = _download_histdata_zip(symbol, year, cache)
        for candle in _read_histdata_zip(zip_path):
            if datetime(2018, 1, 1) <= candle.timestamp < datetime(2025, 1, 1):
                by_time[candle.timestamp] = candle
    return [by_time[key] for key in sorted(by_time)]


def _download_histdata_zip(symbol: str, year: int, cache: Path) -> Path:
    out = cache / symbol / f"DAT_ASCII_{symbol}_M1_{year}.zip"
    if out.exists() and out.stat().st_size > 0:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    referer = f"{BASE_URL}/{symbol.lower()}/{year}"
    page = _http_get(referer)
    token = _extract_token(page)
    data = urllib.parse.urlencode(
        {
            "tk": token,
            "date": str(year),
            "datemonth": str(year),
            "platform": "ASCII",
            "timeframe": "M1",
            "fxpair": symbol,
        }
    ).encode("ascii")
    request = urllib.request.Request(
        GET_URL,
        data=data,
        headers={
            "User-Agent": "smc-lss-platform dataset acquisition",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": referer,
            "Origin": "https://www.histdata.com",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = response.read()
    if not zipfile.is_zipfile(_bytes_path(payload, out)):
        out.unlink(missing_ok=True)
        raise ValueError(f"HistData did not return a valid zip for {symbol} {year}")
    return out


def _bytes_path(payload: bytes, out: Path) -> Path:
    out.write_bytes(payload)
    return out


def _http_get(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "smc-lss-platform dataset acquisition"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read().decode("utf-8", errors="replace")


def _extract_token(page: str) -> str:
    match = re.search(r'id=["\']tk["\'][^>]*value=["\']([^"\']+)["\']', page)
    if not match:
        raise ValueError("HistData download token not found")
    return html.unescape(match.group(1))


def _read_histdata_zip(path: Path) -> Iterable[Candle]:
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not names:
            raise ValueError(f"no csv payload in {path}")
        with archive.open(names[0]) as fh:
            for raw in fh:
                line = raw.decode("ascii", errors="strict").strip()
                if not line:
                    continue
                parts = line.split(";")
                if len(parts) < 5:
                    raise ValueError(f"invalid HistData row in {path}: {line!r}")
                timestamp = datetime.strptime(parts[0], "%Y%m%d %H%M%S") + timedelta(hours=5)
                yield Candle(
                    timestamp=timestamp,
                    open=float(parts[1]),
                    high=float(parts[2]),
                    low=float(parts[3]),
                    close=float(parts[4]),
                    volume=float(parts[5]) if len(parts) > 5 and parts[5] else 0.0,
                )


def _resample(source: list[Candle], timeframe: str) -> list[Candle]:
    delta = TIMEFRAME_DELTAS[timeframe]
    minutes = int(delta.total_seconds() // 60)
    buckets: OrderedDict[datetime, list[Candle]] = OrderedDict()
    for candle in source:
        bucket_start = _floor_time(candle.timestamp, minutes)
        buckets.setdefault(bucket_start, []).append(candle)
    output: list[Candle] = []
    for timestamp, rows in buckets.items():
        if len(rows) != minutes:
            continue
        expected = [timestamp + timedelta(minutes=offset) for offset in range(minutes)]
        actual = [row.timestamp for row in rows]
        if actual != expected:
            continue
        output.append(
            Candle(
                timestamp=timestamp,
                open=rows[0].open,
                high=max(row.high for row in rows),
                low=min(row.low for row in rows),
                close=rows[-1].close,
                volume=sum(row.volume for row in rows),
            )
        )
    return output


def _floor_time(value: datetime, minutes: int) -> datetime:
    day_start = value.replace(hour=0, minute=0, second=0, microsecond=0)
    offset_minutes = int((value - day_start).total_seconds() // 60)
    return day_start + timedelta(minutes=(offset_minutes // minutes) * minutes)


def _write_csv(path: Path, candles: Iterable[Candle]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["time", "open", "high", "low", "close", "volume", "session", "news_flag"])
        for candle in candles:
            writer.writerow(
                [
                    _format_time(candle.timestamp),
                    f"{candle.open:.10f}",
                    f"{candle.high:.10f}",
                    f"{candle.low:.10f}",
                    f"{candle.close:.10f}",
                    f"{candle.volume:.0f}",
                    _session_for(candle.timestamp),
                    "false",
                ]
            )


def _details(integrity: str, manifest: str, contract: str) -> dict[str, object]:
    return {
        "recommended_source": SOURCE,
        "dataset_version": "Dataset_v1.0",
        "symbols": sorted(EXPECTED_SYMBOLS),
        "timeframes": sorted(EXPECTED_TIMEFRAMES),
        "coverage": {"from": "2018-01-01", "to": "2024-12-31"},
        "integrity_status": integrity,
        "manifest_status": manifest,
        "contract_status": contract,
        "replay_status": "BLOCKED",
    }


def _blocked(reason: str) -> dict[str, object]:
    return {
        "stage": "market_data_acquisition",
        "status": "BLOCKED",
        "reason": reason,
        "next_action": "Keep dataset approval and replay blocked.",
        "details": _details("BLOCKED", "BLOCKED", "BLOCKED"),
        "guardrail": GUARDRAIL,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/market/approved/st_c3"))
    parser.add_argument("--cache", type=Path, default=Path("data/market/raw/histdata/st_c3"))
    parser.add_argument("--write-files", action="store_true")
    parser.add_argument("--no-validate", action="store_true")
    args = parser.parse_args()
    result = acquire_histdata_dataset(args.data, cache_dir=args.cache, write_files=args.write_files, validate=not args.no_validate)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] != "ACCEPTED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
