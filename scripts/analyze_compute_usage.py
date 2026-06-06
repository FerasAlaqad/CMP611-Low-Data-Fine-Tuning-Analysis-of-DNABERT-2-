#!/usr/bin/env python3
"""Aggregate runtime / compute usage from train_results.json and eval_results.json.

New runs generated after the post-presentation patch save train_results.json.
For older runs, only eval_runtime may be available; those rows are retained but
marked as missing train runtime.
"""

import argparse
import json
import re
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--results-root", required=True)
    p.add_argument("--out-dir", required=True)
    return p.parse_args()


def parse_meta(path: Path) -> dict:
    text = str(path)
    task = "unknown"
    for candidate in ["core_promoter", "nontata_promoter", "promoter", "splice"]:
        if f"/{candidate}/" in text or f"{candidate}_" in path.name:
            task = candidate
            break
    ratio = "unknown"
    seed = "unknown"
    m = re.search(r"/(r(?:0p05|0p1|1|10|100)_seed(\d+))/", text)
    if m:
        split = m.group(1)
        seed = m.group(2)
        ratio_tag = split.split("_seed")[0]
        ratio_map = {"r0p05": 0.05, "r0p1": 0.10, "r1": 1.0, "r10": 10.0, "r100": 100.0}
        ratio = ratio_map.get(ratio_tag, "unknown")
    return {"task": task, "ratio_percent": ratio, "seed": seed}


def main() -> int:
    args = parse_args()
    root = Path(args.results_root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for eval_path in root.rglob("eval_results.json"):
        row = {"eval_file": str(eval_path), **parse_meta(eval_path)}
        eval_data = json.loads(eval_path.read_text())
        row.update({k: eval_data.get(k) for k in eval_data.keys() if k.startswith("eval_")})
        row["train_wall_clock_seconds"] = eval_data.get("train_wall_clock_seconds")
        row["train_examples"] = eval_data.get("train_examples")
        row["peak_gpu_memory_mb"] = eval_data.get("peak_gpu_memory_mb")

        train_path = eval_path.with_name("train_results.json")
        row["has_train_results_json"] = train_path.exists()
        if train_path.exists():
            train_data = json.loads(train_path.read_text())
            row["train_runtime"] = train_data.get("train_runtime")
            row["train_samples_per_second"] = train_data.get("train_samples_per_second")
            row["train_steps_per_second"] = train_data.get("train_steps_per_second")
            row["wall_clock_seconds"] = train_data.get("wall_clock_seconds")
            row["peak_gpu_reserved_mb"] = train_data.get("peak_gpu_reserved_mb")
            row["gpu_name"] = train_data.get("gpu_name")
        rows.append(row)

    if not rows:
        print(f"No eval_results.json files found under {root}")
        return 1

    df = pd.DataFrame(rows)
    all_csv = out_dir / "compute_usage_all_runs.csv"
    df.to_csv(all_csv, index=False)

    numeric_cols = [
        "train_runtime",
        "wall_clock_seconds",
        "train_wall_clock_seconds",
        "eval_runtime",
        "peak_gpu_memory_mb",
        "peak_gpu_reserved_mb",
        "train_samples_per_second",
    ]
    present = [c for c in numeric_cols if c in df.columns]
    summary = (
        df.groupby(["task", "ratio_percent"])[present]
        .agg(["mean", "std", "count"])
        .reset_index()
    )
    summary.columns = ["_".join(map(str, c)).strip("_") for c in summary.columns]
    summary_csv = out_dir / "compute_usage_summary.csv"
    summary.to_csv(summary_csv, index=False)

    lines = [
        "# Compute Usage Analysis",
        "",
        f"Rows: {len(df)}",
        "",
        "If `has_train_results_json` is false, that run was produced before train-resource logging was added. Re-run the selected grid to measure training cost.",
        "",
        "## Summary",
        "",
        _markdown_table(summary),
        "",
    ]
    report_md = out_dir / "compute_usage_analysis.md"
    report_md.write_text("\n".join(lines))
    print(f"Saved: {all_csv}")
    print(f"Saved: {summary_csv}")
    print(f"Saved: {report_md}")
    return 0


def _markdown_table(frame: pd.DataFrame) -> str:
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


if __name__ == "__main__":
    raise SystemExit(main())
