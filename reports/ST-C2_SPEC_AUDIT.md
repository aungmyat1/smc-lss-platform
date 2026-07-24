# ST-C2 Specification Audit — Consolidation Pass

**Date:** 2026-07-24
**Scope:** consolidate `specs/st-c2.yaml` (v1.0.0) plus all four addenda in
`reports/audit/ST_C2_HYBRID_LIQUIDITY_FIRST_RCR.md` into
`specs/st-c2_v1.1.0.yaml`; verify every rule is deterministic, measurable,
and testable; flag every remaining placeholder, assumption, or owner
decision explicitly. No strategy logic modified, no parameters optimized,
no production code written. This document and its companion
`reports/ST-C2_IMPLEMENTATION_READINESS.md` are the deliverables for that
task.

**Method:** direct re-read of `specs/st-c2.yaml`, the full RCR file
(all four addenda), `config/research_costs.yaml`, `docs/CHARTER.md`'s risk
envelope, and the prior governance audit
(`reports/audit/ST_C2_GOVERNANCE_CONFORMANCE_AUDIT.md`) for its original
gate-by-gate requirement table. Every closure claim below cites the
specific addendum/decision number that closed it. Every open item is
listed explicitly — none is filled by inference beyond what is labeled
`applied:` in the consolidated spec (a low-risk, flagged, direct
application of an already-recorded decision, distinct from a fresh
decision).

---

## 1. Gate-by-gate matrix

Baseline requirement per gate: the original governance audit's §F table
(`ST_C2_GOVERNANCE_CONFORMANCE_AUDIT.md`), which enumerated exactly what a
deterministic point-in-time engine would need for each gate. Status below
reflects the state after all four RCR addenda plus this consolidation
pass's own re-check.

