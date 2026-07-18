#!/usr/bin/env python3
"""Render feature_analytics.run() output into the three Phase 0.5 reports:
reports/feature_quality_report.md, reports/feature_importance.md,
reports/feature_interactions.md. Read-only analysis — no rule/engine
changes. Run across every active symbol (config/watchlist.yaml) so a
feature's apparent edge can be checked for cross-symbol consistency rather
than trusted from one series.

Usage:
  python src/write_feature_reports.py
"""
import os
import feature_analytics as fa

SYMBOLS = [
    ("EURUSD", "data/EURUSD_M5.csv"),
    ("XAUUSD", "data/XAUUSD-VIP_M5.csv"),
    ("BTCUSD", "data/BTCUSD_M5.csv"),
]

MIN_N = 30   # below this, a stat is reported but marked NOT ENOUGH DATA, not ranked


def _fmt(v):
    return "—" if v is None else v


def _quality_section(sym, res):
    lines = [f"## {sym}", f"`{res['n_bars']:,}` bars, ATR period {res['atr_period']}.", ""]
    lines.append("### Binary / event features")
    lines.append("| Feature | Occurrence | Frequency % | ATR mean (active) | ATR stdev (active) | Session dist. |")
    lines.append("|---|---|---|---|---|---|")
    for name, r in sorted(res["binary_results"].items()):
        sess = ", ".join(f"{k} {v}%" for k, v in r["session_distribution_pct"].items())
        lines.append(f"| `{name}` | {r['occurrence']} | {r['frequency_pct']} | "
                     f"{_fmt(r['atr_mean'])} | {_fmt(r['atr_stdev'])} | {sess or '—'} |")
    lines.append("")
    lines.append("### State features (duration/episodes)")
    lines.append("| Field | State | Occurrence (bars) | Frequency % | Episodes | Avg duration (bars) | Max duration (bars) |")
    lines.append("|---|---|---|---|---|---|---|")
    for name, r in res["state_results"].items():
        for state, s in sorted(r["states"].items(), key=lambda kv: -kv[1]["occurrence_bars"]):
            lines.append(f"| `{name}` | {state} | {s['occurrence_bars']} | {s['frequency_pct']} | "
                         f"{s['episodes']} | {_fmt(s['avg_duration_bars'])} | {_fmt(s['max_duration_bars'])} |")
    lines.append("")
    return lines


