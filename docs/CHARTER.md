# SMC-LSS Platform — Project Charter

## Objective
Operate a disciplined trading system where Claude Cowork first helps author,
normalize, validate, and approve a versioned strategy contract, and only then
supports the execution layer that trades that approved contract on MT5.

## Vision (end state)
A hands-off loop where the human sets the operating presets and Claude executes the
mechanical work in two stages:

1. Strategy approval: source spec → machine-readable contract → validation →
   approval.
2. Execution: approved contract → risk gate → canonical execution pipeline →
   broker → reconciliation → journal → report.

Demo auto-trading comes first. Live auto-trading is unlocked only after the approved
strategy passes its evidence gates and the execution layer is operational.

## Operating policy

### Autonomy
| Environment | Behavior |
|---|---|
| **Strategy approval** | Claude Cowork may draft, revise, normalize, and validate the strategy source into an approved contract. |
| **Demo** + approved contract + execution layer ready | **Auto-execute** — place + set SL/TP, reconcile, and journal. |
| **Demo** without an approved contract or without the execution layer | **Propose-mode** — analyze, size, journal the intent; hold for review (current state). |
| **Live** + approved contract + demo evidence gates passed + owner approval | **Auto-execute** — place + manage + journal + report to Telegram. |
| **Live** before promotion | **Blocked** — no live orders until the approved strategy and demo gates pass. |
| **Unverified / not demo** | **Blocked** — no order; alert only (fail-safe). |

**Safety interlock:** the execution runtime may only consume an approved strategy
contract derived from `docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md`. Until that
contract exists and the execution layer is built, the loop remains in propose-mode
or analysis-only mode — it must never invent live orders from unapproved rules.

See `docs/adr/ADR-0001-two-track-strategy-lifecycle.md` for the two-track
execution/research lifecycle governing which spec may execute.

### Strategy source
`docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md` is the human-readable source of truth
for the new strategy-approval workflow. It must be normalized into a machine-readable
approved contract before the execution layer may consume it.

### Risk envelope (hard gates)
- Risk/trade: **0.5%** demo, **1.0%** live.
- Daily loss stop: **3%**.
- Max open positions: **3**.
- Portfolio heat: **4%**.
- Minimum reward:risk **2.0**.
- Never widen a stop; stops only tighten.
- Symbol eligibility and position amount are configuration-driven and must be
  enforced by the execution layer.

### Telegram reporting
- Send a Telegram message for every scheduled scan summary.
- Send a Telegram message for every GO, NO-GO, SKIP, fill, modify, close, reject,
  risk stop, and daily/weekly performance summary.
- Telegram delivery failure must not trigger duplicate orders; it is logged and
  retried/reportable as an ops failure.

## Strategy approval workflow
1. Write or revise the source strategy.
2. Normalize the source into a machine-readable contract.
3. Backtest and validate the contract with closed-candle-only rules.
4. Compare evidence against the approval gates.
5. Approve one immutable version or reject and revise.
6. Deploy only the approved contract to the execution layer.

## Safety gates (every run, in order)
1. **Environment verification** — resolve login → server name; demo-safe only when
   the server contains "Demo" (never the connector `account_type` field).
2. **Strategy verification** — the execution runtime must load an approved contract;
   unapproved or missing contracts are NO-GO.
3. **Risk gate** — position sizing + all limits; lots rounded down; REFUSE on any breach.
4. **Execution gate** — auto-send only when the environment, approved strategy,
   symbol, position amount, risk, and promotion gates match the configured policy;
   every order carries a stop.
5. **Journaling + Telegram** — every GO, NO-GO, fill, reject, modify, close, and
   risk stop is logged immutably and reported to Telegram.

## Demo → Live promotion gates
Flip `promote_to_live: true` only when ALL hold on the demo track:
- ≥ 40 journaled trades under the locked approved contract
- Positive expectancy (≥ +0.2R) and profit factor ≥ 1.3
- Max drawdown ≤ 15%; rule-adherence ≥ 95% (no un-journaled or off-spec trades)
- Walk-forward / out-of-sample validation passed
- Two consecutive clean weekly reviews with no critical mistakes

## Success metrics (KPIs)
Expectancy (R), profit factor, win%, max drawdown, rule-adherence %, average
R:R realized, and uptime of the scheduled loop (runs completed vs scheduled).

## Scope
**In:** strategy approval workflow, approved contract packaging, demo auto-execution,
promoted live auto-execution, configuration-driven symbols/strategy/position limits,
Telegram reporting, sizing, trade management, journaling, reporting, backtest/
validation of rule changes.
**Out:** discretionary overrides, non-watchlist symbols, news-driven or fundamental
trading, martingale/averaging-down, any stop-widening.

## Roadmap
- **M0 — Strategy approval foundation (current):** rewrite governance around source
  strategy, approved contract, and execution separation.
- **M1 — Approved strategy contract:** normalize the v3.6 source into a versioned,
  machine-readable contract.
- **M2 — Validation:** prove the contract with backtest, walk-forward, and OOS gates.
- **M3 — Execution layer:** build the canonical MT5 execution path, risk gate,
  reconciliation, and journaling.
- **M4 — Demo automation:** connect the approved contract to demo auto-execution.
- **M5 — Live pilot:** promote only after demo evidence and owner approval.

## Key risks & mitigations
- **Strategy drift** → immutable versions, approval gate, and contract checksum.
- **Broker/data outage mid-run** → env + connection preflight; skip symbol, log, alert.
- **Mis-sized non-USD symbols** → pull live tick value per symbol; config specs are fallback only.
- **Environment misread (demo vs live)** → server-name gate + attestation; fail-safe to blocked.
- **Over-optimization** → rule changes only through backtest/validation with locked out-of-sample data.
- **Schedule drift / DST** → cadence anchored to UTC killzones; local times documented.

_Strategy source of record: **`docs/strategy/SMC-LSS-v3.6-SIGNAL-SPEC.md`**.
The approved execution contract does not exist yet; it is the next deliverable.
`specs/v1.yaml` and `specs/v3.5.yaml` remain historical references only._
