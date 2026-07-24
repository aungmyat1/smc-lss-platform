# ST-C2 v1.2 GBPUSD Existence Check

**Scope:** S1-G2 reference implementation existence scan for frozen `specs/st-c2_v1.2.0.yaml`.

## Data Availability

- htf: `data\GBPUSD_H4.csv` - present
- mf: `data\GBPUSD_M15.csv` - present
- ltf: `data\GBPUSD_M3.csv` - present

## Verdict

**SIGNAL_FOUND**

Checked windows: `1365`

First signal time: `2026-06-10 17:15`
Direction: `short`

The S1-G2 minimum existence floor (`>=1`) is satisfied by the reference scan.

## Data Provenance

- `data/GBPUSD_H4.csv`: exported from the local MT5 terminal via `src/load_history.py`.
- `data/GBPUSD_M15.csv`: exported from the local MT5 terminal via `src/load_history.py`.
- `data/GBPUSD_M3.csv`: derived from complete contiguous `GBPUSD_M1` groups because the terminal rejected native `TIMEFRAME_M3` with invalid params.
- Temporary `GBPUSD_M1.csv` and `GBPUSD_M30.csv` helper files were removed after derivation.

## Authorization Boundary

This report does not authorize execution, demo trading, live trading, broker integration, or production promotion.
