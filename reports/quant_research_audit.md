# SMC-LSS Quantitative Research & Determinism Audit

**Role:** Lead Quantitative Research Architect / Strategy Validation Auditor
**Scope:** Full strategy pipeline — concept through production readiness. Code changes are OUT of scope for this pass; every recommendation below is a proposal, not an action taken.
**Generated:** 2026-07-18
**Basis:** Direct source review (`src/`, `specs/`, `docs/`, `.claude/skills/`, `config/`, `tests/`) plus this session's real-history backtest evidence (`reports/backtest_v35_*.json`).

**Note on scoring:** `reports/production_readiness.md` (73% overall) scores *infrastructure/integration* readiness (skills wired, MCP connectivity, live order round-trip). This audit scores a different axis — *research determinism and statistical validity* — and is not meant to reconcile with that number. A system can be well-integrated and simultaneously not yet research-grade.

**Note on in-flight work:** This session has an uncommitted, partially-tested rewrite of `src/signal_v35.py` (E-trigger detection, IFVG mechanics, direction-neutral variants, dedup) addressing several findings below. Findings are marked `[OPEN]` or `[IN PROGRESS — UNCOMMITTED]` accordingly. Nothing here should be read as "already fixed and shipped."

---

## 1. Trading Concept

**Is the hypothesis testable?** Partially. "SMC-LSS" (E-trigger × M-model matrix) is stated as 9 parameterized cells with a clear formula layer (`generate_signal`), which *is* testable. But the underlying causal claim — "a higher-timeframe reaction at a marked POI predicts a tradeable reversal" — has no stated null hypothesis, no stated effect-size target derived from theory, and no pre-registered acceptance threshold outside the ad hoc `expectancy >= +0.2R, PF >= 1.3` gate in `docs/CHARTER.md`. Those numbers appear to be conventional round thresholds, not derived from a power calculation against the strategy's expected trade frequency.

**Is the edge clearly defined?** No, prior to this session's spec work. The v3.5 ruleset (`docs/strategy/SMC-LSS-v3.5-SIGNAL-RULESET.md`) is nine hand-verified chart examples generalized into prose ("a marked POI," "external liquidity," "strong displacement") with no numeric thresholds. This session's `docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md` addresses the *implementability* gap but the resulting numeric thresholds are declared defaults, not derived from data — see §13 (Statistical Validation) and §14 (Robustness) below for why that distinction matters.

| | |
|---|---|
| **Severity** | High |
| **Location** | `docs/strategy/SMC-LSS-v3.5-SIGNAL-RULESET.md` §1; `docs/CHARTER.md` "Demo → Live promotion gates" |
| **Problem** | No pre-registered hypothesis test, no power analysis behind the ≥40-trade / ≥0.2R gate, no stated null. |
| **Why it matters** | Without a pre-registered acceptance criterion, any post hoc "it passed" is vulnerable to unconscious threshold-shopping — exactly the failure mode walk-forward/OOS discipline exists to prevent. |
| **Recommended deterministic solution** | Before the next optimization pass, write down (versioned, in `specs/`) the null hypothesis, the minimum detectable effect size given expected trade frequency, and the resulting required sample size *before* looking at new results. |
| **Implementation priority** | Medium |
| **Estimated research effort** | 0.5–1 day |

---

## 2. Formal Definitions

This is the area this session's `SMC-LSS-v3.6-SIGNAL-SPEC.md` was written to fix, and it substantially does — E1/E2/E3, displacement, IFVG inversion, entry type, target hierarchy, and expiry are now numeric. Two things remain:

| | |
|---|---|
| **Severity** | Medium |
| **Location** | `docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md` §9 (session/DST) |
| **Problem** | Session windows are declared as fixed UTC clock times with DST drift explicitly *not* corrected, described as "a documented approximation." That's honest, but it's still a discretionary judgment call embedded in a "machine-testable" spec — two independent developers reading "documented approximation" could reasonably choose to correct for DST or not. |
| **Why it matters** | A killzone boundary that silently drifts up to an hour twice a year changes which candles are session-eligible, which changes trade count and results, without being visible in any single backtest run. |
| **Recommended deterministic solution** | State explicitly: "DST correction: NO, by design, permanently" (or build the correction) — remove the word "approximation" in favor of an unambiguous, final decision either way. |
| **Implementation priority** | Low |
| **Estimated research effort** | Documentation only, <1 hour, unless DST correction is chosen (~0.5 day) |

| | |
|---|---|
| **Severity** | Medium |
| **Location** | `docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md` §5, §6, §8 (all `[TUNABLE]` constants) |
| **Problem** | ~15 numeric constants (ATR multiple, wick ratios, max-age windows) are individually well-defined but their *joint* behavior has never been tested — e.g. does `displacement_atr_mult=1.5` interact badly with `ifvg_max_age_m5_bars=20` in a way that structurally excludes valid setups? |
| **Why it matters** | A spec can be 100% unambiguous and still be wrong. Determinism and correctness are different properties; this audit can confirm the former, not the latter. |
| **Recommended deterministic solution** | Route every constant through the `optimization` skill's IS/OOS grid process (§14 below) before treating any of them as more than a placeholder. |
| **Implementation priority** | High (blocks trusting any v3.6 backtest result) |
| **Estimated research effort** | 2–4 days once the engine implements the spec end-to-end |

