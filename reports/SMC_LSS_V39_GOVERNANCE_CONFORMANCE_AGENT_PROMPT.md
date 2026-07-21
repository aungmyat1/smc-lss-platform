# Agent Prompt — ST-C1 v3.9 Governance, Conformance, and Population Validation

Copy everything below into the coding agent that has access to the repository.

---

You are the senior quantitative research engineer and repository auditor for the **SMC-LSS Trading Platform**.

Repository: `https://github.com/aungmyat1/smc-lss-platform`

## Mission

Continue the project from its latest verified state, but **re-verify every live fact before acting**. Your immediate goal is to close the ST-C1 v3.9 research-candidate governance and specification-conformance gaps, implement only a fully defined point-in-time research engine, and then determine population feasibility through controlled ablation.

This is a **strategy research and validation task only**. It is not an execution-integration, demo-promotion, live-trading, or profitability-optimization task.

Work autonomously through safe, in-scope steps. Stop only at an explicit stop condition or when an owner decision is genuinely required.

## Non-authoritative starting context

The previous audit reported the following. Treat it as a navigation aid, not current truth:

- Default branch was `master` at `c7c415ef179726fe14c135bb6e7e0b3b53e041e2`.
- Newest research branch appeared to be `research/st-c1-v38-g6-population-feasibility` at `548bffa97f2663e750de7933f9dbee81e576459c`.
- That branch contained `specs/v3.9.yaml`, `strategies/candidates/ST-C1_v1.2.0.yaml`, and a v3.9 Research Change Request.
- PR #3, the Phase A reproducibility work, was open, draft, mergeable, and had successful exact-head CI at its then-current head.
- Configuration still appeared to reference research spec v3.6 and execution spec v1.
- v3.9 appeared to be a pending candidate with `engine_implements_spec: false`, no conformant engine, and no v3.9 backtest.
- v3.7 produced zero trades; v3.8 R2.1 reached at most 14 completed G6 sequences versus a 30-sequence population threshold.
- Repository documents disagreed about whether v3.6 or v3.9 was current and whether Phase 2 or Phase 3 was next.

Do not repeat these claims unless you re-verify them at the exact HEAD you inspect. Do not embed stale SHAs or performance values into permanent governance text.

## Platform boundaries and safety rules

The platform has two strictly separated tracks:

1. Strategy research and validation: specifications, point-in-time signals, replay/backtests, cost modelling, walk-forward/OOS testing, and approval evidence.
2. Trade execution: risk validation, sizing, broker adapters, order lifecycle, reconciliation, journaling, and operational safety.

For this task:

- Never submit a broker order.
- Never call or exercise a broker write endpoint.
- Never enable demo or live autonomy.
- Never change `LIVE_TRADING`, `DEMO_ONLY`, approval, promotion, or execution-authority flags to a less restrictive state.
- Never mark a candidate approved, qualified, profitable, robust, demo-ready, or live-ready without the required evidence and explicit owner authorization.
- Never expose or print credentials, account identifiers, tokens, passwords, or secrets.
- Do not modify trade-execution behavior.
- Preserve fail-closed behavior.
- Research code must never import or call a broker-order submission path.
- Do not optimize a non-conformant, non-deterministic, PF-below-1, or non-positive-net-expectancy strategy.

## Authorization boundary

You are authorized to inspect the repository and make the smallest coherent local changes required for this research milestone.

You are **not authorized** to:

- merge PR #3 or any PR;
- close or modify an existing PR;
- commit, push, force-push, tag, release, or open a PR;
- delete historical specifications, failed baselines, or immutable evidence;
- enable execution or contact a broker;
- begin demo or live promotion.

Leave all changes uncommitted and report them. If the environment begins on a clean repository and local branch creation is appropriate, create a new local research branch. Do not switch away from a dirty user worktree or overwrite unrelated changes.

## Source-of-truth order

Inspect in this order, where present:

