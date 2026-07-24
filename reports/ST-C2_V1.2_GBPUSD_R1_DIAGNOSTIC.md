# ST-C2 v1.2 GBPUSD R1 Liquidity Diagnostic

**Scope:** S1-G2 diagnostic after the initial short M3 history produced a false zero-signal result.

## Classification

**DATA_COVERAGE_CAUSE_CONFIRMED**

The initial existence scan failed at R1 when only about nine days of M3 history were available. After extending the M1-derived M3 coverage, qualifying GBPUSD signals appear.

## Data Coverage

| TF | Bars | Range | Duplicates | Flat | Bad OHLC | Weekend Bars | Gap Count |
|---|---:|---|---:|---:|---:|---:|---:|
| htf | 5000 | 2023-05-08 08:00 -> 2026-07-24 08:00 | 0 | 0 | 0 | 0 | 172 |
| mf | 30000 | 2025-05-09 23:45 -> 2026-07-24 11:30 | 0 | 8 | 0 | 0 | 65 |
| ltf | 16642 | 2026-06-05 16:51 -> 2026-07-24 11:48 | 0 | 69 | 0 | 0 | 35 |

### Gap Examples

**htf:**
- `2023-05-12 20:00` -> `2023-05-15 00:00` = 3120 minutes
- `2023-05-19 20:00` -> `2023-05-22 00:00` = 3120 minutes
- `2023-05-26 20:00` -> `2023-05-29 00:00` = 3120 minutes
- `2023-06-02 20:00` -> `2023-06-05 00:00` = 3120 minutes
- `2023-06-09 20:00` -> `2023-06-12 00:00` = 3120 minutes
- `2023-06-16 20:00` -> `2023-06-19 00:00` = 3120 minutes
- `2023-06-23 20:00` -> `2023-06-26 00:00` = 3120 minutes
- `2023-06-30 20:00` -> `2023-07-03 00:00` = 3120 minutes
- `2023-07-07 20:00` -> `2023-07-10 00:00` = 3120 minutes
- `2023-07-14 20:00` -> `2023-07-17 00:00` = 3120 minutes

**mf:**
- `2025-05-09 23:45` -> `2025-05-12 00:00` = 2895 minutes
- `2025-05-16 23:45` -> `2025-05-19 00:00` = 2895 minutes
- `2025-05-23 23:45` -> `2025-05-26 00:00` = 2895 minutes
- `2025-05-30 23:45` -> `2025-06-02 00:00` = 2895 minutes
- `2025-06-06 23:45` -> `2025-06-09 00:00` = 2895 minutes
- `2025-06-13 23:45` -> `2025-06-16 00:00` = 2895 minutes
- `2025-06-20 23:45` -> `2025-06-23 00:00` = 2895 minutes
- `2025-06-27 23:45` -> `2025-06-30 00:00` = 2895 minutes
- `2025-07-04 23:45` -> `2025-07-07 00:00` = 2895 minutes
- `2025-07-11 23:45` -> `2025-07-14 00:00` = 2895 minutes

**ltf:**
- `2026-06-05 23:54` -> `2026-06-08 00:03` = 2889 minutes
- `2026-06-08 23:54` -> `2026-06-09 00:00` = 6 minutes
- `2026-06-09 23:54` -> `2026-06-10 00:03` = 9 minutes
- `2026-06-10 23:54` -> `2026-06-11 00:00` = 6 minutes
- `2026-06-11 23:54` -> `2026-06-12 00:03` = 9 minutes
- `2026-06-12 23:54` -> `2026-06-15 00:03` = 2889 minutes
- `2026-06-15 23:54` -> `2026-06-16 00:00` = 6 minutes
- `2026-06-16 23:54` -> `2026-06-17 00:03` = 9 minutes
- `2026-06-17 23:54` -> `2026-06-18 00:00` = 6 minutes
- `2026-06-18 23:54` -> `2026-06-19 00:00` = 6 minutes

## Liquidity-Only Scan

- H4 swing highs: `528`
- H4 swing lows: `513`
- H4 equal high/low pools at 5 pips tolerance: `2307`
- H4 sweeps at wick ratio 0.6: `87`
- Bull sweeps: `42`
- Bear sweeps: `45`

### Wick-Ratio Sensitivity

| Wick ratio | Sweep count |
|---:|---:|
| 0.2 | 430 |
| 0.3 | 332 |
| 0.4 | 238 |
| 0.5 | 161 |
| 0.6 | 87 |

## Rolling R1 Evidence

