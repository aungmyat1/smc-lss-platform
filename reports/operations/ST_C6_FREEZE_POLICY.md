# ST-C6 Repository Freeze Policy

Status: **ACTIVE**

The data-pipeline engineering phase is frozen for replay readiness. Changes to
the following areas are allowed only for verified defects, reproducibility fixes,
or operational evidence updates:

| Area | Freeze Status |
| --- | --- |
| ST-C1 strategy specification | FROZEN |
| ST-C2 deterministic rule engine | FROZEN |
| ST-C3 governance thresholds | FROZEN |
| Provider qualification criteria | FROZEN |
| ST-C5 orchestration and gates | FROZEN |

## Permitted Changes

- Bug fixes with clear reproduction evidence
- Report refreshes produced by existing commands
- Operational evidence from MT5 synchronization attempts
- Documentation updates that clarify existing process without changing gates
- Execution-infrastructure work that does not unlock replay, demo, or live paths

## Prohibited Changes Until Replay Completion

- Threshold relaxation
- Manual dataset approval
- Strategy logic changes
- Replay unlock without approved dataset evidence
- New ST-C5.x framework phases
- New governance gates that duplicate existing ST-C5/ST-C3 decisions

## Current Guardrail

Dataset remains not approved. Replay, strategy validation, demo, and live remain
blocked until the existing pipeline produces the required evidence.
