# Full Code Audit - SMC-LSS Platform

Audit date: 2026-07-24  
Auditor: Codex  
Repository: https://github.com/aungmyat1/smc-lss-platform  
Verdict: **BLOCKED**

## 1. Executive Verdict

**BLOCKED.** S1-G2 work may continue inside the existing Stage A reference-only boundary, but S1-G2 may not close. S1-G3, A3, Stage B, broker integration, demo, live, and production remain blocked.

No evidence was found that the ST-C2 Stage A reference modules import MT5, submit orders, or directly contact a broker. However, the current repository cannot pass the requested audit because the exact audited SHA has failing CI, the local full test suite timed out, the worktree is dirty, and the ST-C2 reference scanner/evidence layer contains conformance defects that can invalidate reported signal timing and FVG/sweep eligibility.

Finding counts: P0=0, P1=4, P2=4, P3=1.

## 2. Verified Repository State

| Item | Verified state |
|---|---|
| Current branch | `master` |
| Current HEAD | `5ac448b962be255ef84538dfc2169dee2cad52d1` |
| Remote default branch | `origin/HEAD -> origin/master` |
| Remote master HEAD | `5ac448b962be255ef84538dfc2169dee2cad52d1` |
| Fetch status | `git fetch --prune origin` succeeded |
| Merge base with master | `5ac448b962be255ef84538dfc2169dee2cad52d1` |
| Ahead/behind | `0 0` |
| Worktree | Dirty before audit |
| Open PRs | 1 open PR: `#1 Source-verify and implement E1M1 gap reaction rules` |
| Latest merged PR | `#15 Add ST-C3 funnel overhaul plan`, merged `2026-07-24T16:40:57Z` at audited SHA |
| CI for audited SHA | GitHub Actions `CI` failed, run `30110038467` |
| Python | `Python 3.14.0`, `C:\Python314\python.exe` |
| Dependency file | `requirements.txt`: `pytest`, `pandas`, `PyYAML` only; unpinned |
| Audit output collision | None for the two required audit files |

Dirty worktree inventory before audit:

- Modified: `CLAUDE.md`, `NEXT_ACTION.md`, `PROJECT_STATUS.md`, `ROADMAP.md`, `governance/st_c2_stage_status.yaml`, `reports/ST-C2_V1.2_GBPUSD_EXISTENCE_CHECK.md`, `reports/validation/st_c2/A2_CONFORMANCE_RESULTS.json`, `reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json`, `specs/st_c2/conformance_manifest.yaml`, `specs/st_c2/rule_to_test_map.yaml`, `tests/st_c2/test_existence_reproduction.py`, `tests/st_c2/test_traceability.py`, `tests/test_st_c2_reference.py`, `validation/st_c2/interfaces.py`, `validation/st_c2_reference.py`.
- Added: `reports/validation/st_c2/GC4_REJECTION_EVIDENCE_REPORT.md`, `reports/validation/st_c2/GC4_RULE_CLOSURE_REPORT.md`, `reports/validation/st_c2/GC4_SIGNAL_CANDIDATE_REPORT.md`, `reports/validation/st_c2/GC4_STATE_MACHINE_REPORT.md`, `reports/validation/st_c2/GC4_TRADE_PLAN_REPORT.md`, `reports/validation/st_c2/GC4_WORKTREE_CHECKPOINT.md`, `tests/st_c2/test_gc4_evidence.py`, `validation/st_c2/evidence_gc4.py`.
- Worktrees: `D:/ddev/smc-lss-platform` at master; `D:/ddev/smc-lss-platform-stc3` at `8981dc3c1db742e883ba161a70bfaaefe56bf09b`.

## 3. Governance Alignment Matrix

