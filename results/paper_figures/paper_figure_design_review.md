# Paper Figure Design Review

## Existing Figure Review

- Presentation figures under `project final presentation/figures_nature_final/` should not be used directly in the paper. They were designed for slides and contain slide-style emphasis.
- The paper should use a smaller, cleaner figure set focused on methodology, performance, practical data thresholds, and compute usage.
- No ablation-study figure should be created because no architecture ablation was performed.
- No error-analysis figure should be created because no class-wise error or motif-level analysis was performed.
- No deployment/reproducibility workflow figure is necessary; reproducibility details are better handled in the Methods text.

## Final Figure Set

### Figure 1: Experimental Pipeline

Purpose: Summarize the full experimental workflow without overloading the reader.

What it shows:
- Input datasets.
- Train-only low-data subsampling.
- DNABERT-2 full fine-tuning.
- Fixed test-set evaluation.

What should not be included:
- Detailed dataset sizes.
- Full hyperparameter list.
- Long explanations.
- Any title inside the figure.

Layout:
- Four horizontally aligned rounded boxes.
- Thin arrows between boxes.
- One compact task strip below.

Text labels inside figure:
- Input datasets
- 4 tasks / train/dev/test
- Low-data splits
- train only / 5 ratios x 3 seeds
- Fine-tuning
- DNABERT-2 / full model
- Evaluation
- fixed test / F1, AUROC, AUPRC
- Promoter | Core promoter | Splice site | Non-TATA promoter
- Only train split is downsampled; dev/test splits remain fixed

Recommended type:
- Minimal pipeline diagram.

Warning:
- Do not add model internals here; that would clutter the figure.

Generated files:
- `paper_fig1_pipeline.pdf`
- `paper_fig1_pipeline.svg`
- `paper_fig1_pipeline.png`

### Figure 2: Main F1-Macro Result Matrix

Purpose: Present the main quantitative result compactly.

What it shows:
- Mean F1-macro by task and training-data ratio.
- Three-seed aggregate values.

What should not be included:
- AUROC/AUPRC values.
- Runtime values.
- Long notes.

Layout:
- Task rows.
- Training-ratio columns.
- Cell color encodes F1-macro.
- Cell text gives exact value rounded to three decimals.

Text labels inside figure:
- Task
- Training data (%)
- F1-macro
- Task names and ratio labels only.

Recommended type:
- Heatmap with numeric annotations.

Warning:
- Keep the caption short and put methodological details in the text, not inside the figure.

Generated files:
- `paper_fig2_f1_heatmap.pdf`
- `paper_fig2_f1_heatmap.svg`
- `paper_fig2_f1_heatmap.png`

### Figure 3: Practical Performance Drop vs Full Data

Purpose: Address the instructor's request for determining the data level at which performance drops.

What it shows:
- Mean paired F1 drop relative to 100% training data.
- Lower-data conditions only: 0.05%, 0.1%, 1%, 10%.
- Green border marks cells with practical drop below 0.05 F1.

What should not be included:
- p-values, because only three seeds are available.
- Overstated statistical significance claims.

Layout:
- Heatmap of F1 drop vs 100%.
- Rows are tasks.
- Columns are low-data ratios.
- Cell annotations show mean F1 drop.

Text labels inside figure:
- Task
- Training data (%)
- F1 drop vs 100%
- green border: drop < 0.05

Recommended type:
- Heatmap with threshold outline.

Warning:
- Describe this as practical-drop/effect-size analysis, not a strong formal hypothesis test.

Generated files:
- `paper_fig3_practical_drop_heatmap.pdf`
- `paper_fig3_practical_drop_heatmap.svg`
- `paper_fig3_practical_drop_heatmap.png`

### Figure 4: Resource Profile

Purpose: Show how reducing training data changes computational cost.

What it shows:
- Panel A: training runtime across all ratios, including 100%.
- Panel B: peak GPU memory across all ratios.
- Runtime decreases strongly, while memory is mostly stable.

What should not be included:
- F1 values.
- Detailed train example counts.
- Long explanatory labels.

Layout:
- Two-panel line chart.
- Log-scale x-axis for data ratios.
- Log-scale runtime axis in Panel A.
- Linear memory axis in Panel B.

Text labels inside figure:
- A
- B
- Training data (%)
- Training runtime (min)
- Peak GPU memory (GB)
- Task legend.

Recommended type:
- Two-panel line chart.

Warning:
- Caption should state that resource profiling used seed13 on Tesla T4.

Generated files:
- `paper_fig4_resource_profile.pdf`
- `paper_fig4_resource_profile.svg`
- `paper_fig4_resource_profile.png`