- Checked windows: `16563`
- Rejection counts: `{'R1': 10904, 'R5': 2734, 'SIGNAL': 473, 'R3': 2452}`
- Last-sweep age range in H4 bars: `0` / `29` / `71`

## Ten Rejected Window Samples

### `2026-06-05 20:48`

- H4 range: `2026-03-30 00:00` -> `2026-06-05 20:00` (300 bars)
- Sweeps in 300-bar H4 window: `4`
- Recent sweeps within max age: `0`
- Last sweep age H4 bars: `21`
- Last sweep: `{'i': 278, 'dir': 'bear', 'level': 1.3476, 'reclaim': 1.34634}`

### `2026-06-05 20:51`

- H4 range: `2026-03-30 00:00` -> `2026-06-05 20:00` (300 bars)
- Sweeps in 300-bar H4 window: `4`
- Recent sweeps within max age: `0`
- Last sweep age H4 bars: `21`
- Last sweep: `{'i': 278, 'dir': 'bear', 'level': 1.3476, 'reclaim': 1.34634}`

### `2026-06-05 20:54`

- H4 range: `2026-03-30 00:00` -> `2026-06-05 20:00` (300 bars)
- Sweeps in 300-bar H4 window: `4`
- Recent sweeps within max age: `0`
- Last sweep age H4 bars: `21`
- Last sweep: `{'i': 278, 'dir': 'bear', 'level': 1.3476, 'reclaim': 1.34634}`

### `2026-06-05 20:57`

- H4 range: `2026-03-30 00:00` -> `2026-06-05 20:00` (300 bars)
- Sweeps in 300-bar H4 window: `4`
- Recent sweeps within max age: `0`
- Last sweep age H4 bars: `21`
- Last sweep: `{'i': 278, 'dir': 'bear', 'level': 1.3476, 'reclaim': 1.34634}`

### `2026-06-05 21:00`

- H4 range: `2026-03-30 00:00` -> `2026-06-05 20:00` (300 bars)
- Sweeps in 300-bar H4 window: `4`
- Recent sweeps within max age: `0`
- Last sweep age H4 bars: `21`
- Last sweep: `{'i': 278, 'dir': 'bear', 'level': 1.3476, 'reclaim': 1.34634}`

### `2026-06-05 21:03`

- H4 range: `2026-03-30 00:00` -> `2026-06-05 20:00` (300 bars)
- Sweeps in 300-bar H4 window: `4`
- Recent sweeps within max age: `0`
- Last sweep age H4 bars: `21`
- Last sweep: `{'i': 278, 'dir': 'bear', 'level': 1.3476, 'reclaim': 1.34634}`

### `2026-06-05 21:06`

- H4 range: `2026-03-30 00:00` -> `2026-06-05 20:00` (300 bars)
- Sweeps in 300-bar H4 window: `4`
- Recent sweeps within max age: `0`
- Last sweep age H4 bars: `21`
- Last sweep: `{'i': 278, 'dir': 'bear', 'level': 1.3476, 'reclaim': 1.34634}`

### `2026-06-05 21:09`

- H4 range: `2026-03-30 00:00` -> `2026-06-05 20:00` (300 bars)
- Sweeps in 300-bar H4 window: `4`
- Recent sweeps within max age: `0`
- Last sweep age H4 bars: `21`
- Last sweep: `{'i': 278, 'dir': 'bear', 'level': 1.3476, 'reclaim': 1.34634}`

### `2026-06-05 21:12`

- H4 range: `2026-03-30 00:00` -> `2026-06-05 20:00` (300 bars)
- Sweeps in 300-bar H4 window: `4`
- Recent sweeps within max age: `0`
- Last sweep age H4 bars: `21`
- Last sweep: `{'i': 278, 'dir': 'bear', 'level': 1.3476, 'reclaim': 1.34634}`

### `2026-06-05 21:15`

- H4 range: `2026-03-30 00:00` -> `2026-06-05 20:00` (300 bars)
- Sweeps in 300-bar H4 window: `4`
- Recent sweeps within max age: `0`
- Last sweep age H4 bars: `21`
- Last sweep: `{'i': 278, 'dir': 'bear', 'level': 1.3476, 'reclaim': 1.34634}`

## Governance Decision

Do not advance to S1-G3. The next action is to review the R1 evidence and decide whether to repair data coverage, improve detector fidelity inside the frozen spec, or open a new candidate/RCR for GBPUSD rule-set calibration.

Execution, demo, live, broker, and production authority remain blocked.
