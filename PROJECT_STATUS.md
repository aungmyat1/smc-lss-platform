# PROJECT_STATUS.md — SMC-LSS Platform

**Audit date:** 2026-07-22 (research-track update; see §5)
**Status:** Configuration governance complete; ST-C1 strategy research/validation in
progress. Execution layer remains blocked — nothing below changes that.
**Current phase:** Strategy research and validation (not execution-layer work).
**Current milestone:** ST-C1 v3.9 "Clean SMC" preset (v1.2.0 candidate) filed as
the follow-up Research Change Request targeting the `REJECTED_NO_DISPLACEMENT`
bottleneck — candidate created, population-feasibility backtest not yet run
(see §5). Not execution-layer work.

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

## 5. ST-C1 v3.7 / v3.8 research track (2026-07-21/22)

Separate from and subordinate to the M1-M2.3 work above (§1-4), which
concerns the original v3.6-derived approval scaffold. This section tracks
the newer 10-gate (G1-G10) conformance research line:

- **v3.7 result: OVERFILTERED / statistically INCONCLUSIVE.** A locked
  12-cell ablation (`reports/ablation/ST_C1_V37_ABLATION_REPORT.md`) across
  EURUSD/GBPUSD/XAUUSD full history produced **zero trades in every cell**,
  including the loosest configuration. Root cause: G6 (the M5
  poi-entry-to-sweep-to-displacement-to-CHoCH-to-retrace sequence)
  saturates the funnel before the location/net-reward gates under test can
  ever be exercised.
- **v3.8 status: hypothesis REJECTED within tested range, no candidate
  created.** A preregistered R2.1 experiment
  (`reports/audit/ST_C1_V38_G6_POPULATION_RCR.md`,
  `reports/audit/ST_C1_V38_FINAL_VALIDATION_DECISION.md`) tested whether
  widening `poi_entry_to_sweep_max_m5_bars` (30 -> 72 -> 144) restores a
  statistically usable G6 population. It does not, within the tested range:
  even at 144 bars (the task ceiling), only 14 completed G6 sequences were
  found across all three symbols over the full available history, short of
  the precommitted 30-sequence floor. No `specs/v3.8.yaml` or
  `strategies/candidates/ST-C1_v1.2.0.yaml` was created.
- **Execution layer: blocked.** **Demo/live: blocked.** Nothing in this
  research track changes `config/watchlist.yaml`'s autonomy block
  (`demo: proposal_only`, `live: disabled`, `promote_to_live: false`) or any
  approval/promotion flag.