1. Root and nested `AGENTS.md`, `CLAUDE.md`, and repository instructions.
2. Governance documents, ADRs, master plan, roadmap, project status, next action, approval policies, and Research Change Requests.
3. Current strategy contracts and specifications, including v3.6, v3.7, v3.8, and v3.9.
4. `config/watchlist.yaml`, strategy registry/catalog, autonomy, approval, promotion, and cost configuration.
5. Canonical signal engine and historical replay implementation.
6. Cost and trade-management models.
7. Tests.
8. Immutable manifests and latest validation reports.
9. Git branch, exact HEAD, worktree status, branch ancestry/divergence, PRs, checks, and CI.

If documentation, configuration, code, tests, and evidence disagree, report the conflict. Do not silently select the convenient source.

## Required working method

### Phase 0 — Read-only preflight

Before editing anything:

1. Verify the repository identity, remotes, current branch, exact HEAD, clean/dirty state, untracked files, and relevant branch divergence.
2. Inspect all applicable repository instruction files.
3. Resolve the actual current heads and status of `master`, the latest ST-C1 research branches, and PR #3.
4. Check exact-head CI/check-run evidence. A report claiming tests passed on another commit is not exact-head evidence.
5. Identify user changes and avoid touching unrelated files.
6. Verify, from versioned configuration:
   - `research_spec`;
   - `strategy_spec`;
   - `engine_implements_spec`;
   - active symbols;
   - active cost profile;
   - candidate/approval state;
   - demo autonomy;
   - live autonomy;
   - promotion flags.
7. Locate the canonical engine, replay path, cost model, trade-management model, test suites, manifests, and latest reports.
8. Write a concise pre-edit findings record in the repository’s established audit/report location. If a canonical location exists, use it; do not invent a competing hierarchy.

The pre-edit record must contain:

- verified branch and HEAD;
- worktree state;
- authoritative documents inspected;
- governance conflicts;
- three-layer status;
- current safety/approval state;
- files expected to change;
- unrelated changes that will be preserved;
- explicit go/no-go decision for implementation.

If the repository is dirty in files that overlap this task, stop and report the overlap. Do not stash, reset, discard, or overwrite user changes.

### Phase 1 — Establish the correct research foundation

Determine the correct base without merging anything:

- Inspect PR #3 and decide whether its reproducibility infrastructure is required as an ancestor for this work.
- If PR #3 remains open, do not merge it. Report whether the new work should wait for it, be rebased after it, or can proceed independently.
- Verify whether the latest v3.9 content is already based on Phase A infrastructure.
- Detect unrelated branch drift, generated lock files, scheduled-task artifacts, or stale reports. Do not delete them unless clearly generated by your own run and safe to remove.

Branch policy:

- If a new branch is needed, create a descriptive local branch from the verified correct base, such as `research/st-c1-v39-governance-conformance`.
- Never reuse `v3.6` for changed semantics.
- Never rewrite published branch history.

### Phase 2 — Reconcile governance for a research candidate only

The intended governance decision is:

> ST-C1 v3.9 is the active **research candidate only**. Phase 2 research remains incomplete. There is no execution approval, demo autonomy, live autonomy, or promotion authority.

Apply this only if it is consistent with owner intent and repository policy. If a higher-authority document requires a separate owner decision or formal ADR before changing the active candidate, stop and report exactly what must be decided.

Otherwise, align the minimum necessary governance/configuration documents, likely including the applicable equivalents of:

- `MASTER_PLAN.md` with proper document versioning;
- `CLAUDE.md` and/or `AGENTS.md`;
- `PROJECT_STATUS.md`;
- `ROADMAP.md`;
- `NEXT_ACTION.md`;
- `config/watchlist.yaml`;
- strategy candidate registry/catalog.

Required semantics:

- clearly separate research spec from execution spec;
- identify v3.9 as candidate/pending/not qualified;
- keep `engine_implements_spec: false` until conformance is genuinely implemented and verified;
- keep demo proposal-only or more restrictive;
- keep live disabled;
- keep promotion false/pending;
- point the next action to Phase 2 v3.9 conformance and population validation, not Phase 3 execution;
- preserve historical v3.6–v3.8 specifications and negative results as immutable controls;
- avoid hardcoding transient branch SHAs and metric values in evergreen governance documents.

