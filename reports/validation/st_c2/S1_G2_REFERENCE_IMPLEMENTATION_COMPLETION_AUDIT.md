# ST-C2 v1.2 GBPUSD S1-G2 Reference Implementation Completion Audit

**Date:** 2026-07-24
**Repository:** `D:\ddev\smc-lss-platform`
**Branch:** `master`
**HEAD:** `49e957a84ebad34d19c4254aee2dee99421677c0`
**Origin relationship at audit start:** `origin/master...HEAD = 0 behind / 0 ahead`
**Strategy:** ST-C2 v1.2.0
**Market scope:** GBPUSD
**Gate:** A2 / S1-G2 Reference Implementation Completion Review

## Verdict

**S1-G2 REMAINS OPEN**

The reference implementation satisfies the minimum existence floor, but direct
repository evidence does not prove faithful coverage of the frozen ST-C2 v1.2.0
strategy contract. Do not authorize A2/S1-G3 yet.

## Frozen-Spec Identity

The active frozen contract is `specs/st-c2_v1.2.0.yaml`. It identifies
`id: ST-C2`, `version: 1.2.0`, `status: frozen`, and
`implementation_authorization: scoped_reference_implementation_granted` at
lines 23-29. It also states that `engine_implements_spec: false` at line 28.

## Current Lifecycle Status

`CLAUDE.md` lines 36-54 and `MASTER_PLAN.md` lines 52-70 place the project in
Stage A / A2 at S1-G2, with A3 and execution/demo/production blocked.

## Reproduced Existence Signal

Command run:

```text
python -m validation.run_st_c2_gbp_existence
```

Result from `reports/ST-C2_V1.2_GBPUSD_EXISTENCE_CHECK.md`:

- Verdict: `SIGNAL_FOUND`
- Checked windows before first signal: `1365`
- First signal time: `2026-06-10 17:15`
- Direction: `short`

Data hashes:

| File | SHA256 |
|---|---|
| `data/GBPUSD_H4.csv` | `46B642EAD3C7FBBB839FCC0609FE9C2082C2732F4573DDE813987CFDD10C50FE` |
| `data/GBPUSD_M15.csv` | `DBAE313BEBB714A8C813995B541E30DFEE4DDD2AEB05243E61FB0653154E0BB8` |
| `data/GBPUSD_M3.csv` | `05F302868ACE44FF8C04BD2438FE598AE5A5D6ABAF0092655E87CB417BB851C2` |

This signal is evidence of existence only. It is not profitability, edge, A2
completion, A3 authorization, or execution authorization.

## Rule-Coverage Summary

Detailed machine-readable inventory:
`reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json`.

| Metric | Value |
|---|---:|
| Total frozen rules inventoried | 45 |
| Implemented rules | 7 |
| Tested rules | 6 |
| Positive-case coverage | 5 |
| Negative-case coverage | 2 |
| Boundary-case coverage | 0 |
| Missing rule-test mappings | 37 |
| S1-G2 completion eligible | false |

The current `specs/st_c2/rule_to_test_map.yaml` acceptance value
`missing_rule_test_mappings: 0` is not supported by this audit.

## Critical Conformance Findings

### 1. Bias Conformance Fails

Frozen contract evidence:

- `specs/st-c2_v1.2.0.yaml:88` says bull/bear classification uses
  `htf_bos_and_choch_only`.
- `specs/st-c2_v1.2.0.yaml:90` requires `bias_evidence_timestamp`.

Implementation evidence:

- `validation/st_c2_reference.py:124` defines `_bias_from_sweep()`.
- `_bias_from_sweep()` returns `long` for a bull sweep and `short` otherwise.

Finding: equating liquidity-sweep direction with HTF BOS/CHoCH bias is not
authorized by the frozen contract. Minimum HTF structural bias logic is missing.

### 2. Dealing Range / OTE Is Partial

Frozen contract evidence:

- `specs/st-c2_v1.2.0.yaml:149-153` requires the dealing range to come from
  liquidity-stage external liquidity and freeze at the triggering swing.

Implementation evidence:

- `validation/st_c2_reference.py:128` defines `_in_discount_or_premium()`.
- The function uses the max high and min low of the full MF window.

Finding: the implementation does not preserve triggering range identity, frozen
range policy, anchoring invalidation, stale-range handling, or boundary tests.

### 3. FVG Conformance Is Partial And Has Hardcoded Precision

Frozen contract evidence:

- `specs/st-c2_v1.2.0.yaml:164-203` defines HTF/MF/LTF FVG age, overlap,
  confluence, invalidation, tie-breaking, rounding, and wick-to-wick geometry.

Implementation evidence:

