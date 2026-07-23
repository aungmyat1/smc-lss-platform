# ST-C2 Governance and Specification-Conformance Audit

Audit date: 2026-07-22
Auditor: project-governance-agent (read-only audit; no code/spec/git-state changes)
Branch audited: `research/st-c2-contract-and-conformance`
Local HEAD at audit time: `87552296eb5dbb91be03c8e921a57d7923bd205a` (verified equal to
`origin/research/st-c2-contract-and-conformance`; working tree clean)

This file records, as a permanent repository artifact, the read-only ST-C2 conformance
audit performed in-session. It existed only in conversation until now; this write closes
that gap so the audit is checkable against the repository going forward, per the
Verification Principle (`project-governance-agent.md`): claims must be checkable against
files, not against prior conversation turns.

Scope: read-only. No file was created, edited, or deleted to produce the analysis below
(other than this record itself, written after the analysis was complete). No backtest was
run. No git state (commit/branch/stash/reset) was touched. No PM-Agent/Code-Agent
scaffold, `agents/workflow.md`, `docs/roadmap.md`, or alternative governance/agent-
authority file was created — a prior proposal to add those was already reviewed and
rejected in an earlier session and is not reopened here.

---

## A. Executive verdict

ST-C2 implementation **may NOT start**. Backtesting **may NOT start**. Demo/live state
changed: **NO**. The RCR (`reports/audit/ST_C2_HYBRID_LIQUIDITY_FIRST_RCR.md`) is filed,
logged, and committed per `docs/RESEARCH-CHARTER.md`'s six-question template, but it
explicitly states it "does not authorize implementation on its own" and is "awaiting
explicit `project-governance-agent`/owner authorization" — no such authorization was
recorded anywhere in the repo at audit time (`NEXT_ACTION.md`, `reports/research_log.md`,
and git history were all checked; none showed an authorization decision, only a
filed-and-pending state). Independent of that procedural gate, the RCR and
`specs/st-c2.yaml` were not implementation-ready on their own merits: the
population-feasibility floor was explicitly deferred until after signal counts are
observed (a real pre-registration/degrees-of-freedom gap, not just a formality),
`specs/st-c2.yaml` contained an internal, unresolved numeric conflict between
`t1_liquidity.rr_min: 2.0` and `risk.min_rr: 3.0`, and most of the ten gates lacked the
exact deterministic rules (zone boundaries, tie-breaks, entry price formula,
stop-buffer units, freshness/invalidation, rejection codes) needed for a point-in-time
engine. Primary decision at audit time: **RCR_ADDENDUM_REQUIRED**.

