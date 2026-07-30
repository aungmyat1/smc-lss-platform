# ST-C3 Timeframe Requirements Report

Status: **VERIFIED**

Date: 2026-07-30

## Required Timeframes

Frozen ST-C3 v1.0.7 requires:

- `H4`
- `M15`
- `M3`

## Technical Evidence

ST-C3 v1.0.7 uses:

- H4 for HTF bias, macro structure, HTF liquidity, and sweep context
- M15 for sweep, displacement, BOS, dealing range, OTE, FVG/OB, and target
  evidence
- M3/M1 for LTF confirmation, session gatekeeper, entry window, invalidation
  swing, and expiry evidence

Repository evidence:

- `specs/st-c3_v1.0.7.yaml` defines `timeframes.htf: H4`,
  `timeframes.mf: M15`, and `timeframes.ltf: [M3, M1]`.
- `validation/st_c3/evidence_builder.py` documents H4, M15, and M3/M1
  evidence inputs.
- `validation/st_c3/dataset_loader.py` currently requires
  `EXPECTED_TIMEFRAMES = {"H4", "M15", "M3"}`.

## M3 Requirement

M3 is fundamental to the frozen ST-C3 v1.0.7 dataset contract because the
current replay/dataset loader expects an M3 file for each approved symbol.

The strategy does not require broker-native M3 candles specifically.

M3 can be deterministically generated from complete M1 data if:

- every minute in the M3 aggregation window exists
- aggregation windows align to UTC minute multiples divisible by 3
- open is the first M1 open
- high is the max M1 high
- low is the min M1 low
- close is the last M1 close
- volume is the sum of M1 volumes
- incomplete windows are rejected, not filled
- the resulting file passes the unchanged ST-C3 validator

## Verification

`tools/st_c3_acquire_histdata_dataset.py` implements deterministic M1 to M3
aggregation.

`tests/test_st_c3_market_data_acquisition.py` verifies that:

- only complete three-minute windows are emitted
- OHLCV aggregation is deterministic
- incomplete source windows are dropped instead of fabricated

`tools/st_c3_verify_dukascopy_provider.py` verifies that a limited
Dukascopy tick sample can reconstruct complete M1 bars for sampled UTC
hours. Complete M1 bars can then serve as a deterministic basis for M3,
M15, and H4 construction.

## Recommendation For Future Dataset Guidance

Do not require broker-native M3 in future acquisition guidance.

Allow M3 to be derived from complete M1 or tick data, provided the derived
M3 files pass the frozen dataset contract and existing integrity validator.

Do not modify the current frozen contract during this sprint.
