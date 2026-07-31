# ST-C3 Session Calendar Qualification Report

Status: **BLOCKED**

Reason: session-calendar compatibility is not yet qualified; source-integrity sample remains incomplete

Recommendation: **CONTINUE_EVIDENCE_COLLECTION**

Guardrail: Session calendar qualification is evidence only; it does not change ST-C3 contracts, validators, approval, replay, or prices.

## Research Question

Which provider's trading calendar matches the assumptions encoded in the ST-C3 Dataset Contract?

## Sources

- ST-C3 contract/loader: `contracts/DATASET_CONTRACT.yaml and validation/st_c3/dataset_loader.py`
- Dukascopy DST notice: https://www.dukascopy.com/swiss/english/about/ournews/daylight-saving-time-2025-in-the-us
- Dukascopy FX market hours: https://www.dukascopy.com/swiss/english/fx-market-tools/forex-market-hours/
- HistData timezone FAQ: https://www.histdata.com/f-a-q/

## Provider Profiles

### ST-C3 Dataset Contract

- Basis: contract/loader
- Trading week close UTC: Friday 22:00 UTC year-round by current loader
- DST behavior: no DST adjustment encoded
- Daily rollover time: 22:00 UTC treated as rollover evidence bucket in source-integrity tooling
- Holiday handling: weekends plus fixed Jan 1 and Dec 25 closures
- Expected zero-tick periods: `weekend/fixed-holiday closure only; market-open missing timestamps block approval`
- Bar-generation policy: all required fixed-timeframe candles must exist; no fabrication/interpolation
- Session-boundary conventions: UTC-only fixed boundaries
- Compatibility assessment: baseline contract, not a provider

### Dukascopy

- Basis: official DST notice plus live probes
- Trading week close UTC: observed Friday 22:00 UTC in winter and Friday 21:00 UTC during DST
- DST behavior: official Dukascopy notice says FX trading day/opening/settlement changes from 22:00 GMT to 21:00 GMT during US DST
- Daily rollover time: provider opening/settlement shifts with US DST per official notice
- Holiday handling: not fully qualified for ST-C3 sample
- Expected zero-tick periods: `{'Friday 20:00 PARSED': 10, 'Friday 21:00 EMPTY_PAYLOAD': 8, 'Friday 21:00 PARSED': 2, 'Friday 22:00 EMPTY_PAYLOAD': 8, 'Monday 21:00 PARSED': 2}`
- Bar-generation policy: tick source; zero-byte source hours observed at DST Friday 21:00 UTC
- Session-boundary conventions: DST_FRIDAY_CLOSE_PROVIDER_CALENDAR_MISMATCH
- Compatibility assessment: session mismatch with current fixed-UTC ST-C3 Friday close assumption

### HistData

- Basis: FAQ plus cached M1 reference comparison
- Trading week close UTC: cached reference shows many DST Friday 21:00 UTC rows and zero Friday 22:00 UTC rows in the focused probes
- DST behavior: official FAQ says CSV timestamps use EST without daylight-saving adjustments
- Daily rollover time: not fully qualified for ST-C3 sample
- Holiday handling: not fully qualified for ST-C3 sample
- Expected zero-tick periods: `{'DUKASCOPY_AND_REFERENCE_ABSENT': 49, 'DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT': 151}`
- Bar-generation policy: M1 bar files; methodology for zero-volume/carry-forward bars remains unqualified
- Session-boundary conventions: fixed EST timestamp convention converted to UTC in current reference tooling
- Compatibility assessment: closer to current fixed Friday 22:00 UTC assumption for probed DST Friday close, but full suitability remains unqualified

## Comparison Matrix

| Criterion | ST-C3 Dataset Contract | Dukascopy | HistData |
|---|---|---|---|
| `trading_week_close_utc` | Friday 22:00 UTC year-round by current loader | observed Friday 22:00 UTC in winter and Friday 21:00 UTC during DST | cached reference shows many DST Friday 21:00 UTC rows and zero Friday 22:00 UTC rows in the focused probes |
| `dst_behavior` | no DST adjustment encoded | official Dukascopy notice says FX trading day/opening/settlement changes from 22:00 GMT to 21:00 GMT during US DST | official FAQ says CSV timestamps use EST without daylight-saving adjustments |
| `daily_rollover_time` | 22:00 UTC treated as rollover evidence bucket in source-integrity tooling | provider opening/settlement shifts with US DST per official notice | not fully qualified for ST-C3 sample |
| `holiday_handling` | weekends plus fixed Jan 1 and Dec 25 closures | not fully qualified for ST-C3 sample | not fully qualified for ST-C3 sample |
| `expected_zero_tick_periods` | weekend/fixed-holiday closure only; market-open missing timestamps block approval | {'Friday 20:00 PARSED': 10, 'Friday 21:00 EMPTY_PAYLOAD': 8, 'Friday 21:00 PARSED': 2, 'Friday 22:00 EMPTY_PAYLOAD': 8, 'Monday 21:00 PARSED': 2} | {'DUKASCOPY_AND_REFERENCE_ABSENT': 49, 'DUKASCOPY_ZERO_TICK_REFERENCE_PRESENT': 151} |
| `bar_generation_policy` | all required fixed-timeframe candles must exist; no fabrication/interpolation | tick source; zero-byte source hours observed at DST Friday 21:00 UTC | M1 bar files; methodology for zero-volume/carry-forward bars remains unqualified |
| `session_boundary_conventions` | UTC-only fixed boundaries | DST_FRIDAY_CLOSE_PROVIDER_CALENDAR_MISMATCH | fixed EST timestamp convention converted to UTC in current reference tooling |
| `compatibility_assessment` | baseline contract, not a provider | session mismatch with current fixed-UTC ST-C3 Friday close assumption | closer to current fixed Friday 22:00 UTC assumption for probed DST Friday close, but full suitability remains unqualified |

## Decision Layer

- Data completeness: not final until 100-day deterministic source-integrity sample completes
- Session compatibility: not final until provider calendars are reviewed against ST-C3 replay assumptions
- Provider freeze rule: after provider selection, use one canonical data source and session calendar for all ST-C3 v1.x validation stages

## Decision

No provider is accepted or rejected by this report. The Dataset Contract remains unchanged, dataset approval remains blocked, and replay remains blocked.
