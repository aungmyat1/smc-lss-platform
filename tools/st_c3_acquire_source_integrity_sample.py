#!/usr/bin/env python3
"""Acquire the deterministic ST-C3 source-integrity evidence sample.

This tool downloads raw Dukascopy evidence-sample hours only. It does not
construct approved dataset files, approve data, change contracts, fill candles,
or open replay.
"""
from __future__ import annotations

import argparse
import json
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Iterable

from tools.st_c3_acquire_dukascopy_dataset import (
    ACQUISITION_PROGRESS,
    DOWNLOAD_RECOVERY_LOG,
    RAW_CACHE,
    _cache_path,
    _download_hour,
    _format_time,
)
from tools.st_c3_statistical_source_integrity import (
    _deterministic_sample,
    _open_hours,
    _parse_date,
    _source_calendar_exclusions,
    _source_required_hours,
    _trading_days,
)
from tools.st_c3_verify_dukascopy_provider import _parse_bi5_ticks
from validation.st_c3.dataset_loader import EXPECTED_SYMBOLS

REPORT_JSON = Path("reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_SAMPLE_ACQUISITION.json")
REPORT_MD = Path("reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_SAMPLE_ACQUISITION.md")
PARALLEL_STATUS_JSON = Path("reports/validation/st_c3/data_integrity/PARALLEL_EXECUTION_STATUS.json")
PERFORMANCE_PROFILE_JSON = Path("reports/validation/st_c3/data_integrity/PERFORMANCE_PROFILE.json")
PERFORMANCE_PROFILE_MD = Path("reports/validation/st_c3/data_integrity/PERFORMANCE_PROFILE.md")
GUARDRAIL = "Evidence-sample acquisition downloads raw source files only; it does not approve data, change governance, or open replay."