| Source | Active stage/gate | Strategy | Execution/demo/live | Alignment |
|---|---|---|---|---|
| `MASTER_PLAN.md` | Stage A, A2, S1-G2 open | ST-C2 v1.2.0 GBPUSD frozen | Blocked | Authoritative |
| `CLAUDE.md` | Stage A, A2, S1-G2 open | ST-C2 v1.2.0 GBPUSD frozen | Blocked | Aligned, but first signal text says `2026-06-26 17:51` |
| `PROJECT_STATUS.md` | Stage A, A2, S1-G2 open | ST-C2 v1.2.0 GBPUSD frozen | Blocked | Aligned |
| `ROADMAP.md` | Stage A, A2, S1-G2 open | ST-C2 v1.2.0 GBPUSD frozen | Blocked | Aligned |
| `NEXT_ACTION.md` | S1-G2 remaining mappings | ST-C2 v1.2.0 GBPUSD frozen | Blocked | Aligned |
| `governance/st_c2_stage_status.yaml` | A2/S1-G2 in progress | ST-C2 v1.2.0 GBPUSD | Blocked | Aligned |
| `specs/st-c3_v1.0.0.yaml` | Draft intake only | ST-C3 draft, no implementation authorization | Blocked | Correctly non-authoritative |

Contradictions:

- Repository baseline claim says open PR count is zero, but GitHub reports one open PR.
- Higher/lower evidence distinguishes two signal timestamps: `2026-06-10 17:15` as the first raw existence signal and `2026-06-26 17:51` as the first GC4 trade-plan-accepted signal. The distinction is now documented in status/roadmap, but audit evidence must avoid treating them as the same milestone.
- CI says the exact audited SHA fails the existence reproduction test, so any local or report claim that S1-G2 evidence is reproducible must be qualified.

## 4. Architecture And Dependency Boundaries

Observed ST-C2 Stage A dependency direction:

`validation/st_c2_reference.py` -> `validation/st_c2/*` evidence/structure/symbol helpers -> `src/smc_engine.py` pure candle primitives.

No direct broker import was found in `validation/st_c2_reference.py` or `validation/st_c2/*`. The reference kernel has a text guard for `MetaTrader5`, `mt5.`, `place_order`, and `broker_adapter`. Repository-level broker/MT5 and order-payload code still exists in older execution-adjacent modules such as `src/load_history.py`, `src/live_signal.py`, and `src/smc_master.py`; those are not imported by the ST-C2 reference path inspected here.

Boundary assessment:

- Stage A ST-C2 reference path does not submit orders.
- Stage A ST-C2 reference path does not import broker adapters.
- Config dependencies are file-based and deterministic, but dependency versions are unpinned.
- Generated reports are consumed by traceability tests, so reports are acting as test inputs. This is acceptable as audit evidence but fragile as runtime authority.
- ST-C2 and ST-C3 namespaces are separated in specs; ST-C3 uses `ST-C3-R*` rejection codes and remains draft.

## 5. ST-C2 Frozen-Rule Coverage Matrix

Independent recalculation used `reports/validation/st_c2/A2_RULE_COVERAGE_MATRIX.json` plus `specs/st_c2/rule_to_test_map.yaml`.

Summary:

| Status | Count |
|---|---:|
| Total inventoried frozen rules | 45 |
| Implemented and tested | 25 |
| Implemented not tested | 3 |
| Partially implemented | 13 |
| Not implemented | 4 |
| Missing from rule-to-test map | 10 |

Rules requiring continued S1-G2 work:

- Missing/not implemented: `STC2-STRUCT-002`, `STC2-STRUCT-003`, `STC2-STRUCT-006`, `STC2-LIQ-002`, `STC2-FVG-007`.
- Implemented but not tested or mapped weakly: `STC2-TF-001`, `STC2-LIQ-001`, `STC2-LIQ-005`, `STC2-LIQ-006`, `STC2-POI-001`.
- Partial and conformance-critical: `STC2-BIAS-004`, `STC2-FVG-003`, `STC2-FVG-004`, `STC2-FVG-005`, `STC2-LTF-001`, `STC2-LTF-003`, `STC2-ENTRY-001`, `STC2-ENTRY-002`, `STC2-ENTRY-003`, `STC2-TARGET-001`, `STC2-MGMT-001`, `STC2-REJECT-001`, `STC2-DEDUP-001`.