def write_quality_report(all_results):
    lines = [
        "# Feature Quality Report (Phase 0.5)",
        "",
        "Descriptive statistics only — occurrence, frequency, duration, session "
        "distribution, and ATR distribution per feature. No predictive claims here; "
        "see `feature_importance.md` for that. Read-only: generated from "
        "`src/feature_analytics.py` against the Phase 0 feature database "
        "(`src/features.py`), no signal-engine or rule changes made.",
        "",
        f"Horizons used elsewhere in this report set: {all_results[0][1]['horizons']} bars "
        "(~1h, ~4h on M5). R unit: forward price change / ATR(t) at the feature's own bar "
        "— an ATR-normalized proxy, not a trade-level R (no stop/target exists at this layer).",
        "",
    ]
    for sym, res in all_results:
        lines += _quality_section(sym, res)
    path = "reports/feature_quality_report.md"
    os.makedirs("reports", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return path


def _importance_section(sym, res):
    lines = [f"## {sym}", ""]
    lines.append(f"Ranked by |z| at the primary horizon ({res['horizons'][0]} bars), "
                 f"minimum {MIN_N} occurrences to be ranked (lower-n features are still "
                 "reported per-feature below, just not ranked here).")
    lines.append("")
    lines.append("| Rank | Feature | z vs baseline | mean R (active) | baseline mean R | n | frequency % |")
    lines.append("|---|---|---|---|---|---|---|")
    for i, r in enumerate(res["importance"], 1):
        flag = " ⚠️" if abs(r["z"]) >= 2 else ""
        lines.append(f"| {i} | `{r['name']}`{flag} | {r['z']} | {r['mean_R']} | "
                     f"{r['baseline_mean_R']} | {r['n']} | {r['frequency_pct']} |")
    lines.append("")
    lines.append("⚠️ = \\|z\\| >= 2 (a simple effect-size flag, NOT statistical proof — "
                 "no multiple-testing correction applied across the ~15 features tested here; "
                 "see reports/quant_research_audit.md Sec 13/14 for why bootstrap/Monte Carlo "
                 "is still required before treating any single feature's edge as established).")
    lines.append("")
    lines.append("### Full predictive-value detail (all horizons, every binary feature)")
    lines.append("| Feature | Horizon | n | mean R | baseline mean R | win rate % | baseline win rate % | z |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for name, r in sorted(res["binary_results"].items()):
        for h, hs in r["horizons"].items():
            note = "" if hs["n"] >= MIN_N else " (low n)"
            lines.append(f"| `{name}`{note} | {h} | {hs['n']} | {_fmt(hs['mean_R'])} | "
                         f"{_fmt(hs['baseline_mean_R'])} | {_fmt(hs['win_rate_pct'])} | "
                         f"{_fmt(hs['baseline_win_rate_pct'])} | {_fmt(hs['z_vs_baseline'])} |")
    lines.append("")
    return lines


def write_importance_report(all_results):
    lines = [
        "# Feature Importance Report (Phase 0.5)",
        "",
        "Predictive value per feature: does the feature's presence precede price "
        "movement in its implied direction, relative to the unconditional baseline? "
        "Ranking is a transparent effect-size score (|z| = |mean difference| / standard "
        "error of the conditional sample), not a black-box importance score — every "
        "number here is reproducible from `src/feature_analytics.py` directly.",
        "",
        "**Cross-symbol check**: a feature ranked highly on only ONE of the three "
        "symbols below is weaker evidence than one that ranks consistently across all "
        "three — single-symbol effects are exactly what unvalidated backtests "
        "(reports/quant_research_audit.md's v3.5 baseline) turned out to be noise.",
        "",
    ]
    for sym, res in all_results:
        lines += _importance_section(sym, res)

    # cross-symbol consistency table: which features rank in the top 10 on 2+ symbols
    lines.append("## Cross-symbol consistency")
    top_sets = {}
    for sym, res in all_results:
        top_names = {r["name"] for r in res["importance"][:10]}
        for name in top_names:
            top_sets.setdefault(name, []).append(sym)
    consistent = {k: v for k, v in top_sets.items() if len(v) >= 2}
    if consistent:
        lines.append("Features in the top-10 by |z| on 2 or more symbols:")
        lines.append("")
        lines.append("| Feature | Symbols |")
        lines.append("|---|---|")
        for name, syms in sorted(consistent.items(), key=lambda kv: -len(kv[1])):
            lines.append(f"| `{name}` | {', '.join(syms)} |")
    else:
        lines.append("No feature ranked in the top-10 by |z| on 2 or more symbols — "
                     "every apparent effect found is currently single-symbol only. "
                     "Treat all rankings above as hypotheses to re-test, not conclusions.")
    lines.append("")

    path = "reports/feature_importance.md"
    os.makedirs("reports", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return path


def _interactions_section(sym, res):
    lines = [f"## {sym}", ""]
    lines.append("| Interaction | Occurrence | Frequency % | Horizon | n | mean R | baseline mean R | win rate % | z |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for ir in res["interaction_results"]:
        first = True
        for h, hs in ir["horizons"].items():
            occ = ir["occurrence"] if first else ""
            freq = ir["frequency_pct"] if first else ""
            note = "" if hs["n"] >= MIN_N else " (low n)"
            lines.append(f"| `{ir['label']}` | {occ} | {freq} | {h}{note} | {hs['n']} | "
                         f"{_fmt(hs['mean_R'])} | {_fmt(hs['baseline_mean_R'])} | "
                         f"{_fmt(hs['win_rate_pct'])} | {_fmt(hs['z_vs_baseline'])} |")
            first = False
    lines.append("")
    return lines


def write_interactions_report(all_results):
    lines = [
        "# Feature Interactions Report (Phase 0.5)",
        "",
        "Five requested interaction pairs (plus session x sweep split by direction and "
        "session), each measured as: does the CO-OCCURRENCE of both conditions on the "
        "same bar carry a different forward-R signature than baseline? This does not "
        "test sequencing (e.g. 'sweep THEN CHoCH within N bars') — that's a v3.6 §7 "
        "sequencing question for the signal-engine rewrite, not a Phase 0.5 feature-"
        "database question. Same-bar co-occurrence is a coarser, honest first cut.",
        "",
    ]
    for sym, res in all_results:
        lines += _interactions_section(sym, res)
    path = "reports/feature_interactions.md"
    os.makedirs("reports", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return path


def _redundancy_note(all_results):
    lines = ["", "## Redundant / highly correlated features (|phi| >= 0.7)", ""]
    for sym, res in all_results:
        lines.append(f"### {sym}")
        if not res["redundant"]:
            lines.append("None found at this threshold.")
        else:
            lines.append("| Feature A | Feature B | phi |")
            lines.append("|---|---|---|")
            for a, b, phi in res["redundant"]:
                lines.append(f"| `{a}` | `{b}` | {phi} |")
        lines.append("")
    return lines


def main():
    all_results = []
    for sym, path in SYMBOLS:
        if not os.path.exists(path):
            print(f"skip {sym}: {path} not found")
            continue
        print(f"analyzing {sym} ({path}) ...")
        res = fa.run(sym, path)
        all_results.append((sym, res))
        print(f"  {res['n_bars']} bars, {len(res['binary_results'])} binary features, "
             f"{len(res['redundant'])} redundant pairs")

    if not all_results:
        raise SystemExit("no symbol data found under data/ — run load_history.py first")

    qpath = write_quality_report(all_results)
    ipath = write_importance_report(all_results)
    xpath = write_interactions_report(all_results)

    # append redundancy detail to the quality report (most natural home for it)
    with open(qpath, "a", encoding="utf-8") as fh:
        fh.write("\n".join(_redundancy_note(all_results)))

    print("wrote", qpath)
    print("wrote", ipath)
    print("wrote", xpath)


if __name__ == "__main__":
    main()
