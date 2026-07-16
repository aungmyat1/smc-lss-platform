---
name: optimization
description: >-
  Parameter optimization with overfit guards. Trigger on 'optimize', 'parameter
  sweep', 'tune'.
---

# optimization

## Purpose
Search parameters on in-sample data and guard against overfitting via out-of-sample checks.

## Inputs
- parameter grid
- in-sample / out-of-sample split

## Outputs
- ranked parameter sets with IS and OOS metrics; recommended robust set

## Workflow
1. Define grid.
2. Evaluate each on in-sample.
3. Re-evaluate top sets on out-of-sample.
4. Prefer stable (IS~OOS) over peak IS.

## Decision rules
- Reject params that shine IS but degrade OOS.
- Fewer parameters preferred (robustness).

## Validation checklist
- [ ] IS/OOS split honored
- [ ] OOS reported for every recommendation

## Failure handling
- Only IS improvement -> reject as overfit.
- Tiny sample -> inconclusive.

## Examples
Grid over swing-lookback {2,3,4}: lookback 3 best OOS PF 1.4 vs IS 1.5 => robust choice.

## Acceptance criteria
- [ ] Recommends a set with OOS support
- [ ] overfit flagged explicitly