Difference from the starting claim:

- The current checked artifacts report 45 rules and 10 missing mappings after GC4, not 20. The earlier 20-missing state corresponds to the post-GC3 status recorded in `A2_CONFORMANCE_RESULTS.json`, before GC4 decision evidence.

## 6. Test And CI Evidence

| Command | Result |
|---|---|
| `git diff --check` | PASS |
| `python -m compileall -q src validation tests` | PASS |
| `python -m pytest -q tests/test_st_c2_reference.py` | PASS, 8 passed in 2.00s |
| `python -m pytest -q tests/st_c2/test_gc4_evidence.py` | PASS, 4 passed in 1.35s |
| `python -m pytest -q tests/st_c2/test_evidence_gc3.py tests/st_c2/test_structural_conformance.py tests/st_c2/test_traceability.py` | PASS, 15 passed in 6.70s |
| `python -m pytest -q tests/st_c2` | TIMED OUT after 120s |
| `python -m pytest -q tests/st_c2/test_existence_reproduction.py` | TIMED OUT after 180s locally |
| `python -m validation.run_st_c2_gbp_existence` | TIMED OUT after 240s locally; command writes an existing report, so it was not repeated |
| `python -m pytest -q` | TIMED OUT after 300s locally |
| GitHub Actions `CI` for exact SHA | FAIL: 1 failed, 214 passed, 4 skipped, 1 warning |

GitHub Actions failure:

- `tests/st_c2/test_existence_reproduction.py::test_existence_signal_reproduction`
- Failure: expected `**SIGNAL_FOUND**` in `reports/ST-C2_V1.2_GBPUSD_EXISTENCE_CHECK.md`; report content did not contain it in CI.

Skipped, timed-out, or missing tests were not treated as passed.

## 7. Data-Integrity And Quantitative-Bias Assessment

Key risks:

- H4/M15 window slicing can include bars that are not closed at the M3 `asof` time if CSV timestamps are candle-open timestamps.
- Existence reproduction depends on local data files not present or not equivalent in CI.
- `data/GBPUSD_M3.csv` is derived from M1; the derivation contiguity and non-overlap proof was not independently reproduced because the report-generating command timed out.
- Full-history reuse before the `2026-07-23` prospective lock means current ST-C2 evidence cannot support OOS or statistical-edge claims.
- The exact accepted signal timestamp is not audit-reliable until the close-boundary issue is fixed and CI can reproduce the same data/report state.

No profitability, statistical edge, or production readiness is approved by this audit.

## 8. Security And Operational Safety

P0 safety result: no direct Stage A ST-C2 broker submission path was found.

Residual risks:

- Legacy modules can build order payloads, and `src/load_history.py` can initialize MT5, but they are outside the inspected ST-C2 reference import path.
- `requirements.txt` is unpinned, so CI installed floating versions (`pytest 9.1.1`, `pandas 3.0.5`) while local Python 3.14 had different installed versions.
- Report-generating validation commands write into tracked evidence paths, which makes tests capable of rewriting audit artifacts.

## 9. Findings

### P1-001 - Higher-timeframe scanner can include unclosed H4/M15 candles

