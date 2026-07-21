# Phase A Stop Report

Decision: `BLOCKED`

## Repository

- Branch: `research/st-c1-baseline-runner-v2-clean`
- HEAD: `d521cdd3e997b1a900c5f0ecf558194921e6cb5c`
- Merge base: `d521cdd3e997b1a900c5f0ecf558194921e6cb5c`
- Ahead/behind: `0/0`
- Merge-base ref: `origin/research/st-c1-baseline-runner-v2-clean`
- Code tree SHA: `3fb17c32c20231e80bd79e452e196357d1a82e05`
- Strategy contract SHA256: `21f874e75b4864aa0e35f8c3510e7aa925adb08b21e14e2efb405ee2e12f481e`
- Research spec SHA256: `11f6efcc816723c7b3de91cf0b7af62fffca68110b0f67c9bab3c71049568cf1`
- Cost profile SHA256: `3515706b655d6f0e534b3878204482b310f8103ab2a4247d4b660a48fd40ceb2`

## Validation Status

- Full suite status: `blocked`
- CI status: `unknown`
- Coverage complete: `False`
- Clean runs match: `True`
- Resumed run supplied: `True`

### Decision Reasons
- Full suite status is 'blocked'.
- CI status is 'unknown'.
- Required dataset coverage is incomplete or invalid.

## Changed Files

### Replay
- none

### Data
- none

### Artifacts
- none

### Tests
- none

### Ci
- none

### Docs
- none

## Required Coverage

| Symbol | Timeframe | Status | Source Symbol | Path | Rows | Validation |
|---|---|---|---|---|---|---|
| EURUSD | M5 | valid | EURUSD | data\EURUSD_M5.csv | 80000 | ok |
| EURUSD | H1 | valid | EURUSD | data\EURUSD_H1.csv | 9000 | ok |
| EURUSD | D1 | valid | EURUSD | data\EURUSD_D1.csv | 500 | ok |
| GBPUSD | M5 | missing |  |  |  | missing required dataset |
| GBPUSD | H1 | missing |  |  |  | missing required dataset |
| GBPUSD | D1 | missing |  |  |  | missing required dataset |
| XAUUSD | M5 | valid | XAUUSD-VIP | data\XAUUSD-VIP_M5.csv | 80000 | ok |
| XAUUSD | H1 | valid | XAUUSD-VIP | data\XAUUSD-VIP_H1.csv | 9000 | ok |
| XAUUSD | D1 | valid | XAUUSD-VIP | data\XAUUSD-VIP_D1.csv | 500 | ok |

## Reproducibility

| Check | Result |
|---|---|
| clean manifest raw hash | False |
| clean manifest normalized | True |
| clean latest normalized | True |
| clean metrics | True |
| clean trades hash | True |
| clean management hash | True |
| clean rejected hash | True |
| clean equity hash | True |
| resumed manifest raw hash | False |
| resumed manifest normalized | True |
| resumed latest normalized | True |
| resumed metrics | True |
| resumed trades hash | True |
| resumed management hash | True |
| resumed rejected hash | True |
| resumed equity hash | True |

## Trade Cost Reconciliation

| Check | Value |
|---|---|
| trade_count | 243.0 |
| gross_r | -1.881703 |
| net_r | -94.657647 |
| spread_r | 74.010183 |
| slippage_r | 18.765759 |
| commission_r | 0.0 |
| swap_r | 0.0 |
| total_cost_drag_r | 92.775942 |
| gross_minus_cost_minus_net_r | 2e-06 |
| component_minus_cost_drag_r | 0.0 |
| max_trade_gross_net_residual_r | 8.795000001615705e-07 |
| max_trade_component_residual_r | 1.0000023031864202e-10 |

## Cost Breakdown

| Check | Value |
|---|---|
| trade_count | 243.0 |
| gross_r | -1.881703 |
| net_r | -94.657647 |
| spread_r | 74.010183 |
| slippage_r | 18.765759 |
| commission_r | 0.0 |
| swap_r | 0.0 |
| total_cost_drag_r | 92.775942 |
| reported_gross_r | -1.881703 |
| reported_net_r | -94.657647 |
| reported_spread_r | 74.010183 |
| reported_slippage_r | 18.765759 |
| reported_commission_r | 0.0 |
| reported_swap_r | 0.0 |
| reported_total_cost_drag_r | 92.775946 |

## Safety Statement

No strategy parameters were optimized.
No broker orders were sent.
Live trading remains disabled.
