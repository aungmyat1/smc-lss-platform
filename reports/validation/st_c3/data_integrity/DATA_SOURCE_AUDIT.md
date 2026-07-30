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
| `data/market/approved/st_c3/*.csv` | HistData.com Generic ASCII M1 candidate | `tools.st_c3_acquire_histdata_dataset`; M1 converted from EST-no-DST to UTC and derived to H4/M15/M3 | UTC-normalized candidate CSV timestamps | BLOCKED / NOT_APPROVED | Missing timestamps remain in every required file under the ST-C3 validator |
| superseded MT5 candidate | Local MT5 terminal candidate | `tools.st_c3_download_mt5_dataset` candidate export and prior placement | UTC-normalized CSV timestamps | REJECTED_FOR_CANONICAL_APPROVAL | Partial M15 coverage, one-row M3 files, market-open H4/M15 gaps |
| `data/*.csv` legacy files | Local MT5 terminal / historical repo artifacts | `src/load_history.py` and older scripts | Mixed/legacy formatting | NOT_APPROVED_FOR_ST_C3 | Not governed by ST-C3 manifest, not canonical |

## Current Candidate Findings

- `EURUSD_H4.csv` first blocking gap: `2018-01-02T04:00:00Z`
- `EURUSD_M15.csv` first blocking gap: `2018-01-02T05:00:00Z`
- `EURUSD_M3.csv` first blocking gap: `2018-01-02T05:06:00Z`
- `GBPUSD_H4.csv` first blocking gap: `2018-01-02T20:00:00Z`
- `GBPUSD_M15.csv` first blocking gap: `2018-01-02T02:30:00Z`
- `GBPUSD_M3.csv` first blocking gap: `2018-01-02T02:33:00Z`
- HistData source archives were downloaded for `EURUSD` and `GBPUSD`
  covering 2017-2024, but source gaps and incomplete aggregation windows
  prevent approval under the current continuity contract.

## API / Provider Limitations Observed

- Candidate downloads are allowed only while the dataset manifest is
  unapproved. Once the manifest and contract are approved, the dataset is
  immutable and the MT5 downloader refuses replacement.
- HistData source timestamps are EST without daylight-saving adjustment and
  must be converted to UTC before validation.
- HistData M1 data did not satisfy the repository's strict continuity
  contract when aggregated to H4/M15/M3.
- Native MT5 M3 retrieval returned unusable current/future-range stubs in
  this environment.
- Chunked MT5 downloads improved request reliability but did not provide
  complete historical coverage.
- Exact-candle recovery cannot repair gaps when the provider does not return
  the requested timestamp.

## Authoritative Source Recommendation

Select the next owner-approved historical data provider that can deliver
complete UTC-normalized EURUSD/GBPUSD H4/M15/M3 data for 2018-2024.

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

Do not attempt replay or A3. Reject the HistData candidate for canonical
approval and try Dukascopy Historical Data Export / JForex historical data
next. After replacement, rerun:

```powershell
python -m tools.st_c3_data_integrity --data data/market/approved/st_c3 --recover --write-reports
python -m tools.st_c3_dataset_contract --contract contracts/DATASET_CONTRACT.yaml --data data/market/approved/st_c3
```