Category: data integrity / lookahead bias  
Evidence: `validation/st_c2_reference.py:100-109`, `validation/st_c2_reference.py:286-305`  
Direct evidence: `_window_asof_indexed` uses `bisect_right(times, asof)` and returns bars with timestamp `<= asof`. `scan_history` passes the current M3 bar timestamp as `asof` for H4 and M15 windows. If data timestamps are candle opens, an H4 bar at `16:00` is included for an M3 decision at `17:15` even though that H4 candle is not closed until `20:00`.  
Reproduction: run `scan_history` with H4 open-time candles and inspect H4 windows for an M3 `asof` inside the H4 interval.  
Expected: H4/M15 windows include only closed candles at the M3 decision time.  
Actual: H4/M15 windows include bars whose open timestamp is less than or equal to the M3 time.  
Impact: invalidates no-lookahead, closed-candle confirmation, H4/M15/M3 alignment, and the reproduced signal timestamp.  
Affected gate: S1-G2.  
Remediation: define timestamp semantics, compute timeframe close times, and slice H4/M15 with `bar_close_time <= asof`; add cutoff tests around intra-H4 and intra-M15 M3 bars.  
Tests required: positive closed-boundary case, negative intra-candle lookahead case, and exact reproduction of `2026-06-10 17:15` / `2026-06-26 17:51` after close-time correction.  
Confidence: high.  
Blocks S1-G2 closure: yes.

### P1-002 - FVG chain can pass without required HTF FVG overlap

Category: ST-C2 conformance  
Evidence: `validation/st_c2/fvg_confirmation.py:145-177`, `validation/st_c2/evidence_fvg_ltf.py:72-83`  
Direct evidence: `detect_fvg_chain` appends the selected MF FVG even when `selected_htf is None`; `EvidenceBuilder.build_fvg_chain` sets `continuity = mf_fvg is not None and ltf_fvg is not None` and `valid = continuity`, ignoring missing HTF FVG evidence.  
Reproduction: construct windows with MF and LTF FVGs but no overlapping H4 FVG. The builder can return `valid=True`.  
Expected: frozen chain requires HTF FVG valid -> MF overlap -> LTF within MF displacement, with cascade failure if any lower/upper link is absent.  
Actual: MF+LTF is enough for valid evidence.  
Impact: can manufacture eligibility through incomplete confluence evidence.  
Affected gate: S1-G2.  
Remediation: require confirmed HTF FVG and explicit MF overlap before validity; encode cascade rejection details.  
Tests required: negative missing-HTF case, negative non-overlap case, positive HTF/MF/LTF chain case.  
Confidence: high.  
Blocks S1-G2 closure: yes.

### P1-003 - Liquidity sweep max-age is evaluated at sweep time, not decision cutoff

Category: ST-C2 conformance / data integrity  
Evidence: `validation/st_c2/structure.py:452-543`  
Direct evidence: `age = i - int(pool.source_indices[0])` is checked when a sweep candidate is found; confirmed sweeps are then sorted and the earliest confirmed sweep is returned. There is no check that the selected sweep remains within `max_sweep_age_bars_htf` at the current cutoff.  
Reproduction: create a valid sweep within 20 bars of the pool, append many H4 bars, and call `structural_context`; the old confirmed sweep can still be selected.  
Expected: sweep age must be valid relative to the current decision window.  
Actual: a historically valid sweep can remain eligible indefinitely.  
Impact: stale liquidity can pass R1 and contaminate later OTE/FVG/signal evidence.  
Affected gate: S1-G2.  
Remediation: evaluate sweep age against `len(htf_candles)-1` or close-time cutoff and choose the correct current eligible sweep.  
Tests required: boundary age 20 pass, age 21 fail, multiple sweep latest/nearest deterministic selection.  
Confidence: high.  
Blocks S1-G2 closure: yes.

### P1-004 - Signal timestamp can differ from actual LTF confirmation timestamp

