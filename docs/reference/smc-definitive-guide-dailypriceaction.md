# Reference: The Definitive SMC Guide (Daily Price Action)

**Type:** External reference material — NOT an authoritative spec.
**Status:** Recorded for reference only. Adds no rule, changes no `specs/*.yaml`, and
carries no execution or promotion authority. Any use of a concept below in a candidate
strategy must still go through an RCR per [`../RESEARCH-CHARTER.md`](../RESEARCH-CHARTER.md).
**Source:** Daily Price Action — "The Definitive SMC Guide" by Justin Bennett
(dailypriceaction.com/blog/smart-money-concepts/). Last updated by source 2026-01-30.
Captured 2026-07-22. Third-party author; wording preserved as supplied by the owner.
**Companion doc:** [`smc-8step-entry-model-dailypriceaction.md`](smc-8step-entry-model-dailypriceaction.md)
— the same author's step-by-step entry model. This file is the concept glossary; that one
is the execution walkthrough.

> Caveat: this is a conceptual/educational overview, not a validated ruleset. Every term
> below is a *definition*, not an edge. The platform's job is to turn any concept adopted
> into a point-in-time, non-repainting, testable rule and prove it on cost-adjusted data —
> never to treat "smart money does X" as established fact.

---

## What SMC is (as supplied)

A framework for reading price through **liquidity, structure, and market inefficiencies**
rather than lagging indicators. Premise: institutional order flow leaves repeating patterns
across timeframes; studying them gives a cleaner read on where price is trying to go and
supports more mechanical, less emotional decisions. Smart money needs liquidity to fill
large positions, which creates predictable behavior around highs, lows, and liquidity
zones.

## Core concepts

**Market structure** — the foundation. Trend read via higher highs / higher lows / lower
highs / lower lows; tells you trending vs ranging and filters false signals.

**Break of Structure (BOS)** — confirms *continuation*. Want a clean close beyond a prior
swing high/low; strong BOS lines up with displacement, signalling intent.

**Change of Character (CHoCH)** — first sign of a possible *reversal*; price breaks a key
swing against trend. Stronger inside a liquidity zone or after a sweep.

**Internal vs external structure** — external = major swings defining the broader trend
(keeps you aligned with HTF); internal = smaller swings inside (refines intraday entries).
Use both.

## Liquidity family

**Liquidity** — price seeks swing highs/lows and equal highs before major moves; smart
money uses these to trigger stop runs / fill positions.

**Equal highs / equal lows** — attract liquidity; retail sees support/resistance, but they
usually become targets. Often swept before reversal or continuation.

**Liquidity sweeps (grabs)** — a spike above/below a level to trigger stops, clearing
traders before the real move; often followed by strong reversals. Author's favored setup:
*liquidity sweep reversals*.

## Inefficiency family

**Fair Value Gaps (FVGs)** — form when price moves too fast and leaves orders unfilled
(inefficiency); act as magnets, revisited on retracements. Bullish and bearish variants
help time entries.

**Order blocks** — areas where large positions were placed before a major move
("institutional footprint"). Bullish OB before bullish expansion; bearish OB before bearish.
On revisit, look for rejection/strength.

**Breaker blocks** — a failed order block that flips to new support/resistance; signals a
directional shift, often after sweeps.

**Imbalances and voids** — directional moves with little opposition, often filled later;
voids show where price may return on retracement.

**Price rebalancing** — market fills inefficient areas from rapid moves; aligns with FVGs
or order blocks, giving a clean place to manage risk.

**Balanced price range** — where the market found fairness between buyers/sellers; attracts
price on retracements.

## Location & entry-refinement family

**Premium and discount zones** — 50% of the dealing range divides premium (above) from
discount (below). Buy discount in uptrends, sell premium in downtrends; prevents chasing.

**Optimal Trade Entry (OTE)** — refined retracement zone between the **62% and 79%** levels;
aligns with liquidity or supply/demand for higher probability. Works best in trends, 1H+.

**Supply and demand zones** — where buyers/sellers previously stepped in aggressively;
stronger when aligned with FVGs, order blocks, or liquidity.

## Intent / momentum family

**Displacement** — a strong move signalling intent / institutional activity; confirms
structure breaks and often follows liquidity grabs.

**Propulsion blocks** — markers during aggressive expansions; clean continuation setups on
revisit.

