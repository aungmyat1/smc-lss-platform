# ST-C3 Data Recovery Log

Recovery attempted: **True**

Final status: **BLOCKED**

Reason: EURUSD_H4.csv missing candle 2018-12-26T00:00:00Z

## Attempts

- `BLOCKED` EURUSD H4 2018-12-26T00:00:00Z: approved source did not return the exact missing candle
- `BLOCKED` EURUSD H4 2019-01-02T00:00:00Z: approved source did not return the exact missing candle
- `BLOCKED` EURUSD H4 2019-12-26T00:00:00Z: approved source did not return the exact missing candle
- `BLOCKED` EURUSD H4 2020-01-02T00:00:00Z: approved source did not return the exact missing candle
- `BLOCKED` EURUSD H4 2022-12-26T00:00:00Z: approved source did not return the exact missing candle
- `BLOCKED` EURUSD H4 2022-12-26T04:00:00Z: approved source did not return the exact missing candle
- `BLOCKED` EURUSD H4 2023-01-02T00:00:00Z: approved source did not return the exact missing candle
- `BLOCKED` EURUSD M15 2022-12-26T00:00:00Z: approved source did not return the exact missing candle
- `BLOCKED` EURUSD M15 2022-12-26T00:15:00Z: approved source did not return the exact missing candle
- `BLOCKED` EURUSD M15 2022-12-26T00:30:00Z: approved source did not return the exact missing candle
- `BLOCKED`   : recovery capped at 10 gaps; 136 gaps not attempted

## Guardrail

No candles were fabricated or interpolated. Only exact candles returned by the approved source may be merged.

## Required Data Source

A complete owner-approved EURUSD/GBPUSD H4/M15/M3 historical dataset covering 2018-01-01 through 2024-12-31.