---

## 3. Rule Library

**Convertible to IF/THEN?** Yes for E1/E2/E3/M1/M2/M3 as specified in v3.6. **Not yet** for risk management (see §11) — that remains English prose in `.claude/skills/risk-management/SKILL.md`, meant to be followed by an LLM agent step-by-step at execution time, not compiled into deterministic code that runs the same way every time.

| | |
|---|---|
| **Severity** | Critical |
| **Location** | `.claude/skills/risk-management/SKILL.md`; `.claude/skills/optimization/SKILL.md`; `.claude/skills/validation/SKILL.md` |
| **Problem** | These three skills — sizing/limits, parameter optimization, and statistical validation — are all procedural instructions for an LLM to execute manually ("1. get_account_info -> equity. 2. dollar risk = equity\*risk%..."), not deterministic code. There is no `src/risk.py`, no `src/optimize.py` implementing what these skills describe. |
| **Why it matters** | An LLM given the same "SKILL.md" prompt twice, on the same data, is not guaranteed to produce the same numeric output — LLM-mediated arithmetic and judgment calls (e.g., "which limit checks first," "how to compute correlation") aren't reproducible the way a pinned function is. For a system whose entire premise (per `docs/CHARTER.md`) is "the system never improvises," having risk limits enforced by a prompt rather than a pinned function is a direct contradiction of that premise. |
| **Recommended deterministic solution** | Port `risk-management`'s workflow into a pure function (`src/risk.py`) that daily_runner.py calls directly, with the LLM/skill layer only for narration/reporting, never for the actual limit arithmetic. Same for `optimization`'s IS/OOS grid search — that should be a script, not a manually-followed checklist. |
| **Implementation priority** | Critical — this is the highest-leverage single fix available |
| **Estimated research effort** | 2–3 days for risk.py; 3–5 days for a real optimize.py with grid search + OOS re-check |

---

## 4. Feature Extraction

| | |
|---|---|
| **Severity** | Medium |
| **Location** | `src/smc_engine.py` (all detection functions); `src/signal_v35.py` (`_e1_trigger`/`_e2_trigger`/`_e3_trigger`/`detect_structure_m1/m2/m3`) |
| **Problem** | Feature generation (swings, FVGs, order blocks, sweeps, ATR, displacement) and trading decisions (entry/stop/target, GO/NO-GO) are *not* cleanly separated — `signal_v35.analyze()` computes features and makes the trade decision in the same call, discarding intermediate feature state (no feature vector is persisted per bar). |
| **Why it matters** | Without a persisted, reusable feature layer, you can't build a feature-store for future ML-assisted research, can't audit "what did the detector actually see" after the fact beyond what the final `Structure` object happened to carry, and can't reuse features across strategy variants without re-running detection from scratch. |
| **Recommended deterministic solution** | Add a `features(symbol, m5, h1, d1) -> dict` pure function that computes and returns every named quantity (swings, ATR, displacement candidates, POI states) independent of any decision logic; have `analyze()` consume that dict rather than calling `smc_engine` functions inline. |
| **Implementation priority** | Medium (valuable but not blocking near-term validation) |
| **Estimated research effort** | 2–3 days |

`smc_engine.py`'s functions ARE individually reusable pure functions (`swings`, `fvgs`, `order_blocks`, `liquidity_sweeps`, `atr`, `displacement_move`, `mitigation_status`) — this is a real strength; the gap is orchestration-level separation, not primitive-level.

---

## 5. Signal Engine

