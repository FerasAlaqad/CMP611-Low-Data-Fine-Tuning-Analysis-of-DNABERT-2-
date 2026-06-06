#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[1/5] Environment check"
python -m pip install -q -r requirements.txt
python -m pip uninstall -y peft >/dev/null 2>&1 || true
python scripts/check_environment.py

echo "[2/5] Download GUE (skip if already exists)"
python scripts/download_gue.py --out-dir data/raw

echo "[3/5] Build low-data splits"
python scripts/build_low_data_splits.py \
  --source-dir data/raw/GUE/prom/prom_300_all \
  --output-root data/low_data/prom_300_all \
  --ratios 0.01,0.05,0.10,0.25,1.0 \
  --seeds 13,42,3407

echo "[4/5] Train experiments"
python scripts/run_low_data_experiments.py --config configs/promoter_low_data.yaml

echo "[5/5] Aggregate results"
python scripts/aggregate_results.py \
  --results-root outputs/experiments \
  --out-csv outputs/summary_all_runs.csv \
  --out-mean-csv outputs/summary_mean_std.csv

echo "Pipeline completed."
