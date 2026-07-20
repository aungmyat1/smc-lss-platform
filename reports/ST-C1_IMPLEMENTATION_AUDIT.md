# ST-C1 Implementation Audit

| Rule | Status | Evidence |
|---|---|---|
| Entry logic | PARTIAL | `validation/historical_replay_engine.py:250-304` enforces H1 bias, session, sweep, and POI gating plus next-bar entry; `src/live_signal.py:16-28` adds equilibrium/structure confirmation, but explicit CHoCH, premium/discount, and sequential invalidation telemetry are not persisted. |
| Exit logic | FAIL | `validation/historical_replay_engine.py:360-413` simulates only stop-first or target or timeout; the contract management layer (`strategies/candidates/ST-C1_v1.yaml:184-197`) requires break-even, partial take, and time-stop management that are absent from replay. |
| Risk sizing | FAIL | Replay validation does not size by stop distance; the live sizing code exists in `src/live_signal.py:30-49`, but the validation runner writes fixed execution assumptions and no lot sizing path is used. |
| Stop placement | PARTIAL | `validation/historical_replay_engine.py:322-344` places stops beyond sweep/OB/FVG references with ATR buffer, but the validation path is symbol-agnostic and uses a fixed point size. |
| Take profit | PARTIAL | `validation/historical_replay_engine.py:346-358` uses swing extremum fallback/min-RR logic, but not the contract language of nearest unswept external liquidity (`strategies/candidates/ST-C1_v1.yaml:191-197`). |
| Break-even | FAIL | No replay state advances the stop to breakeven after +1R; the management clause in the contract is not implemented in replay. |
| Session filters | PASS | `validation/historical_replay_engine.py:145-156` and `validation/historical_replay_engine.py:266-275` restrict trades to London/NewYork UTC windows. |
| Liquidity rules | PASS/PARTIAL | Sweep confirmation is enforced in `validation/historical_replay_engine.py:276-283`; however prior-session liquidity, inducement distance, and explicit equal-high/low pool scoring are not separately measured. |
| Order block rules | PARTIAL | OB detection is present (`validation/historical_replay_engine.py:215-225`), but freshness/mitigation/invalidation state is not recorded as a first-class audit field. |
| FVG rules | PARTIAL | FVG detection exists (`validation/historical_replay_engine.py:215-225`), but age expiry/inversion mechanics from the fuller spec are not represented in the replay telemetry. |
| MSS rules | PARTIAL | The replay uses a simplified latest-swing-break signal via `src/live_signal.py:16-28`; no separate MSS lifecycle is persisted for audit. |
| CHoCH rules | PARTIAL | CHoCH is implied by the signal helper and contract text (`strategies/candidates/ST-C1_v1.yaml:107-109`, `src/live_signal.py:16-28`) but not recorded as an explicit audited event. |

## Audit Conclusion

- The implementation is deterministic and reproducible, but it is only a partial realization of the richer contract language.
- The biggest gap is not entry generation; it is post-entry management and execution realism.
