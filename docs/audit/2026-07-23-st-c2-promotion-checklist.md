# ST-C2 → MT5 Demo Go/No-Go Checklist

**Grounded in:** `specs/st-c2.yaml`, `docs/CHARTER.md`, `MASTER_PLAN.md`, `PROJECT_STATUS.md`,
and the owner decisions already on record in `reports/audit/ST_C2_HYBRID_LIQUIDITY_FIRST_RCR.md`.
Read-only reference document — creates no new authority, changes no existing gate. Where a
number below comes from `docs/CHARTER.md`, that document remains the actual source of truth;
this checklist is an operational restatement, not a replacement.

**Status:** not evaluated. ST-C2 currently has `engine_implements_spec: false`, no engine, no
backtest — every item below is presently unmet by default, not because of any known defect.

---

## 1. Strategy specification completeness (`specs/st-c2.yaml`)
- Path: `specs/st-c2.yaml` (confirmed — not `ST-C2_v1.yaml`, no such file exists).
- Version field present and set (currently `version: 1.0.0`).
- Liquidity-first pipeline fully specified: HTF/MF/LTF stages, sessions, execution — no TODOs
  or narrative-only rules.
- All thresholds numeric (sweep size, OTE bands, FVG rules, invalidation logic, session times).
- Spec consistent with `MASTER_PLAN.md` and `PROJECT_STATUS.md` — no contradictions in enabled
  symbols, sessions, or risk model.

**Known open items as of 2026-07-23** (per `reports/audit/ST_C2_GOVERNANCE_CONFORMANCE_AUDIT.md`
and its correction): G4 (premium/discount location) entirely undefined; G7 stop-distance min/max
bounds undefined; several RCR pre-registration fields blank (see
`docs/audit/2026-07-23-st-c2-owner-decision-brief.md`). This section fails today on those grounds.

**Go/No-Go:** If any rule is ambiguous, missing parameters, or contradicts `MASTER_PLAN.md`/
`docs/CHARTER.md` → **NO-GO**.

---

## 2. Rule determinism (no discretionary logic)
- Liquidity sweep: explicit numeric definition (ticks/pips beyond prior high/low, within what
  window) — `specs/st-c2.yaml`'s `liquidity_stage` already has numeric fields here
  (`equal_highs_tolerance_pips`, `wick_ratio_min`, etc.); confirm none require judgment calls.
- BOS/CHoCH: fully mechanical, no "contextual bias."
- OTE/FVG/OB logic: fixed ratios, candle relationships, gap rules — **currently blocked by the
  unresolved G4 friction points** in `docs/audit/2026-07-23-g4-decision-aid.md`.
- Invalidation, SL/TP, partials: structural, not judgment calls — **G7 bounds still undefined.**
- Session filter: exact timestamps for London/NY sessions (already numeric in the spec:
  `utc_open`/`utc_close`); no fuzzy logic.

**Go/No-Go:** If any part of ST-C2 requires human interpretation to trade → **NO-GO**.

---

## 3. Historical replay requirements
- Deterministic replay: same input data → same candle sequence → same trades, every run.
- **Dataset source: MT5**, via the `metatrader_mcp_server` MCP bridge configured in `.mcp.json`,
  materialized to local CSVs by `src/load_history.py` (`data/<SYMBOL>_<TF>.csv` — gitignored).
  Validate gaps, time ordering, and symbol consistency against that actual pipeline — not a
  third-party dataset.
- Timestamps normalized to a single reference (UTC) for session slicing.
- Session slicing correctly extracts London/NY from the full day; no cross-session leakage.
- No future leakage: indicators, structure, and signals use only information available at
  decision time (closed-candle-only, per `docs/RESEARCH-CHARTER.md`).

**Go/No-Go:** If replay outputs differ across runs, or any future leakage is detected →
**NO-GO**.

---

## 4. Statistical validation gates (aligned with `docs/CHARTER.md`)

Two distinct, already-established gates apply at different points — do not conflate them:

**Feasibility gate (owner decision 12, this candidate's population floor):**
- ≥ 30 completed trades for population feasibility.
- ≥ 100 completed trades before any statistical performance claim; below 100 is
  INSUFFICIENT/OVERFILTERED, not evidence of profitability.

**Demo→live promotion gate (`docs/CHARTER.md`, "Demo → Live promotion gates" — the actual
authoritative numbers, unchanged by this checklist):**
- ≥ 40 journaled trades under the locked, approved contract.
- Expectancy ≥ +0.2R and profit factor ≥ 1.3.
- Max drawdown ≤ 15%; rule-adherence ≥ 95% (no un-journaled or off-spec trades).
- Walk-forward / out-of-sample validation passed.
- Two consecutive clean weekly reviews, no critical mistakes.

**Go/No-Go:** If any CHARTER metric fails → **NO-GO**. Any tightening or loosening of these
numbers is a `docs/CHARTER.md` amendment requiring explicit owner sign-off — never a side
effect of a backtest result or this checklist.

---

## 5. Robustness validation requirements
- Parameter robustness: small perturbations in key parameters (OTE bands, sweep thresholds) do
  not collapse PF below 1.3 or expectancy below +0.2R.
- Regime robustness: tested across different volatility regimes and trending-vs-ranging
  structure, on XAUUSD (ST-C2's only enabled symbol — EURUSD/GBPUSD are `enabled: false` in
  `specs/st-c2.yaml`; do not require GBPUSD robustness unless that scope decision changes first).
- Session robustness: confirm performance isn't a single-week anomaly within the spec's own
  London/NY sessions.
- Adversarial conditions: news spikes, gaps, thin liquidity do not produce drawdown beyond the
  15% bar.

**Go/No-Go:** If the edge disappears under minor perturbations or realistic stress → **NO-GO**.

---

## 6. Governance approval checklist
Governance must explicitly confirm:
- Spec completeness and determinism.
- Replay reproducibility, no future leakage.
- Statistical gates (§4) passed.
- Robustness tests (§5) documented and passed.
- No cherry-picking of periods or symbols.
- No hidden filters or untracked parameters.
- Results logged in `PROJECT_STATUS.md` and, where relevant, `MASTER_PLAN.md`.

**Go/No-Go:** If governance flags any violation or unresolved concern → **NO-GO**.

---

## 7. MT5 demo deployment prerequisites
Only after all prior sections are satisfied:
- Execution adapter implemented, deterministic, tested against the MT5 MCP bridge in a demo
  sandbox — no live funds.
- Risk model: position sizing, SL/TP, kill-switch implemented exactly per `specs/st-c2.yaml` +
  `docs/CHARTER.md`.
- Environment isolation: demo account only, verified via server-name check (never `account_type`
  alone, per `CLAUDE.md`'s hard rule) — no path to live without a separate, explicit promotion.
- All trades mirrored to the journal and governance logs; real-time rule-adherence tracking.

**Go/No-Go:** If the demo environment is not fully isolated or risk controls are incomplete →
**NO-GO**.

---

## 8. Final promotion rule (Research → MT5 Demo)
ST-C2 moves from research to MT5 demo only when:
- `specs/st-c2.yaml` is complete, deterministic, and version-locked.
- The replay engine is deterministic and leak-free.
- Statistical gates match `docs/CHARTER.md` and are all passed.
- Robustness tests are passed and documented.
- Governance issues an explicit APPROVED verdict.
- The MT5 demo environment is isolated, risk-controlled, and fully logged.

**If any item fails → ST-C2 remains in research. Only full compliance → MT5 demo execution
allowed.**