| Gate | Status | Closed by | Residuals (still open) |
|---|---|---|---|
| G1 — HTF bias | **PARTIAL** | Same-bar BOS/CHoCH tie-break: 1st addendum decision 5. Swing fractal window (k=3): 3rd addendum Cluster 1 Q1. Protected-structure lifecycle: 3rd addendum Cluster 1 Q3. | Bull/bear classification rule never explicitly stated (mechanically implied, not decided). Bias-evidence-timestamp field never specified. Both new findings from this pass — see §3. |
| G2 — external/protected structure | **CLOSED** | Multi-candidate pool tie-break (distance → timestamp → identifier): 1st addendum decision 3. External-vs-internal swing distinction: 3rd addendum Cluster 1 Q2. Protected high/low lifecycle: shared with G1 (3rd addendum Cluster 1 Q3). Pool-level stable-identifier composition (SHA-256 of structural attributes): **6th addendum, Decision 2.** | None. |
| G3 — close-confirmed BOS/CHoCH | **CLOSED** | Same-bar classification boundary: 1st addendum decision 5. Wick-probe-rejection mechanics: 3rd addendum Phase 1 (existing convention, `close_beyond_structure_required` + choch-bos skill). Multi-CHoCH sequencing (2nd/3rd): 3rd addendum Cluster 1 Q4. | 4th+ CHoCH has no rule — narrow, see §3, not treated as blocking G3's core closure. |
| G4 — premium/discount location | **CLOSED** | All five sub-items (swing source, range-freeze policy, anchoring-swing invalidation, equilibrium boundary, OTE band) closed in full by 2nd addendum. | None. |
| G5 — fresh/valid HTF POI/FVG | **CLOSED** | Freshness/invalidation rule (50% mitigation): 1st addendum decision 4. Rounding convention: 3rd addendum Cluster 3 Q10. HTF-MTF alignment, LTF placement, size-validation source, no-stacking, cascade-invalidation: all 2nd addendum G5 rules 1-5. Multi-zone tie-break: 3rd addendum Cluster 3 Q9. Zone-boundary formula (wick-to-wick displacement, verified against `src/smc_engine.py`'s `fvgs()`): **6th addendum, Decision 1.** | None. |
| G6 — LTF sweep + structure confirmation | **CLOSED** (one flagged low-risk item) | Fill timing, expiry/cancellation: 1st addendum decisions 2, 8, 9. `max_setup_bars` vs `entry_window_bars` relationship: 3rd addendum Cluster 2 Q5. First-qualifying-bar rule: 3rd addendum Cluster 2 Q6. Sweep reclaim-close timing: 3rd addendum Cluster 2 Q7. LTF displacement/close-confirmation fields: 3rd addendum Phase 1 (existing convention). | `internal_bos_required`'s definition is only *implied* by Cluster 1 Q2's external/internal rule ("unblocks" it, per the 3rd addendum's own text) — never explicitly restated as a closure. Low-risk, flagged in the consolidated spec as `applied:`, recommend one-line owner confirmation. |
| G7 — structural invalidation/stop | **CLOSED** | Anchor/buffer/rounding: 1st addendum decision 6. Min/max stop-distance bounds (35/150 points) and the out-of-bounds behavior: 2nd addendum G7 decisions 1-4. | None. |
| G8 — net reward after costs | **CLOSED** | `rr_min` conflict resolution and cost model: 1st addendum decisions 1, 10. Cost profile verified present (`config/research_costs.yaml` XAUUSD row: spread 25.0 pts, slippage 5.0 pts, commission 0, swap 0). | None. |
| G9 — logical target before entry | **CLOSED** | T1/T2 both-mandatory, pre-entry selection: 1st addendum decisions 1, 7. | None. |
| G10 — precommitted trade management | **CLOSED** | Pre-fill limit expiry: 1st addendum decision 8. Time stop (none, structure/R-based only): 3rd addendum Cluster 4 Q11. Emergency-exit concept + triggers: 3rd addendum Cluster 4 Q12. Portfolio-level loss circuit breaker (`risk.hard_kill_switch`, PROVISIONAL): 5th addendum, Decision B. Session-close-forces-exit (conditional, near invalidation only): 6th addendum, Decision 3. Emergency-exit thresholds ratified PROVISIONAL working values (20 pts / 60 s): 6th addendum, Decision 5. Invalidation-buffer distance (2.5 points, final): **7th addendum.** | None substantive. A units flag (pips vs. points, resolved as points per established `buffer_pips` precedent) is recorded in the 7th addendum — low-risk, not blocking. |
| Entry / order-simulation | **CLOSED** | Exact limit price, placement/confirmation timing, next-bar fill: 1st addendum decisions 2, 9. Limit expiry/cancellation: decision 8. Same-bar entry/stop/target ambiguity (stop-first): decision 9. Bid/ask (mid-price): 3rd addendum Cluster 4 Q13. Gap-through (fill-at-open): Q14. Partial-fill (accept + scale): Q15. `duplicate_setup_policy` (one_position_at_a_time, log-only): 5th addendum, Decision A. Post-fill event-priority ordering (stop → target → management → diagnostics): **6th addendum, Decision 4.** | None. |
| RCR pre-registration | **CLOSED** | Primary/secondary metrics, multiple-testing control, OOS boundary, max experiment count, allowed-parameter-changes list: all 2nd addendum. Population-feasibility (30) / statistical-claim (100) floors: 1st addendum decision 12. | None. |

**Summary (updated after the seventh addendum, 2026-07-24):** 10 of 12
rows fully CLOSED (G2, G3, G4, G5, G7, G8, G9, G10, order-simulation, RCR
pre-registration), 1 CLOSED with one flagged low-risk item (G6), and 1
PARTIAL (G1 — two low-risk items, non-blocking). No substantive blockers
remain.

---

## 2. Cross-checks performed this pass

- **Cost profile citation (G8, decision 10):** `config/research_costs.yaml`
  v1 confirmed to contain the exact XAUUSD row the 2nd addendum's G7
  rationale assumed (spread 25.0 pts + slippage 5.0 pts = the 30-point
  cost-noise floor behind the 35-point minimum stop distance). Consistent,
  no discrepancy found.
- **Risk block vs. `docs/CHARTER.md`:** `specs/st-c2.yaml`'s
  `per_trade_risk_pct` (0.5%), `max_positions` (3), and `daily_loss_pct`
  (3%) match CHARTER's platform-wide figures exactly. `min_rr` (3.0) and
  `portfolio_heat_pct` (3.0%) are both **stricter** than CHARTER's floor/
  ceiling (2.0 min RR, 4% heat) — a candidate-level tightening, not a
  conflict. `weekly_loss_pct` (7.0%) has no CHARTER equivalent to check
  against; not flagged as a conflict, just unmatched.
- **Original `specs/st-c2.yaml` retained, not deleted or overwritten.**
  `specs/st-c2_v1.1.0.yaml` is additive, matching the disposition every
  addendum already committed to.

---

## 3. New findings from this consolidation pass (not previously flagged)

Produced by re-deriving the full gate matrix from source documents rather
than trusting prior summaries at face value — consistent with this
project's established verification practice.

1. **G2's "stable identifier" was never actually closed — a scope
   conflation, now separated.** The 4th addendum's task (assigned by the
   prior governance-sequencing turn) was framed as verifying "G2's stable
   identifier tie-break field composition." What it actually verified was
   the **replay-engine deduplication key** (repeat-detection of one
   still-valid setup across successive evaluation bars). Decision 3 (1st
   addendum) needs a **different** identifier — one that distinguishes
   between multiple *simultaneously-qualifying liquidity pools* for the
   tie-break chain (distance → timestamp → identifier). These are related
   but distinct concepts; closing one does not close the other. **Closed
   2026-07-24: the sixth addendum's Decision 2 (SHA-256 hash of structural
   attributes) closes the pool-level identifier specifically, leaving all
   three now-distinct identifier mechanisms (dedup key, pool identifier,
   duplicate-setup policy) separately decided.**