- `validation/st_c2_reference.py:136` defines `_matching_mf_fvg()`.
- `validation/st_c2_reference.py:138` hardcodes `points * 0.00001`.

Finding: fixed wick-to-wick geometry is partially delegated to `smc_engine.fvgs`,
but confluence-chain, freshness, invalidation, tie-break, rounding, and approved
GBPUSD point metadata are missing.

### 4. LTF Confirmation Is Partial

Frozen contract evidence:

- `specs/st-c2_v1.2.0.yaml:205-220` requires internal BOS, closed-candle break,
  displacement body ratio, stronger CHoCH constraints, max setup age, and first
  qualifying bar.

Implementation evidence:

- `validation/st_c2_reference.py:143` defines `_ltf_confirmation()`.
- `validation/st_c2_reference.py:144` hardcodes `k=2`.

Finding: the implementation checks only the last close against a prior swing. It
does not return the required structured event evidence, enforce internal BOS,
displacement, first qualifying bar, max setup age, or pre-sweep rejection.

### 5. State Machine Is Missing

The frozen sequence spans liquidity, bias, OTE, FVG alignment, LTF confirmation,
entry, stop, target, risk, management, rejection, and dedup rules. No
deterministic state model exists for states such as `BIAS_ELIGIBLE`,
`SWEEP_DETECTED`, `POI_ACTIVE`, `CONFIRMATION_VALID`, `TRADE_PLAN_READY`,
`INVALIDATED`, or `EXPIRED`.

### 6. Trade Plan Is Missing

Frozen contract evidence:

- `specs/st-c2_v1.2.0.yaml:225-288` defines entry, stop, target, cost profile,
  gross/net reward, and risk gates.

Implementation evidence:

- `validation/st_c2_reference.py:37-43` defines `DetectionResult` with only
  decision, symbol, direction, rejection code, stages, and signal time.

Finding: no research-only logical trade plan exists. Entry, SL, target, gross R,
net R, cost profile, target hierarchy, stop bounds, and expiration are not
proven.

### 7. Rejection-Code Coverage Is Incomplete

Frozen contract evidence:

- `specs/st-c2_v1.2.0.yaml:359-371` records R1-R7 and explicitly notes missing
  distinct mappings for stop invalidity, insufficient net-R, missing cost
  profile, and missing target.

Implementation evidence:

- `validation/st_c2_reference.py:171-196` returns R6/R1/R3/R4/R5 only.

Finding: the known coverage gap is not resolved or formally mapped with
subcodes. Negative cases do not assert the missing failure modes.

### 8. Stable Identifiers Are Missing

Frozen contract evidence:

- `specs/st-c2_v1.2.0.yaml:112-114` requires SHA-256 stable identifiers for
  liquidity pool tie-breaks.
- `specs/st-c2_v1.2.0.yaml:398-403` defines dedup identity.

Finding: no stable IDs are implemented for liquidity pools, structural events,
sweeps, FVGs, confirmations, signals, or trade plans.

### 9. Golden-Case Library Is Not Yet Sufficient

Existing tests use inline arrays in `tests/test_st_c2_reference.py:17-53`.
They cover a small positive/mirror/no-liquidity/determinism slice, but not a
versioned golden-case library with expected primitives, events, state
transitions, trade-plan fields, R values, identifiers, and rejection behavior.

## Completed Fixes During This Audit

- Reproduced the GBPUSD existence result from current local files.
- Created `A2_RULE_COVERAGE_MATRIX.json`.
- Created `A2_CONFORMANCE_RESULTS.json`.
- Created this S1-G2 completion audit.
- Updated governance/status artifacts to keep S1-G2 open.

## S1-G2 Blocking Gaps

1. Implement HTF BOS/CHoCH structural bias separately from liquidity sweep
   direction.
2. Implement structural dealing-range identity and OTE lifecycle.
3. Replace hardcoded point conversion with approved GBPUSD metadata.
4. Complete FVG confluence, age, invalidation, tie-break, and rounding rules.
5. Complete LTF confirmation evidence and tests.
6. Add deterministic state-machine evidence and tests.
7. Add research-only logical trade-plan object and conformance tests.
8. Resolve R1-R7 detailed reason coverage for stop/net-R/cost/target failures.
9. Add stable identifiers and determinism tests.
10. Build a versioned golden-case library.
11. Correct rule-to-test traceability so missing mappings are not reported as
    zero until proven.

## Gate Decision

```text
S1-G2 REMAINS OPEN
```

Exact next milestone:

```text
S1-G2 Gap Closure — HTF Bias, OTE, FVG, LTF Evidence, State, Trade Plan,
Rejection Subcodes, Stable IDs, and Golden-Case Contract
```

A3 historical/statistical validation, execution, demo, live, broker
integration, and production promotion remain blocked.
