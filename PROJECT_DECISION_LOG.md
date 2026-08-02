# Project Decision Log

This is an append-only operational decision log. Each entry records the
decision, evidence, rationale, and affected documents. It does not replace the
ST-C governance artifacts.

| Date | Decision | Evidence | Rationale | Outcome | Affected Documents |
| --- | --- | --- | --- | --- | --- |
| 2026-08-02 | Freeze research data pipeline framework | `reports/operations/ST_C6_FREEZE_POLICY.md` | ST-C1 through ST-C5 framework is mature; remaining blocker is external data acquisition. | Framework frozen except verified defects and operational evidence refreshes. | `reports/operations/ST_C6_FREEZE_POLICY.md` |
| 2026-08-02 | Open OP-01 Broker History Acquisition Campaign | `reports/operations/OP_01_BROKER_HISTORY_ACQUISITION_CAMPAIGN.md` | VTMarkets-Demo history evidence must be resolved operationally without new ST-C phases. | OP-01 opened; VTMarkets-Demo remains under evaluation. | `reports/operations/OP_01_ATTEMPT_TRACKER.json` |
| 2026-08-02 | VTMarkets-Demo Attempt 02 stopped at history gate | `reports/operations/ST_C6_OPERATIONAL_ATTEMPT_02.md` | Terminal is connected and symbols are selected, but M1 is unavailable in-window and M15 starts after the required date. | `REQUIRES_HISTORY_SYNC`; no export or replay actions allowed. | `reports/operations/OP_01_PROVIDER_CAPABILITY_MATRIX.md` |
| 2026-08-02 | Make Attempt 03 the final controlled VTMarkets-Demo synchronization attempt | `reports/operations/OP_01_ATTEMPT_03_PROTOCOL.md` | Repeated identical synchronization failures should not be retried indefinitely. | Pending Attempt 03. | `reports/operations/OP_01_ATTEMPT_TRACKER.json` |
| 2026-08-02 | Activate provider evaluation freeze rule | `reports/operations/OP_01_PROVIDER_EVALUATION_FREEZE_RULE.md` | Provider comparisons are unreliable if server, account type, symbols, timeframes, date range, or validation criteria change mid-evaluation. | Active for OP-01 provider evaluations. | `reports/operations/OP_01_PROVIDER_CAPABILITY_MATRIX.md` |
| 2026-08-02 | Classify VTMarkets-Demo as operationally insufficient for ST-C3 history | `reports/operations/OP_01_ATTEMPT_03_RESULT.md` | Three controlled attempts produced materially identical lower-timeframe history failures. | VTMarkets-Demo closed for ST-C3 historical research data; next provider is MetaQuotes Demo. | `reports/operations/OP_01_PROVIDER_CAPABILITY_MATRIX.md` |
| 2026-08-02 | Prepare ST-C7 strategy validation program | `reports/operations/ST_C7_STRATEGY_VALIDATION_PROGRAM.md` | Once a dataset is approved, the next uncertainty is whether the frozen strategy has a statistically measurable edge. | ST-C7 prepared but blocked pending approved dataset. | `reports/operations/ST_C7_STRATEGY_VALIDATION_PROGRAM.md` |
| 2026-08-02 | Open OP-02 MetaQuotes Demo qualification | `reports/operations/providers/MetaQuotes/OP_02_METAQUOTES_DEMO_QUALIFICATION.md` | VTMarkets-Demo is closed for ST-C3 history; next provider must use the unchanged frozen ST-C5 pipeline. | OP-02 pending execution. | `reports/operations/OP_01_PROVIDER_CAPABILITY_MATRIX.md` |
| 2026-08-02 | Freeze ST-C7 replay gates before results | `reports/operations/ST_C7_VALIDATION_GATES.md` | Strategy validation standards must be predeclared before replay evidence exists. | ST-C7 gates frozen pending approved dataset. | `reports/operations/ST_C7_REPLAY_SPECIFICATION.md` |
