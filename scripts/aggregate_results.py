#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

import pandas as pd

RATIO_MAP = {
    "r0p05": 0.05,
    "r0p1": 0.10,
    "r1": 1.0,
    "r10": 10.0,
    "r100": 100.0,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate evaluation metrics.")
    parser.add_argument("--results-root", required=True)
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--out-mean-csv", required=True)
    return parser.parse_args()


def parse_run(path: Path) -> dict:
    text = str(path)
    task = "unknown"
    for candidate in ["core_promoter", "nontata_promoter", "promoter", "splice"]:
        if f"/{candidate}/" in text or f"{candidate}_" in text:
            task = candidate
            break

    ratio = None
    seed = None
    match = re.search(r"/(r(?:0p05|0p1|1|10|100)_seed(\d+))/", text)
    if match:
        ratio = RATIO_MAP.get(match.group(1).split("_seed")[0])
        seed = int(match.group(2))
    else:
        match = re.search(r"_r(0p05|0p1|1|10|100)_seed(\d+)", text)
        if match:
            ratio = RATIO_MAP.get("r" + match.group(1))
            seed = int(match.group(2))

    return {"task": task, "ratio_percent": ratio, "seed": seed}


def main() -> int:
    args = parse_args()
    results_root = Path(args.results_root)
    out_csv = Path(args.out_csv)
    out_mean_csv = Path(args.out_mean_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_mean_csv.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for path in sorted(results_root.rglob("eval_results.json")):
        row = {"file": str(path), **parse_run(path)}
        row.update(json.loads(path.read_text()))
        rows.append(row)

    if not rows:
        raise SystemExit(f"No eval_results.json files found under {results_root}")

    df = pd.DataFrame(rows).sort_values(["task", "ratio_percent", "seed"], na_position="last")
    df.to_csv(out_csv, index=False)

    metric_cols = [c for c in df.columns if c.startswith("eval_")]
    summary = df.groupby(["task", "ratio_percent"])[metric_cols].agg(["mean", "std"]).reset_index()
    summary.columns = ["_".join(map(str, col)).strip("_") for col in summary.columns]
    summary.to_csv(out_mean_csv, index=False)

    print(f"Saved: {out_csv}")
    print(f"Saved: {out_mean_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
