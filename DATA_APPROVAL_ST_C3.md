# ST-C3 Dataset Approval Record

**Status:** NOT APPROVED
**Strategy:** ST-C3
**Spec:** `specs/st-c3_v1.0.7.yaml`
**Dataset directory:** `data/market/approved/st_c3/`
**Manifest:** `data/market/approved/st_c3/DATASET_MANIFEST_ST_C3.yaml`

Current manifest state: `approved: false` / `approval_status: NOT_APPROVED`.
This is intentional until integrity, manifest, and contract checks all pass.

Current candidate state: HistData.com Generic ASCII M1 was acquired and
normalized into H4/M15/M3 candidate files, but integrity validation failed
with missing timestamps in every required file. Dataset approval remains
blocked.

## Purpose

This document records owner approval for historical datasets used by the
ST-C3 ultra-fast validation pipeline. Dataset approval does not accept
S1-G5 or S1-G6, does not pass A2, does not open A3, and does not authorize
execution, broker integration, demo trading, live trading, or production.

## Required Dataset Scope

- Symbols: GBPUSD, EURUSD unless a later owner decision changes scope.
- Timeframes: H4, M15, M3.
- Date range: 2018-01-01 through 2024-12-31 unless a later owner decision
  records a narrower approved range.
- Timezone: UTC.
- Required candle columns: `time`, `open`, `high`, `low`, `close`, `volume`.

## Approval Checklist

- Dataset files are placed under `data/market/approved/st_c3/`.
- `DATASET_MANIFEST_ST_C3.yaml` exists and has `approved: true`.
- Every manifest dataset path exists.
- Every manifest SHA-256 matches the file bytes.
- Every CSV has the required candle columns, including non-negative `volume`.
- Timestamps are parseable, monotonic, and duplicate-free per file.
- Requested symbols, timeframes, and date range are covered by the manifest.
- Manifest session windows match ST-C3 v1.0.7: London `07:00`-`10:00`
  UTC, New York `13:00`-`16:00` UTC.
- If a `session` column is present, each value is one of `LONDON`, `NY`, or
  `OTHER`.
- If a `news_flag` column is present, each value is boolean-like.
- Symbol metadata exists for every approved symbol with exact `pip_size`,
  `min_tick`, and `lot_size` values.

## Owner Decision

- Decision: PENDING
- Approved by:
- Date:
- Notes: HistData candidate rejected for canonical approval on 2026-07-30.
