# ST-C3 Dataset Approval Sprint Report

## Dataset Version

`Dataset_v0.1_blocked_candidate`

## Data Source(s)

Current candidate source: local MetaTrader 5 terminal export.

Status: **rejected for canonical approval**.

Reason: the current candidate data is fragmented and does not satisfy the
frozen ST-C3 v1.0.7 dataset contract.

## Coverage

Required active ST-C3 v1.0.7 scope:

- Symbols: `EURUSD`, `GBPUSD`
- Timeframes: `H4`, `M15`, `M3`
- Coverage: `2018-01-01` through `2024-12-31`
- Timezone: UTC

The broader canonical-dataset idea of adding `XAUUSD`, `H1`, and `M5` is
reserved for a future dataset-contract revision. It is not adopted into the
active v1.0.7 scope.

## Integrity Status

**FAIL / BLOCKED**

Current blockers include:

- `EURUSD_H4.csv` first missing market-open candle:
  `2018-12-26T00:00:00Z`
- `GBPUSD_H4.csv` first missing market-open candle:
  `2018-12-26T00:00:00Z`
- `EURUSD_M15.csv` starts in 2022 instead of 2018
- `GBPUSD_M15.csv` starts in 2022 instead of 2018
- `EURUSD_M3.csv` is a one-row 2025 stub
- `GBPUSD_M3.csv` is a one-row 2025 stub

## Manifest Status

**FAIL / BLOCKED**

The manifest is explicitly `approved: false` / `approval_status:
NOT_APPROVED`. Manifest hashes must not be rebuilt until all integrity checks
pass.

## Replay Status

**BLOCKED**

A3 is closed. Replay, backtest, demo, and live execution remain blocked.

## Recovery Status

Automatic recovery was attempted for the first 10 detected gaps.

Result: **BLOCKED**. The approved MT5 source did not return exact matching
candles for the attempted gaps. Recovery was capped with 136 additional gaps
left unattempted. No candles were fabricated, interpolated, or manually
edited.

## Files Changed / Added In Sprint

- `contracts/DATASET_CONTRACT.yaml`
- `tools/st_c3_dataset_contract.py`
- `tools/st_c3_data_integrity.py`
- `tools/st_c3_download_mt5_dataset.py`
- `tests/test_st_c3_dataset_governance.py`
- `data/market/approved/st_c3/DATASET_MANIFEST_ST_C3.yaml`
- `reports/validation/st_c3/data_integrity/DATA_SOURCE_AUDIT.md`
- `reports/validation/st_c3/data_integrity/DATASET_RELEASE_NOTES.md`
- `reports/validation/st_c3/data_integrity/DATA_INTEGRITY_REPORT.md`
- `reports/validation/st_c3/data_integrity/VALIDATION_SUMMARY.md`
- `reports/validation/st_c3/data_integrity/RECOVERY_LOG.md`
- `reports/validation/st_c3/data_integrity/UPDATED_MANIFEST.json`
- `.github/workflows/ci.yml`
- `CHANGELOG.md`

## Documentation Updated

- Dataset contract added.
- Data source audit added.
- Dataset release notes added.
- Data integrity and recovery reports generated.
- CI contract guardrail added.

## Recommendation

Do not modify strategy code.

Owner must replace the current candidate files with a complete canonical
EURUSD/GBPUSD H4/M15/M3 dataset covering `2018-01-01` through
`2024-12-31`, then run:

```powershell
python -m tools.st_c3_data_integrity --data data/market/approved/st_c3 --recover --write-reports
python -m tools.st_c3_dataset_contract --contract contracts/DATASET_CONTRACT.yaml --data data/market/approved/st_c3 --require-approved
```

If the strict contract command returns `ACCEPTED`, the owner may consider a
separate A3-opening decision. Until then, replay remains blocked.
