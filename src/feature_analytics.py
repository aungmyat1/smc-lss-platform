#!/usr/bin/env python3
"""Phase 0.5 — Feature Database analytics: validate the Phase 0 feature
table BEFORE the signal engine consumes it.

Read-only. Does not modify src/signal_v35.py, src/features.py, or
src/smc_engine.py, and does not change any trading rule — this measures
whether the raw building blocks carry any signal at all, independent of
how a future strategy might combine them.

Definitions (stated explicitly, per this project's no-qualitative-terms
convention — reports/quant_research_audit.md Sec 2):
  - Forward-return horizons: 12 bars (~1h) and 48 bars (~4h) on M5. Two
    horizons, not one, so a feature's apparent edge can be checked for
    consistency rather than trusted from a single arbitrary window.
  - R unit: forward price change / ATR(t) measured AT the bar the feature
    is observed. This is an ATR-normalized proxy, not a trade-level R —
    no stop/target exists at this layer (no strategy has been rewritten
    yet), so this cannot be a real R-multiple. Treat it as "how many
    ATRs did price move" for cross-symbol/cross-volatility comparability.
  - Directional features (sweep_bull/bear, bos bull/bear, trend BULLISH/
    BEARISH, premium/discount) are scored against the direction they
    imply: R is signed so positive = price moved the expected way.
  - "Win" = R > 0 at the given horizon — an expected-direction check, NOT
    a target-hit definition (there is no target at this layer).
  - Baseline = the same statistic computed unconditionally (every bar),
    for comparison. A feature with conditional stats indistinguishable
    from baseline carries no signal, however plausible it looks.
  - Significance: z = (mean_cond - mean_base) / SE, where SE is the
    conditional sample's own standard error (stdev / sqrt(n)) — a simple,
    transparent effect-size check, not a substitute for the bootstrap/
    Monte Carlo work reports/quant_research_audit.md Phase 5 calls for at
    the strategy level. |z| >= 2 is annotated but not treated as proof.

Usage:
  python src/feature_analytics.py --symbol EURUSD --candles data/EURUSD_M5.csv
"""
from __future__ import annotations
import argparse, math, os, statistics
import smc_engine as e
import features as feat

HORIZONS = (12, 48)


# ---------------------------------------------------------------- forward R

def compute_forward_r(c, atr_period=14):
    """Per-bar {horizon: raw signed forward R} — (close[t+h]-close[t])/ATR(t).
    None where t+h is out of range."""
    n = len(c)
    out = []
    for t in range(n):
        atr_t = e.atr(c, t, atr_period)
        row = {}
        for h in HORIZONS:
            if t + h >= n or atr_t <= 0:
                row[h] = None
            else:
                row[h] = (c[t + h]["close"] - c[t]["close"]) / atr_t
        out.append(row)
    return out


# ---------------------------------------------------------------- features

def _feature_series(rows):
    """Named boolean feature -> (is_active_at_t, implied_direction) series,
    extracted from the Phase 0 feature rows. direction: +1 bull-implied,
    -1 bear-implied, 0 non-directional (reported but not R-scored)."""
    series = {}
    series["sweep_bull"] = [(r["sweep_bull"], 1) for r in rows]
    series["sweep_bear"] = [(r["sweep_bear"], -1) for r in rows]
    series["choch"] = [(r["choch"], 0) for r in rows]
    series["bos_bull"] = [(r["bos_dir"] == "bull", 1) for r in rows]
    series["bos_bear"] = [(r["bos_dir"] == "bear", -1) for r in rows]
    series["trend_bullish"] = [(r["trend"] == "BULLISH", 1) for r in rows]
    series["trend_bearish"] = [(r["trend"] == "BEARISH", -1) for r in rows]
    series["discount"] = [(r["premium_discount"] == "DISCOUNT", 1) for r in rows]
    series["premium"] = [(r["premium_discount"] == "PREMIUM", -1) for r in rows]
    series["ob_bull_present"] = [(r["ob_bull_zone"] is not None, 1) for r in rows]
    series["ob_bear_present"] = [(r["ob_bear_zone"] is not None, -1) for r in rows]
    series["ob_bull_fresh"] = [(r["ob_bull_status"] == "FRESH", 1) for r in rows]
    series["ob_bear_fresh"] = [(r["ob_bear_status"] == "FRESH", -1) for r in rows]
    series["fvg_bull_present"] = [(r["fvg_bull_zone"] is not None, 1) for r in rows]
    series["fvg_bear_present"] = [(r["fvg_bear_zone"] is not None, -1) for r in rows]
    series["session_london"] = [(r["session"] == "LONDON", 0) for r in rows]
    series["session_newyork"] = [(r["session"] == "NEWYORK", 0) for r in rows]
    series["session_off"] = [(r["session"] == "OFF", 0) for r in rows]
    return series