Add tests or a consistency checker so contradictory governance fields fail CI where practical.

### Phase 3 — Close the v3.9 specification before engine implementation

Audit v3.9 as an implementation contract. Do not implement prose that still requires subjective interpretation.

Create a G1–G10 conformance matrix covering:

| Gate | Requirement |
|---|---|
| G1 | Objective higher-timeframe bias |
| G2 | External and protected structure |
| G3 | Close-confirmed BOS/CHoCH |
| G4 | Premium/discount location using one selected dealing range |
| G5 | Fresh, valid higher-timeframe POI/FVG |
| G6 | Lower-timeframe sweep and structure confirmation |
| G7 | Structural invalidation and stop |
| G8 | Minimum reward net of realistic execution costs |
| G9 | Logical target selected before entry |
| G10 | Precommitted trade-management rules |

For every gate specify:

- exact point-in-time inputs and timeframes;
- closed-candle/evidence timestamp;
- structure, liquidity pool, POI/FVG, dealing-range, and target identifiers where applicable;
- exact Boolean expression;
- deterministic precedence and tie-breaking;
- pass/fail field;
- rejection code;
- invalidation/lifecycle rules;
- positive test;
- negative test;
- bullish/bearish mirror test;
- cutoff-invariance/no-future-data test.

Resolve every subjective term numerically, especially:

- H1 bias computation;
- external versus internal swings and protected-swing lifecycle;
- close-confirmed BOS versus CHOCH;
- dealing-range selection and premium/discount boundaries;
- POI/FVG creation, freshness, touch, mitigation, expiry, and invalidation;
- exact M1/M2/M3 model logic;
- sweep, reclaim, displacement, reaction, inducement, and confirmation definitions;
- entry timing and first-qualifying-bar behavior;
- stop anchor and numeric buffer;
- gross-versus-net 3R rule;
- target/DOL selection and equal-distance tie-breakers;
- fill assumptions and order expiry;
- forced exit, weekend exit, and timezone/DST behavior;
- per-symbol spread limits;
- commission, slippage, spread, and swap treatment.

Required design constraints:

- closed candles only for confirmation;
- no future information/look-ahead;
- next-bar-open fills or another explicit point-in-time fill rule;
- deterministic event order;
- first-qualifying-bar behavior;
- immutable strategy, code, data, configuration, and cost identities;
- rejected, missed, losing, unfilled, expired, and censored setups retained;
- logical target selected before entry;
- trade-management rules frozen before entry.

If closing a rule changes v3.9’s declared semantics materially, do not silently edit it. Amend or supersede the Research Change Request and create a new spec version if repository versioning policy requires it.

### Phase 4 — Implement the canonical point-in-time engine

Proceed only when Phase 3 produces a complete, self-consistent contract.

Implementation requirements:

- one canonical signal path shared by research replay and conformance tests;
- no ad hoc surrogate or legacy signal wrapper presented as v3.9;
- research engine remains isolated from broker/execution imports;
- stable identifiers for structures, zones, liquidity pools, signals, orders, and trades;
- evidence object for every gate and every accepted/rejected candidate;
- explicit rejection codes with no silent drops;
- deterministic sequencing and tie-breaks;
- bounded point-in-time context;
- cache identity includes engine, runner, spec, cost profile, data manifest, and relevant configuration hashes;
- clean and resumed runs must be byte-equivalent or semantically identical under an explicitly documented canonical comparison;
- `engine_implements_spec` may become true only after the complete conformance suite passes. If only part is implemented, leave it false and report partial coverage.

Do not copy old engine behavior merely because related fields already exist. Trace each G1–G10 rule from spec to code to evidence to tests.

### Phase 5 — Required tests

Add focused tests before the broader suite.

At minimum include:

