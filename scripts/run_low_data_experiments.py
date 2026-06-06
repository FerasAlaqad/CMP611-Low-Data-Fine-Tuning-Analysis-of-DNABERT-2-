#!/usr/bin/env python3
import argparse
import pathlib
import subprocess
import sys

import yaml


def ratio_tag(r: float) -> str:
    if float(r) == 1.0:
        return "100"
    return str(int(round(float(r) * 100)))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run low-data DNABERT-2 experiments.")
    parser.add_argument("--config", type=str, required=True, help="YAML config path.")
    parser.add_argument(
        "--create-splits-if-missing",
        action="store_true",
        help="Auto-create low-data splits if output folders are missing.",
    )
    return parser.parse_args()


def run_cmd(cmd):
    print("\n[RUN]", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> int:
    args = parse_args()
    cfg = yaml.safe_load(pathlib.Path(args.config).read_text())

    source_data_dir = pathlib.Path(cfg["source_data_dir"])
    low_data_root = pathlib.Path(cfg["low_data_root"])
    output_root = pathlib.Path(cfg["output_root"])
    output_root.mkdir(parents=True, exist_ok=True)

    low_data_ratios = cfg["low_data_ratios"]
    seeds = cfg["seeds"]
    methods = cfg["methods"]
    tr = cfg["training"]
    lora = cfg.get("lora", {})

    if args.create_splits_if_missing and not low_data_root.exists():
        run_cmd(
            [
                sys.executable,
                "scripts/build_low_data_splits.py",
                "--source-dir",
                str(source_data_dir),
                "--output-root",
                str(low_data_root),
                "--ratios",
                ",".join(str(x) for x in low_data_ratios),
                "--seeds",
                ",".join(str(x) for x in seeds),
            ]
        )

    for method in methods:
        use_lora = method == "lora_ft"
        for ratio in low_data_ratios:
            for seed in seeds:
                split_dir = low_data_root / f"r{ratio_tag(ratio)}_seed{seed}"
                if not split_dir.exists():
                    raise FileNotFoundError(f"Missing split folder: {split_dir}")

                run_name = f"{cfg['project_name']}_{method}_r{ratio_tag(ratio)}_seed{seed}"
                out_dir = output_root / "experiments" / method / f"r{ratio_tag(ratio)}" / f"seed{seed}"
                out_dir.mkdir(parents=True, exist_ok=True)

                cmd = [
                    sys.executable,
                    "scripts/train_dnabert2.py",
                    "--model_name_or_path",
                    cfg["model_name_or_path"],
                    "--data_path",
                    str(split_dir),
                    "--run_name",
                    run_name,
                    "--output_dir",
                    str(out_dir),
                    "--seed",
                    str(seed),
                    "--model_max_length",
                    str(tr["model_max_length"]),
                    "--num_train_epochs",
                    str(tr["num_train_epochs"]),
                    "--per_device_train_batch_size",
                    str(tr["per_device_train_batch_size"]),
                    "--per_device_eval_batch_size",
                    str(tr["per_device_eval_batch_size"]),
                    "--gradient_accumulation_steps",
                    str(tr["gradient_accumulation_steps"]),
                    "--learning_rate",
                    str(tr["learning_rate"]),
                    "--warmup_steps",
                    str(tr["warmup_steps"]),
                    "--weight_decay",
                    str(tr["weight_decay"]),
                    "--evaluation_strategy",
                    "steps",
                    "--save_strategy",
                    "steps",
                    "--eval_steps",
                    str(tr["eval_steps"]),
                    "--save_steps",
                    str(tr["save_steps"]),
                    "--logging_steps",
                    str(tr["logging_steps"]),
                    "--load_best_model_at_end",
                    "True",
                    "--metric_for_best_model",
                    "eval_f1_macro",
                    "--greater_is_better",
                    "True",
                    "--save_total_limit",
                    "2",
                    "--report_to",
                    "none",
                ]

                if tr.get("use_fp16", False):
                    cmd.extend(["--fp16", "True"])

                if use_lora:
                    cmd.extend(
                        [
                            "--use_lora",
                            "True",
                            "--lora_r",
                            str(lora.get("r", 8)),
                            "--lora_alpha",
                            str(lora.get("alpha", 16)),
                            "--lora_dropout",
                            str(lora.get("dropout", 0.05)),
                            "--lora_target_modules",
                            str(lora.get("target_modules", "query,value")),
                        ]
                    )
                else:
                    cmd.extend(["--use_lora", "False"])

                run_cmd(cmd)

    print("\nAll experiments completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
