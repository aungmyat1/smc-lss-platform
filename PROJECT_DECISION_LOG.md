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
