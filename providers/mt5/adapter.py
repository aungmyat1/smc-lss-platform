from providers.common.adapter import HealthCheck, ProviderMetadata


class MT5Adapter:
    name = "mt5"

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata("Broker MT5 Export", ("EURUSD", "GBPUSD"), ("M3", "M15", "H4"), "BROKER_SERVER_UNVERIFIED", "broker_terms_required", None)

    def health_check(self) -> HealthCheck:
        return HealthCheck("Broker MT5 Export", False, "COMPLETE_EXPORT_UNAVAILABLE", "No complete broker MT5 export has been validated.")

    def download_sample(self, output_dir, *, days=100):
        return {"status": "BLOCKED", "reason": "Complete local MT5 terminal export unavailable."}

    def download_range(self, output_dir, start, end):
        return {"status": "BLOCKED", "reason": "Complete local MT5 terminal export unavailable."}

    def normalize(self, input_dir, output_dir):
        return {"status": "BLOCKED", "reason": "No complete MT5 sample acquired."}

    def validate(self, normalized_dir):
        return {"status": "NOT_EVALUATED", "st_c3_status": "NOT_RUN", "reason": "Complete export unavailable."}
