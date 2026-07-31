# ST-C4 Canonical Data Specification

## Scope

- Strategy family: ST-C3/ST-C4 validation data only.
- Symbols: EURUSD and GBPUSD.
- Required timeframes: M3, M15, H4, derived from a single provider.
- Historical depth: 2021-01-01 through 2025-12-31 minimum for ST-C3 replay readiness.
- Timestamp precision: source precision preserved; canonical bars use UTC minute timestamps.
- Timezone policy: all normalized data must be UTC. Source timezone conversions must be documented and reproducible.
- DST handling: provider session shifts must be explicitly encoded in metadata and validated against source documentation.
- Weekend handling: no fabricated weekend bars; market-open expectations must follow documented FX trading week.
- Holiday handling: New Year, Christmas, Good Friday/Easter, broker holidays, and provider-specific closures must be classified.
- Corporate action policy: not applicable to spot FX EURUSD/GBPUSD.
- Missing-data tolerance: effective unexplained missing-minute rate must be below 0.001 and unknown gaps must be zero before ST-C3 readiness.
- Storage format: immutable raw source files, normalized CSV/parquet-compatible schema, processed timeframe bars, metadata, and checksums.

## Canonical Schema

`timestamp,symbol,open,high,low,close,volume,spread,provider,timezone,session`

## Governance

The rejected ST-C3 Dukascopy dataset remains archived and immutable. No replay,
statistical validation, demo, or live trading stage may be unlocked by ST-C4
benchmark artifacts alone.
