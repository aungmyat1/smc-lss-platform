# ST-C1 v3.7 Pre-Edit Findings

Recorded: 2026-07-21
Scope: research/backtesting only. No broker orders, no demo/live changes, no strategy-rule edits made before this report.

## 1. Verified git state

- Baseline branch stated: `research/st-c1-baseline-runner-v2-clean` @ `0510dca5a9d925ae154ba18c95dac53ecb0b292a`
  → **confirmed exact match**, `git rev-parse origin/research/st-c1-baseline-runner-v2-clean` = `0510dca5a9d925ae154ba18c95dac53ecb0b292a`.
- Phase A closure branch stated: `research/st-c1-phase-a-closure` @ `8e43e0af4c8e3cf32911e46e081b8f7aa4aff13b`
  → **confirmed exact match** (`git status --porcelain=2 --branch` reported `branch.oid 8e43e0af4c8e3cf32911e46e081b8f7aa4aff13b`).
- Worktree: clean before any edit.
- PR #3: open, draft, `mergeable: MERGEABLE`, head `8e43e0af4c8e3cf32911e46e081b8f7aa4aff13b` — matches. No divergence to report; safe to proceed as specified.
- New branch created: `research/st-c1-v37-article-conformance`, from Phase A closure HEAD.
- `AGENTS.md` does not exist anywhere in this repository (`git ls-files` — no match). Governance was read instead from `MASTER_PLAN.md`, `CLAUDE.md`, `docs/CHARTER.md`, `docs/RESEARCH-CHARTER.md`, `PROJECT_STATUS.md`, `ROADMAP.md`, `NEXT_ACTION.md`, per CLAUDE.md's own document order.

## 2. Governance conflict identified (must be surfaced, not silently resolved)

`CLAUDE.md`'s "Owner directives (2026-07-18)" section states Phase 3 = **Risk Engine**, built on **locked `specs/v1.yaml`**, with sub-milestones M1 config loader → M2 risk validator → M3 position sizing → M4 approval gate, and says the v3.5 track is parked.

`MASTER_PLAN.md` v3.0.0 (recorded **2026-07-19**, one day later, and explicitly "supersedes v2.1.3") rewrites the phase structure entirely around **v3.6/ST-C1 strategy approval first**: Phase 1 = Strategy Approval Foundation (now complete), Phase 2 = Validation & Packaging (current per `ROADMAP.md`), Phase 3 = **Execution Layer Skeleton** (not "Risk Engine"), Phase 4 = Demo Automation, Phase 5 = Live Pilot. It states directly: *"v3.5/v1 materials remain historical references only. They do not define the new architecture."*

Per `CLAUDE.md`'s own authority order (`MASTER_PLAN.md` > `CLAUDE.md`), **MASTER_PLAN.md wins**: the "Risk Engine / locked v1 engine / v3.5 parked" framing in CLAUDE.md's owner-directives section is stale and superseded. This is flagged per the instruction "stop, identify it, follow the higher authority" — not silently overridden.

**Why this doesn't block the current task:** `NEXT_ACTION.md` (consistent with `PROJECT_STATUS.md`) currently targets Phase 3 M3 "Execution Layer Skeleton" as the in-flight milestone. This task is scoped to research/backtesting only (`src/`, `validation/`, `specs/`, `strategies/candidates/`, `tests/`, `reports/`) and touches no execution-layer or broker code — it sits in the Research ownership lane (`smc_engine.py`, `backtest*.py`, `validate*.py`, `data/`, `reports/` per CLAUDE.md's system-ownership split), orthogonal to the M3 execution-layer work. Proceeding with a research-only spec/engine candidate does not start a second concurrent milestone in the execution-layer sense the "one milestone at a time" rule is protecting.

Secondary staleness: `ROADMAP.md` still marks Phase 2 "🟡 CURRENT" even though `PROJECT_STATUS.md` records M2.1/M2.2/M2.3 as complete and `NEXT_ACTION.md` has already moved to Phase 3 M3 — a documentation-lag issue, not a hard conflict, noted for completeness.

## 3. Spec inventory

| Spec | Track | Status | Notes |
|---|---|---|---|
| `specs/v1.yaml` | execution | `active`/`deployed` | Legacy, EURUSD-only, H4 bias/M15 entry/M1 confirm, single swing-lookback signal. Backs `live_signal.py` today (per system-ownership split). |
| `specs/v3.5.yaml` | research | superseded | All-negative-expectancy historical control (EURUSD/XAUUSD/BTCUSD), direction hard-locked per variant — the defect v3.6 fixes. |
| `specs/v3.6.yaml` | research | `draft`/`RESEARCH_CANDIDATE` | `implementation_status.engine_implements_spec: false` — an explicit, hardcoded safety interlock. Fully parameterized E1/E2/E3 × M1/M2/M3 contract, displacement, sequencing, session, target hierarchy with `REJECT_NO_TARGET`, signal lifecycle, market regime, confidence score, risk, trade management. Richest spec in the repo; **its own §26 checklist lists itself as not fully implemented.** |
| `strategies/candidates/ST-C1_v1.yaml` | candidate | `candidate`/`pending` | Normalized from the v3.6 human spec (`docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md`). Its `poi.premium_discount` and `entry_model.long/short` rules explicitly require discount/premium location — **this requirement exists on paper but is not implemented or tested anywhere in code** (see §5 below). |