- **v3.9 "Clean SMC" preset filed (2026-07-22):** the follow-up Research
  Change Request called for above. Owner supplied a fully specified
  parameter preset that returns to the v3.6/`ST-C1_v1.yaml` E1/E2/E3 schema
  (not v3.7's G1-G10 pipeline) with E1 disabled, E2/E3 wick-ratio filters
  zeroed, and displacement redefined as body-ratio-only (ATR-magnitude
  requirement removed) — directly targeting `REJECTED_NO_DISPLACEMENT`.
  Filed per `docs/RESEARCH-CHARTER.md` in
  `reports/audit/ST_C1_V39_CLEAN_SMC_RCR.md` and `reports/research_log.md`
  BEFORE any backtest ran. Artifacts created: `specs/v3.9.yaml`
  (`engine_implements_spec: false`) and
  `strategies/candidates/ST-C1_v1.2.0.yaml` (`status: candidate`,
  `validation.status: pending`). **The v3.7/v3.8 line is now PARKED** in
  favor of this preset as the active research candidate — v3.7/v3.8 files
  are retained unmodified as historical/parked, not deleted.
- **Next milestone:** run the population-feasibility check (>=30 completed
  sequences across EURUSD/GBPUSD/XAUUSD, >=5 in >=2 symbols — same floor as
  R2.1) against `specs/v3.9.yaml`/`ST-C1_v1.2.0.yaml` via
  `backtest-researcher`, per the precommitted criteria in
  `ST_C1_V39_CLEAN_SMC_RCR.md`. NOT execution-layer work.
- **Data note:** the full local EURUSD/GBPUSD/XAUUSD history has now been
  used for diagnosis across the v3.7 and v3.8 research tasks. It must not be
  described as a pristine, unseen OOS partition in any future validation of
  this strategy family.
- **v3.9 governance/conformance task started (2026-07-22), local branch
  `research/st-c1-v39-governance-conformance`:** Phase 0 preflight found
  `NEXT_ACTION.md` stale (pointed at Phase 3 execution work — corrected) and
  a framework conflict: the task's requested "G1-G10 conformance matrix"
  does not fit v3.9, which deliberately uses the E1/E2/E3+M1/M2/M3 schema,
  not the parked G1-G10 pipeline. Owner decision: audit v3.9 in its own
  E1/E2/E3+M1/M2/M3 terms, not G1-G10 labels. See
  `reports/audit/ST_C1_V39_GOVERNANCE_CONFORMANCE_PRE_EDIT_FINDINGS.md`.
  `research_spec` in `config/watchlist.yaml` still correctly points at
  `specs/v3.6.yaml` (v3.9 is not yet an approved research spec) and no
  autonomy/promotion flag has changed.
- **v3.9 conformance + population-feasibility task completed (2026-07-22):**
  canonical engine built (`src/signal_v39.py`,
  `validation/historical_replay_engine_v39.py`), conformance matrix closed
  (`reports/audit/ST_C1_V39_CONFORMANCE_MATRIX.md`), 26 new tests pass
  (162/162 full suite). **Population-feasibility gate PASSES decisively**:
  138 completed trades across EURUSD (47) + GBPUSD (37) + XAUUSD (54) vs.
  the 30-total/5-per-symbol floor — see
  `reports/audit/ST_C1_V39_POPULATION_ABLATION_SPEC.md` for full results
  and raw evidence in `reports/ablation/st_c1_v39_B{0,1}_*_raw.json`. A
  v3.6-control comparison confirms the population growth traces to the
  intended relaxations (EURUSD/GBPUSD go from 2 trades under v3.6 to 47/37
  under v3.9). **Caveat, not yet resolved:** the same run shows EURUSD/GBPUSD
  deeply net-cost-negative (PF 0.03/0.14) and XAUUSD only marginally
  positive and *worse* than its own v3.6 control (PF 1.06 vs 1.96) — a
  real quantity/quality tradeoff that must be investigated (own
  pre-registered RCR) before any Phase-7-equivalent profitability read.
  `engine_implements_spec` remains `false`; no autonomy/promotion flag
  changed; all work uncommitted on the local branch above.
- **ST-C1 v3.10 "Reversal Capture" filed (2026-07-22), same local branch:**
  owner-directed new trade thesis — E1 (D1 gap reaction) re-enabled with a
  partial-fill tolerance, gated behind an H4 trend-bias DIVERGENCE
  requirement (entry must oppose H4 bias, not agree with it), E2 hold-
  confirmation, E3 internal-liquidity acceptance, auto displacement
  direction, dynamic R:R. Filed as `specs/v3.10.yaml` /
  `strategies/candidates/ST-C1_v1.3.0.yaml` — v3.9 retained unmodified as
  an independent prior candidate/control (its own cost/quality question
  above is separate and unresolved). Engine built
  (`src/signal_v310.py`, `validation/historical_replay_engine_v310.py`),
  14 new tests pass, 178/178 full suite. Found and fixed a real bug (doji-
  candle E1 reaction exclusion) and a real data gap (this repo's H4 CSVs
  are missing/unusably short — added `smc_engine.resample()` to derive
  full-history H4 from H1). Existence check (>=1 signal/symbol,
  precommitted as the interim bar pending a population-floor addendum):
  **cleared decisively** — EURUSD 135, GBPUSD 112, XAUUSD 120 (367 total).
  No net-of-cost read run yet; `engine_implements_spec` stays `false`; no
  autonomy/promotion flag changed; all uncommitted.
