#!/usr/bin/env bash
set -euo pipefail

# Quick sanity run on Colab GPU to verify DNABERT-2 fine-tuning pipeline works.
# This is intentionally small: 1 task, 1 ratio, 1 seed, 1 epoch.

cd "$(dirname "$0")/.."

echo "[1/5] Install deps"
python -m pip install -q -r requirements.txt
python -m pip uninstall -y peft >/dev/null 2>&1 || true

echo "[2/5] Check environment"
python scripts/check_environment.py

echo "[3/5] Download GUE (if missing)"
python scripts/download_gue.py --out-dir data/raw

echo "[4/5] Build a tiny low-data split (1%, single seed)"
python scripts/build_low_data_splits.py \
  --source-dir data/raw/GUE/prom/prom_core_all \
  --output-root data/low_data/prom_core_all_smoke \
  --ratios 0.01 \
  --seeds 13

echo "[5/5] Run one short fine-tuning job"
python scripts/train_dnabert2.py \
  --model_name_or_path zhihan1996/DNABERT-2-117M \
  --data_path data/low_data/prom_core_all_smoke/r1_seed13 \
  --run_name smoke_prom_core_all_r1_seed13 \
  --output_dir outputs/smoke_test \
  --seed 13 \
  --model_max_length 20 \
  --num_train_epochs 1 \
  --per_device_train_batch_size 8 \
  --per_device_eval_batch_size 16 \
  --gradient_accumulation_steps 1 \
  --learning_rate 3e-5 \
  --warmup_steps 10 \
  --weight_decay 0.01 \
  --evaluation_strategy steps \
  --save_strategy steps \
  --eval_steps 100 \
  --save_steps 100 \
  --logging_steps 20 \
  --load_best_model_at_end True \
  --metric_for_best_model eval_f1_macro \
  --greater_is_better True \
  --save_total_limit 1 \
  --report_to none \
  --fp16 True

echo "Smoke test completed. Check:"
echo "outputs/smoke_test/results/smoke_prom_core_all_r1_seed13/eval_results.json"