2. **G5's FVG zone-boundary formula was never pinned**, only its "mode."
   Cluster 3 Q8 answered "fixed 3-candle geometry, not variable-length" —
   a real closure of *one* ambiguity — but the actual formula (which
   candles' highs/lows form the gap boundaries) was never stated by any
   decision, and the codebase's `fvgs()` function was independently found
   (in the 2026-07-23 deferred-gates companion review) not to cleanly
   match this stage's fields. **Closed 2026-07-24: the sixth addendum's
   Decision 1 adopts wick-to-wick displacement, and this pass verified
   directly against `src/smc_engine.py:135-143` that `fvgs()` already
   implements exactly that formula — the claimed ST-C1-lineage precedent
   checked out.**
3. **G1's bull/bear classification rule and bias-evidence-timestamp field**
   were named as required in the original governance audit's gate table
   but never addressed by any of the four addenda. Likely mechanical/
   low-effort to close, but per this task's "resolve nothing by
   assumption" instruction, listed here rather than silently treated as
   obvious.
4. **G10's "session-close forces exit" is distinct from "time stop" and
   was never separately answered.** Cluster 4 Q11 answered "no time
   stop," which plausibly extends to "no forced session-close exit
   either" — but the original governance audit explicitly named these as
   two separate open items, and no decision text says so explicitly.
   Not assumed closed here. **Partially closed 2026-07-24: the sixth
   addendum's Decision 3 answers the concept (conditional exit, near
   invalidation only) but not the numeric "invalidation-buffer distance"
   — one number still missing, not assumed from the unrelated G7 stop
   buffer.**
5. **Order-simulation's post-fill event-priority ordering is a distinct,
   unaddressed question from decision 9's entry/stop/target scope.**
   Decision 9 (1st addendum) resolves same-bar ambiguity between entry,
   stop, and target only. It says nothing about priority when multiple
   *management* events (breakeven activation, partial-take, runner
   activation, stop) could apply on the same bar to an already-open
   position. New gap, not previously listed anywhere. **Closed 2026-07-24:
   the sixth addendum's Decision 4 (stop → target → management →
   diagnostics) is a complete, deterministic total ordering.**
6. **4th+ CHoCH sequencing has no rule.** Cluster 1 Q4 only covers the
   2nd and 3rd CHoCH. Narrow edge case, not treated as blocking G3's
   overall closure, but listed for completeness.
7. **`protected_level_lifecycle.create_on: bos_confirmed`** in the
   consolidated spec is an `applied:` (not `decided:`) field — inferred
   directly from the strategy document's own terminology ("protected low"
   is, by definition in the source document, a post-BOS structure), not
   from a numbered owner decision. Low risk, but labeled distinctly from
   genuine decisions per this task's instruction not to blur the two.
8. **Rejection codes are carried from the original governance audit's own
   proposed naming, not separately owner-ratified.** Included in the
   consolidated spec (§6) for completeness and testability, but flagged
   as non-blocking, low-risk, and worth a one-line confirmation (or
   silent acceptance) at implementation time rather than presented as an
   owner decision.
9. **(Added 2026-07-24, fifth addendum) A proposed "emergency_exit"
   decision did not close the emergency-exit numeric-threshold gap
   flagged above.** A governance-restructuring proposal offered
   `max_daily_loss_pct`/`max_weekly_loss_pct`/`hard_kill_switch_enabled`
   under the name "emergency exit." Checked against source: those numbers
   already existed as `risk.daily_loss_pct`/`weekly_loss_pct`; the new
   content is enforcement behavior (disable entries, conditional close,
   manual re-auth), recorded as `risk.hard_kill_switch` (PROVISIONAL).
   The actual open item — spread-spike/connection-loss numeric thresholds
   for `management.emergency_exit_rules`'s immediate-market-exit concept —
   remains unresolved. Recorded as its own item, not merged into finding 4
   above, to keep the distinction visible for future readers.

---

## 4. Full list of unresolved items (nothing here is resolved by this audit)