| | |
|---|---|
| **Severity** | Critical |
| **Location** | `src/daily_runner.py` lines 42–58 |
| **Problem** | Two independent signal engines run in every scan: the legacy v1 pipeline (`smc_master.run()`, via `src/smc_engine.py`'s simple swing/BOS/premium-discount logic) makes the actual GO/NO-GO/PROPOSE decision and sizing; `signal_v35.analyze()` runs in parallel and its result is attached to the output (`res["v35"] = ...`) but **never consulted for the decision**. The decision-making code path and the "strategy of record" code path are different pieces of code. |
| **Why it matters** | `docs/CHARTER.md` states `specs/v3.5.yaml` is "the strategy of record." The code that actually decides GO/PROPOSE today implements neither v3.5 nor v3.6 — it implements an older, simpler v1 pipeline. Anyone reading `reports/daily_signals.json` and assuming it reflects the documented strategy would be wrong. This is the single largest determinism/consistency gap in the codebase: the system's own documentation and its own decision code disagree about what strategy is running. |
| **Recommended deterministic solution** | Either (a) make `daily_runner.py`'s decision path call `signal_v35.analyze()` and gate on its result once the interlock allows it, with the v1 pipeline demoted to a labeled legacy-reference-only output, or (b) if v1 is intentionally still the operative strategy pending v3.5/v3.6 completion, rename/relabel everything so "strategy of record" language in the charter matches what actually executes. Silence on this is the actual defect, not the choice itself. |
| **Implementation priority** | Critical |
| **Estimated research effort** | 0.5 day (relabeling) to 2 days (full switchover with tests) |

| | |
|---|---|
| **Severity** | High |
| **Location** | `src/signal_v35.py::detect_e_trigger` — `[IN PROGRESS — UNCOMMITTED this session]` |
| **Problem** | As of the start of this audit, `detect_e_trigger` tagged *any* H1 liquidity sweep as E3, *any* H1 order block as E2, and fell back to E1 unconditionally otherwise — no freshness check, no causal validation, no distinction between external and internal liquidity. This is confirmed as the primary driver of the real-data backtest failure (231–816 trades/symbol, 10–23% win rate, negative expectancy on all three symbols, `reports/backtest_v35_*.json`). |
| **Why it matters** | A signal engine that fires on "any pattern present" rather than "the specific causal structure the ruleset describes" is not testing the strategy — it's testing a much looser proxy that happens to share some vocabulary with it. Every backtest number produced before this fix measures the proxy, not SMC-LSS. |
| **Recommended deterministic solution** | The v3.6 rewrite in progress this session (E1 = D1-gap + bounded H1 reaction, E2 = POI freshness/mitigation state machine, E3 = external-liquidity-only sweep+reclaim) is the right shape. It is NOT YET committed, NOT YET run against the full three-symbol dataset, and one real bug was found and fixed mid-session (`_e3_trigger` incorrectly required both a swing high AND swing low to exist in-window, failing on legitimate one-sided sweeps) — indicating the rewrite itself needs a dedicated review pass before being trusted, not just a pytest pass. |
| **Implementation priority** | Critical — this blocks every downstream statistical claim |
| **Estimated research effort** | Already ~60% done this session; 1–2 more days to finish, test, and re-baseline |

---

## 6. Market Structure

`swings()`, `trend()` (`src/smc_engine.py`) are simple, well-tested, deterministic. One gap:

| | |
|---|---|
| **Severity** | Medium |
| **Location** | `src/smc_engine.py::swings` (fixed `k=2`) |
| **Problem** | Swing confirmation lag `k=2` is a single global constant applied identically across every timeframe (M5, H1, D1) and every instrument (EURUSD through BTCUSD). A 2-bar confirmation lag means something very different on M5 (10 minutes) vs D1 (2 days). |
| **Why it matters** | Using one fixed `k` across timeframes/instruments of very different volatility character is an unexamined assumption baked into every downstream detector (order blocks, sweeps, mitigation all depend on `swings()`). |
| **Recommended deterministic solution** | Either justify `k=2` explicitly per timeframe (e.g., via the ATR-normalization pattern already used for displacement) or run it through the optimization/robustness loop as a first-class tunable, not a silent default. |
| **Implementation priority** | Medium |
| **Estimated research effort** | 1 day (sensitivity sweep) |

No BOS/CHoCH-specific module exists as a separate primitive — BOS is implicit inside `order_blocks()` (a BOS event is what defines an order block) and CHoCH is not explicitly detected anywhere in `smc_engine.py`; the `.claude/skills/choch-bos/SKILL.md` skill describes the concept but there's no corresponding `smc_engine.choch()` function. `smc_master.py`'s `latest_signal()` (in `live_signal.py`) does its own ad hoc structure-shift check independent of `smc_engine`'s primitives — a third, separate implementation of "is there a structure shift here."

| | |
|---|---|
| **Severity** | High |
| **Location** | `src/live_signal.py::latest_signal` vs `.claude/skills/choch-bos/SKILL.md` vs `smc_engine.order_blocks`'s implicit BOS |
| **Problem** | Three different pieces of the codebase each have their own notion of "structure shift confirmed" and none of them call a shared primitive. |
| **Why it matters** | If CHoCH/BOS classification ever needs to change (e.g., tightening the confirmation rule), there are three places to find and change it, and no guarantee they'd be changed consistently. |
| **Recommended deterministic solution** | Extract a single `smc_engine.choch_bos(c, k)` function; have `live_signal.py`, `order_blocks()`, and any future v3.6 E-trigger code call it. |
| **Implementation priority** | Medium |
| **Estimated research effort** | 1–2 days |

---

## 7. Liquidity Model

`liquidity_sweeps()` (wick-ratio-gated, k-confirmed) is well-defined and, after this session's O(n²) fix, reasonably efficient. `inducement()` (`smc_engine.py`) is a one-line proxy ("the most recent confirmed swing") with no distinction from "the swing that's actually IN THE WAY of the intended POI" — i.e. it doesn't verify the inducement swing sits *between* current price and the real target zone, just that it's recent.

| | |
|---|---|
| **Severity** | Medium |
| **Location** | `src/smc_engine.py::inducement` |
| **Problem** | `inducement()` returns "the most recent confirmed swing high/low," full stop — no geometric check that this swing is actually positioned as a liquidity trap in front of the real POI (M1's actual intended meaning). |
| **Why it matters** | M1 ("inducement + character change") is currently a much looser pattern-match than its name implies; any recent minor swing counts, whether or not it's actually inducement in the SMC sense. |
| **Recommended deterministic solution** | Require the inducement swing's index to sit between the POI's formation and the entry bar, and its price to sit between current price and the POI zone (geometrically "in the way"). |
| **Implementation priority** | Medium (M1 wasn't touched by this session's E-trigger/M3 work — same-generation gap as the pre-fix M3) |
| **Estimated research effort** | 1 day |

`mitigation_status()` is well-defined (FRESH/MITIGATED/INVALIDATED) and reused correctly for E2/E1 POI freshness in this session's rewrite — no finding here beyond what's already noted in §5.

---

## 8. POI Detection

| | |
|---|---|
| **Severity** | Medium |
| **Location** | `src/smc_engine.py::order_blocks` |
| **Problem** | Order block = "last opposite-color candle before a confirmed BOS," full stop — no size/significance filter (a single-tick doji immediately before a BOS counts equally with a large-range candle), no distinction between a "mitigation block" (an OB that already failed once) and a fresh OB. |
| **Why it matters** | Not every technically-qualifying OB is a meaningful POI; without a significance filter, weak/tiny OBs dilute the signal pool with low-quality zones, and — per this session's real-data backtest — POI quality is directly implicated in the overtrading finding (§5 above). |
| **Recommended deterministic solution** | Add a minimum zone-size filter (e.g., OB range ≥ some ATR fraction) as a `[TUNABLE]` v3.6 parameter, and add an explicit "mitigation block" classification (an OB that has already been fully mitigated once) as a distinct, lower-priority POI type rather than treating every technically-detected OB identically. |
| **Implementation priority** | Medium |
| **Estimated research effort** | 1 day |

No "breaker block" detection exists anywhere in the codebase (a breaker is a failed/reversed OB — related to but distinct from IFVG). Given IFVG (this session's work) already covers the FVG-inversion mechanic and the ruleset's 9 variants don't name breaker blocks explicitly, this is a **Low** severity gap (the concept simply isn't part of the stated strategy), not a defect — flagged for completeness only.

---

## 9. Entry Logic

This session's v3.6 spec (§10) resolves the previous ambiguity (resting limit vs intrabar market fill vs confirmation-close) explicitly in favor of confirmation-close, next-bar-open — matching what `backtest_v35.py` already implements. No open finding here beyond confirming the choice is now written down, not just implicit in the code.

| | |
|---|---|
| **Severity** | Low |
| **Location** | `docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md` §10 |
| **Problem** | The entry-type choice is explicitly justified as a data-availability tradeoff ("the current pipeline has neither the data granularity nor the MT5 plumbing" for resting-limit fill simulation) rather than a strategy-design choice. |
| **Why it matters** | This is fine for now, but it means live execution and backtest fidelity are both bounded by the SAME limitation (no tick data) — if tick data ever becomes available, entry fidelity could materially improve, and that should be tracked as a known future upgrade, not forgotten. |
| **Recommended deterministic solution** | Note in the roadmap (below) as a Phase 5+ item once M5-only data proves insufficient. |
| **Implementation priority** | Low |
| **Estimated research effort** | N/A (tracking only) |

---

## 10. Exit Logic

| | |
|---|---|
| **Severity** | High |
| **Location** | `src/trade_manager.py::manage` |
| **Problem** | Break-even and partial-close ("take 50% at +1R") are hardcoded as a single fixed rule (`be_at_r=1.0`, 50% fixed), with no trailing-stop logic beyond that one step, and no per-horizon differentiation (INTRADAY vs INTRAWEEK vs MULTI_HORIZON positions are all managed identically despite `docs/CHARTER.md`'s own language about "management by horizon"). |
| **Why it matters** | The charter promises horizon-aware management; the code doesn't deliver it. A MULTI_HORIZON "runner" position (E1M3) should plausibly be managed differently from an INTRADAY position, but `trade_manager.py` has no horizon parameter at all. |
| **Recommended deterministic solution** | Extend `manage()` to accept `horizon` and apply per-horizon BE/partial/trail rules (even if the v1 default is "same rule for all," make that an explicit, visible choice rather than an accidental one from a missing parameter). |
| **Implementation priority** | High (directly affects realized R:R, which is a headline KPI) |
| **Estimated research effort** | 1–2 days |

`manage()`'s core R-multiple and target-hit logic is otherwise clean, deterministic, and correctly enforces "stops only tighten" (never widens, per its own docstring) — no finding on that front.

---

## 11. Risk Management

Already flagged as **Critical** in §3 (the whole module is currently prose, not code). Additional specific gaps found by direct inspection:

| | |
|---|---|
| **Severity** | Critical |
| **Location** | `src/dry_run.py` line 64 (`daily_loss_pct` defined, never checked); no file implements portfolio heat or correlation |
| **Problem** | `daily_loss_pct: 3.0` and `portfolio_heat_pct: 4.0` exist as CONFIG VALUES in `config/watchlist.yaml` and as a dict key in `dry_run.py`, but grep across `src/` finds **zero** code that reads realized daily P&L and compares it to `daily_loss_pct`, and **zero** code that computes aggregate open-position heat. Only `max_positions` has an actual enforcement line (`dry_run.py:128`, and only inside the dry-run simulator, not the live `daily_runner.py` path). Correlation limits are named in `risk-management`'s skill description ("Correlation limits" is even in this very audit's required-review list) but there is no correlation code anywhere in the repo. |
| **Why it matters** | Three of the five stated hard safety gates (`docs/CHARTER.md` "Risk envelope") — daily loss stop, portfolio heat, and (implicitly) correlation — currently have no enforcement mechanism in deterministic code. If `engine_implements_spec` were flipped to `true` today, nothing in the codebase would stop the system from blowing through the daily loss stop or stacking correlated exposure, because nothing computes those quantities from live account/position state. |
| **Recommended deterministic solution** | Build `src/risk_gate.py`: pull `get_account_info` + `get_all_positions` via the MT5 MCP, compute realized-today P&L (vs. day-start equity) and aggregate open-position heat (sum of at-risk % across open positions), refuse new orders when either threshold is breached. Correlation: define a simple pairwise return-correlation check across the active watchlist (even a crude 20-bar rolling correlation is better than nothing) before allowing 2+ correlated positions simultaneously. |
| **Implementation priority** | Critical — this is a precondition for `engine_implements_spec: true`, full stop, independent of signal quality |
| **Estimated research effort** | 3–4 days |

---

## 12. Data Requirements

| | |
|---|---|
| **Severity** | High |
| **Location** | `src/load_history.py`; `src/signal_v35.py::INSTRUMENT_PROFILES` |
| **Problem** | Spread values (`fx_major: 0.00008`, `metal: 0.30`, `crypto: 20.0`) are per-asset-CLASS hardcoded constants, not pulled from the live broker. This session's real backtests used these flat, unverified numbers as the entire transaction-cost model — no commission line item at all, no variable/volatility-scaled slippage. |
| **Why it matters** | Every expectancy/PF number in `reports/backtest_v35_*.json` this session is net of a cost assumption that has never been checked against VTMarkets-Demo's actual quoted spreads. If real spread is meaningfully wider (plausible for XAUUSD-VIP or BTCUSD, both showing especially bad results — XAUUSD had 816 trades and the worst drawdown, -135.7R), the true picture could be even worse than reported; if narrower, results are unnecessarily pessimistic. Either way, the number is currently a guess presented with backtest-report precision (2-3 significant figures), which overstates its own reliability. |
| **Recommended deterministic solution** | Pull live `symbol_info` (spread, tick_size, tick_value) via the MT5 MCP for each active symbol, cache it with a timestamp, and use the CACHED REAL value in `INSTRUMENT_PROFILES` rather than a hand-picked constant. Add a commission-per-lot constant (VTMarkets' actual published commission schedule) as a separate cost term. |
| **Implementation priority** | High — directly affects trust in every existing backtest number |
| **Estimated research effort** | 1 day (pull + wire); ongoing (needs periodic refresh) |

| | |
|---|---|
| **Severity** | Medium |
| **Location** | `src/smc_engine.py::load_candles` |
| **Problem** | No data-integrity validation on ingest: no check for duplicate timestamps, missing bars (gaps), out-of-order rows beyond the final sort, or zero-range/zero-volume anomaly bars. |
| **Why it matters** | A silent duplicate or gap in 80,000+ rows of M5 data (this session loaded ~80k bars per symbol) is very hard to spot by inspection and could quietly distort swing/FVG/sweep detection around the anomaly. |
| **Recommended deterministic solution** | Add a `validate_candles(c)` pass: assert strictly increasing timestamps, flag (don't silently drop) any gap wider than N×timeframe, assert `high >= max(open,close) and low <= min(open,close)` per bar. |
| **Implementation priority** | Medium |
| **Estimated research effort** | 0.5 day |

---

## 13. Statistical Validation

| | |
|---|---|
| **Severity** | Critical |
| **Location** | `src/backtest_v35.py::_metrics` |
| **Problem** | Reported metrics are point estimates only: expectancy, PF, win rate, max DD — no confidence intervals, no bootstrap resampling, no standard error on expectancy. The `n < 30` caveat is a STRING annotation in the JSON output, not a gate that blocks or flags the run programmatically (a caller that doesn't read the `caveat` field would never know). |
| **Why it matters** | "Expectancy: -0.123R" reads as a precise fact; without a confidence interval, there's no way to know whether that's meaningfully different from zero given the sample size, or noise. This session's own EURUSD result (377 trades) is large enough to be somewhat informative, but XAUUSD's 816 trades and BTCUSD's 231 both need the same rigor applied before anyone treats the sign of the expectancy as meaningful. |
| **Recommended deterministic solution** | Add bootstrap resampling (e.g. 2,000 resamples of the trade-R sequence) to `_metrics()`, reporting a 95% CI on expectancy and PF alongside the point estimate. Make the `n < 30` (or better, a proper power-based minimum) caveat a machine-readable boolean gate (`statistically_valid: bool`), not just a string. |
| **Implementation priority** | Critical |
| **Estimated research effort** | 1–2 days |

| | |
|---|---|
| **Severity** | High |
| **Location** | Repo-wide |
| **Problem** | No Sharpe ratio, no deflated Sharpe ratio (correcting for the number of trials/parameter combinations tried), computed anywhere in code. |
| **Why it matters** | Given `optimization`'s workflow (grid search over parameters) will inevitably try multiple configurations, an undeflated Sharpe/PF invites exactly the multiple-testing false-positive risk that deflated Sharpe exists to control for. |
| **Recommended deterministic solution** | Once `optimize.py` (§3, §14) exists and performs a real grid search, compute deflated Sharpe using the number of trials attempted as an input. |
| **Implementation priority** | High, but sequenced after §3/§14 (there's nothing to deflate yet since no real grid search exists) |
| **Estimated research effort** | 1 day, once the grid-search infra exists |

---

## 14. Robustness

| | |
|---|---|
| **Severity** | Critical |
| **Location** | Repo-wide — no Monte Carlo, sensitivity, or parameter-stability code exists |
| **Problem** | The `optimization` skill (§3 above) describes a grid-search + IS/OOS process in prose but there is no executable implementation. No Monte Carlo trade-reshuffling (to distinguish "the strategy has an edge" from "the specific sequence of wins/losses got lucky"). No sensitivity analysis (small perturbation of each `[TUNABLE]` constant to check if results are a knife-edge or a stable plateau). |
| **Why it matters** | Every one of the ~15 new v3.6 numeric constants (§2) is a single point estimate with no evidence it sits on a stable plateau rather than a lucky spike. Without sensitivity testing, "backtest passed" and "found a fragile overfit" are indistinguishable. |
| **Recommended deterministic solution** | Build `src/robustness.py`: (a) Monte Carlo — reshuffle the realized trade-R sequence N times, report the distribution of terminal equity/max-DD, compare the actual (ordered) result against that distribution; (b) sensitivity — for each `[TUNABLE]` constant, re-run the backtest at ±10%/±25% and confirm expectancy sign and rough magnitude are stable, not a cliff-edge. |
| **Implementation priority** | Critical — required before trusting any tuned parameter set |
| **Estimated research effort** | 3–5 days |

---

## 15. Walk Forward

| | |
|---|---|
| **Severity** | Critical |
| **Location** | `src/validate.py` |
| **Problem** | A real, sound walk-forward IS/OOS implementation exists — but it imports `from backtest import collect, metrics`, i.e. the LEGACY v1 engine (`src/backtest.py`), not `signal_v35`/`backtest_v35`. Running `python src/validate.py --all` today validates a strategy that isn't the one described in the charter as "the strategy of record." |
| **Why it matters** | This is the same disconnect as §5 (the two-engines problem) manifesting specifically in the validation tooling: the one piece of code that could answer "does v3.5/v3.6 have a real edge, OOS?" doesn't actually test v3.5/v3.6 at all. As it stands, `reports/validation_result.json` (if regenerated) would produce an ACCEPT/REJECT verdict about the wrong strategy. |
| **Recommended deterministic solution** | Add a `backtest_v35`-based path to `validate.py` (or a parallel `validate_v35.py`) that splits chronologically, runs `backtest_v35.run_backtest()` on each half, and applies the same ACCEPT/REJECT/INCONCLUSIVE logic already written (which is itself sound — `IS positive AND OOS >= 0.5*IS` is a reasonable persistence check). Only a single rolling split is implemented; consider adding multiple rolling windows (true walk-forward, not a single train/test split) once the single-split path is wired correctly. |
| **Implementation priority** | Critical |
| **Estimated research effort** | 1 day to wire the existing split logic to `backtest_v35`; 2–3 more days for true multi-window rolling walk-forward |

No CPCV (combinatorial purged cross-validation) exists anywhere — only a single 70/30 chronological split. Given the small expected trade counts, CPCV would materially improve statistical power over a single split; noted as a Phase 4/5 roadmap item rather than a separate Critical finding, since a working single-split OOS check should land first.

---

## 16. Implementation Readiness

**Can every rule be implemented without human interpretation?**

- E1/E2/E3, M1(partial)/M2(partial)/M3, displacement, IFVG, entry type, target hierarchy, expiry/dedup: **yes**, as of this session's `SMC-LSS-v3.6-SIGNAL-SPEC.md` (M1/M2 detection functions haven't been re-derived to match the spec's sequencing constraints the way M3 was — see §7 note below).
- Risk management (§11), optimization/validation workflows (§3): **no** — currently require human/LLM judgment at execution time, which is precisely what `docs/CHARTER.md` says the system should never do ("the system never improvises").

| | |
|---|---|
| **Severity** | Medium |
| **Location** | `src/signal_v35.py::detect_structure_m1`, `detect_structure_m2` |
| **Problem** | Only `detect_structure_m3` was rewritten this session to enforce the v3.6 §7 sequencing constraints (sweep → displacement → zone → retrace, in strict bar-index order) and displacement gate (§5). `detect_structure_m1`/`detect_structure_m2` still use the pre-v3.6 "find the most recent matching FVG/OB, no ordering or displacement check" approach. |
| **Why it matters** | M1/M2 are two-thirds of the M-model space; leaving them at the old fidelity level while M3 is rewritten means the engine is now internally inconsistent — some variants are spec-compliant, most aren't yet. |
| **Recommended deterministic solution** | Apply the same sequencing/displacement treatment given to M3 to M1 (inducement sweep → character change) and M2 (OB+FVG Gold Zone), even though the source ruleset doesn't name "displacement" for these — at minimum, add explicit `i_sweep < i_zone_creation` ordering and a max-age bound, matching v3.6 §7/§8's general sequencing rule. |
| **Implementation priority** | High |
| **Estimated research effort** | 2–3 days |

| | |
|---|---|
| **Severity** | Medium |
| **Location** | `src/backtest_v35.py::run_backtest` `consumed` set (this session's dedup addition) |
| **Problem** | The one-signal-per-structure dedup set is local to a single `run_backtest()` call (in-memory, not persisted). In live operation, `daily_runner.py` runs as a fresh process on each scheduled scan (per `docs/daily-loop-runbook.md`) — there is no persistent store carrying "already-fired structures" across separate scan invocations. |
| **Why it matters** | The mechanism identified this session as the single biggest lever on the overtrading problem in backtest would NOT carry over to live/demo operation as currently wired — a live deployment could still re-fire on the same structure across different scheduled runs. |
| **Recommended deterministic solution** | Persist consumed structure-keys to `data/consumed_structures.csv` (or similar, matching the existing `data/journal.csv` pattern) and have `daily_runner.py` load/save it each run. |
| **Implementation priority** | High — otherwise the dedup fix doesn't actually reach production behavior |
| **Estimated research effort** | 1 day |

---

# FINAL REPORT

## 1. Readiness Score: **32 / 100**

A system with unusually strong safety *governance* (explicit interlocks, demo-first gating, an honest charter that already says "propose-mode, not yet ready") sitting on top of a research pipeline that is not yet statistically rigorous and a risk-management layer that is not yet deterministic. The governance discipline is worth real credit — many systems at this stage don't have it — but it doesn't substitute for the missing statistical infrastructure.

## 2. Research Maturity Level: **Early-Stage Systematic Research**

Hypothesis stated, formula layer deterministic, detection layer under active (uncommitted) redevelopment this session, zero validated edge to date. Comparable to a strategy that has just finished its first honest backtest and discovered it doesn't work as originally coded — which is exactly what happened this session.

## 3. Determinism Score: **45 / 100**

Strong in the formula layer (`generate_signal`, now direction-neutral and DOL-gate-correct) and the shared primitives (`smc_engine.py`). Weak in risk management (prose, not code — §3/§11) and undermined by the two-parallel-engines problem (§5) that makes "what strategy actually runs" ambiguous even where the code itself is deterministic.

## 4. Backtest Readiness: **40 / 100**

The engine runs, produces real per-symbol metrics on 7–13 months of real history, and (after this session's O(n²) fix) does so in reasonable time. Missing: commission model, verified-not-guessed spread, data-integrity validation on ingest, and a machine-readable (not just string-annotated) minimum-sample gate.

## 5. Statistical Readiness: **18 / 100**

No confidence intervals, no bootstrap, no deflated Sharpe, no multiple-testing correction anywhere in code. This is the lowest-scoring dimension and the one most likely to produce false confidence if skipped.

## 6. Validation Readiness: **20 / 100**

The walk-forward *logic* in `validate.py` is sound in concept (chronological split, persistence check) but is wired to the wrong engine entirely (§15) — currently answers a question about v1, not v3.5/v3.6. No CPCV, no multi-window rolling walk-forward.

## 7. Production Readiness: **10 / 100 (appropriately, by design)**

Correctly blocked: `engine_implements_spec: false`, `promote_to_live: false`, demo-only, no Telegram reporting, no reconciliation, no persistent daily-loss/heat enforcement. This LOW score is the system behaving correctly, not a defect — flagging it only so it isn't misread as "10% done" rather than "10% because it correctly refuses to claim more."

---

## 8. Top 20 Improvements, Ranked by Impact

| # | Improvement | Severity | Section |
|---|---|---|---|
| 1 | Resolve the two-parallel-engines problem — make the documented "strategy of record" match the code that actually decides GO/NO-GO | Critical | §5 |
| 2 | Port `risk-management` skill into deterministic code (`src/risk.py`), including daily-loss and portfolio-heat enforcement that currently doesn't exist anywhere | Critical | §3, §11 |
| 3 | Finish, test, and commit the in-progress v3.6 E-trigger rewrite (E1/E2/E3 causal validation) — currently the single largest driver of backtest quality | Critical | §5 |
| 4 | Wire `validate.py`'s walk-forward logic to `backtest_v35`/v3.6 instead of the legacy v1 engine | Critical | §15 |
| 5 | Add bootstrap confidence intervals + a machine-readable minimum-sample gate to backtest metrics | Critical | §13 |
| 6 | Build real Monte Carlo trade-reshuffling + sensitivity analysis for every `[TUNABLE]` v3.6 constant | Critical | §14 |
| 7 | Replace hardcoded/guessed spread constants with live-pulled `symbol_info`, and add a commission term | High | §12 |
| 8 | Extend M1/M2 structure detection to the same sequencing/age rigor M3 received this session | High | §16 |
| 9 | Persist the one-signal-per-structure dedup set across live scan invocations, not just within one backtest run | High | §16 |
| 10 | Add horizon-aware trade management (BE/partial/trail differ by INTRADAY/OVERNIGHT/INTRAWEEK/MULTI_HORIZON) | High | §10 |
| 11 | Build a real `optimize.py` grid-search + OOS-recheck implementation (currently prose-only) | High | §3, §14 |
| 12 | Add data-integrity validation on candle ingest (gaps, duplicates, malformed OHLC) | Medium | §12 |
| 13 | Add a correlation-limit check across the active watchlist before allowing simultaneous correlated positions | Critical | §11 |
| 14 | Unify the three separate "structure shift" implementations into one shared `choch_bos()` primitive | High | §6 |
| 15 | Add a minimum zone-size/significance filter to order-block detection | Medium | §8 |
| 16 | Tighten `inducement()` to require actual geometric positioning, not just recency | Medium | §7 |
| 17 | Make session-window DST handling an explicit permanent decision, not a hedge-worded "approximation" | Medium | §2 |
| 18 | Justify or ATR-normalize the fixed `k=2` swing-confirmation lag across timeframes | Medium | §6 |
| 19 | Deflate Sharpe/PF by trial count once real grid search exists | High | §13 |
| 20 | Move toward multi-window rolling walk-forward / CPCV beyond the current single 70/30 split | Medium | §15 |

---

## 9. Roadmap

> **Addendum (2026-07-18, post-review):** the owner reviewed this audit and
> proposed inserting a Research Layer *before* Phase 1 — a reusable,
> queryable feature database built once, shared by every future strategy,
> rather than each strategy recomputing detection inline. This generalizes
> §4's finding (feature/decision separation, previously scoped as Phase 2)
> into the platform's actual starting point. Adopted below as **Phase 0**.
> One piece of that proposal was reframed rather than adopted as-is:
> per-detector precision/recall requires an independent ground truth that
> doesn't exist for chart patterns (measuring a rule against itself is
> circular) — folded into Phase 0's edge-per-feature measurement instead,
> which is answerable without circularity ("of N confirmed sweeps, what
> fraction preceded a reversal of magnitude X within Y bars"). A proposed
> full institutional directory reorganization (00–14 numbered folders) was
> not adopted — the *principle* (feature engineering separated from
> strategy logic) is captured below without a repo-wide reorg, which is
> premature with a single strategy on the platform.

**Phase 0 — Research Foundation** *(new — build before resuming Phase 1)*
Build `src/features.py`: compute swings, trend, BOS/CHoCH, liquidity sweeps
(internal vs external), order blocks, FVG/IFVG, mitigation state,
premium/discount, ATR, session/day/hour **once** per symbol over the full
series (pointer-based confirmation lookup, not per-bar-growing-window —
that reintroduces the O(n²) bug fixed earlier this session), persisted to
`data/features_<SYMBOL>_M5.csv`. Add edge-per-feature measurement (does a
confirmed sweep/OB/FVG condition actually precede favorable movement,
independent of any full strategy) — this answers "is the logic weak or is
detection wrong" before combining detectors into a strategy, and is the
empirically-answerable version of the detector-validation idea. Exit
criterion: every M5/H1/D1 series has a materialized feature table, and each
primitive has a standalone forward-edge measurement, before Phase 1 resumes.

**Phase 1 — Deterministic Rules** *(in progress this session)*
Finish v3.6 spec-to-code for M1/M2 (matching M3's rigor), commit and re-baseline the E-trigger rewrite, resolve the two-engine ambiguity (#1, #3, #8 above). Exit criterion: `daily_runner.py`'s decision path and `docs/CHARTER.md`'s "strategy of record" language agree, and every M-model has explicit sequencing/age enforcement.

**Phase 2 — Feature Extraction**
Separate feature computation from decision logic (`features()` pure function, §4); add data-integrity validation on ingest (#12). Exit criterion: every detector consumes a persisted feature dict rather than recomputing inline.

**Phase 3 — Signal Engine**
Port risk-management to deterministic code including daily-loss/heat/correlation enforcement (#2, #13); persist dedup state across scans (#9); add horizon-aware trade management (#10). Exit criterion: every stated hard safety gate in `docs/CHARTER.md`'s risk envelope has a corresponding, tested function — none left as prose only.

**Phase 4 — Statistical Validation**
Bootstrap confidence intervals, machine-readable sample-size gate, live-pulled cost model (#5, #7). Exit criterion: every backtest report carries a CI, not just a point estimate.

**Phase 5 — Robustness Testing**
Monte Carlo reshuffling, per-constant sensitivity sweeps (parameter-stability
plots: PF vs. each `[TUNABLE]` constant — a strategy whose PF swings wildly
under a small parameter nudge is fragile, not edge-bearing), regime-split
results (trending/ranging, high/low volatility, London/NY/Asian, per
session — this is often where "the edge" turns out to actually live, or not
live uniformly), and feature-importance decomposition (which conditions —
HTF bias, sweep, OB, FVG — contribute the most R, to simplify rather than
keep accreting rules), real `optimize.py` (#6, #11). Exit criterion: every
`[TUNABLE]` constant in `specs/v3.6.yaml` has documented sensitivity
results, and expectancy is broken down by regime and by contributing
feature, not reported only as one aggregate number.

**Phase 6 — Walk-Forward Validation**
Wire `validate.py` to v3.5/v3.6 (#4); move from single split to rolling multi-window walk-forward, consider CPCV (#20). Exit criterion: `validation_result.json` reflects the actual strategy of record and a genuine OOS-persistence verdict.

**Phase 7 — Demo Deployment**
Only after Phases 1–6 pass their exit criteria — this is already correctly how `docs/CHARTER.md`'s M2/M2.5/M3 milestones are sequenced; this audit's recommendation is to hold that gate exactly where it already is, not relax it because infrastructure work (this session's data loading, perf fixes) has made progress. Passing Phase 1–3 infrastructure work does not by itself constitute passing Phase 4–6 statistical validation — they are different questions.

---

_This audit reviewed code and documentation state as of 2026-07-18. It does not itself modify any code. Findings referencing "this session's uncommitted work" should be re-verified once that work is committed and independently tested — an in-progress rewrite is evidence of direction, not yet evidence of correctness._