def acquire_source_integrity_sample(
    *,
    cache_dir: str | Path = RAW_CACHE,
    start_date: date = date(2021, 1, 1),
    end_date: date = date(2025, 12, 31),
    target_sample_days: int = 100,
    seed: int = 107,
    max_days: int | None = None,
    max_hours: int | None = None,
    workers: int = 1,
    retries: int = 3,
    write_report: bool = True,
) -> dict[str, Any]:
    started = time.perf_counter()
    cache = Path(cache_dir)
    population = _trading_days(start_date, end_date)
    sample_days = _deterministic_sample(population, target_sample_days, seed)
    completed_before = [day for day in sample_days if _day_cache_complete(cache, day, EXPECTED_SYMBOLS)]
    pending_days = [day for day in sample_days if day not in completed_before]
    selected_days = pending_days[:max_days] if max_days is not None else pending_days
    workers = max(1, int(workers))
    provider_calendar_exclusions = _source_calendar_exclusions(selected_days, sorted(EXPECTED_SYMBOLS))
    tasks, day_plans, stopped_by_limit = _plan_tasks(selected_days, max_hours, workers)
    attempts = _execute_tasks(tasks, cache, retries, workers)
    day_progress: list[dict[str, Any]] = []

    for day_plan in day_plans:
        day = day_plan["day"]
        day_attempts = [item for item in attempts if item["sample_day"] == day.isoformat()]
        completed_so_far = [sample_day for sample_day in sample_days if _day_cache_complete(cache, sample_day, EXPECTED_SYMBOLS)]
        failed_for_day = [item for item in day_attempts if item["status"] == "FAILED"]
        day_progress.append(
            {
                "sample_day": day.isoformat(),
                "status": "BLOCKED" if failed_for_day else ("PARTIAL" if day_plan["partial"] else "COMPLETE"),
                "attempted_source_hours": len(day_attempts),
                "downloaded_source_hours": len([item for item in day_attempts if item["status"] == "DOWNLOADED"]),
                "cached_verified_source_hours": len([item for item in day_attempts if item["status"] == "CACHED_VERIFIED"]),
                "provider_calendar_excluded_source_hours": day_plan["provider_calendar_excluded_source_hours"],
                "failed_source_hours": failed_for_day,
                "completed_sample_days_after_day": len(completed_so_far),
            }
        )

    completed_after = [day for day in sample_days if _day_cache_complete(cache, day, EXPECTED_SYMBOLS)]
    failed = [item for item in attempts if item["status"] == "FAILED"]
    acquisition_elapsed_seconds = time.perf_counter() - started
    profile_started = time.perf_counter()
    parse_profile = _profile_parse_and_m1(attempts)
    profile_elapsed_seconds = time.perf_counter() - profile_started
    elapsed_seconds = time.perf_counter() - started
    performance = _performance_profile(attempts, elapsed_seconds, acquisition_elapsed_seconds, profile_elapsed_seconds, parse_profile, workers)
    parallel_status = _parallel_status(tasks, attempts, workers)
    status = "BLOCKED" if failed else "IN_PROGRESS"
    result = {
        "stage": "source_integrity_sample_acquisition",
        "status": status,
        "reason": _reason(failed, completed_after, target_sample_days, stopped_by_limit),
        "next_action": _next_action(failed, completed_after, target_sample_days),
        "details": {
            "coverage": {"from": start_date.isoformat(), "to": end_date.isoformat()},
            "target_sample_days": target_sample_days,
            "sample_seed": seed,
            "completed_sample_days_before": len(completed_before),
            "completed_sample_days_after": len(completed_after),
            "remaining_sample_days": max(target_sample_days - len(completed_after), 0),
            "selected_days": [day.isoformat() for day in selected_days],
            "day_progress": day_progress,
            "provider_calendar_exclusions": provider_calendar_exclusions,
            "attempted_hours": len(attempts),
            "downloaded_or_cached_hours": len([item for item in attempts if item["status"] in {"DOWNLOADED", "CACHED_VERIFIED"}]),
            "failed_hours": failed,
            "stopped_by_limit": stopped_by_limit,
            "first_remaining_day": _first_remaining(sample_days, completed_after),
            "execution": {
                "mode": "parallel" if workers > 1 else "sequential",
                "workers": workers,
                "planned_tasks": len(tasks),
                "elapsed_seconds": elapsed_seconds,
                "acquisition_elapsed_seconds": acquisition_elapsed_seconds,
                "profiling_elapsed_seconds": profile_elapsed_seconds,
            },
            "parallel_execution": parallel_status,
            "performance_profile": performance,
        },
        "guardrail": GUARDRAIL,
        "recommendation": "CONTINUE_EVIDENCE_COLLECTION",
    }
    if write_report:
        REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
        REPORT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        REPORT_MD.write_text(_markdown(result), encoding="utf-8")
        _write_sprint_progress(result)
        _write_parallel_and_performance_reports(result)
    return result


def _plan_tasks(selected_days: list[date], max_hours: int | None, workers: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]:
    tasks: list[dict[str, Any]] = []
    day_plans: list[dict[str, Any]] = []
    stopped_by_limit = False
    for day in selected_days:
        day_start = len(tasks)
        excluded_hours_for_day = [hour for hour in _open_hours(day) if hour not in _source_required_hours(day)]
        partial = False
        for hour in _source_required_hours(day):
            for symbol in sorted(EXPECTED_SYMBOLS):
                if max_hours is not None and len(tasks) >= max_hours:
                    stopped_by_limit = True
                    partial = True
                    break
                tasks.append(
                    {
                        "task_index": len(tasks),
                        "sample_day": day.isoformat(),
                        "symbol": symbol,
                        "hour": hour,
                        "scheduled_worker": (len(tasks) % workers) + 1,
                    }
                )
            if stopped_by_limit:
                break
        if len(tasks) > day_start or partial:
            day_plans.append(
                {
                    "day": day,
                    "partial": partial,
                    "provider_calendar_excluded_source_hours": len(excluded_hours_for_day) * len(EXPECTED_SYMBOLS),
                }
            )
        if stopped_by_limit:
            break
    return tasks, day_plans, stopped_by_limit


