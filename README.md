# Low-Data Fine-Tuning Analysis of DNABERT-2 for Human Regulatory Sequence Classification

This repository contains the reproducibility code, notebooks, figures, and cleaned result summaries for the CMP611 bioinformatics study on DNABERT-2 low-data fine-tuning.

The manuscript LaTeX source and final manuscript PDF are intentionally **not committed yet**. They are ignored via `.gitignore` and will be added later when the paper is finalized.

## Study Summary

- **Model:** `zhihan1996/DNABERT-2-117M`
- **Main question:** How does reducing labeled training data affect DNABERT-2 fine-tuning performance, practical F1 degradation, seed variability, and resource usage?
- **Tasks:**
  - Promoter Detection
  - Core Promoter Detection
  - Splice Site Prediction
  - Non-TATA Promoter Detection
- **Training-data ratios:** `0.05%`, `0.1%`, `1%`, `10%`, `100%`
- **Seeds:** `13`, `42`, `3407`
- **Main metric:** F1-macro
- **Supporting metrics:** AUROC, AUPRC, accuracy, MCC, precision-macro, recall-macro
- **Resource profiling:** seed 13 only

## Repository Structure

```text
configs/                         Training/config examples
scripts/                         Data preparation, training, aggregation, and analysis scripts
notebooks/                       Colab notebooks used for smoke tests, final runs, and follow-up analyses
results/                         Cleaned CSV/MD/ZIP result summaries
results/paper_figures/           Publication figures and figure-generation code
results/statistical_analysis_stronger/
                                 Paired-drop and bootstrap analysis outputs
results/resource_analysis/        Resource profiling tables and figures
paper/figures/                   Figure PDFs used by the manuscript
```

## Reproducing the Pipeline

Install dependencies:

```bash
pip install -r requirements.txt
```

Check the environment:

```bash
python scripts/check_environment.py
```

Download GUE data:

```bash
python scripts/download_gue.py --out-dir data/raw
```

Build low-data splits and run training using the provided scripts/notebooks. The final Colab notebook is:

```text
notebooks/CMP611_Final_Epoch_LowData_Colab.ipynb
```

Aggregate per-run JSON outputs:

```bash
python scripts/aggregate_results.py \
  --results-root outputs/final_epoch/main_runs \
  --out-csv outputs/final_epoch_summary_all_runs.csv \
  --out-mean-csv outputs/final_epoch_summary_mean_std.csv
```

Generate paper figures from cleaned result tables:

```bash
python results/paper_figures/make_paper_figures.py
```

## Notes

- Final manuscript `.tex` and manuscript `.pdf` files are not tracked at this stage.
- Raw datasets, checkpoints, local outputs, and virtual environments are ignored.
- The committed result summaries are cleaned paper-facing outputs, not raw Colab runtime directories.
