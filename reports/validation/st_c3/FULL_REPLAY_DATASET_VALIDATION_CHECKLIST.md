# ST-C3 Full Replay Dataset Validation Checklist

**Status:** Checklist only

## Required Checks

- Manifest exists at `data/market/approved/st_c3/DATASET_MANIFEST_ST_C3.yaml`.
- Manifest has `approved: true` after owner approval.
- Manifest `spec_version` is `"1.0.7"`.
- Manifest symbols match the frozen ST-C3 v1.0.7 instrument scope:
  `EURUSD`, `GBPUSD`.
- Manifest timeframes include `H4`, `M15`, `M3`.
- Manifest date or coverage range covers the requested replay window.
- Each CSV path exists under `data/market/approved/st_c3/`.
- Each SHA-256 hash matches file bytes.
- Required columns exist: `time`, `open`, `high`, `low`, `close`.
- Timestamps are parseable, strictly increasing, duplicate-free, and cadence
  matches timeframe.
- Optional `news_flag` values are boolean-like.
- Optional `session` values are `LONDON`, `NY`, or `OTHER`.
- Session windows match ST-C3 v1.0.7.
- Symbol metadata exists for every symbol with exact `pip_size`, `min_tick`,
  and `lot_size` values.

## Guardrail

Dataset validation authorizes data intake only. It does not accept S1-G5 or
S1-G6, pass A2, open A3, or authorize execution.