def _execute_tasks(tasks: list[dict[str, Any]], cache: Path, retries: int, workers: int) -> list[dict[str, Any]]:
    if workers <= 1:
        return [_execute_task(task, cache, retries) for task in tasks]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(lambda task: _execute_task(task, cache, retries), tasks))


def _execute_task(task: dict[str, Any], cache: Path, retries: int) -> dict[str, Any]:
    path = _cache_path(cache, task["symbol"], task["hour"])
    cache_present_before = path.exists() and path.stat().st_size > 0
    started = time.perf_counter()
    result = _download_hour(task["symbol"], task["hour"], cache, retries=retries)
    elapsed = time.perf_counter() - started
    return {
        **result,
        "task_index": task["task_index"],
        "sample_day": task["sample_day"],
        "scheduled_worker": task["scheduled_worker"],
        "cache_present_before": cache_present_before,
        "elapsed_seconds": elapsed,
    }


def _day_cache_complete(cache: Path, day: date, symbols: Iterable[str]) -> bool:
    return all(
        (path := _cache_path(cache, symbol, hour)).exists() and path.stat().st_size > 0
        for hour in _source_required_hours(day)
        for symbol in symbols
    )


def _first_remaining(sample_days: list[date], completed_days: list[date]) -> str | None:
    completed = set(completed_days)
    for day in sample_days:
        if day not in completed:
            return day.isoformat()
    return None


def _reason(failed: list[dict[str, Any]], completed_after: list[date], target: int, stopped_by_limit: bool) -> str:
    if failed:
        first = failed[0]
        return f"{first['symbol']} {first['hour_utc']} evidence-sample download failed: {first['reason']}"
    if len(completed_after) >= target:
        return "deterministic source-integrity evidence sample is fully cached"
    if stopped_by_limit:
        return f"bounded evidence-sample acquisition completed; {len(completed_after)}/{target} target days cached"
    return f"evidence-sample acquisition in progress; {len(completed_after)}/{target} target days cached"


def _next_action(failed: list[dict[str, Any]], completed_after: list[date], target: int) -> str:
    if failed:
        return "Retry failed evidence-sample hours; do not alter dataset policy."
    if len(completed_after) >= target:
        return "Rerun statistical source-integrity report and proceed to evidence review."
    return "Continue deterministic evidence-sample acquisition in bounded batches."


