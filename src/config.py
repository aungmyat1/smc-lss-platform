#!/usr/bin/env python3
"""Configuration loader for the SMC-LSS live execution path (Phase 3 M1).

Loads and validates config/watchlist.yaml (risk, symbols, execution knobs) and
specs/v1.yaml (v1 strategy shape). Fails closed: a missing or invalid value
raises ConfigError rather than being silently defaulted, so a broken config
blocks the live path instead of running on a guessed value.
"""
from __future__ import annotations

import logging
from typing import Any, NoReturn

import yaml

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Raised when configuration is missing or fails schema validation."""


def _reject(message: str) -> NoReturn:
    logger.error(message)
    raise ConfigError(message)


def _load_yaml(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except FileNotFoundError:
        _reject(f"config file not found: {path}")
    except yaml.YAMLError as ex:
        _reject(f"{path}: invalid YAML ({ex})")
    if not isinstance(data, dict):
        _reject(f"{path}: expected a YAML mapping at top level")
    return data


def _type_name(typ: type | tuple[type, ...]) -> str:
    if isinstance(typ, tuple):
        return " or ".join(t.__name__ for t in typ)
    return typ.__name__


def _require(d: dict, key: str, path: str, typ: type | tuple[type, ...] | None = None) -> Any:
    if key not in d or d[key] is None:
        _reject(f"{path}: missing required key '{key}'")
    v = d[key]
    numeric = typ is int or typ == (int, float)
    if typ is not None and (not isinstance(v, typ) or (numeric and isinstance(v, bool))):
        _reject(f"{path}: '{key}' must be {_type_name(typ)}, got {type(v).__name__}")
    return v


def _positive(v: float, path: str, key: str) -> float:
    if not (isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0):
        _reject(f"{path}: '{key}' must be a positive number, got {v!r}")
    return v


def _hour(v: int, path: str, key: str) -> int:
    if not (isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 24):
        _reject(f"{path}: '{key}' must be an hour in [0, 24], got {v!r}")
    return v


class RiskConfig:
    def __init__(self, d: dict, path: str) -> None:
        self.risk_pct_demo = _positive(_require(d, "risk_pct_demo", path, (int, float)), path, "risk_pct_demo")
        self.risk_pct_live = _positive(_require(d, "risk_pct_live", path, (int, float)), path, "risk_pct_live")
        self.min_rr = _positive(_require(d, "min_rr", path, (int, float)), path, "min_rr")
        self.daily_loss_pct = _positive(_require(d, "daily_loss_pct", path, (int, float)), path, "daily_loss_pct")
        self.max_positions = _require(d, "max_positions", path, int)
        if self.max_positions < 1:
            _reject(f"{path}: 'max_positions' must be >= 1")
        self.portfolio_heat_pct = _positive(_require(d, "portfolio_heat_pct", path, (int, float)), path, "portfolio_heat_pct")
        self.position_amount_mode = _require(d, "position_amount_mode", path, str)
        if self.position_amount_mode not in ("risk_pct", "fixed_lot", "fixed_notional"):
            _reject(f"{path}: 'position_amount_mode' must be one of risk_pct|fixed_lot|fixed_notional")
        self.fixed_lot_demo = _require(d, "fixed_lot_demo", path, (int, float))
        self.fixed_lot_live = _require(d, "fixed_lot_live", path, (int, float))
        self.fixed_notional_demo = _require(d, "fixed_notional_demo", path, (int, float))
        self.fixed_notional_live = _require(d, "fixed_notional_live", path, (int, float))

    def risk_pct_for(self, env: str) -> float:
        if env not in ("demo", "live"):
            _reject(f"unknown env '{env}' (expected 'demo' or 'live')")
        return self.risk_pct_live if env == "live" else self.risk_pct_demo


class KillzoneConfig:
    def __init__(self, name: str, d: dict, path: str) -> None:
        self.name = name
        self.start_hour = _hour(_require(d, "start_hour", path, int), path, "start_hour")
        self.end_hour = _hour(_require(d, "end_hour", path, int), path, "end_hour")
        if self.end_hour <= self.start_hour:
            _reject(f"{path}: 'end_hour' must be greater than 'start_hour'")

    def contains(self, hour: int) -> bool:
        return self.start_hour <= hour < self.end_hour


class ExecutionConfig:
    def __init__(self, d: dict, path: str) -> None:
        self.equilibrium_window = _require(d, "equilibrium_window", path, int)
        if self.equilibrium_window < 1:
            _reject(f"{path}: 'equilibrium_window' must be >= 1")
        self.liquidity_sweep_lookback_bars = _require(d, "liquidity_sweep_lookback_bars", path, int)
        if self.liquidity_sweep_lookback_bars < 1:
            _reject(f"{path}: 'liquidity_sweep_lookback_bars' must be >= 1")
        self.breakeven_at_r = _positive(_require(d, "breakeven_at_r", path, (int, float)), path, "breakeven_at_r")
        self.lot_step = _positive(_require(d, "lot_step", path, (int, float)), path, "lot_step")
        kz = _require(d, "killzones", path, dict)
        if not kz:
            _reject(f"{path}: 'killzones' must define at least one session")
        self.killzones = {name: KillzoneConfig(name, v, f"{path}.killzones.{name}") for name, v in kz.items()}

    def session_of(self, hour: int) -> tuple[str, bool]:
        for kz in self.killzones.values():
            if kz.contains(hour):
                return kz.name.upper() + "-KZ", True
        return "OFF-KZ", False


class SymbolConfig:
    def __init__(self, d: dict, path: str) -> None:
        self.name = _require(d, "name", path, str)
        self.mt5 = _require(d, "mt5", path, str)
        self.pip = _positive(_require(d, "pip", path, (int, float)), path, "pip")
        self.pip_value_per_lot = _positive(_require(d, "pip_value_per_lot", path, (int, float)), path, "pip_value_per_lot")
        self.variants = d.get("variants", [])


class StrategyConfig:
    """Strategy-shape parameters for the legacy v1 engine (specs/v1.yaml)."""

    def __init__(self, d: dict, path: str) -> None:
        self.symbol = _require(d, "symbol", path, str)
        self.htf = _require(d, "htf", path, str)
        self.entry_tf = _require(d, "entry_tf", path, str)
        self.ltf_confirm = _require(d, "ltf_confirm", path, str)
        self.swing_lookback = _require(d, "swing_lookback", path, int)
        if self.swing_lookback < 1:
            _reject(f"{path}: 'swing_lookback' must be >= 1")
        self.equal_level_tol_pips = _positive(_require(d, "equal_level_tol_pips", path, (int, float)), path, "equal_level_tol_pips")
        self.min_fvg_pips = _positive(_require(d, "min_fvg_pips", path, (int, float)), path, "min_fvg_pips")
        self.sessions = _require(d, "sessions", path, list)
        if not self.sessions:
            _reject(f"{path}: 'sessions' must be non-empty")


class Config:
    def __init__(self, watchlist_path: str, spec_path: str, raw_watchlist: dict, raw_spec: dict) -> None:
        self.watchlist_path = watchlist_path
        self.spec_path = spec_path
        self.strategy_spec = _require(raw_watchlist, "strategy_spec", watchlist_path, str)
        self.risk = RiskConfig(_require(raw_watchlist, "risk", watchlist_path, dict), f"{watchlist_path}:risk")
        self.execution = ExecutionConfig(_require(raw_watchlist, "execution", watchlist_path, dict), f"{watchlist_path}:execution")

        symbols = _require(raw_watchlist, "symbols", watchlist_path, dict)
        active = _require(symbols, "active", f"{watchlist_path}:symbols", list)
        if not active:
            _reject(f"{watchlist_path}:symbols.active must list at least one symbol")
        self.symbols_active = [SymbolConfig(s, f"{watchlist_path}:symbols.active[{i}]") for i, s in enumerate(active)]
        pending = symbols.get("pending", [])
        self.symbols_pending = [SymbolConfig(s, f"{watchlist_path}:symbols.pending[{i}]") for i, s in enumerate(pending)]

        self.strategy = StrategyConfig(raw_spec, spec_path)

    def symbol(self, name: str) -> SymbolConfig:
        for s in self.symbols_active + self.symbols_pending:
            if s.name == name:
                return s
        _reject(f"unknown symbol '{name}' (not in {self.watchlist_path} symbols.active/pending)")


def load(watchlist_path: str = "config/watchlist.yaml", spec_path: str = "specs/v1.yaml") -> Config:
    raw_watchlist = _load_yaml(watchlist_path)
    raw_spec = _load_yaml(spec_path)
    return Config(watchlist_path, spec_path, raw_watchlist, raw_spec)
