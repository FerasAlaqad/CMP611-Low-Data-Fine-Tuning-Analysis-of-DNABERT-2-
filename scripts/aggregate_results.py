#!/usr/bin/env python3
import argparse
import json
import pathlib
import re
from typing import Dict, List

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate experiment metrics into CSV files.")
    parser.add_argument("--results-root", type=str, required=True, help="Root experiments folder.")
    parser.add_argument("--out-csv", type=str, required=True, help="All-runs CSV output.")
    parser.add_argument("--out-mean-csv", type=str, required=True, help="Mean/std CSV output.")
    return parser.parse_args()


def collect_json_files(root: pathlib.Path) -> List[pathlib.Path]:
    return list(root.rglob("eval_results.json"))


def extract_meta(path: pathlib.Path) -> Dict[str, str]:
    parts = path.parts
    method = "unknown"
    ratio = "unknown"
    seed = "unknown"
    for p in parts:
        if p in {"standard_ft", "lora_ft"}:
            method = p
        if re.fullmatch(r"r\d+", p):
            ratio = p[1:]
        if p.startswith("seed"):
            seed = p.replace("seed", "")
    return {"method": method, "ratio_percent": ratio, "seed": seed}


def main() -> int:
    args = parse_args()
    results_root = pathlib.Path(args.results_root)
    out_csv = pathlib.Path(args.out_csv)
    out_mean_csv = pathlib.Path(args.out_mean_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_mean_csv.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for fpath in collect_json_files(results_root):
        data = json.loads(fpath.read_text())
        meta = extract_meta(fpath)
        row = {"file": str(fpath), **meta}
        row.update(data)
        rows.append(row)

    if not rows:
        print("No eval_results.json files found.")
        return 1

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)

    metric_cols = [c for c in df.columns if c.startswith("eval_")]
    grouped = df.groupby(["method", "ratio_percent"])[metric_cols].agg(["mean", "std"]).reset_index()
    grouped.columns = ["_".join(col).strip("_") for col in grouped.columns.values]
    grouped.to_csv(out_mean_csv, index=False)

    print(f"Saved all runs: {out_csv}")
    print(f"Saved mean/std: {out_mean_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
