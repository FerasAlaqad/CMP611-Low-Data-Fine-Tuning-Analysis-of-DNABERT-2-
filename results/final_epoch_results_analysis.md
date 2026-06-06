# Final Epoch Results Analysis

This file summarizes the cleaned final result set used for the paper.

## Main observations

- Promoter detection is label-efficient: the 1% condition remains close to the 100% full-data condition.
- Core promoter detection requires more labels than general promoter detection and reaches the no-practical-drop region at 10%.
- Non-TATA promoter detection improves steadily with more data; 10% is close to full-data performance but remains above the strict practical-drop threshold used in the paper.
- Splice site prediction is the most data-hungry task: very low-data regimes remain weak, 10% improves substantially, and 100% remains clearly strongest.
- Resource profiling indicates that lower data ratios mainly reduce runtime, while peak GPU memory stays nearly constant within each task.

See `results/paper_figures/paper_main_results_summary.csv`, `results/paper_figures/paper_main_runs_combined.csv`, and `results/statistical_analysis_stronger/paired_drop_stronger_stats.csv` for the paper-facing numeric outputs.
