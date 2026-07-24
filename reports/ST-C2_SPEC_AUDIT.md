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
| G2 — external/protected structure | **PARTIAL** | Multi-candidate pool tie-break (distance → timestamp → identifier): 1st addendum decision 3. External-vs-internal swing distinction: 3rd addendum Cluster 1 Q2. Protected high/low lifecycle: shared with G1 (3rd addendum Cluster 1 Q3). | The pool-level "stable identifier" field composition (decision 3's *third* tie-break criterion) is still undefined. The 4th addendum closed a *different* thing — the replay-engine dedup key — not this. Conflated in the original task framing; separated here. See §3. |
| G3 — close-confirmed BOS/CHoCH | **CLOSED** | Same-bar classification boundary: 1st addendum decision 5. Wick-probe-rejection mechanics: 3rd addendum Phase 1 (existing convention, `close_beyond_structure_required` + choch-bos skill). Multi-CHoCH sequencing (2nd/3rd): 3rd addendum Cluster 1 Q4. | 4th+ CHoCH has no rule — narrow, see §3, not treated as blocking G3's core closure. |
| G4 — premium/discount location | **CLOSED** | All five sub-items (swing source, range-freeze policy, anchoring-swing invalidation, equilibrium boundary, OTE band) closed in full by 2nd addendum. | None. |
| G5 — fresh/valid HTF POI/FVG | **PARTIAL** | Freshness/invalidation rule (50% mitigation): 1st addendum decision 4. Rounding convention: 3rd addendum Cluster 3 Q10. HTF-MTF alignment, LTF placement, size-validation source, no-stacking, cascade-invalidation: all 2nd addendum G5 rules 1-5. Multi-zone tie-break: 3rd addendum Cluster 3 Q9. | The actual 3-candle **zone-boundary formula** (which candles' highs/lows bound the gap) is still not pinned. 3rd addendum Q8 clarified the geometry *mode* ("fixed_three_candle") but not the *formula*. A field-by-field re-check (`docs/audit/2026-07-23-st-c2-deferred-gates-companion.md` §4) found `src/smc_engine.py`'s `fvgs()` does not cleanly match this stage's fields — a starting primitive, not a confirmed formula. |
| G6 — LTF sweep + structure confirmation | **CLOSED** (one flagged low-risk item) | Fill timing, expiry/cancellation: 1st addendum decisions 2, 8, 9. `max_setup_bars` vs `entry_window_bars` relationship: 3rd addendum Cluster 2 Q5. First-qualifying-bar rule: 3rd addendum Cluster 2 Q6. Sweep reclaim-close timing: 3rd addendum Cluster 2 Q7. LTF displacement/close-confirmation fields: 3rd addendum Phase 1 (existing convention). | `internal_bos_required`'s definition is only *implied* by Cluster 1 Q2's external/internal rule ("unblocks" it, per the 3rd addendum's own text) — never explicitly restated as a closure. Low-risk, flagged in the consolidated spec as `applied:`, recommend one-line owner confirmation. |
| G7 — structural invalidation/stop | **CLOSED** | Anchor/buffer/rounding: 1st addendum decision 6. Min/max stop-distance bounds (35/150 points) and the out-of-bounds behavior: 2nd addendum G7 decisions 1-4. | None. |
| G8 — net reward after costs | **CLOSED** | `rr_min` conflict resolution and cost model: 1st addendum decisions 1, 10. Cost profile verified present (`config/research_costs.yaml` XAUUSD row: spread 25.0 pts, slippage 5.0 pts, commission 0, swap 0). | None. |
| G9 — logical target before entry | **CLOSED** | T1/T2 both-mandatory, pre-entry selection: 1st addendum decisions 1, 7. | None. |
| G10 — precommitted trade management | **PARTIAL** | Pre-fill limit expiry: 1st addendum decision 8. Time stop (none, structure/R-based only): 3rd addendum Cluster 4 Q11. Emergency-exit concept + triggers: 3rd addendum Cluster 4 Q12. | Emergency-exit **numeric thresholds** (20 pts / 60 s) are explicitly flagged illustrative-only, not owner-confirmed, in the 3rd addendum itself. **Session-close-forces-exit for an already-filled position** was never explicitly addressed — distinct from "time stop," per the original audit's own item split; new finding this pass, see §3. |
| Entry / order-simulation | **PARTIAL** | Exact limit price, placement/confirmation timing, next-bar fill: 1st addendum decisions 2, 9. Limit expiry/cancellation: decision 8. Same-bar entry/stop/target ambiguity (stop-first): decision 9. Bid/ask (mid-price): 3rd addendum Cluster 4 Q13. Gap-through (fill-at-open): Q14. Partial-fill (accept + scale): Q15. | `duplicate_setup_policy` — proposed value exists but explicitly flagged unconfirmed (no owner rationale) in the 3rd addendum. **General post-fill event-priority ordering** (breakeven vs. partial vs. runner vs. stop, same bar) is a distinct question from decision 9's entry/stop/target scope and was never addressed — new finding this pass, see §3. |
| RCR pre-registration | **CLOSED** | Primary/secondary metrics, multiple-testing control, OOS boundary, max experiment count, allowed-parameter-changes list: all 2nd addendum. Population-feasibility (30) / statistical-claim (100) floors: 1st addendum decision 12. | None. |

**Summary:** 6 of 12 rows fully CLOSED (G3, G4, G7, G8, G9, RCR
pre-registration), 1 CLOSED with one flagged low-risk item (G6), and 5
PARTIAL with genuine open residuals (G1, G2, G5, G10, order-simulation).

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
   but distinct concepts; closing one does not close the other. The pool-
   level identifier composition remains genuinely open.
2. **G5's FVG zone-boundary formula was never pinned**, only its "mode."
   Cluster 3 Q8 answered "fixed 3-candle geometry, not variable-length" —
   a real closure of *one* ambiguity — but the actual formula (which
   candles' highs/lows form the gap boundaries) was never stated by any
   decision, and the codebase's `fvgs()` function was independently found
   (in the 2026-07-23 deferred-gates companion review) not to cleanly
   match this stage's fields.
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
   Not assumed closed here.
5. **Order-simulation's post-fill event-priority ordering is a distinct,
   unaddressed question from decision 9's entry/stop/target scope.**
   Decision 9 (1st addendum) resolves same-bar ambiguity between entry,
   stop, and target only. It says nothing about priority when multiple
   *management* events (breakeven activation, partial-take, runner
   activation, stop) could apply on the same bar to an already-open
   position. New gap, not previously listed anywhere.
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

---

## 4. Full list of unresolved items (nothing here is resolved by this audit)

| # | Item | Gate | Blocking? |
|---|---|---|---|
| 1 | `duplicate_setup_policy` exact value | Order-simulation | Yes — explicitly flagged unconfirmed by the owner's own prior addendum |
| 2 | Emergency-exit numeric thresholds (spread-spike points, connection-loss seconds) | G10 | Yes — explicitly flagged illustrative-only |
| 3 | FVG zone-boundary formula (3-candle gap price boundaries) | G5 | Yes — no deterministic engine can be built without it |
| 4 | Liquidity-pool "stable identifier" composition | G2 | Yes — decision 3's tie-break chain is incomplete without it |
| 5 | Bull/bear classification rule (explicit statement) | G1 | Likely low-effort, but unresolved |
| 6 | Bias-evidence-timestamp field | G1 | Low-risk, diagnostics-detail level |
| 7 | Session-close-forces-exit for an open position | G10 | Yes — distinct from the already-answered time-stop question |
| 8 | Post-fill event-priority ordering (breakeven/partial/runner/stop) | Order-simulation | Yes — needed for deterministic trade management |
| 9 | 4th+ CHoCH sequencing rule | G1/G3 | Narrow edge case, non-blocking for initial implementation |
| 10 | `protected_level_lifecycle.create_on` — confirm the terminology-based inference | G1 | Low-risk, recommend one-line confirmation |
| 11 | `internal_bos_required` explicit restatement | G6 | Low-risk, recommend one-line confirmation |
| 12 | Rejection code strings — confirm or accept as proposed | All gates | Non-blocking |

Items 1-4 and 7-8 are the substantive blockers. Items 5, 6, 9, 10, 11, 12
are low-risk/narrow and could reasonably be closed with brief confirmations
rather than fresh design sessions, but are not resolved here regardless of
apparent size, per instruction.

---

## 5. What this audit does NOT do

- Does not modify `specs/st-c2.yaml` (v1.0.0, unchanged) or any strategy
  logic.
- Does not optimize or tune any parameter.
- Does not write production code, tests, or an engine.
- Does not authorize implementation, backtesting, demo, live, or promotion.
- Does not itself decide any of the 12 unresolved items above — see
  `reports/ST-C2_IMPLEMENTATION_READINESS.md` for the resulting verdict.
