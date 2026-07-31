# ST-C5 Broker-First Data Qualification Plan

Objective: qualify broker-native MT5 history as the next candidate data source
without changing ST-C3, strategy logic, or validation thresholds.

Broker candidate: **Vantage MT5**

Candidate directory: `research_data\canonical\st_c5_vantage_mt5_candidate`

Workflow:

1. Open and authenticate the broker MT5 terminal.
2. Run `python -m tools.st_c5_broker_data_qualification --acquire`.
3. Let the guarded MT5 downloader export EURUSD/GBPUSD H4/M15/M3.
4. Run preliminary integrity checks.
5. If candidate integrity passes, run the unchanged ST-C3 pipeline in a separate sprint.

Guardrail: ST-C5 broker-data qualification only; dataset approval, replay, strategy validation, demo, and live remain blocked.