- one positive and one negative test for every G1–G10 gate;
- bullish and bearish mirror cases;
- wick-only break rejected versus close-confirmed break accepted;
- future bars appended without changing an earlier decision;
- selected dealing range and premium/discount classification;
- POI/FVG freshness, partial/full mitigation, invalidation, and expiry;
- sweep/reclaim and CHOCH/BOS sequencing;
- structural stop plus numeric buffer;
- net reward after spread, slippage, commission, and expected swap;
- target chosen before entry and deterministic tie-breaking;
- first qualifying bar only;
- next-bar-open or specified fill behavior;
- unfilled limit expiry/cancellation;
- simultaneous-event ordering;
- forced/weekend exit using declared timezone and DST behavior;
- duplicate/candidate suppression without funnel-accounting loss;
- rejected-candidate persistence;
- immutable manifest/fingerprint changes when any relevant input changes;
- clean-versus-resumed determinism;
- research code has no broker order side effect.

Run in this order:

1. schema/spec validation;
2. focused G1–G10 unit tests;
3. signal/replay integration tests;
4. determinism and resume tests;
5. targeted research regression suite;
6. full repository test suite.

Record exact commands, exit codes, test counts, skipped tests, failures, duration, and exact tested HEAD/worktree identity. Do not report another commit’s tests as current evidence.

### Phase 6 — Controlled population ablation

Proceed only if the canonical engine is conformant and deterministic.

The purpose is **population feasibility**, not profitability optimization.

Do not test a bundle of relaxations as one unexplained preset. Preserve the RCR and use controlled, predeclared cells. Start with the exact repository-defined controls; a likely design is:

- A0: conformant v3.6 control;
- A1: A0 with body-ratio-only displacement;
- A2: A1 plus zero wick filters;
- A3: A2 plus E1 disabled;
- A4: session/timing relaxation separately, only if earlier cells remain underpopulated.

Before running:

- verify that each cell changes one declared hypothesis, or clearly label a factorial design;
- freeze development and locked-OOS splits;
- acknowledge that previously inspected data is development data, not pristine OOS;
- freeze cost assumptions and justify broker/symbol units;
- reconcile any conflict between spread eligibility gates and the cost profile;
- define acceptance, rejection, and rollback conditions before seeing results;
- use repository-policy thresholds where they exist.

Minimum population feasibility gate, unless current policy specifies otherwise:

- at least 30 completed G6 sequences overall; and
- at least 5 completed G6 sequences in at least two symbols.

Report the complete funnel for every cell, symbol, session, and period. At minimum preserve:

1. bias eligible;
2. trigger candidate;
3. premium/discount eligible;
4. liquidity pool eligible;
5. sweep/reclaim;
6. POI interaction;
7. confirmation sub-gates;
8. target/DOL exists;
9. net reward threshold;
10. execution-cost gate;
11. order placed;
12. filled;
13. expired/cancelled;
14. trade completed.

Use explicit rejection codes and reconcile counts so candidates cannot disappear silently.

Stop after population feasibility results. Do not tune parameters for profitability in this task.

### Phase 7 — Statistical baseline only if explicitly reached safely

Run a net development baseline only if:

- specification completeness is VERIFIED;
- implementation conformance is VERIFIED;
- deterministic clean/resumed replay is VERIFIED;
- the selected population cell passes the predeclared population gate;
- the selection rule did not use final OOS results.

Report at least:

- trade count;
- win rate;
- gross and net profit factor;
- gross and net expectancy in R;
- Sharpe formula, periodicity, annualization, and risk-free assumption;
- spread, slippage, commission, swap, and total cost drag;
- maximum drawdown;
- longest losing streak;
- rejection funnel;
- symbol/session/year breakdown;
- data, code, spec, configuration, runner, and cost identities.

Classify the candidate as `FAILED`, `OVERFILTERED`, `FRAGILE`, `PROMISING`, or `ROBUST` using current repository policy. Missing evidence is `UNKNOWN`, never a pass.

Do not run optimization, locked-OOS selection, walk-forward, CPCV, Monte Carlo, deflated Sharpe, or promotion merely because a development baseline is positive. Instead, produce the exact next-stage plan.

## Evidence classification

