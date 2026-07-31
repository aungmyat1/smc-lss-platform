from providers.common.adapter import HealthCheck, ProviderMetadata


class TrueFXAdapter:
    name = "truefx"

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata("TrueFX", ("EURUSD", "GBPUSD"), ("tick",), "UNVERIFIED", "account_terms_required", "TRUEFX_TOKEN")

    def health_check(self) -> HealthCheck:
        return HealthCheck("TrueFX", False, "CREDENTIALS_UNAVAILABLE", "TRUEFX_TOKEN/account session is not configured.")

    def download_sample(self, output_dir, *, days=100):
        return {"status": "BLOCKED", "reason": "TrueFX credentials/account access unavailable."}

    def download_range(self, output_dir, start, end):
        return {"status": "BLOCKED", "reason": "TrueFX credentials/account access unavailable."}

    def normalize(self, input_dir, output_dir):
        return {"status": "BLOCKED", "reason": "No TrueFX sample acquired."}

    def validate(self, normalized_dir):
        return {"status": "NOT_EVALUATED", "st_c3_status": "NOT_RUN", "reason": "Credentials unavailable."}
