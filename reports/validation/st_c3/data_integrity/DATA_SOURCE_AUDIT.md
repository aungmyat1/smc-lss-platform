# ST-C3 Data Source Audit

Status: **BLOCKED**

Audit date: 2026-07-30

## Scope

Active frozen ST-C3 v1.0.7 requires:

- Symbols: `EURUSD`, `GBPUSD`
- Timeframes: `H4`, `M15`, `M3`
- Timezone: UTC
- Coverage: `2018-01-01` through `2024-12-31`

The broader sprint suggestion of `XAUUSD`, `H1`, and `M5` is recorded as a
future canonical-dataset target only. It is not adopted into the active
ST-C3 v1.0.7 contract because that would change the current governance
scope.

## Current Sources

| Source | Provider | Method | Timezone | Status | Quality Issues |
|---|---|---|---|---|---|
| `data/market/approved/st_c3/*.csv` | Local MT5 terminal candidate | `tools.st_c3_download_mt5_dataset` candidate export and prior placement | UTC-normalized CSV timestamps | BLOCKED / NOT_APPROVED | Partial M15 coverage, one-row M3 files, market-open H4/M15 gaps |
| `data/*.csv` legacy files | Local MT5 terminal / historical repo artifacts | `src/load_history.py` and older scripts | Mixed/legacy formatting | NOT_APPROVED_FOR_ST_C3 | Not governed by ST-C3 manifest, not canonical |

## Current Candidate Findings

- `EURUSD_H4.csv` first blocking gap: `2018-12-26T00:00:00Z`
- `GBPUSD_H4.csv` first blocking gap: `2018-12-26T00:00:00Z`
- `EURUSD_M15.csv` starts at `2022-07-22T01:45:00Z`, not `2018-01-01`
- `GBPUSD_M15.csv` starts at `2022-07-22T02:15:00Z`, not `2018-01-01`
- `EURUSD_M3.csv` contains one 2025 candle, not the approved 2018-2024 range
- `GBPUSD_M3.csv` contains one 2025 candle, not the approved 2018-2024 range
- MT5 recovery attempted for the first 10 detected gaps and returned no
  exact matching candles.

## API / Provider Limitations Observed

- Candidate downloads are allowed only while the dataset manifest is
  unapproved. Once the manifest and contract are approved, the dataset is
  immutable and the MT5 downloader refuses replacement.
- Native MT5 M3 retrieval returned unusable current/future-range stubs in
  this environment.
- Chunked MT5 downloads improved request reliability but did not provide
  complete historical coverage.
- Exact-candle recovery cannot repair gaps when the provider does not return
  the requested timestamp.

## Authoritative Source Recommendation

Select one owner-approved historical data provider that can deliver complete
UTC-normalized EURUSD/GBPUSD H4/M15/M3 data for 2018-2024.

Required provider capabilities:

- deterministic export or API retrieval
- stable UTC timestamps
- auditable provider/version metadata
- complete historical coverage for all required symbols/timeframes
- reproducible SHA-256 file hashes after export
- no interpolation or synthetic candles

If multiple providers are required, merge precedence must be explicitly
owner-approved before use. Conflict resolution must prefer the primary
provider and reject mismatched OHLC rows unless an owner-signed exception is
recorded.

## Recommendation

Do not attempt replay or A3. Replace the fragmented candidate files with a
complete owner-approved canonical dataset, then rerun:

```powershell
python -m tools.st_c3_data_integrity --data data/market/approved/st_c3 --recover --write-reports
python -m tools.st_c3_dataset_contract --contract contracts/DATASET_CONTRACT.yaml --data data/market/approved/st_c3
```
