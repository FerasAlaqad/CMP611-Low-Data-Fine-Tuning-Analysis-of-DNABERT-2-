#!/usr/bin/env python3
"""Paired F1-drop analysis relative to the full-data condition."""

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd


RATIOS = [0.05, 0.10, 1.00, 10.00, 100.00]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--combined-csv", required=True, help="All-runs result CSV.")
    p.add_argument("--out-dir", required=True, help="Output directory for analysis files.")
    p.add_argument(
        "--practical-drop",
        type=float,
        default=0.05,
        help="Minimum F1 drop treated as practically meaningful.",
    )
    return p.parse_args()


def bootstrap_ci(values: np.ndarray, n_boot: int = 20000, alpha: float = 0.05) -> tuple[float, float]:
    values = np.asarray(values, dtype=float)
    if len(values) == 0:
        return (math.nan, math.nan)
    rng = np.random.default_rng(20260524)
    samples = rng.choice(values, size=(n_boot, len(values)), replace=True).mean(axis=1)
    return (float(np.quantile(samples, alpha / 2)), float(np.quantile(samples, 1 - alpha / 2)))


def paired_drop_analysis(df: pd.DataFrame, practical_drop: float) -> pd.DataFrame:
    rows = []
    metric = "eval_f1_macro"
    for task, task_df in df.groupby("task"):
        pivot = task_df.pivot_table(index="seed", columns="ratio_percent", values=metric, aggfunc="first")
        if 100.0 not in pivot.columns:
            continue
        full = pivot[100.0]
        full_mean = float(full.mean())
        for ratio in [r for r in RATIOS if r != 100.0]:
            if ratio not in pivot.columns:
                continue
            paired = pivot[[ratio, 100.0]].dropna()
            deltas = paired[ratio].to_numpy(dtype=float) - paired[100.0].to_numpy(dtype=float)
            drop = -deltas
            ci_low, ci_high = bootstrap_ci(deltas)
            ratio_mean = float(paired[ratio].mean())
            mean_delta = float(deltas.mean())
            mean_drop = float(drop.mean())
            rel_retained = ratio_mean / full_mean if full_mean else math.nan
            practical = mean_drop >= practical_drop
            conservative = practical and ci_high < 0
            rows.append(
                {
                    "task": task,
                    "ratio_percent": ratio,
                    "n_paired_seeds": len(paired),
                    "f1_mean_ratio": ratio_mean,
                    "f1_mean_100": full_mean,
                    "mean_delta_vs_100": mean_delta,
                    "mean_drop_vs_100": mean_drop,
                    "bootstrap_ci_delta_low": ci_low,
                    "bootstrap_ci_delta_high": ci_high,
                    "relative_f1_retained": rel_retained,
                    "practical_drop_ge_0p05": practical,
                    "conservative_drop_flag": conservative,
                }
            )
    return pd.DataFrame(rows)


def threshold_summary(stats: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for task, g in stats.groupby("task"):
        g = g.sort_values("ratio_percent")
        acceptable = g[~g["practical_drop_ge_0p05"]]
        conservative_ok = g[~g["conservative_drop_flag"]]
        rows.append(
            {
                "task": task,
                "lowest_ratio_without_practical_drop": (
                    float(acceptable["ratio_percent"].iloc[0]) if len(acceptable) else 100.0
                ),
                "lowest_ratio_without_conservative_drop_flag": (
                    float(conservative_ok["ratio_percent"].iloc[0]) if len(conservative_ok) else 100.0
                ),
                "note": "Use conservative threshold in slides/report; n=3 seeds limits formal testing.",
            }
        )
    return pd.DataFrame(rows)


def write_markdown(stats: pd.DataFrame, thresholds: pd.DataFrame, out_md: Path) -> None:
    def md_table(frame: pd.DataFrame) -> str:
        if frame.empty:
            return "_No rows._"
        clean = frame.copy()
        for col in clean.columns:
            if pd.api.types.is_float_dtype(clean[col]):
                clean[col] = clean[col].map(lambda x: "" if pd.isna(x) else f"{x:.4f}")
        headers = list(clean.columns)
        lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
        for _, row in clean.iterrows():
            lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
        return "\n".join(lines)

    lines = [
        "# Paired Drop Analysis",
        "",
        "Comparison target: each lower-data run is paired with the 100% run from the same task and seed.",
        "",
        "Only three seeds are available, so the analysis is reported as paired effect size with bootstrap intervals.",
        "",
        "Decision rule used here:",
        "",
        "- Practical drop: mean F1 decrease from 100% is at least 0.05.",
        "- Conservative drop flag: practical drop is present and the bootstrap CI upper bound for the delta is below 0.",
        "",
        "## Threshold Summary",
        "",
        md_table(thresholds),
        "",
        "## Paired Drop Details",
        "",
        md_table(stats),
        "",
    ]
    out_md.write_text("\n".join(lines))


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.combined_csv)

    stats = paired_drop_analysis(df, args.practical_drop)
    thresholds = threshold_summary(stats)

    stats_csv = out_dir / "paired_drop_analysis.csv"
    threshold_csv = out_dir / "threshold_summary.csv"
    report_md = out_dir / "statistical_analysis.md"
    stats.to_csv(stats_csv, index=False)
    thresholds.to_csv(threshold_csv, index=False)
    write_markdown(stats, thresholds, report_md)

    print(f"Saved: {stats_csv}")
    print(f"Saved: {threshold_csv}")
    print(f"Saved: {report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
