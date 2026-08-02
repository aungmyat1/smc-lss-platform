# OP-01 Provider Evaluation Freeze Rule

Status: **ACTIVE**

Once a provider evaluation begins, the acquisition configuration is frozen until
that provider reaches an operational decision.

## Frozen During Provider Evaluation

| Configuration Area | Frozen Value Source |
| --- | --- |
| Broker server | Provider capability matrix |
| Account type | Provider capability matrix |
| Symbols | ST-C3 requirements: EURUSD, GBPUSD |
| Timeframe requirements | ST-C3/ST-C5 requirements: M1/M3/M15/H4 evidence, H4/M15/M3 candidate export |
| Date range | Required start `2021-01-04T00:00:00Z`; required end per timeframe |
| Validation criteria | Frozen ST-C3 and ST-C5 gates |
| Pipeline sequence | Frozen ST-C5 orchestrator |
| Connection handoff | `reports/operations/PROVIDER_CONNECTION_HANDOFF_CHECKLIST.md` |

## Prohibited During Provider Evaluation

- Changing broker server mid-evaluation
- Switching account type mid-evaluation
- Changing required symbols
- Changing required timeframes
- Lowering historical requirements
- Relaxing ST-C3 thresholds
- Editing exported CSVs manually
- Filling missing bars manually
- Changing export code to force a pass
- Running a history gate while connected to the wrong provider server

## Decision Rule

If the provider fails under the frozen configuration, the failure is evidence
about that provider/account/source combination. Do not reinterpret it as a
software defect unless new evidence proves a reproducible code bug.
