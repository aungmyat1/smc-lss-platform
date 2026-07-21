"""Tests for the Phase 3 M1 configuration loader (src/config.py).
Run: python -m pytest -q"""
import os, sys, textwrap
import pytest
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import config as cfgmod

ROOT = os.path.dirname(os.path.dirname(__file__))
WATCHLIST = os.path.join(ROOT, "config", "watchlist.yaml")
SPEC_V1 = os.path.join(ROOT, "specs", "v1.yaml")
RESEARCH_SPEC = os.path.join(ROOT, "specs", "v3.6.yaml")
V39_SPEC = os.path.join(ROOT, "specs", "v3.9.yaml")


def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(textwrap.dedent(text))


def _yaml_path(path):
    return path.replace("\\", "/")


VALID_WATCHLIST = """\
    strategy_spec: specs/v1.yaml
    research_spec: specs/v3.6.yaml
    governance:
      schema_version: 1
      config_version: 3.6.0
      registry_version: 3.6.0
      approval_package_required: true
      fail_closed: true
    autonomy:
      demo: proposal_only
      live: disabled
      engine_implements_spec: false
      promote_to_live: false
    reporting:
      telegram:
        enabled: false
        bot_token_env: TELEGRAM_BOT_TOKEN
        chat_id_env: TELEGRAM_CHAT_ID
        events: [scan_summary, decision]
    cadence:
      runs_utc: ["07:00", "12:00"]
      weekdays_only: true
      timeframes: {etrigger: H1, context: D1, confirm: M5}
    risk:
      risk_pct_demo: 0.5
      risk_pct_live: 1.0
      position_amount_mode: risk_pct
      fixed_lot_demo: 0.01
      fixed_lot_live: 0.01
      fixed_notional_demo: 0.0
      fixed_notional_live: 0.0
      daily_loss_pct: 3.0
      max_positions: 3
      portfolio_heat_pct: 4.0
      min_rr: 2.0
    execution:
      equilibrium_window: 40
      liquidity_sweep_lookback_bars: 10
      breakeven_at_r: 1.0
      lot_step: 0.01
      killzones:
        london: {start_hour: 7, end_hour: 10}
        ny: {start_hour: 12, end_hour: 15}
    symbols:
      active:
        - {name: EURUSD, mt5: EURUSD, pip: 0.0001, pip_value_per_lot: 10.0, variants: [E1M3]}
      pending: []
    """

VALID_SPEC = """\
    version: 1
    symbol: EURUSD
    htf: H4
    entry_tf: M15
    ltf_confirm: M1
    swing_lookback: 2
    equal_level_tol_pips: 2
    min_fvg_pips: 3
    risk_pct: 1.0
    min_rr: 2.0
    sessions: [london, ny]
    """


@pytest.fixture
def cfg_files(tmp_path):
    wl = tmp_path / "watchlist.yaml"
    spec = tmp_path / "v1.yaml"
    research = tmp_path / "v3.6.yaml"
    watchlist_text = VALID_WATCHLIST.replace("specs/v1.yaml", _yaml_path(str(spec))).replace("specs/v3.6.yaml", _yaml_path(str(research)))
    _write(wl, watchlist_text)
    _write(spec, VALID_SPEC)
    _write(research, VALID_SPEC.replace("version: 1", "version: 3.6"))
    return str(wl), str(spec), str(research)


# --- real repo config: the loader must accept what's actually committed ---

def test_loads_real_repo_config():
    cfg = cfgmod.load(WATCHLIST, SPEC_V1)
    assert cfg.risk.min_rr > 0
    assert cfg.execution.equilibrium_window > 0
    assert len(cfg.symbols_active) >= 1
    assert cfg.strategy.symbol
    assert cfg.schema_version == 1
    assert cfg.config_version == "3.6.0"
    assert cfg.registry_version == "3.6.0"


# --- happy path on a controlled fixture ---

def test_valid_config_loads_and_exposes_typed_values(cfg_files):
    wl, spec, _research = cfg_files
    cfg = cfgmod.load(wl, spec)
    assert cfg.risk.risk_pct_demo == 0.5
    assert cfg.risk.risk_pct_live == 1.0
    assert cfg.risk.min_rr == 2.0
    assert cfg.execution.equilibrium_window == 40
    assert cfg.execution.breakeven_at_r == 1.0
    assert cfg.strategy.swing_lookback == 2
    assert cfg.symbol("EURUSD").mt5 == "EURUSD"
    assert cfg.strategy_spec_path == spec
    assert cfg.research_spec_path.endswith("v3.6.yaml")
    assert cfg.config_hash


def test_risk_pct_for_env(cfg_files):
    wl, spec, _research = cfg_files
    cfg = cfgmod.load(wl, spec)
    assert cfg.risk.risk_pct_for("demo") == 0.5
    assert cfg.risk.risk_pct_for("live") == 1.0
    with pytest.raises(cfgmod.ConfigError):
        cfg.risk.risk_pct_for("paper")


def test_unknown_symbol_raises(cfg_files):
    wl, spec, _research = cfg_files
    cfg = cfgmod.load(wl, spec)
    with pytest.raises(cfgmod.ConfigError):
        cfg.symbol("DOESNOTEXIST")


def test_killzone_hour_lookup(cfg_files):
    wl, spec, _research = cfg_files
    cfg = cfgmod.load(wl, spec)
    assert cfg.execution.session_of(8) == ("LONDON-KZ", True)
    assert cfg.execution.session_of(13) == ("NY-KZ", True)
    assert cfg.execution.session_of(23) == ("OFF-KZ", False)