STATE_FIELDS = {
    "trend": lambda r: r["trend"],
    "premium_discount": lambda r: r["premium_discount"],
    "ob_bull_status": lambda r: r["ob_bull_status"],
    "ob_bear_status": lambda r: r["ob_bear_status"],
    "session": lambda r: r["session"],
}


# ---------------------------------------------------------------- stats

def _mean(xs):
    return statistics.mean(xs) if xs else None


def _stdev(xs):
    return statistics.stdev(xs) if len(xs) >= 2 else None


def _win_rate(rs):
    return round(100 * sum(1 for r in rs if r > 0) / len(rs), 2) if rs else None


def _z(mean_cond, mean_base, cond_vals):
    if mean_cond is None or mean_base is None or len(cond_vals) < 2:
        return None
    se = _stdev(cond_vals) / math.sqrt(len(cond_vals))
    if se == 0:
        return None
    return round((mean_cond - mean_base) / se, 2)


def run_lengths(values):
    """Consecutive-run lengths for a state series (list of hashable values)."""
    runs = []
    if not values:
        return runs
    cur, n = values[0], 1
    for v in values[1:]:
        if v == cur:
            n += 1
        else:
            runs.append((cur, n))
            cur, n = v, 1
    runs.append((cur, n))
    return runs


def session_distribution(active_idx, sessions):
    dist = {}
    for i in active_idx:
        s = sessions[i]
        dist[s] = dist.get(s, 0) + 1
    total = len(active_idx) or 1
    return {k: round(100 * v / total, 1) for k, v in sorted(dist.items(), key=lambda kv: -kv[1])}


def analyze_binary_feature(name, series, forward_r, rows, baseline_r):
    active_idx = [i for i, (active, _d) in enumerate(series) if active]
    n = len(rows)
    freq = round(100 * len(active_idx) / n, 3) if n else 0.0
    direction = series[0][1] if series else 0

    atr_vals = [rows[i]["atr"] for i in active_idx if rows[i]["atr"] is not None]
    sessions = [rows[i]["session"] for i in range(n)]

    per_horizon = {}
    for h in HORIZONS:
        cond_r = []
        for i in active_idx:
            raw = forward_r[i][h]
            if raw is None:
                continue
            cond_r.append(raw * direction if direction != 0 else raw)
        base_r = [v * direction if direction != 0 else v for v in baseline_r[h] if v is not None]
        mean_cond, mean_base = _mean(cond_r), _mean(base_r)
        per_horizon[h] = {
            "n": len(cond_r),
            "mean_R": round(mean_cond, 4) if mean_cond is not None else None,
            "baseline_mean_R": round(mean_base, 4) if mean_base is not None else None,
            "win_rate_pct": _win_rate(cond_r),
            "baseline_win_rate_pct": _win_rate(base_r),
            "z_vs_baseline": _z(mean_cond, mean_base, cond_r),
        }

    return {
        "name": name, "direction": direction,
        "occurrence": len(active_idx), "frequency_pct": freq,
        "atr_mean": round(_mean(atr_vals), 6) if atr_vals else None,
        "atr_stdev": round(_stdev(atr_vals), 6) if atr_vals else None,
        "session_distribution_pct": session_distribution(active_idx, sessions),
        "horizons": per_horizon,
    }


def analyze_state_field(name, extractor, rows):
    values = [extractor(r) for r in rows]
    runs = run_lengths(values)
    by_state = {}
    for state, length in runs:
        by_state.setdefault(state, []).append(length)
    n = len(values)
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return {
        "name": name,
        "states": {
            str(state): {
                "occurrence_bars": counts.get(state, 0),
                "frequency_pct": round(100 * counts.get(state, 0) / n, 2) if n else 0,
                "episodes": len(lengths),
                "avg_duration_bars": round(_mean(lengths), 2) if lengths else None,
                "max_duration_bars": max(lengths) if lengths else None,
            }
            for state, lengths in by_state.items()
        },
    }


# ---------------------------------------------------------------- interactions

INTERACTIONS = [
    ("sweep_bull + choch", "sweep_bull", "choch", 1),
    ("sweep_bear + choch", "sweep_bear", "choch", -1),
    ("sweep_bull + ob_bull_present", "sweep_bull", "ob_bull_present", 1),
    ("sweep_bear + ob_bear_present", "sweep_bear", "ob_bear_present", -1),
    ("ob_bull_present + fvg_bull_present", "ob_bull_present", "fvg_bull_present", 1),
    ("ob_bear_present + fvg_bear_present", "ob_bear_present", "fvg_bear_present", -1),
    ("trend_bullish + discount", "trend_bullish", "discount", 1),
    ("trend_bearish + premium", "trend_bearish", "premium", -1),
    ("session_london + sweep_bull", "session_london", "sweep_bull", 1),
    ("session_london + sweep_bear", "session_london", "sweep_bear", -1),
    ("session_newyork + sweep_bull", "session_newyork", "sweep_bull", 1),
    ("session_newyork + sweep_bear", "session_newyork", "sweep_bear", -1),
]


