# Low-Data Fine-Tuning Analysis of DNABERT-2

This repository contains the final reproducibility package for the paper:

**Low-Data Fine-Tuning Analysis of DNABERT-2 for Human Regulatory Sequence Classification**

The repository intentionally keeps only the final-run notebook, final training/analysis scripts, paper figures, and cleaned result tables.

## Contents

```text
notebooks/
  CMP611_Final_Epoch_LowData_Colab.ipynb

scripts/
  check_environment.py
  download_gue.py
  build_low_data_splits.py
  train_dnabert2.py
  aggregate_results.py
  analyze_final_statistics.py
  analyze_compute_usage.py

results/
  final_epoch_all_seeds_combined.csv
  final_epoch_all_seeds_summary_mean_std.csv
  paper_figures/
  statistical_analysis_stronger/
  resource_analysis/

paper/figures/
  paper_fig1_pipeline.pdf
  paper_fig2_f1_trends.pdf
  paper_fig3_practical_drop_heatmap.pdf
  paper_fig4_resource_profile.pdf
```

## Final Experiment

- Model: `zhihan1996/DNABERT-2-117M`
- Tasks: promoter, core promoter, splice site, Non-TATA promoter
- Training ratios: `0.05%`, `0.1%`, `1%`, `10%`, `100%`
- Seeds: `13`, `42`, `3407`
- Primary metric: F1-macro
- Supporting metrics: AUROC, AUPRC, accuracy, MCC, precision-macro, recall-macro
- Resource profiling: seed 13 only

## Reproduction

Install dependencies:

```bash
pip install -r requirements.txt
```

The final run workflow is in:

```text
notebooks/CMP611_Final_Epoch_LowData_Colab.ipynb
```

The notebook uses the scripts under `scripts/` to check the environment, download GUE, build low-data splits, fine-tune DNABERT-2, and aggregate results.

Paper-facing figures can be regenerated with:

```bash
python results/paper_figures/make_paper_figures.py
```

## Manuscript Files

The final manuscript `.tex` and manuscript `.pdf` are intentionally ignored for now. They will be added later when the paper is finalized.
