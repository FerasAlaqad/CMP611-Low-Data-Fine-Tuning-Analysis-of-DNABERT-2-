#!/usr/bin/env python3
import argparse
import json
import pathlib
from typing import List

import pandas as pd


def parse_float_list(value: str) -> List[float]:
    return [float(x.strip()) for x in value.split(",") if x.strip()]


def parse_int_list(value: str) -> List[int]:
    return [int(x.strip()) for x in value.split(",") if x.strip()]


def ratio_tag(r: float) -> str:
    known = {
        0.0005: "0p05",
        0.001: "0p1",
        0.01: "1",
        0.10: "10",
        1.0: "100",
    }
    for value, tag in known.items():
        if abs(r - value) < 1e-12:
            return tag
    percent = r * 100
    text = f"{percent:g}".replace(".", "p")
    return text


def stratified_sample(df: pd.DataFrame, ratio: float, seed: int) -> pd.DataFrame:
    if "label" not in df.columns:
        raise ValueError("Expected 'label' column in CSV.")
    if ratio >= 1.0:
        return df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    sampled_parts = []
    for _, group in df.groupby("label"):
        n = max(1, int(round(len(group) * ratio)))
        n = min(n, len(group))
        sampled_parts.append(group.sample(n=n, random_state=seed))

    sampled = pd.concat(sampled_parts, axis=0).sample(frac=1.0, random_state=seed)
    return sampled.reset_index(drop=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create low-data train splits.")
    parser.add_argument("--source-dir", type=str, required=True, help="Folder with train/dev/test CSV.")
    parser.add_argument("--output-root", type=str, required=True, help="Where to write low-data folders.")
    parser.add_argument("--ratios", type=str, default="0.01,0.05,0.10,0.25,1.0")
    parser.add_argument("--seeds", type=str, default="13,42,3407")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_dir = pathlib.Path(args.source_dir)
    output_root = pathlib.Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    train_path = source_dir / "train.csv"
    dev_path = source_dir / "dev.csv"
    test_path = source_dir / "test.csv"
    for path in [train_path, dev_path, test_path]:
        if not path.exists():
            raise FileNotFoundError(f"Missing file: {path}")

    train_df = pd.read_csv(train_path)
    dev_df = pd.read_csv(dev_path)
    test_df = pd.read_csv(test_path)

    if "sequence" not in train_df.columns or "label" not in train_df.columns:
        raise ValueError("Expected columns: sequence,label")

    ratios = parse_float_list(args.ratios)
    seeds = parse_int_list(args.seeds)

    for r in ratios:
        for seed in seeds:
            subset = stratified_sample(train_df, r, seed)
            split_dir = output_root / f"r{ratio_tag(r)}_seed{seed}"
            split_dir.mkdir(parents=True, exist_ok=True)

            subset.to_csv(split_dir / "train.csv", index=False)
            dev_df.to_csv(split_dir / "dev.csv", index=False)
            test_df.to_csv(split_dir / "test.csv", index=False)

            meta = {
                "source_dir": str(source_dir),
                "ratio": r,
                "seed": seed,
                "train_size": int(len(subset)),
                "dev_size": int(len(dev_df)),
                "test_size": int(len(test_df)),
                "label_distribution_train": subset["label"].value_counts().to_dict(),
            }
            (split_dir / "meta.json").write_text(json.dumps(meta, indent=2))
            print(f"[OK] {split_dir} | train={len(subset)}")

    print("All low-data splits are created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