def analyze_interaction(label, a_series, b_series, direction, forward_r, baseline_r, n):
    both_idx = [i for i in range(n) if a_series[i][0] and b_series[i][0]]
    per_horizon = {}
    for h in HORIZONS:
        cond_r = [forward_r[i][h] * direction for i in both_idx if forward_r[i][h] is not None]
        base_r = [v * direction for v in baseline_r[h] if v is not None]
        mean_cond, mean_base = _mean(cond_r), _mean(base_r)
        per_horizon[h] = {
            "n": len(cond_r),
            "mean_R": round(mean_cond, 4) if mean_cond is not None else None,
            "baseline_mean_R": round(mean_base, 4) if mean_base is not None else None,
            "win_rate_pct": _win_rate(cond_r),
            "z_vs_baseline": _z(mean_cond, mean_base, cond_r),
        }
    return {"label": label, "occurrence": len(both_idx),
            "frequency_pct": round(100 * len(both_idx) / n, 4) if n else 0, "horizons": per_horizon}


# ---------------------------------------------------------------- correlation

def phi_coefficient(a, b):
    """Pearson correlation for two binary (0/1) series — the standard
    correlation measure for binary variables (phi coefficient)."""
    n = len(a)
    if n == 0:
        return None
    n11 = sum(1 for x, y in zip(a, b) if x and y)
    n10 = sum(1 for x, y in zip(a, b) if x and not y)
    n01 = sum(1 for x, y in zip(a, b) if not x and y)
    n00 = sum(1 for x, y in zip(a, b) if not x and not y)
    n1_, n0_ = n11 + n10, n01 + n00
    n_1, n_0 = n11 + n01, n10 + n00
    denom = math.sqrt(n1_ * n0_ * n_1 * n_0)
    if denom == 0:
        return None
    return round((n11 * n00 - n10 * n01) / denom, 3)


# ---------------------------------------------------------------- orchestration

def run(symbol, candles_path, atr_period=14, corr_threshold=0.7):
    c = e.load_candles(candles_path)
    rows = feat.compute_features(c, atr_period=atr_period)
    forward_r = compute_forward_r(c, atr_period=atr_period)
    n = len(rows)
    baseline_r = {h: [row[h] for row in forward_r] for h in HORIZONS}

    series_map = _feature_series(rows)
    binary_results = {name: analyze_binary_feature(name, s, forward_r, rows, baseline_r)
                      for name, s in series_map.items()}
    state_results = {name: analyze_state_field(name, extractor, rows)
                     for name, extractor in STATE_FIELDS.items()}

    interaction_results = []
    for label, a_name, b_name, direction in INTERACTIONS:
        interaction_results.append(analyze_interaction(
            label, series_map[a_name], series_map[b_name], direction, forward_r, baseline_r, n))

    # importance: rank by |z| at the primary (first) horizon, requiring a
    # minimum sample size so a rare-but-huge-z feature doesn't top the list
    # on 5 occurrences.
    MIN_N_FOR_RANKING = 30
    primary_h = HORIZONS[0]
    importance = []
    for name, res in binary_results.items():
        hstat = res["horizons"][primary_h]
        if hstat["n"] < MIN_N_FOR_RANKING or hstat["z_vs_baseline"] is None:
            continue
        importance.append({
            "name": name, "z": hstat["z_vs_baseline"], "mean_R": hstat["mean_R"],
            "baseline_mean_R": hstat["baseline_mean_R"], "n": hstat["n"],
            "frequency_pct": res["frequency_pct"],
        })
    importance.sort(key=lambda r: -abs(r["z"]))

    # correlation matrix over binary features
    bool_series = {name: [1 if s[i][0] else 0 for i in range(n)] for name, s in series_map.items()}
    names = list(bool_series.keys())
    corr_pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            phi = phi_coefficient(bool_series[a], bool_series[b])
            if phi is not None:
                corr_pairs.append((a, b, phi))
    corr_pairs.sort(key=lambda x: -abs(x[2]))
    redundant = [p for p in corr_pairs if abs(p[2]) >= corr_threshold]

    return {
        "symbol": symbol, "n_bars": n, "atr_period": atr_period, "horizons": HORIZONS,
        "binary_results": binary_results, "state_results": state_results,
        "interaction_results": interaction_results, "importance": importance,
        "corr_pairs": corr_pairs, "redundant": redundant,
    }
