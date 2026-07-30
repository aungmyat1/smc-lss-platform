# ST-C3 Dataset Contract Review

Status: **BLOCKED**

Reason: current contract requires missing timestamps to block approval, but source evidence shows market-open zero-tick minutes

Recommendation: **OPEN_GOVERNANCE_CHANGE_REQUEST**

Guardrail: Dataset Contract Review does not change the contract, approve data, fill candles, or open replay.

## Current Contract Policy

- Dataset version: `Dataset_v1.0_5Y`
- Approval status: `NOT_APPROVED`
- Replay status: `BLOCKED`
- Missing timestamps check: `required`
- Allowed gap policy: `weekend_and_fixed_holiday_only`

## Evidence

- Zero-tick probe count: `3`
- Aggregation mismatch count: `0`

| Symbol | Timestamp | Verdict | Fresh Dukascopy | HistData Present |
|---|---|---|---|---|
| `EURUSD` | `2021-01-04T22:45:00Z` | `DUKASCOPY_AND_REFERENCE_ABSENT` | `MATCHED_CACHE` | `False` |
| `EURUSD` | `2021-01-04T22:46:00Z` | `DUKASCOPY_AND_REFERENCE_ABSENT` | `MATCHED_CACHE` | `False` |
| `GBPUSD` | `2021-01-04T22:19:00Z` | `DUKASCOPY_AND_REFERENCE_ABSENT` | `MATCHED_CACHE` | `False` |

## Options

- `retain_strict_contract`: Keep requiring every market-open timeframe candle. Dukascopy tick-derived data remains unsuitable unless a provider supplies complete bars. Governance impact: no rule change.
- `define_zero_tick_candle_policy`: Open a governance change to define deterministic candles for zero-tick minutes, with explicit evidence and owner approval. Governance impact: contract and validator change required.
- `select_bar_provider`: Use an authoritative M1/bar provider that emits complete zero-volume or carry-forward bars under a documented methodology. Governance impact: provider qualification and dataset contract evidence required.

## Required Decision

Owner/governance must choose a contract policy before five-year production acquisition continues.
No candles were fabricated, interpolated, or manually inserted.
