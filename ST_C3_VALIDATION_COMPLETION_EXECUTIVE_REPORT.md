# ST-C3 Validation Completion Executive Report

Date: 2026-07-31

## 1. Repository Status

ST-C3 strategy, strategy contract, rule engine, detection engine, replay
engine, dataset contract, dataset governance, session calendar qualification,
and aggregation validation remain frozen or complete per the current governance
state. No strategy, replay, statistical formula, approval gate, dataset
contract, or governance weakening changes were made in this sprint.

## 2. Validation Progress

Provider qualification evidence collection was completed using the existing
guardrailed Dukascopy source-integrity acquisition pipeline:

- Deterministic target sample days: `100`
- Completed deterministic sample days: `100`
- Remaining deterministic sample days: `0`
- Failed source hours in final acquisition batch: `0`
- Parallel workers used: `8`
- Source-integrity acquisition artifact:
  `reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_SAMPLE_ACQUISITION.json`

The statistical source-integrity report was regenerated after completing the
sample:

- Statistically sufficient: `true`
- Audited cached days: `103`
- Total expected minutes: `288240`
- Total missing market-open minutes: `1240`
- Missing-minute rate: `0.004301970580072162`
- 95% confidence interval: `0.004069558281261814` to `0.004547595328160722`
- Pre-registered threshold: `0.001`
- Statistical artifact:
  `reports/validation/st_c3/data_integrity/SOURCE_INTEGRITY_STATISTICAL_REPORT.json`

## 3. Provider Qualification Decision

**OPEN_DATA_GOVERNANCE_REVIEW**

Dukascopy cannot be accepted as the canonical ST-C3 v1.x provider in the
current gate state because the measured missing-minute rate exceeds the
pre-registered threshold.

Root-cause distribution:

- `ROLLOVER_ZERO_TICK`: `773`
- `OFF_SESSION_ZERO_TICK`: `458`
- `PRIMARY_SESSION_ZERO_TICK`: `9`

Cross-source comparison for sampled missing observations:

- Observations checked: `200`
- Reference present: `151`
- Reference absent: `49`

## 4. Dataset Approval Status

Dataset Approval: **NOT_APPROVED**

No canonical provider approval was generated. No provider was frozen. No
canonical 2021-01-01 through 2025-12-31 dataset was built or approved.

## 5. Replay Status

Replay: **BLOCKED**

Replay remains blocked because dataset approval is still `NOT_APPROVED`.

## 6. Statistical Validation Summary

Strategy statistical validation was not run. It remains blocked until one
canonical dataset is approved and replay is unlocked through the existing
gates.

## 7. Remaining Risks

- Dukascopy source suitability is unresolved under the completed 100-day
  evidence sample.
- Missing market-open minutes exceed the pre-registered threshold.
- A small number of missing minutes occur during primary trading sessions.
- Dataset approval, replay, robustness testing, walk-forward validation, demo
  promotion, and live review are all blocked by the provider evidence decision.

## 8. Recommendation

**OPEN_DATA_GOVERNANCE_REVIEW**