Category: ST-C2 conformance / deterministic state transitions  
Evidence: `validation/st_c2_reference.py:239-249`, `validation/st_c2_reference.py:282-283`, `validation/st_c2/fvg_confirmation.py:180-237`  
Direct evidence: `detect_ltf_confirmation` scans the last `max_setup_bars` and returns the first qualifying event, but `analyze_windows` stamps the signal as `ltf[-1]["time"]`. Later bars can inherit an earlier confirmation while producing a new signal timestamp.  
Reproduction: append non-confirming M3 bars after the first qualifying CHoCH but within the setup window; observe confirmation timestamp remains earlier while `signal_time` moves to the last bar.  
Expected: signal timestamp and state transition evidence must correspond to the first qualifying confirmation or to a documented entry-window candidate rule.  
Actual: signal timestamp is the current window end regardless of confirmation time.  
Impact: duplicate-signal control, first qualifying bar semantics, and existence timestamp evidence are unreliable.  
Affected gate: S1-G2.  
Remediation: separate confirmation timestamp from entry-window candidate timestamp; implement duplicate rejection and entry-window expiry explicitly.  
Tests required: first-bar signal test, duplicate later-window rejection test, expiry at 15 M3 bars.  
Confidence: high.  
Blocks S1-G2 closure: yes.

### P2-001 - Logical trade plan collapses T1 and T2 into one target

Category: ST-C2 conformance / trade-plan evidence  
Evidence: `validation/st_c2/evidence_gc4.py:358-382`  
Direct evidence: `target_1` and `target_2` are both set to `target_price`, derived from one dealing-range extreme. The frozen spec requires both T1 and T2 mandatory objectives.  
Reproduction: inspect any confirmed `LogicalTradePlan` from `DecisionEvidenceBuilder`; both targets are identical.  
Expected: T1 and T2 should be separately evidenced, or the mapping should remain not implemented.  
Actual: one target is duplicated into two fields.  
Impact: logical trade-plan conformance is overstated.  
Affected gate: S1-G2.  
Remediation: model T1/T2 evidence separately or mark target evidence incomplete.  
Tests required: positive distinct target evidence, missing T1 rejection, missing T2 rejection.  
Confidence: high.  
Blocks S1-G2 closure: yes.

### P2-002 - Exact audited SHA has failing CI

Category: CI / reproducibility  
Evidence: GitHub Actions run `30110038467` for `5ac448b962be255ef84538dfc2169dee2cad52d1`  
Direct evidence: CI failed with `1 failed, 214 passed, 4 skipped`; failing test is `tests/st_c2/test_existence_reproduction.py::test_existence_signal_reproduction`.  
Reproduction: view the CI run or run `python -m pytest -q` on the CI checkout.  
Expected: exact audited SHA has passing CI before evidence can be treated as reproducible.  
Actual: CI is red.  
Impact: S1-G2 completion evidence is not reproducible in the canonical environment.  
Affected gate: S1-G2.  
Remediation: make data/report fixtures reproducible in CI or classify the test as data-blocked with honest assertions.  
Tests required: CI full suite green for the audited/fixed SHA.  
Confidence: high.  
Blocks S1-G2 closure: yes.

### P2-003 - Baseline repository-state claim says zero open PRs, but GitHub reports one

Category: governance / repository verification  
Evidence: `gh pr list --state open` returned PR `#1`, branch `arena/019f7116-smc-lss-platform`.  
Direct evidence: Open PR title is `Source-verify and implement E1M1 gap reaction rules`.  
Reproduction: run `gh pr list --repo aungmyat1/smc-lss-platform --state open`.  
Expected: baseline claims match verified repository state or are explicitly corrected.  
Actual: starting claim said zero open PRs.  
Impact: repository-state audit evidence would be inaccurate if the starting claim were trusted.  
Affected gate: governance audit.  
Remediation: update audit baselines/status docs when open PR state changes.  
Tests required: none; verification command evidence is sufficient.  
Confidence: high.  
Blocks S1-G2 closure: no.

### P2-004 - Requirements are unpinned and environments diverge