def _performance_profile(
    attempts: list[dict[str, Any]],
    elapsed_seconds: float,
    acquisition_elapsed_seconds: float,
    profiling_elapsed_seconds: float,
    parse_profile: dict[str, Any],
    workers: int,
) -> dict[str, Any]:
    downloaded = [item for item in attempts if item["status"] == "DOWNLOADED"]
    cached = [item for item in attempts if item["status"] == "CACHED_VERIFIED"]
    failed = [item for item in attempts if item["status"] == "FAILED"]
    total_bytes = sum(int(item.get("bytes") or 0) for item in attempts)
    total_task_seconds = sum(float(item.get("elapsed_seconds") or 0.0) for item in attempts)
    status_seconds = {
        status: sum(float(item.get("elapsed_seconds") or 0.0) for item in attempts if item["status"] == status)
        for status in sorted({item["status"] for item in attempts})
    }
    bottlenecks = _bottlenecks(acquisition_elapsed_seconds, parse_profile)
    return {
        "mode": "parallel" if workers > 1 else "sequential",
        "workers": workers,
        "elapsed_seconds": elapsed_seconds,
        "acquisition_elapsed_seconds": acquisition_elapsed_seconds,
        "profiling_elapsed_seconds": profiling_elapsed_seconds,
        "attempted_source_hours": len(attempts),
        "downloaded_source_hours": len(downloaded),
        "cached_verified_source_hours": len(cached),
        "failed_source_hours": len(failed),
        "cache_hit_rate": (len(cached) / len(attempts)) if attempts else None,
        "download_throughput_hours_per_minute": (len(attempts) / (elapsed_seconds / 60.0)) if elapsed_seconds > 0 else None,
        "payload_bytes": total_bytes,
        "payload_megabytes": total_bytes / 1_000_000,
        "total_task_seconds": total_task_seconds,
        "task_seconds_by_status": status_seconds,
        "avg_seconds_per_downloaded_hour": statistics.fmean(float(item.get("elapsed_seconds") or 0.0) for item in downloaded) if downloaded else None,
        "avg_seconds_per_cached_hour": statistics.fmean(float(item.get("elapsed_seconds") or 0.0) for item in cached) if cached else None,
        "parallel_efficiency_proxy": (total_task_seconds / (elapsed_seconds * workers)) if elapsed_seconds > 0 and workers > 0 else None,
        "stage_timings": {
            "download_cache_seconds": acquisition_elapsed_seconds,
            "bi5_decompression_parse_seconds": parse_profile["bi5_decompression_parse_seconds"],
            "m1_reconstruction_seconds": parse_profile["m1_reconstruction_seconds"],
            "aggregation_seconds": None,
            "validation_seconds": None,
            "cross_provider_lookup_seconds": None,
            "report_generation_seconds": profiling_elapsed_seconds,
        },
        "stage_notes": {
            "download_cache_seconds": "includes network download, cache verification, retries, and payload parse verification inside _download_hour",
            "bi5_decompression_parse_seconds": "post-acquisition profiling pass over successful source-hour files",
            "m1_reconstruction_seconds": "post-acquisition minute grouping profile over parsed ticks",
            "aggregation_seconds": "not run in provider-qualification acquisition pipeline",
            "validation_seconds": "not run in provider-qualification acquisition pipeline",
            "cross_provider_lookup_seconds": "measured by statistical/cross-provider report generation, not acquisition",
            "report_generation_seconds": "time spent on post-acquisition profiling before report serialization",
        },
        "profiled_successful_files": parse_profile["profiled_files"],
        "profiled_ticks": parse_profile["profiled_ticks"],
        "profiled_m1_rows": parse_profile["profiled_m1_rows"],
        "top_bottlenecks": bottlenecks,
    }