def test_loaded_config_is_immutable(cfg_files):
    wl, spec, _research = cfg_files
    cfg = cfgmod.load(wl, spec)
    with pytest.raises(AttributeError):
        cfg.strategy.symbol = "GBPUSD"
    with pytest.raises(AttributeError):
        cfg.risk.min_rr = 3.0
    with pytest.raises(TypeError):
        cfg.governance["schema_version"] = 2


# --- fail-closed: missing/invalid values must raise, never silently default ---

def test_missing_file_raises(cfg_files):
    _, spec, _research = cfg_files
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load("does/not/exist.yaml", spec)


def test_missing_risk_key_raises(tmp_path, cfg_files):
    _, spec, _research = cfg_files
    broken = VALID_WATCHLIST.replace("min_rr: 2.0\n", "")
    wl = tmp_path / "broken.yaml"
    _write(wl, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(wl), spec)


def test_invalid_risk_pct_type_raises(tmp_path, cfg_files):
    _, spec, _research = cfg_files
    broken = VALID_WATCHLIST.replace("risk_pct_demo: 0.5", 'risk_pct_demo: "half a percent"')
    wl = tmp_path / "broken.yaml"
    _write(wl, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(wl), spec)


def test_negative_risk_pct_raises(tmp_path, cfg_files):
    _, spec, _research = cfg_files
    broken = VALID_WATCHLIST.replace("risk_pct_demo: 0.5", "risk_pct_demo: -0.5")
    wl = tmp_path / "broken.yaml"
    _write(wl, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(wl), spec)


def test_invalid_position_amount_mode_raises(tmp_path, cfg_files):
    _, spec, _research = cfg_files
    broken = VALID_WATCHLIST.replace("position_amount_mode: risk_pct", "position_amount_mode: yolo")
    wl = tmp_path / "broken.yaml"
    _write(wl, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(wl), spec)


def test_empty_active_symbols_raises(tmp_path, cfg_files):
    _, spec, _research = cfg_files
    broken = VALID_WATCHLIST.replace(
        "      active:\n        - {name: EURUSD, mt5: EURUSD, pip: 0.0001, pip_value_per_lot: 10.0, variants: [E1M3]}\n",
        "      active: []\n")
    wl = tmp_path / "broken.yaml"
    _write(wl, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(wl), spec)


def test_killzone_end_before_start_raises(tmp_path, cfg_files):
    _, spec, _research = cfg_files
    broken = VALID_WATCHLIST.replace(
        "london: {start_hour: 7, end_hour: 10}", "london: {start_hour: 10, end_hour: 7}")
    wl = tmp_path / "broken.yaml"
    _write(wl, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(wl), spec)


def test_missing_spec_key_raises(tmp_path, cfg_files):
    wl, _spec, _research = cfg_files
    broken = VALID_SPEC.replace("swing_lookback: 2\n", "")
    spec = tmp_path / "broken_spec.yaml"
    _write(spec, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(wl, str(spec))


def test_unknown_governance_key_rejected(tmp_path, cfg_files):
    _, spec, research = cfg_files
    broken = VALID_WATCHLIST.replace(
        "      fail_closed: true\n",
        "      fail_closed: true\n      unexpected_key: nope\n",
    )
    wl = tmp_path / "broken_governance.yaml"
    _write(wl, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(wl), spec)


def test_version_compatibility_rejected(tmp_path, cfg_files):
    _, spec, research = cfg_files
    broken = VALID_WATCHLIST.replace("config_version: 3.6.0", "config_version: 3.7.0")
    wl = tmp_path / "broken_versions.yaml"
    _write(wl, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(wl), spec)


def test_strategy_spec_must_match_loaded_spec_path(tmp_path, cfg_files):
    wl, spec, research = cfg_files
    broken = VALID_WATCHLIST.replace("strategy_spec: specs/v1.yaml", "strategy_spec: specs/other.yaml")
    broken_path = tmp_path / "broken_strategy_path.yaml"
    _write(broken_path, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(broken_path), spec)


# --- governance consistency: contradictory fail-closed fields must fail CI ---
# Added for the ST-C1 v3.9 governance/conformance task. v3.9 is a pending
# research candidate (engine_implements_spec: false everywhere) and must
# stay that way until a conformant engine and its full test suite exist.
# This test fails CI the moment any of these interlocks silently drift to a
# less restrictive state, instead of relying on prose in status docs.

def test_real_repo_autonomy_flags_are_fail_closed():
    cfg = cfgmod.load(WATCHLIST, SPEC_V1)
    assert cfg.autonomy.demo != "auto_on_engine_ready"
    assert cfg.autonomy.demo != "auto"
    assert cfg.autonomy.live == "disabled"
    assert cfg.autonomy.engine_implements_spec is False
    assert cfg.autonomy.promote_to_live is False


def test_v39_spec_still_declares_engine_not_implemented():
    with open(V39_SPEC, "r", encoding="utf-8") as fh:
        v39 = yaml.safe_load(fh)
    assert v39["implementation_status"]["engine_implements_spec"] is False
    assert v39["status"] in ("draft", "candidate", "research_candidate")
    assert v39["track"] == "research"


def test_watchlist_research_spec_does_not_point_at_unconformant_v39():
    cfg = cfgmod.load(WATCHLIST, SPEC_V1)
    with open(V39_SPEC, "r", encoding="utf-8") as fh:
        v39 = yaml.safe_load(fh)
    if cfg.research_spec_path.replace("\\", "/").endswith("v3.9.yaml"):
        assert v39["implementation_status"]["engine_implements_spec"] is True, (
            "config/watchlist.yaml points research_spec at specs/v3.9.yaml, "
            "but v3.9 declares engine_implements_spec: false — the config "
            "must not adopt an unconformant research spec as active."
        )