**Change in state of delivery** — market shifts from slow movement to aggressive
displacement, usually after liquidity grabs or major structure shifts.

**Breakaway gaps** — price leaves an area without looking back (announcements/earnings);
show conviction, can become targets.

**SMT divergence** — compares related markets; when one sweeps liquidity and the other does
not, it signals imbalance. Confirms setups alongside structure and FVGs.

## Assembling it

**SMC entry models** — combine liquidity, structure, gaps, imbalances into a clear setup
(e.g. liquidity sweep into an FVG). Repeat often; studyable on historical data.

**SMC trading strategies** — define the *order of operations* (HTF structure → liquidity →
context → entry) to reduce randomness. Goal: remove emotion, make execution mechanical.

**London session** — clean displacement and liquidity grabs; often sets the day's high/low
and creates the liquidity NY later reacts to.

**New York session** — builds on London; sweeps at the open then sharp moves. AM =
continuation or fast reversals; PM = slower, cleaner.

**Power of Three** — accumulation → manipulation → distribution: range first, sweep
liquidity, then expand. Common in high volatility.

## Risk & exits

**Stop placement** — beyond the structure that invalidates the idea; using liquidity zones
gives cleaner risk and fewer false signals; forces you to define why you're in.

**Liquidity-based take profits** — price gravitates toward equal highs/lows, imbalances,
old swings; predictable exits in the direction of institutional flow.

**Confirmation vs anticipation entries** — confirmation waits for a real structure break /
displacement; anticipation enters earlier by reading intent (needs experience). Both work
if risk is defined.

## Discipline

**How to backtest SMC** — measure how often patterns (structure, sweeps, displacement,
rebalancing) appear across history to build confidence without risking money.

**Common mistakes (author's list):** learning everything at once; marking every FVG/OB;
ignoring higher timeframes; trading every BOS/CHoCH as a setup; entering too early on a
sweep; ignoring news/sentiment; forcing SMC onto sideways markets; no risk plan;
overconfidence after a few wins.

**FAQ takeaways:** SMC reads structure/liquidity/price action instead of indicators; differs
from traditional TA by focusing on intent; the underlying behaviors (liquidity grabs,
structure shifts, imbalances) are real but still require discipline and risk management;
beginner-friendly if you start with structure; works across FX/crypto/stocks/commodities
with timeframe/risk adjustments.

---

## Cross-reference to platform artifacts

Navigation aid only — asserts no equivalence and validates nothing.

| Concept | Platform skill (`.claude/skills/`) | Spec/candidate touchpoint |
|---|---|---|
| Market structure, BOS, CHoCH | `market-structure`, `choch-bos` | HTF/LTF structure & bias stages |
| Internal vs external structure | `market-structure`, `inducement` | inducement / liquidity stage |
| Liquidity, equal H/L, sweeps | `liquidity-sweep` | liquidity/inducement stage (ST-C2) |
| FVGs, imbalances, rebalancing | `fair-value-gap`, `mitigation` | FVG alignment stage |
| Order blocks, breakers, S&D | `order-block` | POI selection |
| Premium/discount, OTE | `premium-discount` | OTE stage |
| Displacement / delivery change | `choch-bos`, `entry-confirmation` | displacement gate |
| Sessions (London/NY), Power of 3 | `session-filter` | session windows |
| Stops, liquidity-based TPs | `risk-management`, `trade-management` | stop mode, targets t1/t2/t3 |
| Entry models, confirmation | `entry-confirmation`, `smc-trading-master` | LTF confirmation stage |
| How to backtest SMC | `backtesting`, `backtest-researcher`, `validation` | replay engine, validation gates |

**Coverage note:** every concept in this guide already has a corresponding atomic skill in
the platform — the deterministic infrastructure exists. What the guide does *not* provide,
and what the platform still requires, is the piece that has repeatedly been the bottleneck:
a parameterization that survives the **cost model** on real data. v3.7–v3.10 all implemented
these concepts and still came out net-losing. This reference explains the "what"; it does
not resolve the open "does it clear cost" question.

**Data-hygiene note:** full local EURUSD/GBPUSD/XAUUSD history is already used for
diagnosis across every ST-C1 variant and cannot be treated as pristine OOS for any future
test motivated by this reference.
