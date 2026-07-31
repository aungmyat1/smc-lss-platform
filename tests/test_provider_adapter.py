from __future__ import annotations

from providers.dukascopy import DukascopyAdapter
from providers.tiingo import TiingoAdapter
from providers.truefx import TrueFXAdapter


def test_provider_adapters_expose_common_interface(tmp_path):
    for adapter in (DukascopyAdapter(), TrueFXAdapter(), TiingoAdapter()):
        assert adapter.metadata().provider
        assert adapter.health_check().provider
        assert adapter.download_sample(tmp_path)["status"] in {"SKIPPED", "BLOCKED"}
        assert adapter.download_range(tmp_path, "2025-01-01", "2025-01-02")["status"] == "BLOCKED"
        assert adapter.normalize(tmp_path, tmp_path)["status"] in {"SKIPPED", "BLOCKED"}
        assert adapter.validate(tmp_path)["st_c3_status"] in {"FAIL", "NOT_RUN"}


def test_credential_gated_adapter_blocks_without_token(tmp_path):
    result = TiingoAdapter().download_sample(tmp_path)

    assert result["status"] == "BLOCKED"
    assert "token" in result["reason"].lower()