Category: reproducibility / dependency governance  
Evidence: `requirements.txt` contains only `pytest`, `pandas`, `PyYAML`; CI installed Python 3.12 packages, local audit used Python 3.14.  
Direct evidence: CI installed `pytest 9.1.1`, `pandas 3.0.5`; local environment had `pytest 8.3.5`, `pandas 2.3.3`, many unrelated packages including `metatrader5`.  
Reproduction: compare `requirements.txt`, CI log, and `python -m pip list --format=freeze`.  
Expected: validation evidence uses reproducible dependency versions.  
Actual: dependency versions float.  
Impact: tests, pandas parsing, and validation outputs may differ across machines.  
Affected gate: S1-G2 evidence reproducibility.  
Remediation: add a pinned constraints/lock file or supported environment declaration.  
Tests required: CI and local reproduction using the pinned environment.  
Confidence: high.  
Blocks S1-G2 closure: no, but must be resolved before stronger reproducibility claims.

### P3-001 - Report-generating existence command rewrites tracked evidence path

Category: audit hygiene / test side effects  
Evidence: `validation/run_st_c2_gbp_existence.py:13`, `validation/run_st_c2_gbp_existence.py:82`  
Direct evidence: `REPORT_PATH` points to `reports/ST-C2_V1.2_GBPUSD_EXISTENCE_CHECK.md`, and `build_report()` writes it.  
Reproduction: run `python -m validation.run_st_c2_gbp_existence`.  
Expected: tests should not rewrite historical evidence unless explicitly invoked in a controlled artifact path.  
Actual: reproduction command writes the canonical report.  
Impact: audit/test runs can mutate evidence files in a dirty worktree.  
Affected gate: S1-G2 audit evidence handling.  
Remediation: separate pure reproduction from report writing, or write to a temp/output argument by default.  
Tests required: pure reproduction test that performs no tracked-file write.  
Confidence: high.  
Blocks S1-G2 closure: no.

## 10. Remediation Plan

1. Fix H4/M15 closed-candle slicing and timestamp semantics before accepting any existence signal.
2. Fix FVG-chain validity to require HTF/MF/LTF cascade continuity, overlap, freshness, and invalidation evidence.
3. Fix liquidity sweep current-age evaluation and deterministic sweep selection.
4. Split LTF confirmation timestamp, entry-window candidate timestamp, duplicate rejection, and expiry semantics.
5. Correct logical trade-plan T1/T2 evidence or mark it incomplete.
6. Make existence reproduction deterministic in CI without relying on unavailable local data.
7. Pin or constrain the supported validation environment.
8. Convert report-writing reproduction commands to pure checks or explicit output paths.

## 11. Gate Recommendation

| Gate | Recommendation |
|---|---|
| S1-G2 work may continue | Yes, within Stage A reference-only scope |
| S1-G2 may close | No |
| S1-G3 may start | No |
| A3 may start | No |
| Stage B may start | No |

## 12. Not Verified

- No broker, MT5 terminal, exchange, or external trading account was contacted.
- No order submission, demo simulation, or live simulation was run.
- The M1-to-M3 derivation was not independently regenerated.
- The full local pytest suite did not complete within 300 seconds.
- The existence reproduction command timed out locally and was not rerun because it writes a tracked evidence file.
- No profitability, OOS edge, walk-forward validity, robustness, or production readiness was assessed.

## Owner-Decision Summary

Audit verdict: **BLOCKED**.  
Audited SHA: `5ac448b962be255ef84538dfc2169dee2cad52d1`.  
P0/P1/P2/P3 counts: `0/4/4/1`.  
Test results: focused ST-C2 tests passed; exact-SHA CI failed; local full pytest timed out.  
S1-G2 recommendation: continue remediation, do not close.  
Top five remediation actions: fix close-time slicing, fix FVG cascade validity, fix sweep current-age eligibility, fix LTF signal timestamp/duplicate semantics, fix distinct T1/T2 evidence.  
Changed files from this audit: `reports/audit/FULL_CODE_AUDIT_2026-07-24.md`, `reports/audit/FULL_CODE_AUDIT_FINDINGS_2026-07-24.json`.  
Unverified items: M1-to-M3 derivation, full local suite pass, pure existence reproduction, any statistical edge.
