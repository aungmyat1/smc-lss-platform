# Reference: 8-Step SMC Entry Model (Daily Price Action)

**Type:** External reference material — NOT an authoritative spec.
**Status:** Recorded for reference only. Adds no rule, changes no `specs/*.yaml`, and
carries no execution or promotion authority. Any use of this in a candidate strategy
must still go through an RCR per [`../RESEARCH-CHARTER.md`](../RESEARCH-CHARTER.md).
**Source:** Daily Price Action — "Smart Money Concepts trading strategy" walkthrough
(dailypriceaction.com). Captured 2026-07-22. Third-party author; wording preserved as
supplied by the owner.
**Why recorded:** owner-supplied discretionary SMC framework, kept as a human-readable
reference point for comparing against the platform's deterministic candidate specs.

> Caveat: this is a discretionary, chart-narrated method ("I wait for confirmation",
> "it looks tempting"). The platform's job is to translate ideas like these into
> point-in-time, non-repainting, testable rules — not to adopt them as-is. Treat every
> subjective phrase below as a hypothesis to be operationalized and backtested, never as
> a validated edge.

---

## The method (as supplied)

A simple, repeatable Smart Money Concepts framework built around clean price action and
objective rules rather than opinions or hindsight. Aimed at traders who understand SMC
basics but struggle to turn them into consistent execution — entering too late, chasing
moves, or getting stopped out unnecessarily.

### Step 1 — Define market structure on the higher time frame
Start with structure; it is non-negotiable. Before entries, FVGs, or Fibonacci, establish
what price is doing structurally. Example: EURUSD on the HTF may look like it is turning
up, but a series of lower highs and lower lows shows the overall trend is still down, so a
move higher may only be a pullback. HTF structure sets direction and context for every
trade idea.

### Step 2 — Identify external highs and lows
External levels sweep internal structure, take liquidity, and mark where larger
participants may be active. A push higher after taking internal lows does not confirm
anything on its own — an external low may be forming but is not valid yet. Confirmation
comes from a clean **one-hour break of structure**: a real candle *close* through
structure, not a wick. Once that BOS prints, the external low is confirmed.

### Step 3 — Confirm direction with change of character
After the BOS, watch how price reacts to decide whether the move is real or a temporary
pullback. Confirmation is a **change of character (CHoCH)**: price fails to make a higher
high, then closes strongly lower on the one-hour chart, signalling sellers are back in
control. This is the first true layer of confirmation — direction is confirmed by price,
not assumed.

### Step 4 — Mark premium and discount using OTE
Use a modified Fibonacci with the 50% level as the dividing line. After a bearish CHoCH,
only look for shorts in **premium** (above 50%). Anything in discount (below 50%) is
ignored for shorts even if price drops fast. Waiting for premium and using Optimal Trade
Entry (OTE) enforces patience and keeps entries aligned with the trend.

### Step 5 — Define areas of interest with Fair Value Gaps
FVGs form when price moves aggressively and leaves inefficiencies, often revisited later.
A one-hour FVG sitting inside the OTE zone is an *area of interest*, not an entry. Drop to
the 15-minute chart: a lower-timeframe FVG that lines up with the 1H gap and OTE
strengthens the setup. Multiple timeframes pointing to the same region focus attention on
the key levels.

### Step 6 — Pre-plan targets before the entry
Know where price is likely to go before entering. Mark logical targets using structure,
prior highs/lows, and obvious liquidity zones. Example: first target a prior low; second
target below equal lows where sell-side liquidity rests. Pre-planning keeps decisions
objective and doubles as a trade filter — if the targets do not make sense in context, the
setup is not worth taking.

### Step 7 — Wait for lower time frame confirmation
Once price reaches the HTF area of interest, drop to the lower timeframe (usually the
five-minute). Even with a clear HTF bias, price can move against it internally. Do not
enter yet — wait for a clear **CHoCH on the 5-minute**: price breaks structure, takes out
the most recent internal low, and closes below it. This filters low-quality setups; most
traders jump in too early here.

### Step 8 — Execute with lower time frame confirmation
The trigger: price forms a lower high and then breaks structure on the LTF — a "stronger
change of character" — showing momentum shifting in line with the HTF bias. Execution is
now a plan across structure, liquidity, and multi-timeframe confirmation, not a reaction.

**8a — Entry, stop, invalidation.** Stop always at invalidation, never a random number —
placed beyond the lower high that formed before the break. A stop has two jobs: protect
capital and invalidate the idea.

**8b — Risk-to-reward.** Check R:R before entering; minimum **3R**. Example offers just
under 3R to the first target and more to the second — good enough. Consistency over
perfect numbers.

### Managing the trade
Take partial profit at the first target, let the remainder run toward the second while
structure holds. In the example the first target hits quickly; the second is reached later
as liquidity below the lows is taken.

### Why it works
Mechanical, rooted in price action, structure-first. Not about indicators or predicting
algo behavior — about structure shifts and participant intent. OTE enforces patience, FVGs
define areas, LTF confirmation gates entry. Stacking confluence raises probability. The
essentials: trading rules, structure, confirmation, and a stop that makes sense.

---

## Cross-reference to platform artifacts

Each step maps to an existing atomic skill and/or candidate-spec concept. This is a
navigation aid only — it asserts no equivalence and validates nothing.

| Article step | Platform skill (`.claude/skills/`) | Related spec concept |
|---|---|---|
| 1 HTF structure | `market-structure` | HTF bias stage (ST-C2), H4 bias |
| 2 External highs/lows, BOS | `liquidity-sweep`, `choch-bos` | liquidity stage, BOS confirmation |
| 3 CHoCH direction | `choch-bos` | HTF/LTF CHoCH |
| 4 Premium/discount, OTE | `premium-discount` | OTE stage, discount/premium thresholds |
| 5 FVG areas of interest | `fair-value-gap` | FVG alignment stage (HTF/MF/LTF) |
| 6 Pre-plan targets | `trade-management` | targets t1/t2/t3, liquidity draws |
| 7 LTF confirmation | `entry-confirmation` | LTF confirmation stage |
| 8 Execute + stop + R:R | `entry-confirmation`, `risk-management` | execution stage, `min_rr` |

**Closest active candidate:** ST-C2 ("Hybrid Liquidity-First Unified SMC Pipeline",
`specs/st-c2.yaml`) is the platform candidate most structurally similar to this
liquidity→bias→OTE→FVG→LTF-CHoCH sequence. ST-C2 has **no RCR filed yet** and
`engine_implements_spec: false` — nothing here changes that. If any idea from this article
is to influence ST-C2, it belongs in that RCR as a stated, falsifiable hypothesis.

**Data-hygiene note:** the full local EURUSD/GBPUSD/XAUUSD history has already been used
for diagnosis across every ST-C1 variant and cannot be treated as pristine OOS for any
future test motivated by this reference.
