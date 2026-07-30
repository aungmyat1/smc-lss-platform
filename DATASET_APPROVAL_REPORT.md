# ST-C3 Dataset Approval Report

Status: **NOT_APPROVED**

Date: 2026-07-30

## Dataset Candidate

Dataset version target: `Dataset_v1.0`

Current candidate source: HistData.com Generic ASCII M1, normalized to UTC and
derived into H4, M15, and M3.

## Approval Gate Result

The dataset is **not approved**.

Reason:

The HistData-derived candidate fails the existing ST-C3 data integrity
validator. Missing candles remain in every required symbol/timeframe file.

First blocking failure:

`EURUSD_H4.csv` missing `2018-01-02T04:00:00Z`

## Manifest

Manifest path:

`data/market/approved/st_c3/DATASET_MANIFEST_ST_C3.yaml`

Manifest status:

`approved: false`

`approval_status: NOT_APPROVED`

Manifest hashes were not regenerated as approved release hashes because
integrity validation failed.

## Contract

Contract path:

`contracts/DATASET_CONTRACT.yaml`

Contract status: **BLOCKED**

Replay status: **BLOCKED**

## Replay Readiness

Replay is **not ready**.

Statistical validation remains locked until replay completes.

Demo and live trading remain locked.

## Governance Statement

No strategy rules, detection logic, replay logic, statistical calculations,
validation rules, or approval gates were modified.

No candles were fabricated, interpolated, forward-filled, back-filled, or
manually edited.

## Required Next Action

Reject the HistData candidate for canonical approval and attempt the next
authoritative source: Dukascopy Historical Data Export / JForex historical
data. If that source also fails continuity validation, escalate to a paid
institutional provider or owner-approved broker export.
