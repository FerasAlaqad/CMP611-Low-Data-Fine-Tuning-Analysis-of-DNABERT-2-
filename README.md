# Low-Data Fine-Tuning Analysis of DNABERT-2

Reproducibility package for **Low-Data Fine-Tuning Analysis of DNABERT-2 for Human Regulatory Sequence Classification**.

This repository contains the code, notebook workflow, aggregate result tables, resource-analysis tables, and paper figures used to evaluate how DNABERT-2 fine-tuning behaves when labeled training data is systematically reduced across human regulatory sequence classification tasks.

## Study Overview

- **Model:** [`zhihan1996/DNABERT-2-117M`](https://huggingface.co/zhihan1996/DNABERT-2-117M)
- **Task family:** human regulatory sequence classification
- **Tasks:** promoter detection, core promoter detection, splice site prediction, Non-TATA promoter detection
- **Training-data ratios:** `0.05%`, `0.1%`, `1%`, `10%`, `100%`
- **Random seeds:** `13`, `42`, `3407`
- **Primary metric:** F1-macro
- **Additional metrics:** accuracy, MCC, macro precision, macro recall, AUROC, AUPRC
- **Practical-drop analysis:** paired F1 drop relative to the same-task, same-seed `100%` condition
- **Resource profiling:** separate seed-13 profiling pass for runtime and peak CUDA memory

The main experiment uses fixed validation/dev and test sets. Only the training split is downsampled.

## Repository Layout

```text
notebooks/
  CMP611_Final_Epoch_LowData_Colab.ipynb     End-to-end Colab workflow used for final runs

scripts/
  check_environment.py                       Environment and CUDA sanity check
  download_gue.py                            Download/extract GUE archive
  build_low_data_splits.py                   Stratified low-data split creation
  train_dnabert2.py                          DNABERT-2 sequence-classification fine-tuning
  aggregate_results.py                       Aggregate eval_results.json files into CSV summaries
  analyze_final_statistics.py                Paired F1-drop and threshold analysis
  analyze_compute_usage.py                   Runtime and peak-memory aggregation
  make_paper_figures.py                      Regenerate quantitative paper figures from CSV tables

results/
  final_epoch_all_seeds_combined.csv         Per-run final metrics for 60 runs
  final_epoch_all_seeds_summary_mean_std.csv Mean/std metrics by task and ratio
  paper_figures/                             Figure input tables
  statistical_analysis_stronger/             Practical-drop and threshold summaries
  resource_analysis/                         Runtime and GPU-memory tables

figures/
  paper_fig1_pipeline.pdf/.png               Final experimental design figure used in the paper
  paper_fig2_f1_trends.pdf/.png              Main F1-macro trend figure
  paper_fig3_practical_drop_heatmap.pdf/.png Practical-drop heatmap
  paper_fig4_resource_profile.pdf/.png       Runtime and peak-memory figure
```

Raw datasets, model checkpoints, and transient Colab output directories are intentionally not tracked. They are either reproducible from public sources or too large for a clean code repository.

## Environment

The final runs were executed in Google Colab with an NVIDIA Tesla T4 GPU. The recorded environment used Python 3.12, PyTorch with CUDA, Hugging Face Transformers 4.39.3, scikit-learn, pandas, NumPy, and Matplotlib.

Install the Python dependencies with:

```bash
pip install -r requirements.txt
```

For a local sanity check:

```bash
python scripts/check_environment.py
```

A CUDA GPU is strongly recommended for training. The analysis and figure-generation scripts can be run on CPU once the CSV result tables are available.

## Data Sources

The final study uses four tasks:

| Task | Source | Classes | Max sequence length | Full train | Dev | Test |
|---|---:|---:|---:|---:|---:|---:|
| Promoter detection | GUE | 2 | 300 | 47,356 | 5,920 | 5,920 |
| Core promoter detection | GUE | 2 | 70 | 47,356 | 5,920 | 5,920 |
| Splice site prediction | GUE | 3 | 400 | 36,496 | 4,562 | 4,562 |
| Non-TATA promoter detection | Genomic Benchmarks | 2 | 251 | 24,387 | 2,710 | 9,034 |

GUE tasks are obtained with `scripts/download_gue.py`. The Non-TATA promoter dataset is obtained through the `genomic-benchmarks` package inside the Colab notebook.

## Reproducing the Final Workflow

The canonical end-to-end workflow is the Colab notebook:

```text
notebooks/CMP611_Final_Epoch_LowData_Colab.ipynb
```

It performs environment setup, dataset download/preparation, low-data split construction, DNABERT-2 fine-tuning, metric aggregation, resource profiling, and output packaging.

### 1. Download GUE

```bash
python scripts/download_gue.py --out-dir data/raw
```

### 2. Build low-data splits

Example for one GUE task after the raw CSV files are available:

```bash
python scripts/build_low_data_splits.py \
  --source-dir data/raw/path/to/task_csv_folder \
  --output-root data/low_data/final_epoch/prom_300_all \
  --ratios 0.0005,0.001,0.01,0.1,1.0 \
  --seeds 13,42,3407
```

The final notebook contains the exact paths used for all four tasks, including the Genomic Benchmarks Non-TATA promoter conversion step.

### 3. Fine-tune DNABERT-2

Example command for one split:

```bash
python scripts/train_dnabert2.py \
  --model_name_or_path zhihan1996/DNABERT-2-117M \
  --data_path data/low_data/final_epoch/prom_300_all/r1_seed13 \
  --run_name promoter_r1_seed13 \
  --output_dir outputs/final_epoch/main_runs/promoter/r1_seed13 \
  --seed 13 \
  --model_max_length 300 \
  --num_train_epochs 3 \
  --per_device_train_batch_size 8 \
  --per_device_eval_batch_size 16 \
  --gradient_accumulation_steps 1 \
  --learning_rate 3e-5 \
  --warmup_ratio 0.06 \
  --weight_decay 0.01 \
  --evaluation_strategy epoch \
  --save_strategy no \
  --logging_steps 10 \
  --load_best_model_at_end False \
  --report_to none \
  --use_lora False \
  --fp16 True
```

The full 60-run grid is executed by the notebook rather than by typing every command manually.

### 4. Aggregate metrics

```bash
python scripts/aggregate_results.py \
  --results-root outputs/final_epoch/main_runs \
  --out-csv results/final_epoch_all_seeds_combined.csv \
  --out-mean-csv results/final_epoch_all_seeds_summary_mean_std.csv
```

### 5. Run paired practical-drop analysis

```bash
python scripts/analyze_final_statistics.py \
  --combined-csv results/final_epoch_all_seeds_combined.csv \
  --out-dir results/statistical_analysis_stronger \
  --practical-drop 0.05
```

### 6. Aggregate resource usage

```bash
python scripts/analyze_compute_usage.py \
  --results-root outputs/final_epoch/resource_profile_seed13 \
  --out-dir results/resource_analysis
```

Resource profiling was performed as a separate seed-13 pass. It should be interpreted as a practical runtime and peak-memory measurement under the recorded Colab T4 environment, not as a replicated statistical estimate.

### 7. Regenerate quantitative figures

```bash
python scripts/make_paper_figures.py
```

This regenerates Figure 2, Figure 3, and Figure 4 from the CSV tables under `results/`. Figure 1 is included as a final static manuscript asset because it was designed separately as an experimental-design schematic.

## Existing Result Tables

The repository already includes the final aggregate tables used in the manuscript:

- `results/final_epoch_all_seeds_combined.csv`
- `results/final_epoch_all_seeds_summary_mean_std.csv`
- `results/statistical_analysis_stronger/paired_drop_stronger_stats.csv`
- `results/statistical_analysis_stronger/threshold_summary_stronger.csv`
- `results/resource_analysis/paper_table_resource_usage_real.csv`
- `results/resource_analysis/real_resource_reduction_by_task_ratio.csv`

These files allow the paper tables and quantitative figures to be reproduced without rerunning the full GPU training grid.

## Notes on Reproducibility

- Raw datasets are not committed; the notebook and scripts document how they are obtained.
- Model checkpoints are not committed; DNABERT-2 is downloaded from Hugging Face at runtime.
- Training outputs under `outputs/` are ignored because they are large runtime artifacts.
- Final result CSVs and paper figures are tracked because they are small and needed to verify the reported analysis.
- The final manuscript PDF is submitted separately from this code repository.

## Limitations of This Repository

This repository reproduces the reported DNABERT-2 fine-tuning workflow and analysis. It does not include external model baselines, motif-level interpretation, class-wise error analysis, or full checkpoint artifacts.