| # | Item | Gate | Blocking? | Status |
|---|---|---|---|---|
| 1 | ~~`duplicate_setup_policy` exact value~~ | Order-simulation | — | **CLOSED, 5th addendum Decision A** |
| 2 | ~~Emergency-exit numeric thresholds~~ (ratified as PROVISIONAL working values) | G10 | — | **CLOSED (provisional), 6th addendum Decision 5** |
| 3 | ~~FVG zone-boundary formula~~ | G5 | — | **CLOSED, 6th addendum Decision 1 (verified against code)** |
| 4 | ~~Liquidity-pool "stable identifier" composition~~ | G2 | — | **CLOSED, 6th addendum Decision 2** |
| 5 | ~~Bull/bear classification rule~~ | G1 | — | **CLOSED, 8th addendum Decision 1 (HTF BOS+CHoCH only)** |
| 6 | ~~Bias-evidence-timestamp field~~ | G1 | — | **CLOSED, 8th addendum Decision 2** |
| 7 | ~~Session-close invalidation-buffer distance~~ | G10 | — | **CLOSED, 7th addendum (2.5 points, final)** |
| 8 | ~~Post-fill event-priority ordering~~ | Order-simulation | — | **CLOSED, 6th addendum Decision 4** |
| 9 | ~~4th+ CHoCH sequencing rule~~ | G1/G3 | — | **CLOSED, 8th addendum Decision 3 (keyed to existing HTF displacement threshold)** |
| 10 | ~~`protected_level_lifecycle.create_on`~~ | G1 | — | **CLOSED, 9th addendum Decision 10 — recorded as a revision (CHoCH-triggered, not BOS-triggered), not a mere confirmation** |
| 11 | ~~`internal_bos_required` explicit restatement~~ | G6 | — | **CLOSED, 9th addendum Decision 11** |
| 12 | ~~Rejection code strings~~ | All gates | — | **CLOSED, 10th addendum — R1-R7 ratified, replacing the prior 12-code scheme.** Coverage gap flagged (no distinct code for stop-invalidity/net-R-insufficient/cost-profile-missing/target-missing), non-blocking residual. |
| 13 | `risk.hard_kill_switch` — PROVISIONAL, subject to future risk research per the owner's own label | Risk (new, beyond original gate table) | Not blocking initial implementation scope, but PROVISIONAL means it may change | New, 5th addendum Decision B |
| 14 | MF-to-LTF structural inheritance rule (≤40 bars, LTF displacement confirms MF direction) | New, beyond original gate table | Not blocking; a submission framed as closing items 10-12 actually introduced this instead | New candidate, 8th addendum — **not yet applied**, needs owner confirmation it's intended scope |
| 15 | Liquidity-tagging consistency rule (all tag types use the Addendum-6 stable-identifier hash) | New, extends G2 Decision 2's scope | Not blocking; same submission as #14 | New candidate, 8th addendum — **not yet applied**, needs owner confirmation |
| 16 | FVG-chain continuity rule | G5 | Not blocking per se, but **overlaps two already-CLOSED G5 rules** (HTF-MTF alignment, LTF-inside-confluence-zone) with different wording ("MF displacement" vs. "confluence zone") — risks an internal contradiction if applied as-is | **STILL not applied after two restatement attempts (9th, 10th addenda)** — "MF displacement" was redefined as "relative to MF swing anchor," but no MF-level swing concept exists anywhere in this spec, and the relationship to G5 rule 2's confluence zone is still unstated. Also flags reuse of the already-decided `wick_to_wick_displacement` FVG-boundary phrase for what appears to be a different mechanism. |
| 17 | R1-R7 coverage gap: no code for stop-invalidity, insufficient net-R, missing cost-profile, or missing target (formerly G7/G8/G9 in the replaced 12-code scheme) | G7/G8/G9 | Non-blocking, flagged residual for implementation time | New, 10th addendum |

**Updated 2026-07-24 (eighth addendum):** items 5, 6, and 9 are now
closed. **Items 10, 11, 12 remain open** — a submission framed as
answering "the six confirmations" (audit items 5, 6, 9, 10, 11, 12) in
fact answered only the first three; the other three of its six points
were new content (items 14-16 above), not answers to 10-12. No
substantive blockers remain among the original gate-matrix rows, but
items 10-12 are still unconfirmed and items 14-16 are new, unapplied
proposals — one of which (16) needs reconciliation against existing
decisions before it can be applied at all.

---

## 5. What this audit does NOT do

- Does not modify `specs/st-c2.yaml` (v1.0.0, unchanged) or any strategy
  logic.
- Does not optimize or tune any parameter.
- Does not write production code, tests, or an engine.
- Does not authorize implementation, backtesting, demo, live, or promotion.
- Does not itself decide any of the 12 unresolved items above — see
  `reports/ST-C2_IMPLEMENTATION_READINESS.md` for the resulting verdict.
