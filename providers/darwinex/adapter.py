from providers.common.adapter import HealthCheck, ProviderMetadata


class DarwinexAdapter:
    name = "darwinex"

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata("Darwinex", ("EURUSD", "GBPUSD"), ("tick",), "UNVERIFIED", "live_account_terms_required", "DARWINEX_FTP_USER")

    def health_check(self) -> HealthCheck:
        return HealthCheck("Darwinex", False, "CREDENTIALS_UNAVAILABLE", "Darwinex FTP credentials are not configured.")

    def download_sample(self, output_dir, *, days=100):
        return {"status": "BLOCKED", "reason": "Darwinex FTP credentials unavailable."}

    def download_range(self, output_dir, start, end):
        return {"status": "BLOCKED", "reason": "Darwinex FTP credentials unavailable."}

    def normalize(self, input_dir, output_dir):
        return {"status": "BLOCKED", "reason": "No Darwinex sample acquired."}

    def validate(self, normalized_dir):
        return {"status": "NOT_EVALUATED", "st_c3_status": "NOT_RUN", "reason": "Credentials unavailable."}
