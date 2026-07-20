# ST-C1 Execution Audit

| Component | Status | Evidence |
|---|---|---|
| Spread / slippage / commission in replay | PARTIAL | Replay uses fixed `spread_points=25`, `slippage_points=3`, `commission_r=0` in `validation/historical_replay_engine.py:165-181` and persists them in the report assumptions. |
| Symbol-specific pip conversion | FAIL | The validation path hardcodes `point_size=0.0001` for every symbol (`validation/historical_replay_engine.py:165-181`, `validation/historical_replay_engine.py:413-417`), while `config/watchlist.yaml:57-58` defines `EURUSD pip=0.0001` and `XAUUSD pip=0.1`. |
| Contract / tick metadata | FAIL | Replay does not read per-symbol contract size or tick size from the active symbol metadata; the execution audit is therefore symbol-agnostic. |
| Lot sizing / risk sizing | FAIL | The replay path does not call the sizing helper in `src/live_signal.py:30-49`; it computes R-multiples only, not broker lots or account-based exposure. |
| Execution assumptions by symbol | FAIL | EURUSD and XAUUSD both ran under the same execution assumptions in `reports/ST-C1_REAL_DATA_STATISTICAL_VALIDATION.md` assumptions block, despite differing pip scales. |
| Live sizing code path | PASS (separate path) | `src/live_signal.py:30-49` uses per-symbol pip and pip value from config for live sizing, proving the repo already knows the metadata it failed to use in validation. |

## Measured Impact

- EURUSD average gross R: `-0.0420`; average cost drag: `5.7218R`; average net R: `-5.7638R`.
- EURUSD gross winners converted to net losers: `31/31`.
- XAUUSD average gross R: `0.1629`; average cost drag: `0.0005R`; average net R: `0.1624R`.
- XAUUSD gross winners converted to net losers: `0/40`.

## Conclusion

- Execution realism is the primary implementation defect in the validation path.
- The replay engine is not using symbol-specific execution metadata, which is a direct contributor to the EURUSD collapse.