## 4. Code inventory — three competing, behaviorally different signal implementations

This is the central finding, and it sharpens `reports/audit/st_c1_strategy_conformance_matrix.md`'s existing "surrogate" conclusion into a specific root cause:

1. **`src/signal_v35.py`** (508 lines) — the closest attempt at the v3.6 E-trigger/M-model contract: causal `_e1_trigger`/`_e2_trigger`/`_e3_trigger` with freshness/mitigation checks, ATR-normalized `displacement_move` (via `smc_engine.py`), IFVG inversion + retrace for M3, `REJECT_NO_TARGET` (already fixed here — no-DOL is not a silent pass), session killzone filter, `max_e_to_m_h1_bars` staleness check, and structure-key dedup. Has the most complete positive/negative test coverage (`tests/test_signal_v35.py`, 16 tests). **Not called anywhere in the historical replay path.**
2. **`src/live_signal.py::latest_signal`** (82-line module) — the **v1 legacy execution signal**: one M5/H1-agnostic window, a single swing-break-plus-equilibrium check (`px > sh and px < eq` for long), no E-trigger/M-model concept, no HTF causal structure at all. Per CLAUDE.md's system-ownership split this module belongs to **Production Execution**, not Research.
3. **`validation/historical_replay_engine.py::evaluate_features`** (988 lines) — **imports and calls `live_signal.latest_signal` directly** (`from live_signal import latest_signal`, then `sig = latest_signal(m5_window, k, eq_window)`) as its `"signal"` feature, then layers its own bespoke sweep/POI/stop/target logic on top — a **fourth, distinct rule set** matching neither v3.6's E/M contract nor `ST-C1_v1.yaml`'s stated `entry_model`.

**Answer to "which engine produced the 363-trade baseline":** it is `historical_replay_engine.py`, whose actual signal-detection call is `live_signal.py`'s v1 legacy swing/equilibrium function, wrapped in ad hoc sweep/POI checks — **not** `signal_v35.py`'s E-trigger/M-model engine, and not a dedicated ST-C1 implementation. This directly explains why the conformance matrix rates E1/E2/E3, displacement, and real CHoCH classification as MISSING/PARTIAL/MISLABELED: those rules live only in `signal_v35.py`, a module the baseline never imports. It is also a boundary violation of the project's own Research/Production split (a Production Execution module feeding a Research replay engine).

## 5. Gate-by-gate mapping (G1–G10 framework vs. current baseline code)

| Gate | Current state | Evidence |
|---|---|---|
| G1 HTF bias | PARTIAL | `_directional_bias` uses H1 (or M5 fallback) swings → `e.trend`, plus ad hoc 2-/3-bar fallback heuristics. No protected-high/low concept, no close-buffer parameter, no explicit pivot confirmation rule tied to a spec field. |
| G2 external/protected structure | MISSING | No dealing-range / external-vs-internal distinction in the replay engine. `signal_v35._e3_trigger` has a real external-extremity concept (range-lookback max/min) but is not called from the replay path. |
| G3 BOS/CHoCH | MISLABELED | Replay engine's `choch_time`/`choch_break_level`/`choch_reason` fields are fabricated post hoc from the v1 `latest_signal` stop level — not an independently classified close-confirmed reversal, confirming the conformance matrix's "MISLABELED" verdict. |
| G4 premium/discount | PARTIAL / UNVERIFIED | `live_signal.latest_signal` has an implicit equilibrium check (`px < eq` gates long) but it is undocumented as a location gate, not persisted as a range ID/anchors/timestamp, and `ST-C1_v1.yaml`'s explicit premium/discount requirement is untested by any test file. |
| G5 HTF area of interest (FVG) | VIOLATION | `_select_poi` selects order blocks/FVGs computed on the **M5 execution window** and labels them `poi_type` without any HTF/causal linkage — exactly the "M5 FVG mislabeled as HTF FVG" failure mode this task calls out. |
| G6 M5 trigger ordering | MISSING | Actual gate order in `generate_signal` is: session → v1-legacy signal → bias → sweep → POI → stop → target. No displacement step, no explicit HTF-POI-entry → sweep → displacement → CHoCH → retrace → next-bar-open sequence exists in the replay engine. |
| G7 structural invalidation | PARTIAL | Stop = ATR-buffer off POI/sweep/OB extreme (`_determine_stop`); no persisted invalidation-structure ID or reason code distinct from the stop price itself. |
| G8 net reward gate | GAP, but reusable machinery exists | `_cost_to_r` already computes a real spread+slippage+commission→R breakdown per trade from `symbol_metadata`/`config/research_costs.yaml` (commission/swap explicitly `0.0`, correctly labeled an assumption in code — though not surfaced as an assumption in the human-readable report). This is applied **after** entry, to a trade whose target came from a **gross** `min_rr=2.0` fallback (`_determine_target`) — there is no pre-entry `net_available_rr >= 3.0` rejection anywhere today. |
| G9 preselected target | DEFECT CONFIRMED | `_determine_target` picks the nearest M5-window swing extremum, falling back **silently** to `entry ± min_rr*risk` when none exists — i.e. the exact "no-DOL silently passes" defect that `signal_v35.py` already fixed with `REJECT_NO_TARGET`, but that fix was never ported to the replay engine that actually produced the baseline. |
| G10 fixed management | MOST MATURE PART, reusable | `_simulate_trade_detail` already implements +1R → 50% partial → break-even-to-entry, stop-first same-bar ambiguity handling, and `CENSORED_END_OF_DATA` timeout handling with a `management_events` log. Not wired to horizon-based time stops or session/weekend close (those exist separately, and differently, in `backtest_v35.py`). |

