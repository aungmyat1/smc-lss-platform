# ST-C3 Data Governance Review

## Executive Summary

Decision: **REQUIRES_MANUAL_REVIEW**
Reason: Unknown gaps remain; stop condition prevents approval or rejection-as-final.

## Methodology

All missing minutes were rederived from cached Dukascopy `.bi5` files using the existing source-integrity calendar and parser, then clustered by consecutive symbol-minute gaps.

## Dataset

ST-C3 evidence sample, EURUSD and GBPUSD, 2021-01-01 through 2025-12-31 audited cached days.

## Provider

Dukascopy tick datafeed.

## Evidence

- Total clusters: `902`
- Classification counts: `{'EXPECTED': 303, 'UNEXPECTED': 630, 'UNKNOWN': 307}`
- Calendar event counts: `{'Broker maintenance': 115, 'Daily Maintenance': 303, 'Unexpected market-open period': 822}`

## Gap Statistics

- Total missing minutes: `1240`
- Explained missing minutes: `303`
- Unexplained missing minutes: `937`
- Unknown missing minutes: `307`

## Gap Classification

Every missing minute was assigned to a cluster. Every cluster was classified as EXPECTED, UNEXPECTED, or UNKNOWN.

## Calendar Validation

Weekend, New Year, Christmas, Easter/Good Friday, daily maintenance, DST transition, broker maintenance, and unexpected market-open categories were evaluated.

## DST Validation

DST transition windows were detected with the existing source-integrity DST helper. No governance threshold was changed.

## Provider Findings

Provider evidence is incomplete for final explanation where reference data is absent or unavailable, so unknown clusters remain.

## Statistical Findings

- Original missing rate: `0.004301970580072162`
- Explained missing rate: `0.0010512073272273105`
- Effective missing rate: `0.0032507632528448517`
- Threshold: `0.001`

## Risk Assessment

Unknown gaps remain, and unexplained missing minutes exceed the approval threshold. Dataset approval and replay remain blocked.

## Recommendation

**REQUIRES_MANUAL_REVIEW**

## Decision

Dataset status: **NOT_APPROVED**
Replay status: **BLOCKED**
