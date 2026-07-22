# Reference: Worked Example Trades — E1/E2/E3 × M1/M2/M3 grid (1BULLBEAR "9 Eg" set)

**Type:** External reference material — worked chart examples. NOT an authoritative spec,
NOT evidence of edge.
**Status:** Recorded for reference only. Adds no rule, changes no `specs/*.yaml`, and
carries no execution or promotion authority. Using any pattern here in a candidate must
still go through an RCR per [`../../RESEARCH-CHARTER.md`](../../RESEARCH-CHARTER.md).
**Source:** owner-supplied screenshot set, `…/Downloads/bullbear_d3_bot/9 Eg/` — a
"1BULLBEAR / Day Trading Maneuvers" course deck (slide numbers 57–85 visible). 27 JPEG
chart captures. Captured 2026-07-22.
**Companion refs:** [`../smc-8step-entry-model-dailypriceaction.md`](../smc-8step-entry-model-dailypriceaction.md)
(execution walkthrough) and [`../smc-definitive-guide-dailypriceaction.md`](../smc-definitive-guide-dailypriceaction.md)
(concept glossary). This file is the *worked-example* layer.

> **Read this first — survivorship caveat.** These are hand-picked winning illustrations
> from a teaching deck. Every one resolves cleanly to target. They show the *intended
> geometry* of each E-trigger, not its win rate. This is exactly the population the
> platform's full-history backtests do NOT show — and why v3.9/v3.10, which implement these
> same E1/E2/E3 triggers, came out net-losing across the full population (v3.9 PF 0.138,
> v3.10 PF 0.471). Treat these as "what a textbook win looks like," never as proof the
> trigger is profitable. The gap between this highlight reel and the backtest funnel IS the
> research problem.

---

## The grid — how the set is organized

The 27 captures form a 3×3 matrix of nine example trades. Two independent axes:

**E-axis = entry trigger family** (matches the platform's E1/E2/E3 schema directly):

| Code | Trigger (from slide titles) | Platform analog |
|---|---|---|
| **E1** | "PRICE FILL & REACT 1D GAP" — price fills a daily gap and reacts | E1 = D1 gap reaction (the trigger v3.10 re-enabled) |
| **E2** | "PRICE REACT 1H POI" — reaction at a 1-hour point of interest | E2 = 1H POI continuation |
| **E3** | "PRICE SWEEP LIQUIDITY" — liquidity grab then reverse | E3 = liquidity-sweep entry |

**M-axis = model / setup character** (the "why" behind the entry):

| Code | Model (from slide titles) | Related skill |
|---|---|---|
| **M1** | "Character Change with Inducement" | `choch-bos`, `inducement` |
| **M2** | "Supply/Demand Shift" | `order-block`, `market-structure` |
| **M3** | (third variant; see per-cell captures) | — |

**Workflow inside every example** (top-down, matches the DPA 8-step model Steps 1→7):
`1D check` (bias + buy/sell-side liquidity) → `1H check` (POI / structure) →
`5M confirm, entry and target` (LTF trigger + entry box + R geometry) → one or more
**target horizons**: `5M intraday`, `1H intraweek`, `1H swing`, `1H overnight`, `1D swing`.
Entry captures show the risk box (pink) vs reward box (green) with bar-count, elapsed time,
and volume annotated.

Instruments span the captures: ETHUSD perp (Binance), EUR/GBP and GBP/JPY (Eightcap) —
i.e. crypto and FX, illustrating the author's claim that the schema is instrument-agnostic.

---

## Per-example catalog (all 27 files)

Image links are relative to `./bullbear-9eg/`. **Binaries not yet copied into the repo**
(sandbox unavailable at capture time) — see "Pending" below.

### E1 — 1D gap fill & react
- **E1·M1** — `E1M1, 1H check.jpeg`, `E1M1, 1H intra week target.jpeg`, `E1M1, 5M  confirm, entry and target.jpeg`
- **E1·M2** (Supply/Demand Shift, ETHUSD) — `E1M2, 1D check.jpeg`, `E1M2, 1H check.jpeg`, `E1M2, 5M confirm, entry and target.jpeg`, `E1M2, 1H intraweek traget.jpeg`, `E1M2, 1H swing target.jpeg`
- **E1·M3** — `E1M3, 1D check.jpeg`, `E1M3, 1H check.jpeg`, `E1M3, 5M confirm,entry and target.jpeg`, `E1M3, 1H intraweek target.jpeg`

### E2 — 1H POI react
- **E2·M1** (Character Change with Inducement, EUR/GBP) — `E2M1, 1H check.jpeg`, `E2M1, 5M confirm, entry and target.jpeg`, `E2M1, 1H swing target.jpeg`
- **E2·M2** — `E2M2, 1H check.jpeg`, `E2M2, 5M confirm, entry and overnight target.jpeg`
- **E2·M3** — `E2M3, 1H check.jpeg`, `E2M3, 1H intraweek target.jpeg`

### E3 — liquidity sweep
- **E3·M1** — `E3M1, 1H check.jpeg`, `E3M1, 5M confirm, entry and target.jpeg`, `E3M1, 1H intraweek target.jpeg`
- **E3·M2** (Supply/Demand Shift, GBP/JPY) — `E3M2, 1H check.jpeg`, `E3M2, 5M confirm, entry and target.jpeg`, `E3M2, 1H intraweek target.jpeg`
- **E3·M3** — `E3M3, 1H check.jpeg`, `E3M3, 5M confirm, entry and target.jpeg`

---

## Why this matters to the platform

1. **Ground-truth geometry for the E1/E2/E3 conformance work.** When auditing whether
   `src/signal_v39.py` / `signal_v310.py` fire on the *right* shapes, these nine examples are
   a visual acceptance set: a correct engine should recognize the entry conditions each
   capture depicts. They can seed positive test cases for the E-triggers.

2. **They sharpen the open research question, they don't answer it.** The platform already
   detects all three triggers; the losses come from full-population cost, not from missing
   the pattern. These winners illustrate the numerator (clean setups) with none of the
   denominator (every setup that looked identical and failed net-of-cost).

3. **Target-horizon vocabulary.** The intraday / intraweek / swing / overnight target labels
   map to `trade-management`'s t1/t2/t3 draws — useful if an RCR ever revisits target
   selection.

## Pending / follow-ups
- [ ] Copy the 27 JPEGs into `docs/reference/example-trades/bullbear-9eg/` (blocked by
      sandbox unavailability at capture; do when the shell is back so the links above
      resolve and the reference survives Downloads being cleared).
- [ ] Optional: extract one positive test fixture per E-trigger from the 5M entry captures,
      to strengthen the v3.9/v3.10 conformance suites — research-track, no spec change.

**Data-hygiene note:** these are illustrative captures on ETH/EURGBP/GBPJPY, not the
platform's EURUSD/GBPUSD/XAUUSD test data; they are not an OOS partition and prove nothing
statistically.