## 6. Test and rejection-evidence coverage

- `tests/test_historical_replay.py` — **3 tests total**: happy-path trade+metrics generation, unsorted-data rejection, report-writing. **Zero gate-specific positive/negative fixtures** for bias, structure, location, HTF-FVG, ordering, invalidation, net-RR, or target selection.
- `tests/test_signal_v35.py` — 16 tests, reasonably thorough for its own rules (REJECT_NO_TARGET, RR gate, M1/M3 structure detection, direction-neutrality, determinism) — but exercises a module the baseline doesn't call.
- `tests/test_backtest_v35.py` — 7 tests, thin harness-level coverage only.
- `funnel_counts`/`rejected_candidates` in the replay engine track `session|signal|bias|sweep|poi|risk|target` rejections only — **none of these correspond to E1/E2/E3 causal rejection, displacement rejection, IFVG staleness, net-RR rejection, or premium/discount rejection.** Any new G1–G10 gate trace must introduce new rejection codes; none of the current ones satisfy the "no failed or unknown gate may silently default to pass" requirement for the new contract.

## 7. Cost/management diff: `backtest_v35.py` vs. `historical_replay_engine.py`

- `backtest_v35.simulate_trade`: flat spread-only R-drag (`spread/risk`), no slippage, no commission, no swap, no partials, no break-even — binary/ternary outcome only (`-1.0` / `reward_r` / `0.0`).
- `historical_replay_engine._simulate_trade_detail`: full spread+slippage+commission cost breakdown (symbol-metadata-driven, real point/pip/contract-size lookups), plus a real partial/break-even management simulator with an event log.

**Conclusion: the replay engine's cost and management layers are materially more realistic and should be the retained/extended path for v3.7**, not `backtest_v35.py`'s. `signal_v35.py`'s *signal/structure detection* is the more spec-faithful layer and should be the retained/extended path for the E/M-gate logic. Neither module alone is sufficient; today's architecture duplicates work across all three instead of composing the best parts of each — precisely the "duplicated or competing signal engines" problem this task exists to fix.

## 8. Data availability (for the planned 2×2 ablation)

Local CSVs present for all three required symbols at all three required timeframes: `EURUSD_{M5,H1,D1}.csv`, `GBPUSD_{M5,H1,D1}.csv`, `XAUUSD-VIP_{M5,H1,D1}.csv` (gitignored, local inputs only, per policy). Synthetic-repair counts from Phase A: EURUSD M5 4, GBPUSD M5 15, XAUUSD M5 0 — relevant to the required data-repair sensitivity report.

## 9. Conclusion

The three separating questions from this task's objective map cleanly onto what already exists:

1. **Is the strategy rule completely and objectively specified?** Partially — `specs/v3.6.yaml` is the most complete numeric spec in the repo, but its own `engine_implements_spec: false` interlock and §26 checklist admit it is not fully specified end-to-end (no G4 range-anchor persistence model, no explicit G2 external/protected-structure lifecycle, no G8 net-RR formula).
2. **Does the canonical replay engine enforce the rule point-in-time?** No — the engine that actually produced PR #3's 363-trade baseline enforces a *different, thinner* rule set (v1 legacy signal + ad hoc sweep/POI wrapper), not v3.6/ST-C1 at all.
3. **Does the correctly implemented strategy demonstrate a robust net edge?** Not yet answerable — no implementation exists yet that actually enforces G1–G10 point-in-time, so no such evidence can exist. The Phase A baseline (`PF 0.4272`, expectancy `-0.4116R`) is evidence about the *surrogate*, not about ST-C1/v3.6/v3.7.

No strategy rule was edited to produce this report. Next steps (versioning decision, Research Change Request, `specs/v3.7.yaml`, ST-C1 v1.1.0 contract, canonical engine consolidation, gate-trace schema, tests, and the locked 2×2 ablation) follow in subsequent commits on this branch.
