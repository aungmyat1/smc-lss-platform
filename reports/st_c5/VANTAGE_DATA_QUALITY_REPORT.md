# ST-C5.1 Vantage MT5 Data Quality Report

Decision: **REJECT_DATASET**

Reason: unchanged ST-C3 integrity inspection is blocked

## Coverage

- Symbols: `['EURUSD', 'GBPUSD']`
- Timeframes: `['H4', 'M15', 'M3']`
- Date range observed: `{'from': '2021-01-04T00:00:00Z', 'to': '2025-12-31T23:57:00Z'}`

## Integrity Metrics

- ST-C3 result: `BLOCKED`
- Missing timestamps: `179`
- Duplicate timestamps: `0`
- Issue counts: `{'CSV_COVERAGE': 4}`

## Normalization

- Normalization status: `PASS`
- Timezone: `UTC`
- Source: `Vantage MT5`

## Risk Assessment

The broker candidate cannot be approved because unchanged ST-C3 integrity inspection is blocked. Replay and downstream validation remain blocked.
