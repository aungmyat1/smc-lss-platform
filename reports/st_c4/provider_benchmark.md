# ST-C4 Provider Benchmark

Guardrail: ST-C4 benchmark only; rejected ST-C3 data remains immutable and replay remains blocked.

## Sources

- Dukascopy historical export: https://www.dukascopy.com/swiss/english/marketwatch/historical/
- TrueFX downloads/terms: https://www.truefx.com/truefx-historical-downloads-2/ and https://www.truefx.com/truefx-terms-and-conditions/
- HistData FAQ/specification: https://www.histdata.com/f-a-q/ and https://www.histdata.com/f-a-q/data-files-detailed-specification/
- Darwinex tick data: https://www.darwinex.com/tick-data
- Tiingo Forex API: https://www.tiingo.com/documentation/forex
- Polygon/Massive Forex REST API: https://massive.com/docs/rest/forex/overview

## Matrix

| Provider | Status | Sample | Missing Rate | Quality Score | Blocker |
|---|---|---|---:|---:|---|
| Dukascopy | REJECTED_ST_C3_EVIDENCE | VALIDATED_SAMPLE_FAIL | 0.004301970580072162 | 71.75 | Effective missing rate exceeds ST-C3 threshold and unknown gaps remain |
| HistData | REJECTED_PRIOR_CANDIDATE | VALIDATED_SAMPLE_FAIL | n/a | 50.5 | Timezone policy and prior integrity failure |
| TrueFX | CANDIDATE_REQUIRES_ACCOUNT_OR_COMMERCIAL_ACCESS | NOT_ACQUIRED_ACCESS_REQUIRED | n/a | 71.25 | Account/commercial access and licensing acceptance required before sampling |
| Darwinex | CANDIDATE_REQUIRES_LIVE_ACCOUNT_FTP | NOT_ACQUIRED_ACCESS_REQUIRED | n/a | 68.0 | Live account/FTP access required before sampling |
| Tiingo FX | CANDIDATE_REQUIRES_API_TOKEN | NOT_ACQUIRED_ACCESS_REQUIRED | n/a | 70.25 | Coverage begins 2020, so 2021-2025 is plausible but must be sampled |
| Polygon/Massive Forex | CANDIDATE_REQUIRES_API_SUBSCRIPTION | NOT_ACQUIRED_ACCESS_REQUIRED | n/a | 57.75 | Documented empty intervals conflict with ST-C3 continuous-minute tolerance until sampled |
| Broker MT5 Export | CANDIDATE_REQUIRES_TERMINAL_HISTORY | NOT_ACQUIRED_LOCAL_TERMINAL_REQUIRED | n/a | 44.5 | Local terminal history is broker-specific and not independently reproducible yet |

## Conclusion

No provider is selected as canonical in this sprint because no candidate has a passing validated 100-day sample under ST-C3 governance.