(See the separate addendum filed to `ST_C2_HYBRID_LIQUIDITY_FIRST_RCR.md` for the
owner's subsequent written decisions closing most of these gaps. This audit record is
not itself updated retroactively — it stands as the finding that triggered the
addendum, per the research log's "never overwrite a prior entry" convention.)

## B. Verified repository state

| Field | Value |
|---|---|
| Repository | `smc-lss-platform` (`https://github.com/aungmyat1/smc-lss-platform.git`) |
| Checked-out branch | `research/st-c2-contract-and-conformance` |
| Local HEAD | `87552296eb5dbb91be03c8e921a57d7923bd205a` |
| Target remote HEAD (`origin/research/st-c2-contract-and-conformance`) | `87552296eb5dbb91be03c8e921a57d7923bd205a` |
| Local/remote match | YES — up to date |
| `git status` | clean |
| Base branch | `master` at `c7c415ef179726fe14c135bb6e7e0b3b53e041e2` |
| Divergence from master | 107 files changed, +91,622/-14,295 (inherited ST-C1 v3.7-v3.10 research line plus ST-C2's RCR/spec — this branch carries more than ST-C2 alone) |
| PR state | None found for this branch |
| CI state | Latest run: `CI` workflow, run `29919294411`, success, completed |

## C. Strategy and authority state

| Field | Value |
|---|---|
| Active execution spec | `specs/v1.yaml` (`config/watchlist.yaml: strategy_spec`; ADR-0001 "sole execution authority") |
| Configured research spec | `specs/v3.6.yaml` (`config/watchlist.yaml: research_spec`) — **not** `specs/st-c2.yaml`; ST-C2 is not wired into the config loader |
| ST-C1 disposition | **PARKED** (v3.9 and v3.10) — `PROJECT_STATUS.md` §5 / `ROADMAP.md` Phase 2: v3.9 aggregate net PF 0.138, v3.10 aggregate net PF 0.471, both ~10x below the PF >= 1.3 / expectancy >= +0.2R bar, every symbol of both candidates. Retained, not deleted. |
| ST-C2 disposition | RCR filed, not yet authorized. No engine, no candidate-contract file, no tests, no dedicated agent files. |
| `engine_implements_spec` (`specs/st-c2.yaml`) | `false` |
| Approved strategy | None |
| Cost profile | `config/research_costs.yaml` v1: XAUUSD spread 25.0 pts / slippage 5.0 pts / commission 0 / swap 0 |
| Active symbols (ST-C2) | XAUUSD only (`enabled: true`); EURUSD/GBPUSD both `enabled: false` |
| Demo autonomy | `proposal_only` |
| Live autonomy | `disabled` |
| Promotion state | `promote_to_live: false` |

## D. Three-layer validation table

| Layer | Classification | Evidence |
|---|---|---|
| Spec completeness | **PARTIAL** | `specs/st-c2.yaml` defines thresholds/structure for all six pipeline stages, but omits exact deterministic formulas/tie-breaks/rejection codes for most gates; contains one unresolved internal numeric conflict (G8). |
| Implementation conformance | **NOT IMPLEMENTED** | No `src/signal_stc2.py` (or equivalent), no dedicated replay engine, no `tests/test_*st_c2*` anywhere in the repo. `engine_implements_spec: false` correctly reflects this. |
| Statistical validation | **UNKNOWN** | No backtest has been run; no population-feasibility floor was precommitted at audit time. |

## E. Governance conflict matrix

| ID | Source A | Source B | Conflict | Higher authority | Resolution required |
|---|---|---|---|---|---|
| GC-1 | `CLAUDE.md` "Spec version status" paragraph — `specs/v3.5.yaml` "version of record" | `MASTER_PLAN.md` v3.0.0 + ADR-0001 (Accepted 2026-07-19) — v3.5/v1 legacy, `specs/v1.yaml` sole execution authority | Stale paragraph inside `CLAUDE.md` predates and contradicts a higher-authority, later-dated Accepted ADR | `MASTER_PLAN.md` + ADR-0001 | Does not block ST-C2. Cosmetic cleanup only, no owner action required to proceed with ST-C2. Category B (pre-existing, non-blocking). |
| GC-2 | `AGENT_ALIGNMENT.md` — "Research: SMC-LSS v3.5" | `config/watchlist.yaml` (`research_spec: specs/v3.6.yaml`) + ADR-0001 | Stale summary line | `config/watchlist.yaml` + ADR-0001 | Non-blocking, cosmetic. Does not involve ST-C2. |
| GC-3 | Prior audit-session framing ("Execution: `specs/v1.yaml`... Research: `specs/v3.5.yaml` is a research candidate") | Repo evidence: `config/watchlist.yaml`, `MASTER_PLAN.md` v3.0.0, ADR-0001 | Framing given at audit start was stale relative to the repo's current, later-dated state | Repo evidence per the Verification Principle | Does not affect ST-C2 scope or this audit's conclusions. |
| GC-4 | `specs/st-c2.yaml` internal — `t1_liquidity.rr_min: 2.0` | `specs/st-c2.yaml` internal — `risk.min_rr: 3.0` | Unclear whether a 2R T1 partial target is compatible with an overall 3R entry-eligibility floor | N/A — internal spec conflict | Blocking at audit time. **Resolved by owner decision 1** in the RCR addendum (T1 >= 2.0R AND a preselected T2 >= 3.0R net, both required). |

No conflict was found between `MASTER_PLAN.md`, `PROJECT_STATUS.md`, `ROADMAP.md`,
`NEXT_ACTION.md`, `docs/CHARTER.md`, or `docs/RESEARCH-CHARTER.md` regarding ST-C2's
phase, disposition, or authorization state.

`AGENTS.md` does not exist in this repository (confirmed absent via full-tree search).
`agents/workflow.md`, `docs/roadmap.md`, and `SMC_LSS_V39_GOVERNANCE_CONFORMANCE_AGENT.md`
also do not exist, as expected. `reports/SMC_LSS_V39_GOVERNANCE_CONFORMANCE_AGENT_PROMPT.md`
exists and is correctly treated as historical/superseded narrative only.

## F. Ten-gate conformance matrix (at audit time)

All gates: classification **PARTIAL** at audit time (thresholds exist; exact deterministic
semantics mostly absent). Implementation status for all: **NOT IMPLEMENTED**.

| Gate | Defined evidence | Missing/ambiguous rules (at audit time) | Required tests | Required rejection code |
|---|---|---|---|---|
| G1 HTF bias | `bos.confirmation_bars: 2`, `close_beyond_structure_required: true`, `choch.displacement_body_ratio_min: 0.6`, `reclaim_window_bars: 5` | Swing definition; bull/bear classification; protected-structure lifecycle; same-bar BOS/CHoCH tie-break; evidence timestamp | Positive/negative/tie-break/cutoff-invariance | `BIAS_UNAVAILABLE`, `BIAS_AMBIGUOUS` |
| G2 external/protected structure | `lookback_bars_htf: 300`, `equal_highs/lows_tolerance_pips: 5` | External vs internal swing distinction; protected high/low lifecycle; multi-candidate selection; stable identifiers | Positive/negative/duplicate-identity | `STRUCTURE_UNCONFIRMED` |
| G3 close-confirmed BOS/CHoCH | `confirmation_bars: 2`, `close_beyond_structure_required: true`, `displacement_body_ratio_min: 0.6` | Wick-probe rejection detail; BOS-vs-CHoCH classification boundary; first-counter-trend-break vs later-shift; same-bar ambiguity | Positive/negative/mirror/same-bar-ambiguity | `STRUCTURE_UNCONFIRMED` |
| G4 premium/discount | `fib_anchor_mode: swing_extremes`, `discount/premium_threshold: 0.5`, `max_retrace_pct: 0.786` | Dealing-range anchor tie-break; equilibrium (exactly 0.5) treatment; range invalidation/reselection | Positive/negative/boundary(0.5 exact) | `WRONG_PREMIUM_DISCOUNT` |
| G5 fresh/valid HTF POI/FVG | `min_displacement_bars: 3`, `max_age_bars: 60/20`, `must_overlap_htf_fvg: true`, `max_distance_pips: 10` | No 3-candle FVG size formula; no zone-boundary formula; freshness/partial-vs-full mitigation and penetration % undefined; expiry vs invalidation undistinguished; multi-zone tie-break | Positive/negative/mirror/expiry-boundary | `POI_STALE_OR_INVALID` |
| G6 LTF sweep + structure confirm | `wick_ratio_min: 0.6`, `close_back_in_range_required: true`, `max_sweep_age_bars_htf: 20`, `internal_bos_required: true`, `displacement_body_ratio_min: 0.5`, `max_setup_bars: 20`, `entry_window_bars: 15` | Eligible-liquidity-pool priority order; reclaim-close timing; confirmation-window vs entry-window relationship; first-qualifying-bar behavior | Positive/negative/window-boundary/cutoff-invariance | `SWEEP_NOT_RECLAIMED`, `CONFIRMATION_MISSING` |
| G7 structural invalidation/stop | `mode: structural_invalidation`, `buffer_pips: 2` | Exact stop anchor; buffer unit ambiguity (pips vs points on XAUUSD); min/max distance; broker-precision rounding; same-bar stop/entry ambiguity | Positive/negative/precision-rounding | `STOP_INVALID` |
| G8 net reward after costs | `t1_liquidity.rr_min: 2.0`, `t2_deeper_liquidity.rr_min: 3.0`, `t3_extension.rr_min: 5.0 (disabled)`, `risk.min_rr: 3.0` | **Unresolved internal conflict** (GC-4); no gross-vs-net R formula; no cost-profile identity cited | Net-R computation positive/negative, cost-gate boundary | `NET_R_INSUFFICIENT`, `COST_PROFILE_MISSING` |
| G9 logical target before entry | T1/T2/T3(disabled) hierarchy present | Deterministic T1/T2 selection rule; "known before entry" requirement not explicit; tie-break; 2R-T1-vs-3R-floor coexistence unresolved | Target-selection positive/negative/tie-break | `TARGET_MISSING` |
| G10 precommitted trade management | `break_even_activation_r: 1.5`, `partial_take_r: 2.0`, `partial_take_fraction: 0.5`, `runner_enabled: true` | No time stop; no session-close rule; no emergency-exit rule; no cancellation/limit-expiry rule | Positive/negative for each management rule | `SESSION_INELIGIBLE` |

**Entry/order-simulation rules** (`execution_stage.entry`): only `type: limit_into_fvg`,
`max_slippage_points: 5` were defined at audit time. Missing: exact limit price within the
FVG, placement timestamp, earliest eligible fill bar, next-bar vs same-bar fill policy,
bid/ask treatment, gap-through handling, partial-fill policy, limit expiry, cancellation
triggers, same-candle entry/stop/target ambiguity, deterministic event-priority ordering,
one-position/duplicate-setup behavior. This was the least-specified area of the spec.

## G. RCR completeness matrix (at audit time)

| Pre-registration item | Status | Evidence |
|---|---|---|
| Hypothesis | VERIFIED | RCR states the conjunctive multi-timeframe mechanism explicitly |
| Permitted symbols/timeframe | VERIFIED | XAUUSD only, H4/M15/M3 |
| Development period | NOT IMPLEMENTED | Not stated |
| Validation period | NOT IMPLEMENTED | Not stated |
| Sealed OOS period | NOT IMPLEMENTED | Not stated; `PROJECT_STATUS.md`'s existing data-reuse warning applies |
| Minimum signal/trade count | PARTIAL | Existence check only (>=1 signal); population floor explicitly deferred |
| Primary/secondary metrics | NOT IMPLEMENTED | Not named |
| Cost model | NOT IMPLEMENTED | RCR never cites `config/research_costs.yaml` or a net-of-cost formula |
| Acceptance/rejection criteria | PARTIAL | Rollback given; no ACCEPT criteria beyond existence |
| Rollback condition | VERIFIED | Stated |
| Allowed parameter changes | NOT IMPLEMENTED | Not addressed |
| Max experiment count | NOT IMPLEMENTED | Not addressed |
| Multiple-testing controls | NOT IMPLEMENTED | Not addressed |

**Determination on the deferred population threshold:** not a strict textual violation of
`docs/RESEARCH-CHARTER.md` (a criterion — existence — is stated), but it does create
researcher degrees of freedom consistent with what the charter's deflated-Sharpe/
multiple-testing rationale exists to prevent. Material enough to require an RCR addendum
before implementation, not merely a note. (See addendum, owner decision 12.)

## H. Blocking defects (at audit time)

P0 (safety/authority): none found.

P1 (blocks deterministic implementation): G8/G9 `rr_min` conflict; missing
entry/order-simulation determinism; missing exact zone-boundary/tie-break/freshness
formulas across G2, G4, G5, G6, G7.

P2 (blocks valid baseline): no cost-model citation in the RCR; deferred
population-feasibility floor; no development/validation/sealed-OOS partition defined.

P3 (reporting/maintainability): no `strategies/candidates/ST-C2_v1.yaml`-style normalized
candidate-contract file paired with `specs/st-c2.yaml` (process inconsistency vs. the
ST-C1 pattern, not blocking); `src/smc_engine.py` gained one new, purely additive function
(`resample()`) inherited from the earlier ST-C1 v3.10 data-gap fix — verified non-strategy-
contaminating; stale text in `CLAUDE.md`/`AGENT_ALIGNMENT.md` re: v3.5.

## I-L

See the addendum to `reports/audit/ST_C2_HYBRID_LIQUIDITY_FIRST_RCR.md` for the owner's
12 written decisions closing most of the above gaps, the resulting G1-G10 closure state,
and the remaining blockers. This audit performed no writes at the time it was produced:
files changed: none; files created: none (until this record); commits: none; branches
changed: none; pushes: none; PRs: none; strategy settings changed: none; configuration
changed: none; execution state changed: none; broker orders: none.

## Post-addendum status update (2026-07-23)

The sections above (A-L) are the original, unedited audit findings — preserved as the
finding that triggered the addendum, per the research log's "never overwrite a prior
entry" convention. This section records the outcome *after* the owner's 12 recorded
decisions were applied in the addendum, including a correction to that addendum's own
initial G7 classification.

**Gate status after the addendum (documentation-only; no engine exists):**

| Gate | Status | Note |
|---|---|---|
| G1 | PARTIAL | same-bar BOS/CHoCH ambiguity closed; swing definition + protected-structure lifecycle open |
| G2 | PARTIAL | pool selection/tie-break closed; internal/external distinction + identifier composition open |
| G3 | PARTIAL | BOS/CHoCH classification boundary closed; wick-probe mechanics + multi-CHoCH sequencing open |
| G4 | **NOT DEFINED** | entirely open — no owner decision addresses dealing-range anchors, equilibrium treatment, or reselection |
| G5 | PARTIAL | freshness/invalidation rule closed; FVG formation formula, zone-boundary definition, multi-zone tie-break, rounding convention open |
| G6 | PARTIAL | fill timing + expiry closed; sweep reclaim-close timing + window relationship + first-qualifying-bar detection open |
| G7 | **PARTIAL at the complete-contract level** | decision 6 closes stop anchor, buffer, rounding direction, and precision; minimum/maximum stop-distance sanity bounds remain undefined. (Correction: the RCR addendum originally stated G7 was "fully closed" — that was inaccurate given the audit's own §F table had already flagged "min/max distance" as a required G7 rule; corrected here and in the addendum on 2026-07-23.) |
| G8 | Closed by recorded owner decisions | rr_min conflict resolved (decision 1); cost model + fail-closed pinned (decision 10) |
| G9 | Closed by recorded owner decisions | T1/T2 both-mandatory, pre-entry selection pinned (decisions 1 and 7) |
| G10 | PARTIAL | pre-fill limit expiry closed; post-fill time-stop/session-close/emergency-exit open |
| Order simulation | PARTIAL | price/timing/expiry/same-bar priority closed; bid/ask, gap-through, partial-fill, duplicate-setup open |

**Consolidated remaining-blockers list (post-addendum, so a reader consulting only this
list does not need the per-gate prose above to find the G7 item):**

1. G1/G2 — HTF/external swing definition, external-vs-internal distinction, protected
   high/low lifecycle.
2. G2 — exact composition of the "stable identifier" tie-break field.
3. G3 — wick-probe-rejection mechanics; first-break-vs-later-shift distinction.
4. G4 — dealing-range anchor tie-break, equilibrium (0.5 exact) treatment, range
   invalidation/reselection. Entirely open.
5. G5 — 3-candle FVG formation/size formula, zone-boundary definition, multi-zone
   tie-break, penetration-ratio rounding convention.
6. G6 — liquidity-sweep reclaim-close timing; `max_setup_bars` vs. 15-bar expiry
   relationship; first-qualifying-bar behavior for LTF CHoCH detection.
7. **G7 — minimum and maximum stop-distance sanity bounds remain an owner/
   specification decision.**
8. G10 — time stop / session-close / emergency-exit rules for an already-filled
   open position.
9. Order simulation — bid/ask treatment, gap-through handling, partial-fill policy,
   concurrent duplicate-setup handling.
10. RCR pre-registration — primary/secondary metrics, allowed parameter changes,
    maximum experiment count, multiple-testing controls, exact development/
    validation/sealed-OOS calendar boundaries (decision 11 sets the policy, not the
    dates).

**Statistical preregistration:** PARTIAL — decisions 11 and 12 close the OOS-integrity
policy and the population/statistical-claim floors (>=30 for feasibility, >=100 before
any statistical claim), but primary/secondary metrics, allowed parameter changes,
maximum experiment count, and multiple-testing controls remain unaddressed (item 10
above).

**Specification completeness:** PARTIAL. **Implementation conformance:** NOT
IMPLEMENTED (no engine exists). **Statistical validation:** UNKNOWN (no backtest run).
`engine_implements_spec: false`. Approved strategy: none. Demo autonomy:
`proposal_only`. Live autonomy: `disabled`. Promotion: `false`. None of this state
changed by the addendum or this correction — both are documentation-only.

The canonical-specification-path question (whether/when a versioned file such as
`specs/st-c2_v1.1.0.yaml` is created to carry the closed portions of this contract)
remains open and unresolved by this correction, exactly as left in the prior report —
no path is chosen and no such file is created here.

This correction performed no writes beyond this file and the RCR addendum: no code,
no `specs/*.yaml` mutation, no backtest, no execution/demo/live/promotion state change,
no broker operation.
