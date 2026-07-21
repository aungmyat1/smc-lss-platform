# ST-C1 Strategy Conformance Matrix

Current baseline scope: this report treats the baseline as a test of the implemented ST-C1 surrogate unless every rule below is demonstrated as implemented.

| Declared ST-C1/v3.6 Rule | Actual Replay Implementation | Source | Status | Consequence |
|---|---|---|---|---|
| E1 D1 gap reaction | D1 window is loaded and availability is recorded, but D1 gap objects and H1 first-touch reaction are not used to create signals. | `validation/historical_replay_engine.py::generate_signal`, `evaluate_features` | MISSING | E1 evidence is not represented in the baseline signal set. |
| E2 fresh H1 POI | POI selection uses recent M5 order blocks/FVGs from the execution window, not a lifecycle-managed H1 POI causally linked to H1 BOS. | `HistoricalReplayEngine._select_poi` | PARTIAL | Baseline POI evidence is an execution-timeframe surrogate. |
| E3 external H1 liquidity | Sweep detection uses recent M5 sweeps and does not require H1 dealing-range extremity classification. | `evaluate_features`, `generate_signal` | PARTIAL | E3 baseline cannot be read as strict external-liquidity evidence. |
| Displacement | Core `smc_engine.displacement_move` exists, but Phase A replay signal generation does not require it before entry. | `src/smc_engine.py::displacement_move`, `HistoricalReplayEngine.generate_signal` | PARTIAL | Signals may lack the declared displacement filter. |
| Real CHOCH classification | Signal metadata labels CHOCH from latest generic signal/stop level; it is not a separately classified close-confirmed structural reversal in replay. | `HistoricalReplayEngine.generate_signal` | MISLABELED | CHOCH counts should be treated as surrogate confirmation labels. |
| M1/M2/M3 selection | Replay does not explicitly select among M1/M2/M3; it combines generic signal, sweep, POI, stop, and target checks. | `HistoricalReplayEngine.generate_signal` | MISSING | Funnel counts do not distinguish declared entry models. |
| Causal event ordering | H1/D1 windows are bounded by bar-close visibility, but sweep/POI/confirmation causality is only partially encoded. | `_available_index`, `_bounded_context_window`, `generate_signal` | PARTIAL | Some look-ahead protection exists, but rule ordering is incomplete. |
| POI freshness and invalidation | No FRESH/MITIGATED/INVALIDATED lifecycle or max-age expiry is enforced for replay POIs. | `_select_poi` | MISSING | Old or invalid POIs can enter the surrogate candidate set. |
| Target selection | Uses nearest M5 swing beyond entry with artificial fallback at minimum R when no liquidity level exists. | `_determine_target` | PARTIAL | Baseline targets can exceed identified liquidity evidence. |
| One signal per structure | Structure keys are consumed once per replay. | `HistoricalReplayEngine.replay`, `BatchValidationRunner.run_job` | IMPLEMENTED | Duplicate structures are blocked in the surrogate replay. |
| D1 data usage | D1 is loaded, synchronized, and availability is tracked; D1 rule logic is not used for signal gating. | `load_series`, `_bounded_context_window`, `evaluate_features` | PARTIAL | D1 coverage is necessary for reproducibility but not sufficient for v3.6 conformance. |

Conclusion: Phase A should not claim ST-C1/v3.6 strategy validity. It can only claim reproducibility and performance characteristics of the implemented surrogate replay.
