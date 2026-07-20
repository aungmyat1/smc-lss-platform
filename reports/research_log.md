# Research Log

Per `docs/RESEARCH-CHARTER.md`: every change to `specs/*.yaml` (including new specs)
is pre-registered here with the six questions **before** any backtest is run. Entries
are append-only, in date order; rejected changes stay in the log. Entry count = trial
count for future deflated-Sharpe inputs.

---

## Change: Add LKZ-1 — ICT/SMC London Killzone Asian-Range Sweep (new strategy family)  (spec version: none -> lkz-v1.0)

Date: 2026-07-19
Author: Arena agent (owner-requested transcription), review pending: owner

### Why
Owner request: convert the public video *"Ultimate ICT/SMC London Session Trading
Strategy (Step By Step)"* (Mulham Trading, 2024-02-14, youtu.be/Ujtiqz4bLeU) into a
strategy that is simultaneously (a) human-readable with graphics and (b)
machine-readable for the platform's code agents. The platform currently has no
session-window model: v1/v3.5 trade continuous SMC structure (negative expectancy on
the 2026-07-18 baseline), and v3.6 (IFVG) is unimplemented. LKZ-1 is a *time-gated*
variant — its premise (trade only the 01:30–03:30 NY manipulation against a ranging
Asian range) is orthogonal to the existing always-on trigger set, so it is added as a
new spec family rather than a change to v1/v3.5/v3.6. No existing spec, detection
logic, or `[TUNABLE]` constant was modified.

### Evidence
Source video transcript (full), esp.: only RANGING Asian sessions are traded
("probability goes much lower when we have a trending one"); sweeps before 01:30 are
called out as invalid in two separate worked examples; sweeps must run INTO an HTF POI
("we don't take any liquidity sweep, we take ones that are into a higher timeframe
point of interest"); midnight-open side rule; 3 worked examples with claimed 3:1–6:1
to first structural targets. Related platform evidence: v3.5 baseline negative
expectancy with **overtrading** (377–816 trades per symbol) — LKZ-1's session gate +
1-trade/day cap is a direct, mechanism-level counter-hypothesis to that failure mode.
Video R-multiples are author's claims, unaudited; no external performance data exists.

### Hypothesis
Restricting entries to (a) ranging-Asia days, (b) the 01:30–03:30 NY window, and
(c) sweeps that physically tag an HTF POI on the correct side of the midnight open
will cut trade count by an order of magnitude vs v3.5 and raise average R, because
the gates enforce the AA (accumulate/manipulate) condition the always-on engine
cannot see. If expectancy stays negative after this restriction, the time-gate
premise itself is falsified cheaply (few trades, fast backtest).

### Expected improvement
Pre-registered numbers for the first backtest of a compliant harness, per symbol
(EURUSD/XAUUSD/BTCUSD, same history window as the v3.5 baseline):
- trade count: 5–40 per symbol (vs 231–816 in v3.5)
- win rate: ≥ 45 % with planned partials (vs 10.0–22.8 % in v3.5), **and**
- expectancy: **> 0R** (vs −0.12R..−0.18R in v3.5)
A result with < 30 trades platform-wide is INCONCLUSIVE, not a pass.

### Success criteria
Keep the change (spec remains, harness may be built) only if, per the
`backtest-researcher` ACCEPT gate: OOS expectancy > 0 AND OOS ≥ 0.5 × IS expectancy
(validation skill's existing rule), on a compliant harness that passes unit tests for
every gate fixture (ranging/trending Asia, pre-window sweep rejected, no-POI sweep
rejected, consumed structure rejected). Spec file alone, with no harness, stakes no
claim and must stay `engine_implements_spec: false`.

### Rollback criteria
Automatic revert to "spec quarantined / archived" (status noted here, file kept as
evidence) if: OOS expectancy negative; OR platform-wide trade count < 30 (INCONCLUSIVE
— then try only ONE loosened knob, e.g. window end 03:30→03:00 already encoded as
`manipulation_window_core`, logged as a new entry); OR any gate fixture cannot be made
to pass without violating the video's stated rules (spec untestable as written).

Resolution: **PENDING** — spec + documentation + diagrams committed this session;
no backtest run yet (no harness exists). Next step per spec §implementation_status.