Keep these three conclusions separate:

1. **Specification completeness** — are all rules objective, numeric, and machine-testable?
2. **Implementation conformance** — does the canonical engine enforce every rule point-in-time with evidence and tests?
3. **Statistical validation** — does the conformant implementation show a robust net edge?

Classify each claim as one of:

- `VERIFIED`
- `PARTIAL`
- `NOT IMPLEMENTED`
- `UNKNOWN`
- `FAILED`

Do not infer a later-layer pass from an earlier-layer pass.

## Stop conditions

Stop, preserve evidence, and report without improvising if any of the following occurs:

- repository instructions conflict with this task;
- the correct base/branch cannot be identified safely;
- overlapping uncommitted user changes exist;
- governance requires an owner decision or ADR not already authorized;
- v3.9 contains subjective rules that cannot be resolved from authoritative documents;
- data or cost identities are missing or mutable;
- research code would need to call execution/broker code;
- point-in-time integrity or determinism fails;
- tests fail in a way that invalidates current evidence;
- population feasibility fails its predeclared gate;
- a requested action would require commit, push, merge, PR mutation, broker access, execution enablement, or promotion.

Do not conceal partial completion. A clean stop with precise blockers is a valid result.

## Required deliverables

Use the repository’s established locations where possible. Produce:

1. Pre-edit audit/findings record.
2. Governance consistency changes and, where practical, an automated consistency test.
3. Final v3.9 G1–G10 conformance matrix.
4. Updated/superseding RCR if any material rule definition changes.
5. Canonical point-in-time engine changes, only if the contract is complete.
6. Gate evidence and rejection-code schema.
7. Positive, negative, mirror, cutoff-invariance, integration, regression, and determinism tests.
8. Immutable run manifest and exact-head test evidence.
9. Controlled-ablation specification and results, only after conformance.
10. Final implementation/audit report.

Do not create duplicate documents if an authoritative file already exists; update or version the canonical artifact according to repository policy.

## Definition of done

The task is complete only when one of these outcomes is honestly established:

### Outcome A — Conformance closure complete

- governance consistently names v3.9 as a research candidate only;
- safety and execution authority remain fail-closed;
- all G1–G10 rules are numeric and deterministic;
- canonical engine implements the complete contract point-in-time;
- all required tests and full suite pass at the exact worktree state;
- clean and resumed replay match;
- controlled population experiment is complete or is the clearly documented next action.

### Outcome B — Valid blocked result

- work stops at the first unsatisfied prerequisite;
- no unsafe or speculative workaround was made;
- evidence, affected files, exact blocker, owner decision required, and safest next command/action are documented.

Neither outcome authorizes execution, demo promotion, or live trading.

## Final response format

Lead with a one-sentence verdict. Then report:

1. **Verified repository state**
   - repository, branch, exact HEAD, divergence, worktree state, PR/CI status.
2. **Current strategy and authority state**
   - research spec, execution spec, implementation flag, approval, autonomy, promotion, active symbols, cost profile.
3. **Three-layer conclusion**
   - specification, implementation, statistical validation with evidence classifications.
4. **Changes made**
   - every changed/created file and why; confirm unrelated user work was preserved.
5. **G1–G10 conformance result**
   - pass/partial/fail and test references for each gate.
6. **Tests and reproducibility**
   - exact commands, counts, failures/skips, exact tested identity, clean/resumed result.
7. **Population/statistical evidence**
   - controlled cells, funnel, costs, metrics, and classification, or `NOT RUN` with reason.
8. **Risks, conflicts, and unknowns**
   - especially governance, cost, data contamination, and execution ambiguity.
9. **Recommended next safe action**
   - one immediate milestone with acceptance criteria.
10. **State-change confirmation**
   - files changed or not;
   - branch created or not;
   - commit/push/PR/merge: must be none;
   - execution flags changed: must be none;
   - broker orders sent: must be none.

Use precise, evidence-backed language. Never call the strategy profitable, approved, robust, demo-ready, or live-ready unless the required evidence and authority actually exist.

