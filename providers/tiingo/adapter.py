from providers.common.adapter import HealthCheck, ProviderMetadata


class TiingoAdapter:
    name = "tiingo"

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata("Tiingo FX", ("EURUSD", "GBPUSD"), ("intraday_bars",), "UNVERIFIED", "api_terms_required", "TIINGO_API_TOKEN")

    def health_check(self) -> HealthCheck:
        return HealthCheck("Tiingo FX", False, "CREDENTIALS_UNAVAILABLE", "TIINGO_API_TOKEN is not configured.")

    def download_sample(self, output_dir, *, days=100):
        return {"status": "BLOCKED", "reason": "Tiingo API token unavailable."}

    def download_range(self, output_dir, start, end):
        return {"status": "BLOCKED", "reason": "Tiingo API token unavailable."}

    def normalize(self, input_dir, output_dir):
        return {"status": "BLOCKED", "reason": "No Tiingo sample acquired."}

    def validate(self, normalized_dir):
        return {"status": "NOT_EVALUATED", "st_c3_status": "NOT_RUN", "reason": "Credentials unavailable."}
