# ST-C4.1 Provider Registry

Guardrail: Provider qualification only; ST-C3 thresholds and downstream gates remain unchanged.

| Provider | Status | Evaluation | API | Cost |
|---|---|---|---|---|
| dukascopy | rejected_st_c3_evidence | evaluated_failed_st_c3 | public_historical_export | free |
| truefx | candidate_credentials_required | not_evaluated_credentials_unavailable | historical_download_account | subscription_or_account_dependent |
| tiingo | candidate_api_token_required | not_evaluated_credentials_unavailable | rest | subscription_dependent |
| histdata | rejected_prior_candidate | evaluated_failed_integrity | web_download | free |
| darwinex | candidate_ftp_required | not_evaluated_credentials_unavailable | ftp | account_dependent |
| mt5 | candidate_terminal_export_required | not_evaluated_complete_export_unavailable | local_terminal | broker_dependent |
