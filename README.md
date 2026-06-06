# Low-Data Fine-Tuning Analysis of DNABERT-2

Reproducibility package for the study **Low-Data Fine-Tuning Analysis of DNABERT-2 for Human Regulatory Sequence Classification**.

## Experiment

- Model: `zhihan1996/DNABERT-2-117M`
- Tasks: promoter, core promoter, splice site, Non-TATA promoter
- Training ratios: `0.05%`, `0.1%`, `1%`, `10%`, `100%`
- Seeds: `13`, `42`, `3407`
- Primary metric: F1-macro
- Additional metrics: AUROC, AUPRC, accuracy, MCC, macro precision, macro recall
- Resource profile: seed 13

## Layout

```text
notebooks/                 Colab workflow for the final experiment
scripts/                   Data preparation, training, aggregation, and analysis
results/                   Result tables used in the paper
figures/                   Exported paper figures
```

## Reproduction

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the final workflow in Colab:

```text
notebooks/CMP611_Final_Epoch_LowData_Colab.ipynb
```

Regenerate figures:

```bash
python scripts/make_paper_figures.py
```

The manuscript source and final manuscript PDF are not tracked in this repository yet.