def _profile_parse_and_m1(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    parse_seconds = 0.0
    m1_seconds = 0.0
    profiled_files = 0
    profiled_ticks = 0
    profiled_m1_rows = 0
    for item in attempts:
        if item["status"] not in {"DOWNLOADED", "CACHED_VERIFIED"} or not item.get("path"):
            continue
        path = Path(str(item["path"]))
        if not path.exists() or path.stat().st_size <= 0:
            continue
        hour = datetime.strptime(item["hour_utc"], "%Y-%m-%dT%H:00:00Z").replace(tzinfo=UTC)
        parse_started = time.perf_counter()
        ticks = _parse_bi5_ticks(path.read_bytes(), hour, item["symbol"])
        parse_seconds += time.perf_counter() - parse_started
        m1_started = time.perf_counter()
        minutes = {tick.timestamp.replace(second=0, microsecond=0) for tick in ticks}
        m1_seconds += time.perf_counter() - m1_started
        profiled_files += 1
        profiled_ticks += len(ticks)
        profiled_m1_rows += len(minutes)
    return {
        "bi5_decompression_parse_seconds": parse_seconds,
        "m1_reconstruction_seconds": m1_seconds,
        "profiled_files": profiled_files,
        "profiled_ticks": profiled_ticks,
        "profiled_m1_rows": profiled_m1_rows,
    }


def _bottlenecks(acquisition_elapsed_seconds: float, parse_profile: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        {"stage": "download_cache", "seconds": acquisition_elapsed_seconds},
        {"stage": "bi5_decompression_parse", "seconds": parse_profile["bi5_decompression_parse_seconds"]},
        {"stage": "m1_reconstruction", "seconds": parse_profile["m1_reconstruction_seconds"]},
    ]
    return sorted(rows, key=lambda item: float(item["seconds"]), reverse=True)[:2]


def _parallel_status(tasks: list[dict[str, Any]], attempts: list[dict[str, Any]], workers: int) -> dict[str, Any]:
    planned_by_worker = {str(worker): 0 for worker in range(1, workers + 1)}
    completed_by_worker = {str(worker): 0 for worker in range(1, workers + 1)}
    failed_by_worker = {str(worker): 0 for worker in range(1, workers + 1)}
    seconds_by_worker = {str(worker): 0.0 for worker in range(1, workers + 1)}
    planned_task_order = [_task_key(task) for task in tasks]
    completed_task_order = [_task_key(item) for item in sorted(attempts, key=lambda item: int(item["task_index"]))]
    for task in tasks:
        planned_by_worker[str(task["scheduled_worker"])] += 1
    for item in attempts:
        worker = str(item["scheduled_worker"])
        completed_by_worker[worker] += 1
        seconds_by_worker[worker] += float(item.get("elapsed_seconds") or 0.0)
        if item["status"] == "FAILED":
            failed_by_worker[worker] += 1
    return {
        "mode": "parallel" if workers > 1 else "sequential",
        "workers": workers,
        "deterministic_assignment": "task_index modulo worker_count",
        "planned_tasks": len(tasks),
        "completed_tasks": len(attempts),
        "duplicate_task_count": len(tasks) - len({(task["symbol"], task["hour"]) for task in tasks}),
        "planned_task_order": planned_task_order,
        "completed_task_order": completed_task_order,
        "task_order_matches_plan": planned_task_order == completed_task_order,
        "planned_by_worker": planned_by_worker,
        "completed_by_worker": completed_by_worker,
        "failed_by_worker": failed_by_worker,
        "task_seconds_by_worker": seconds_by_worker,
    }


def _task_key(item: dict[str, Any]) -> str:
    hour = item.get("hour") or item.get("hour_utc")
    if isinstance(hour, datetime):
        hour_text = hour.isoformat().replace("+00:00", "Z")
    else:
        hour_text = str(hour)
    return f"{int(item['task_index']):06d}|{item['symbol']}|{hour_text}"


def _markdown(result: dict[str, Any]) -> str:
    details = result["details"]
    lines = [
        "# ST-C3 Source Integrity Sample Acquisition",
        "",
        f"Status: **{result['status']}**",
        "",
        f"Reason: {result['reason']}",
        "",
        f"Recommendation: **{result['recommendation']}**",
        "",
        f"Guardrail: {result['guardrail']}",
        "",
        "## Progress",
        "",
        f"- Target sample days: `{details['target_sample_days']}`",
        f"- Completed before: `{details['completed_sample_days_before']}`",
        f"- Completed after: `{details['completed_sample_days_after']}`",
        f"- Remaining sample days: `{details['remaining_sample_days']}`",
        f"- Attempted source hours: `{details['attempted_hours']}`",
        f"- Downloaded or cached source hours: `{details['downloaded_or_cached_hours']}`",
        f"- Provider-calendar excluded source hours: `{details['provider_calendar_exclusions']['symbol_hour_count']}`",
        f"- Failed source hours: `{len(details['failed_hours'])}`",
        f"- First remaining sample day: `{details['first_remaining_day']}`",
        f"- Execution mode: `{details['execution']['mode']}`",
        f"- Workers: `{details['execution']['workers']}`",
        f"- Throughput hours/minute: `{details['performance_profile']['download_throughput_hours_per_minute']}`",
        "",
        "## Day Progress",
        "",
        "| Sample Day | Status | Attempted | Downloaded | Cached | Provider Excluded | Failed | Completed After Day |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in details["day_progress"]:
        lines.append(
            f"| `{item['sample_day']}` | `{item['status']}` | {item['attempted_source_hours']} | "
            f"{item['downloaded_source_hours']} | {item['cached_verified_source_hours']} | "
            f"{item['provider_calendar_excluded_source_hours']} | {len(item['failed_source_hours'])} | "
            f"{item['completed_sample_days_after_day']} |"
        )
    lines += [
        "",
        "No candles were fabricated, interpolated, or manually inserted.",
    ]
    return "\n".join(lines) + "\n"


def _write_sprint_progress(result: dict[str, Any]) -> None:
    details = result["details"]
    progress = {
        "stage": result["stage"],
        "status": result["status"],
        "dataset_version": "Dataset_v1.0_5Y",
        "provider": "Dukascopy tick datafeed",
        "evidence_sprint": "source_integrity",
        "coverage": details["coverage"],
        "target_sample_days": details["target_sample_days"],
        "sample_seed": details["sample_seed"],
        "completed_sample_days": details["completed_sample_days_after"],
        "remaining_sample_days": details["remaining_sample_days"],
        "attempted_source_hours_latest_batch": details["attempted_hours"],
        "downloaded_or_cached_source_hours_latest_batch": details["downloaded_or_cached_hours"],
        "provider_calendar_excluded_source_hours_latest_batch": details["provider_calendar_exclusions"]["symbol_hour_count"],
        "failed_source_hours_latest_batch": len(details["failed_hours"]),
        "first_remaining_day": details["first_remaining_day"],
        "validation_status": "SOURCE_INTEGRITY_EVIDENCE_COLLECTION",
        "approval_status": "NOT_APPROVED",
        "replay_status": "BLOCKED",
        "recommendation": result["recommendation"],
        "guardrail": result["guardrail"],
    }
    ACQUISITION_PROGRESS.write_text(json.dumps(progress, indent=2, sort_keys=True), encoding="utf-8")

    failed = details["failed_hours"]
    lines = [
        "# ST-C3 Dukascopy Download Recovery Log",
        "",
        "Dataset version: `Dataset_v1.0_5Y`",
        "",
        "Scope: source-integrity evidence sample only",
        "",
        f"Latest status: **{result['status']}**",
        "",
        f"Completed sample days: `{details['completed_sample_days_after']}/{details['target_sample_days']}`",
        "",
        "## Latest Batch Day Progress",
        "",
        "| Sample Day | Status | Attempted | Provider Excluded | Failed |",
        "|---|---|---:|---:|---:|",
    ]
    for item in details["day_progress"]:
        lines.append(
            f"| `{item['sample_day']}` | `{item['status']}` | "
            f"{item['attempted_source_hours']} | {item['provider_calendar_excluded_source_hours']} | "
            f"{len(item['failed_source_hours'])} |"
        )
    lines += ["", "## Failed Hours", ""]
    if failed:
        for item in failed:
            lines.append(f"- `{item['symbol']}` `{item['hour_utc']}`: {item['reason']}")
    else:
        lines.append("- No failed market-open hours in the latest evidence-sample batch.")
    lines += ["", "No candles were fabricated, interpolated, or manually edited."]
    DOWNLOAD_RECOVERY_LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_parallel_and_performance_reports(result: dict[str, Any]) -> None:
    details = result["details"]
    parallel = {
        "stage": "parallel_evidence_collection",
        "status": result["status"],
        "recommendation": result["recommendation"],
        "guardrail": result["guardrail"],
        "details": details["parallel_execution"],
    }
    performance = {
        "stage": "source_integrity_performance_profile",
        "status": result["status"],
        "recommendation": result["recommendation"],
        "guardrail": result["guardrail"],
        "details": details["performance_profile"],
    }
    PARALLEL_STATUS_JSON.write_text(json.dumps(parallel, indent=2, sort_keys=True), encoding="utf-8")
    PERFORMANCE_PROFILE_JSON.write_text(json.dumps(performance, indent=2, sort_keys=True), encoding="utf-8")
    PERFORMANCE_PROFILE_MD.write_text(_performance_markdown(performance, parallel), encoding="utf-8")


def _performance_markdown(performance: dict[str, Any], parallel: dict[str, Any]) -> str:
    details = performance["details"]
    parallel_details = parallel["details"]
    lines = [
        "# ST-C3 Source Integrity Performance Profile",
        "",
        f"Status: **{performance['status']}**",
        "",
        f"Recommendation: **{performance['recommendation']}**",
        "",
        f"Guardrail: {performance['guardrail']}",
        "",
        "## Throughput",
        "",
        f"- Mode: `{details['mode']}`",
        f"- Workers: `{details['workers']}`",
        f"- Elapsed seconds: `{details['elapsed_seconds']}`",
        f"- Acquisition seconds: `{details['acquisition_elapsed_seconds']}`",
        f"- Profiling/report seconds: `{details['profiling_elapsed_seconds']}`",
        f"- Attempted source hours: `{details['attempted_source_hours']}`",
        f"- Downloaded source hours: `{details['downloaded_source_hours']}`",
        f"- Cached verified source hours: `{details['cached_verified_source_hours']}`",
        f"- Failed source hours: `{details['failed_source_hours']}`",
        f"- Cache hit rate: `{details['cache_hit_rate']}`",
        f"- Download throughput hours/minute: `{details['download_throughput_hours_per_minute']}`",
        f"- Payload MB: `{details['payload_megabytes']}`",
        f"- Parallel efficiency proxy: `{details['parallel_efficiency_proxy']}`",
        f"- Top bottlenecks: `{details['top_bottlenecks']}`",
        "",
        "## Stage Timings",
        "",
        f"- Download/cache seconds: `{details['stage_timings']['download_cache_seconds']}`",
        f"- `.bi5` decompression/parse seconds: `{details['stage_timings']['bi5_decompression_parse_seconds']}`",
        f"- M1 reconstruction seconds: `{details['stage_timings']['m1_reconstruction_seconds']}`",
        f"- Aggregation seconds: `{details['stage_timings']['aggregation_seconds']}`",
        f"- Validation seconds: `{details['stage_timings']['validation_seconds']}`",
        f"- Cross-provider lookup seconds: `{details['stage_timings']['cross_provider_lookup_seconds']}`",
        f"- Report generation/profile seconds: `{details['stage_timings']['report_generation_seconds']}`",
        "",
        "## Stage Notes",
        "",
        f"- Download/cache: {details['stage_notes']['download_cache_seconds']}",
        f"- `.bi5` decompression/parse: {details['stage_notes']['bi5_decompression_parse_seconds']}",
        f"- M1 reconstruction: {details['stage_notes']['m1_reconstruction_seconds']}",
        f"- Aggregation: {details['stage_notes']['aggregation_seconds']}",
        f"- Validation: {details['stage_notes']['validation_seconds']}",
        f"- Cross-provider lookup: {details['stage_notes']['cross_provider_lookup_seconds']}",
        "",
        "## Worker Utilization",
        "",
        f"- Deterministic assignment: `{parallel_details['deterministic_assignment']}`",
        f"- Planned by worker: `{parallel_details['planned_by_worker']}`",
        f"- Completed by worker: `{parallel_details['completed_by_worker']}`",
        f"- Failed by worker: `{parallel_details['failed_by_worker']}`",
        f"- Task seconds by worker: `{parallel_details['task_seconds_by_worker']}`",
        f"- Task order matches plan: `{parallel_details['task_order_matches_plan']}`",
        "",
        "No market data was altered, fabricated, interpolated, or approved.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=RAW_CACHE)
    parser.add_argument("--start-date", type=_parse_date, default=date(2021, 1, 1))
    parser.add_argument("--end-date", type=_parse_date, default=date(2025, 12, 31))
    parser.add_argument("--target-sample-days", type=int, default=100)
    parser.add_argument("--seed", type=int, default=107)
    parser.add_argument("--max-days", type=int, default=None)
    parser.add_argument("--max-hours", type=int, default=None)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--no-report", action="store_true")
    args = parser.parse_args()
    result = acquire_source_integrity_sample(
        cache_dir=args.cache,
        start_date=args.start_date,
        end_date=args.end_date,
        target_sample_days=args.target_sample_days,
        seed=args.seed,
        max_days=args.max_days,
        max_hours=args.max_hours,
        workers=args.workers,
        retries=args.retries,
        write_report=not args.no_report,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] == "BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
