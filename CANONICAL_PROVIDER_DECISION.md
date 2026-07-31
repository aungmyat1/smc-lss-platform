# ST-C3 Canonical Provider Decision

Date: 2026-07-31

## Decision

**OPEN_DATA_GOVERNANCE_REVIEW**

## Provider Under Review

**Dukascopy**

## Decision Scope

This is a provider qualification evidence decision only.

It does not:

- approve Dukascopy as the canonical ST-C3 v1.x provider
- approve a dataset
- update the dataset manifest to approved
- approve the dataset contract
- unblock replay
- open A3
- authorize statistical validation
- authorize demo trading
- authorize live trading

## Evidence Basis

The deterministic source-integrity sample is complete:

- Target sample days: `100`
- Cached complete deterministic sample days: `100`
- Audited cached days, including pilot evidence: `103`
- Symbols: `EURUSD`, `GBPUSD`
- Coverage window: `2021-01-01` through `2025-12-31`

The statistical source-integrity report found:

- Total expected minutes: `288240`
- Total missing market-open minutes: `1240`
- Missing-minute rate: `0.004301970580072162`
- 95% confidence interval: `0.004069558281261814` to `0.004547595328160722`
- Pre-registered threshold: `0.001`

Because the observed missing-minute rate exceeds the threshold, Dukascopy is
not approved for canonical ST-C3 v1.x dataset construction at this time.

## Final Provider Qualification Recommendation

Provider qualification result: **OPEN_DATA_GOVERNANCE_REVIEW**

Next step: review Dukascopy source suitability and contract compatibility
using the completed source-integrity evidence before any provider freeze,
dataset approval, replay, A3, demo, or live trading action.
