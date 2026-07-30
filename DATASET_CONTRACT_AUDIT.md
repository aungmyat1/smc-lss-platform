# ST-C3 Dataset Contract Audit

Status: **AUDITED / BLOCKED PENDING CANONICAL DATASET**

Audit date: 2026-07-30

## Contract Reviewed

`contracts/DATASET_CONTRACT.yaml`

## Mandatory Scope

| Requirement | Contract Value | Notes |
|---|---|---|
| Strategy | `ST-C3` | Frozen strategy line |
| Spec version | `1.0.7` | Contract must not drift to draft v1.0.8 |
| Dataset version | `Dataset_v0.1_blocked_candidate` currently; target `Dataset_v1.0` after acquisition | Current candidate remains blocked |
| Approval status | `NOT_APPROVED` | Replay must remain blocked |
| Integrity status | `BLOCKED` | Existing validators enforce this |
| Replay status | `BLOCKED` | Must not unlock until approval succeeds |
| Timezone | UTC | Source data must be normalized to UTC |
| Symbols | `EURUSD`, `GBPUSD` | XAUUSD is excluded by frozen ST-C3 v1.0.7 |
| Timeframes | `H4`, `M15`, `M3` | M3 is required by ST-C3 LTF evidence |
| Coverage start | `2018-01-01` | Full requested range must be covered |
| Coverage end | `2024-12-31` | Full requested range must be covered |

## Required Files

- `EURUSD_H4.csv`
- `EURUSD_M15.csv`
- `EURUSD_M3.csv`
- `GBPUSD_H4.csv`
- `GBPUSD_M15.csv`
- `GBPUSD_M3.csv`

## Required CSV Schema

The validator requires:

- `time`
- `open`
- `high`
- `low`
- `close`
- `volume`

Optional governed columns:

- `session`
- `news_flag`

## Session Definitions

The manifest and loader require:

- London: `07:00` to `10:00` UTC
- New York: `13:00` to `16:00` UTC

If a `session` column is present, values must be one of:

- `LONDON`
- `NY`
- `OTHER`
- empty string

## Weekend And Holiday Handling

The repository validator permits missing bars only during approved
market-closed windows as implemented in `validation/st_c3/dataset_loader.py`.

Current logic:

- Saturday: market closed
- Sunday: market closed
- Friday after or equal to 22:00 UTC: market closed
- Fixed holidays: January 1 and December 25

Ambiguity:

- The contract does not separately enumerate early closes, bank holidays,
  provider maintenance windows, DST transition policy, or Christmas/New Year
  multi-day thin-market closures.
- This ambiguity must not be resolved by changing the contract during this
  sprint. Providers must satisfy the current validator as written.

## DST Assumptions

The contract requires UTC-normalized timestamps and does not allow
provider-local DST drift in final CSVs.

Ambiguity:

- The contract does not specify a provider-source timezone conversion policy.
  Each acquisition adapter must document source timezone and deterministic
  conversion to UTC before validation.

## Aggregation Rules

The contract does not explicitly require broker-native H4/M15/M3 bars.

The validator requires deterministic fixed spacing and valid OHLCV. Therefore
derived bars are acceptable only if:

- source data is complete enough to build every required bar
- aggregation is deterministic
- no incomplete aggregation window is emitted
- no missing market-open candles remain
- OHLC values obey the repository validator

## Manifest Requirements

The manifest at `data/market/approved/st_c3/DATASET_MANIFEST_ST_C3.yaml`
must contain:

- `approved`
- `approval_status`
- `approval_date`
- `approved_by`
- `spec_version`
- `symbols`
- `timeframes`
- `coverage`
- `files`
- `sessions`
- `symbol_metadata`

The manifest may not claim approval while the dataset contract is blocked.

## Checksum Requirements

Each manifest file entry must include a SHA-256 checksum after validation
passes. Manifest hashes must not be regenerated as approved release hashes
while integrity remains blocked.

## Approval Requirements

Approval requires:

- all six required files present
- zero duplicate timestamps
- strict chronological ordering
- fixed timeframe spacing except allowed market closures
- valid OHLC geometry
- non-negative volume
- full requested coverage
- SHA-256 consistency
- dataset contract approved
- replay remains prohibited unless approved

## Expected Candle Counts

The contract currently records `BLOCKED_PENDING_CANONICAL_PROVIDER_EXPORT`
for expected rows.

Ambiguity:

- Exact expected row counts are not precomputed in the contract because they
  depend on the validator's market-closed calendar and the selected
  provider's availability.
- Counts must be populated only after a provider candidate passes integrity
  validation and manifest generation.

## Audit Conclusion

The dataset contract is sufficiently strict for provider qualification.
The remaining ambiguity is operational: exact row counts, provider-source
timezone conversion, and exceptional market closures are not separately
enumerated in the contract. No contract change is authorized in this sprint.
