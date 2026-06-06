#!/usr/bin/env bash
set -euo pipefail

# Runtime-estimation run (validated on Colab T4):
# - Task: prom_core_all
# - Split: 10%, seed=13
# - max_steps: 600

cd "$(dirname "$0")/.."

python -m pip install -q -r requirements.txt
python -m pip uninstall -y peft >/dev/null 2>&1 || true

python scripts/build_low_data_splits.py \
  --source-dir data/raw/GUE/prom/prom_core_all \
  --output-root data/low_data/prom_core_all_time \
  --ratios 0.10 \
  --seeds 13

START_TS=$(date +%s)

python scripts/train_dnabert2.py \
  --model_name_or_path zhihan1996/DNABERT-2-117M \
  --data_path data/low_data/prom_core_all_time/r10_seed13 \
  --run_name timecheck_r10_seed13 \
  --output_dir outputs/timecheck \
  --seed 13 \
  --model_max_length 20 \
  --max_steps 600 \
  --per_device_train_batch_size 8 \
  --per_device_eval_batch_size 16 \
  --gradient_accumulation_steps 1 \
  --learning_rate 3e-5 \
  --warmup_steps 50 \
  --weight_decay 0.01 \
  --evaluation_strategy steps \
  --save_strategy steps \
  --eval_steps 200 \
  --save_steps 200 \
  --logging_steps 50 \
  --load_best_model_at_end True \
  --metric_for_best_model eval_f1_macro \
  --greater_is_better True \
  --save_total_limit 1 \
  --report_to none \
  --fp16 True

END_TS=$(date +%s)
echo "ELAPSED_SECONDS=$((END_TS - START_TS))"
echo "Results: outputs/timecheck/results/timecheck_r10_seed13/eval_results.json"
