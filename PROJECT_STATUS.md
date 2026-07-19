# PROJECT_STATUS.md — SMC-LSS Platform

**Audit date:** 2026-07-19
**Status:** Configuration governance complete; statistical validation scaffold ready
**Current milestone:** Statistical Validation (M2.3)

This status file reflects the current repository state after the governance audit
and loader hardening work. It supersedes the older audit snapshot that described
the config subsystem as incomplete.

---

## 1. What is complete

### Configuration governance layer

Verified in code and tests:

- `src/config.py` is the single authoritative configuration boundary.
- `src/daily_runner.py` consumes the immutable config object only.
- Duplicate YAML parsing was removed from the runner layer.
- Governance metadata is exposed for audit:
  - `schema_version`
  - `config_version`
  - `registry_version`
  - `config_hash`
  - `strategy_spec`
  - `research_spec`
- The loader fails closed on:
  - missing files
  - missing required keys
  - invalid types
  - unknown keys
  - unsupported schema versions
  - incompatible config/registry versions
  - path mismatches for the loaded strategy spec
- Runtime config objects are immutable.
- End-to-end governance validation passes.

### Validation evidence

- `python -m pytest tests/test_config.py tests/test_daily_runner.py tests/test_strategy_contract_validator.py tests/test_historical_replay.py tests/test_statistical_validation.py -q`
  - Result: `34 passed`
- `python -m py_compile src/config.py src/daily_runner.py validation/strategy_contract_validator.py validation/performance_metrics.py validation/historical_replay_engine.py validation/statistical_validation.py tests/test_config.py tests/test_daily_runner.py tests/test_strategy_contract_validator.py tests/test_historical_replay.py tests/test_statistical_validation.py`
  - Result: passed
- `git diff --check`
  - Result: passed

---

## 2. Current architecture posture

### Approved-strategy preparation

The platform is now prepared for deterministic strategy approval work:

- Source strategy: `docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md`
- Execution-track authority: `specs/v1.yaml`
- Research-track authority: `specs/v3.6.yaml`
- Governance contract: frozen and audited
- Candidate contract: `strategies/candidates/ST-C1_v1.yaml`

### M1 complete

The M1 normalization deliverables are complete:

- `strategies/candidates/ST-C1_v1.yaml`
- `research/ST-C1_RESEARCH_CONTRACT.md`
- `reports/ST-C1_NORMALIZATION_REPORT.md`

### Execution posture

- Demo/live execution remains blocked until the approved strategy contract and
  execution-layer gates are implemented.
- `daily_runner.py` remains propose-mode only.
- No new trading logic was introduced during the governance completion step.

---

## 3. What still needs to happen next

### M2 — Strategy approval and validation

Now that the contract exists, validate it with closed-candle-only backtesting,
out-of-sample checks, walk-forward tests, and approval-gate evidence.

### M2.1 complete

The mechanical validation scaffold is now in place:

- `validation/strategy_contract_validator.py`
- `tests/test_strategy_contract_validator.py`
- `reports/ST-C1_CONTRACT_VALIDATION_REPORT.md`

### M2.2 complete

The historical replay scaffold is now in place:

- `validation/historical_replay_engine.py`
- `validation/performance_metrics.py`
- `tests/test_historical_replay.py`
- `reports/ST-C1_BASELINE_BACKTEST_REPORT.md`

### M2.3 complete

The statistical validation scaffold is now in place:

- `validation/statistical_validation.py`
- `tests/test_statistical_validation.py`
- `reports/ST-C1_STATISTICAL_VALIDATION_REPORT.md`

### M3 — Execution layer skeleton

Only after approval should the canonical execution pipeline, broker adapter,
risk gate, reconciliation, and journaling be completed.

---

## 4. Practical repository note

The repo now has the right governance foundation for strategy approval work.
The next risk is no longer configuration drift. The next risk is strategy
normalization quality and approval discipline.
