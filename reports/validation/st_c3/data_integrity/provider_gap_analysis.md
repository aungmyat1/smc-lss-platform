# ST-C3 Provider Gap Analysis

## Root Cause

The completed evidence set contains Dukascopy zero-tick missing minutes during market-open periods under the current calendar.

## Evidence

- Total missing minutes: `1240`
- Unknown minutes: `307`
- Unexpected minutes: `630`
- Effective missing rate: `0.0032507632528448517`

## Confidence

Medium. Missing minutes are reproducible from cached source files, but not every cluster has enough independent calendar/provider evidence for final explanation.

## Recommendation

**REQUIRES_MANUAL_REVIEW**
