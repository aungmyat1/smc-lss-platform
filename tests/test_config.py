"""Tests for the Phase 3 M1 configuration loader (src/config.py).
Run: python -m pytest -q"""
import os, sys, textwrap
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import config as cfgmod

ROOT = os.path.dirname(os.path.dirname(__file__))
WATCHLIST = os.path.join(ROOT, "config", "watchlist.yaml")
SPEC_V1 = os.path.join(ROOT, "specs", "v1.yaml")


def _write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(textwrap.dedent(text))


VALID_WATCHLIST = """\
    strategy_spec: specs/v3.5.yaml
    autonomy:
      demo: auto_on_engine_ready
      live: auto_on_promotion
      engine_implements_spec: false
      promote_to_live: false
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
    _write(wl, VALID_WATCHLIST)
    _write(spec, VALID_SPEC)
    return str(wl), str(spec)


# --- real repo config: the loader must accept what's actually committed ---

def test_loads_real_repo_config():
    cfg = cfgmod.load(WATCHLIST, SPEC_V1)
    assert cfg.risk.min_rr > 0
    assert cfg.execution.equilibrium_window > 0
    assert len(cfg.symbols_active) >= 1
    assert cfg.strategy.symbol


# --- happy path on a controlled fixture ---

def test_valid_config_loads_and_exposes_typed_values(cfg_files):
    wl, spec = cfg_files
    cfg = cfgmod.load(wl, spec)
    assert cfg.risk.risk_pct_demo == 0.5
    assert cfg.risk.risk_pct_live == 1.0
    assert cfg.risk.min_rr == 2.0
    assert cfg.execution.equilibrium_window == 40
    assert cfg.execution.breakeven_at_r == 1.0
    assert cfg.strategy.swing_lookback == 2
    assert cfg.symbol("EURUSD").mt5 == "EURUSD"


def test_risk_pct_for_env(cfg_files):
    wl, spec = cfg_files
    cfg = cfgmod.load(wl, spec)
    assert cfg.risk.risk_pct_for("demo") == 0.5
    assert cfg.risk.risk_pct_for("live") == 1.0
    with pytest.raises(cfgmod.ConfigError):
        cfg.risk.risk_pct_for("paper")


def test_unknown_symbol_raises(cfg_files):
    wl, spec = cfg_files
    cfg = cfgmod.load(wl, spec)
    with pytest.raises(cfgmod.ConfigError):
        cfg.symbol("DOESNOTEXIST")


def test_killzone_hour_lookup(cfg_files):
    wl, spec = cfg_files
    cfg = cfgmod.load(wl, spec)
    assert cfg.execution.session_of(8) == ("LONDON-KZ", True)
    assert cfg.execution.session_of(13) == ("NY-KZ", True)
    assert cfg.execution.session_of(23) == ("OFF-KZ", False)


# --- fail-closed: missing/invalid values must raise, never silently default ---

def test_missing_file_raises(cfg_files):
    _, spec = cfg_files
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load("does/not/exist.yaml", spec)


def test_missing_risk_key_raises(tmp_path, cfg_files):
    _, spec = cfg_files
    broken = VALID_WATCHLIST.replace("min_rr: 2.0\n", "")
    wl = tmp_path / "broken.yaml"
    _write(wl, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(wl), spec)


def test_invalid_risk_pct_type_raises(tmp_path, cfg_files):
    _, spec = cfg_files
    broken = VALID_WATCHLIST.replace("risk_pct_demo: 0.5", 'risk_pct_demo: "half a percent"')
    wl = tmp_path / "broken.yaml"
    _write(wl, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(wl), spec)


def test_negative_risk_pct_raises(tmp_path, cfg_files):
    _, spec = cfg_files
    broken = VALID_WATCHLIST.replace("risk_pct_demo: 0.5", "risk_pct_demo: -0.5")
    wl = tmp_path / "broken.yaml"
    _write(wl, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(wl), spec)


def test_invalid_position_amount_mode_raises(tmp_path, cfg_files):
    _, spec = cfg_files
    broken = VALID_WATCHLIST.replace("position_amount_mode: risk_pct", "position_amount_mode: yolo")
    wl = tmp_path / "broken.yaml"
    _write(wl, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(wl), spec)


def test_empty_active_symbols_raises(tmp_path, cfg_files):
    _, spec = cfg_files
    broken = VALID_WATCHLIST.replace(
        "      active:\n        - {name: EURUSD, mt5: EURUSD, pip: 0.0001, pip_value_per_lot: 10.0, variants: [E1M3]}\n",
        "      active: []\n")
    wl = tmp_path / "broken.yaml"
    _write(wl, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(wl), spec)


def test_killzone_end_before_start_raises(tmp_path, cfg_files):
    _, spec = cfg_files
    broken = VALID_WATCHLIST.replace(
        "london: {start_hour: 7, end_hour: 10}", "london: {start_hour: 10, end_hour: 7}")
    wl = tmp_path / "broken.yaml"
    _write(wl, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(str(wl), spec)


def test_missing_spec_key_raises(tmp_path, cfg_files):
    wl, _ = cfg_files
    broken = VALID_SPEC.replace("swing_lookback: 2\n", "")
    spec = tmp_path / "broken_spec.yaml"
    _write(spec, broken)
    with pytest.raises(cfgmod.ConfigError):
        cfgmod.load(wl, str(spec))
