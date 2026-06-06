# Figure Strategy and Publication Specifications

Paper: **Low-Data Fine-Tuning Analysis of DNABERT-2 for Human Regulatory Sequence Classification**

## A. Overall Figure Strategy

The strongest main-paper figure set is **four figures**:

1. Experimental design pipeline
2. Main F1-macro trends with mean ± SD
3. Practical F1 drop relative to 100% training data
4. Resource profile: runtime and peak GPU memory

This is the minimal set that supports the paper's core claims without visual redundancy. It covers methodology, label efficiency, practical performance degradation, and compute behavior. Dataset sizes, full metric values, and exact resource numbers should remain in tables because exact numeric comparison is better handled tabularly.

### Existing Figure Decisions

- `paper_fig1_pipeline.pdf`: **updated and keep**. It now includes controlled-experiment structure, train-only downsampling, fixed test evaluation, aggregation, paired-drop analysis, and seed-13 resource profiling.
- `paper_fig2_f1_heatmap.pdf`: **remove/replace**. The heatmap was readable but did not show standard deviation. It is replaced by `paper_fig2_f1_trends.pdf`, which shows mean ± SD across three seeds.
- `paper_fig3_practical_drop_heatmap.pdf`: **keep with minor update**. It directly answers the instructor's requested practical-drop analysis. It is framed as effect-size/practical drop, not formal significance testing.
- `paper_fig4_resource_profile.pdf`: **keep with minor update**. It now explicitly marks that resource profiling used seed 13.

### Main vs Supplementary

Main paper: Figures 1-4.

Supplementary/appendix only if space allows:
- Performance-cost trade-off plot, because it mixes three-seed mean performance with seed-13 runtime and needs careful caveating.
- Dataset statistics table, not a figure.
- Full metric table with AUROC/AUPRC/MCC, not a figure.

Do not add figures merely for quantity. The four-figure set is already enough for a compact conference paper.

## B. Figure-by-Figure Review

### Existing Figure 1: `paper_fig1_pipeline.pdf`

Current role: Methodology overview.

Decision: **Keep after update.**

Reason: The paper does not propose a new architecture, so the figure should emphasize controlled experimental design rather than model internals.

Specific improvements already applied:
- Added analysis stage.
- Added `4 tasks x 5 ratios x 3 seeds = 60 fine-tuning runs`.
- Added seed-13 resource profile note.
- Kept dev/test fixed and train-only downsampling explicit.

### Existing Figure 2: previous heatmap

Current role: Main performance overview.

Decision: **Replace with line plot.**

Reason: The paper-specific instruction requires actual F1-macro mean and standard deviation. A heatmap shows means clearly but hides seed variability. The line plot with error bars better communicates both label-efficiency trends and seed variability.

Replacement file:
- `paper_fig2_f1_trends.pdf`

### Existing Figure 3: `paper_fig3_practical_drop_heatmap.pdf`

Current role: Practical performance drop relative to full data.

Decision: **Keep.**

Reason: This figure directly supports the data-threshold discussion. It makes clear that promoter is label-efficient at 1%, core promoter at 10%, Non-TATA 10% is close but over the strict threshold, and splice remains data-hungry.

Specific improvements already applied:
- Colorbar label changed to `ΔF1 vs 100%`.
- Added concise note: `green border: ΔF1 < 0.05; lower is better`.

### Existing Figure 4: `paper_fig4_resource_profile.pdf`

Current role: Resource behavior under training-data reduction.

Decision: **Keep.**

Reason: It addresses the instructor's request to quantify how much resource use decreases when the data is reduced. It separates runtime and memory, avoiding a misleading combined performance-resource plot.

Specific improvements already applied:
- Added `seed 13 resource profile` inside the memory panel.
- Kept runtime and memory in separate panels.
- Used matching colors across panels and other figures.

## C. Final Recommended Figure Set

### Figure 1: Experimental Design Pipeline

Figure ID: Figure 1

Purpose: Show the controlled low-data fine-tuning workflow.

Why necessary: The paper's contribution is experimental characterization, not architecture design. This figure explains the controlled setup at a glance.

Recommended type: Minimal horizontal pipeline diagram.

Placement: Double-column or wide single-column. Double-column preferred.

Exact layout:
- Five horizontal rounded blocks connected by arrows.
- Blocks: Dataset splits → Train only → Fine-tuning → Test eval. → Analysis.
- Two short notes below the pipeline.

Data required:
- Four tasks.
- Five ratios.
- Three seeds.
- Fixed dev/test design.
- Resource profile seed 13.

Labels inside figure:
- Dataset splits
- 4 tasks / train/dev/test
- Train only
- 0.05, 0.1, 1 / 10, 100%
- Fine-tuning
- DNABERT-2 / seeds 13/42/3407
- Test eval.
- fixed test / F1, AUROC, AUPRC
- Analysis
- mean/std / ΔF1 + resources
- dev/test fixed; train split changes only
- 4 tasks x 5 ratios x 3 seeds = 60 fine-tuning runs; resource profile measured on seed 13

What must be excluded:
- Model internals.
- LoRA.
- Dataset-size table values.
- Long explanations.
- Decorative icons.

Style instructions:
- Light gray rounded boxes.
- Dark gray strokes.
- Thin arrows.
- No title.

Caption guidance:
Caption should state that only the train split was downsampled while dev/test remained fixed.

### Figure 2: Main F1-Macro Results

Figure ID: Figure 2

Purpose: Show label-efficiency trends by task.

Why necessary: This is the main evidence figure for the paper.

Recommended type: Multi-task line plot with markers and error bars.

Placement: Double-column preferred. Single-column would make the legend and error bars hard to read.

Exact layout:
- x-axis: training data ratio as categorical ordered labels: 0.05, 0.1, 1, 10, 100.
- y-axis: F1-macro mean ± SD.
- One colored line per task.
- Error bars show SD over three seeds.
- Legend above the plot, one row.

Data required:
- Mean and SD F1-macro for each task and ratio.

Labels inside figure:
- Training data (%)
- F1-macro (mean ± SD)
- Promoter
- Core promoter
- Non-TATA promoter
- Splice site

What must be excluded:
- Numeric labels on every point.
- AUROC/AUPRC overlays.
- Runtime values.
- Statistical significance markers.

Style instructions:
- Same task colors as all other figures.
- Moderate line width.
- Small markers.
- Subtle y-grid only.
- No title.

Caption guidance:
Caption should state that points are mean over three seeds and error bars are SD.

### Figure 3: Practical Drop / Retained Performance

Figure ID: Figure 3

Purpose: Show task-specific F1 drop relative to 100% training data.

Why necessary: It directly answers when performance begins to drop and supports the practical threshold discussion.

Recommended type: Heatmap of ΔF1 relative to 100%.

Placement: Double-column preferred, but can fit single-column if font size is preserved and cell labels remain readable.

Exact layout:
- Rows: tasks.
- Columns: 0.05%, 0.1%, 1%, 10%.
- Cell color: mean paired F1 drop relative to 100%.
- Cell text: numeric ΔF1 rounded to three decimals.
- Green border marks ΔF1 < 0.05.

Data required:
- Paired drop relative to 100% for each task, ratio, and seed.

Required values:
- Promoter 1% drop = 0.033.
- Promoter 10% drop = 0.015.
- Core promoter 10% drop = 0.021.
- Non-TATA 10% drop = 0.065.
- Splice 10% drop = 0.215.

Labels inside figure:
- Task
- Training data (%)
- ΔF1 vs 100%
- green border: ΔF1 < 0.05; lower is better

What must be excluded:
- p-values.
- “significant” labels.
- Hypothesis-test language.

Style instructions:
- Sequential orange/red color scale.
- Green threshold border only where ΔF1 < 0.05.
- No title.

Caption guidance:
Caption should say this is a practical effect-size analysis, not a formal significance test.

### Figure 4: Resource Profile

Figure ID: Figure 4

Purpose: Show training-time scaling and peak-memory behavior as data ratio changes.

Why necessary: It addresses the instructor's request to quantify resource savings.

Recommended type: Two-panel line plot.

Placement: Double-column.

Exact layout:
- Panel A: training runtime in minutes vs training data ratio.
- Panel B: peak GPU memory in GB vs training data ratio.
- Same task colors in both panels.
- Log-scaled x-axis in both panels.
- Log-scaled y-axis for runtime.
- Linear y-axis for memory.
- Shared legend above panels.

Data required:
- Seed-13 resource profiling table.
- Runtime and peak GPU memory for each task and ratio.

Labels inside figure:
- A
- B
- Training data (%)
- Training runtime (min)
- Peak GPU memory (GB)
- seed 13 resource profile

What must be excluded:
- F1 values.
- Runtime reduction percentages inside the plot.
- Any visual implication that memory decreases with data ratio.

Style instructions:
- Same task colors as Figure 2.
- Thin lines, small markers.
- Subtle grid.
- No title.

Caption guidance:
Caption must state that resource profiling used seed 13 only and should not be interpreted as three-seed averaged compute.

## D. Additional Figures to Avoid

Do not include these in the main paper:

- Formal ablation figure: no architecture/method ablation was performed.
- Error analysis figure: no confusion matrix, class-wise error, motif-level, or interpretability analysis was completed.
- Motif interpretation figure: no motif attribution or biological interpretability data exists.
- External baseline comparison figure: no external baseline or SOTA reproduction was implemented.
- SOTA comparison figure: would require external numbers and citations not currently provided.
- Reproducibility workflow figure: would likely become a generic software diagram; better handled in text.
- Metric consistency figure: F1, AUROC, and AUPRC values are better handled in a table unless a specific inconsistency is being discussed.

## Additional Figure Ideation Decisions

### Label-efficiency threshold summary figure

Decision: **Do not include as a main figure.**

Reason: It would duplicate Figure 3. Use a compact table or one paragraph instead.

If used: appendix only.

### Relative F1 retained figure

Decision: **Do not include as a main figure.**

Reason: It duplicates Figure 3 and can hide absolute performance differences, especially for splice.

If used: not recommended unless the paper needs a simplified presentation figure.

### Performance-cost trade-off figure

Decision: **Optional appendix, not main paper.**

Reason: Scientifically useful, but it mixes three-seed averaged F1 with seed-13-only runtime. This can be honest if clearly labeled, but it is not necessary because Figures 2 and 4 already separate performance and resources cleanly.

Required note if used:
`F1: mean over 3 seeds; runtime: seed 13 resource profile`.

### Task difficulty / data-hunger summary figure

Decision: **Do not include as a figure.**

Reason: It would be partly interpretive/category-based. Better expressed in Discussion using Figure 3.

### Experimental matrix figure

Decision: **Covered by Figure 1.**

Reason: Figure 1 already states 4 x 5 x 3 = 60 runs.

### Seed variability figure

Decision: **Covered by Figure 2.**

Reason: Figure 2 includes SD error bars over three seeds.

## E. Implementation-Ready Specification

### Shared style

- Font: DejaVu Sans or Helvetica/Arial equivalent.
- Export: PDF and SVG for paper; PNG only for preview.
- Resolution: 450 dpi for PNG exports.
- Color palette:
  - Promoter: `#167C80`
  - Core promoter: `#3A68A8`
  - Non-TATA promoter: `#8E5EA2`
  - Splice site: `#D9822B`
  - Neutral text: `#2E3440`
  - Grid: `#D8DEE9`
  - Practical-threshold green: `#1B9E77`
- No figure title inside the canvas.
- Captions carry interpretation; figure body carries only data and labels.

### Figure 1 implementation

- Canvas: 7.7 x 2.25 inches.
- Layout: five rounded boxes, left-to-right.
- Box stroke: 0.85 pt.
- Arrow stroke: 0.85 pt.
- Header font: 8.0 pt bold.
- Body font: 6.8 pt.
- Bottom note font: 7.0-7.4 pt.
- Export: `paper_fig1_pipeline.pdf`, `.svg`, `.png`.

### Figure 2 implementation

- Canvas: 6.9 x 3.05 inches.
- Chart type: line plot with error bars.
- x-axis: categorical ratio labels, ordered 0.05, 0.1, 1, 10, 100.
- y-axis: F1-macro mean ± SD.
- y-range: 0.18-0.98.
- Line width: 1.45 pt.
- Marker size: 4.0 pt.
- Error bar line width: 0.85 pt.
- Cap size: 2.2 pt.
- Legend: top center, four columns, no frame.
- Export: `paper_fig2_f1_trends.pdf`, `.svg`, `.png`.

### Figure 3 implementation

- Canvas: 5.85 x 2.75 inches.
- Chart type: heatmap.
- Color scale: sequential orange/red, vmin 0, vmax >= 0.65.
- Cell text: three decimals.
- Green border: cells where ΔF1 < 0.05.
- Colorbar label: `ΔF1 vs 100%`.
- Annotation: `green border: ΔF1 < 0.05; lower is better`.
- Export: `paper_fig3_practical_drop_heatmap.pdf`, `.svg`, `.png`.

### Figure 4 implementation

- Canvas: 7.05 x 2.85 inches.
- Chart type: two-panel line plot.
- Panel A: runtime, log y-axis.
- Panel B: peak GPU memory, linear y-axis.
- x-axis: log scale in both panels.
- Line width: 1.45 pt.
- Marker size: 3.6 pt.
- Shared legend: top center, four columns, no frame.
- Annotation: `seed 13 resource profile` in memory panel.
- Export: `paper_fig4_resource_profile.pdf`, `.svg`, `.png`.

## F. Final Quality Checklist

Before finalizing the paper figures:

- No titles inside figures.
- No fake data.
- No unsupported claims.
- Consistent task colors across all figures.
- Figures remain readable at two-column width.
- Figure 2 uses mean ± SD, not mean only.
- Figure 3 is described as practical effect-size analysis, not formal significance testing.
- Resource profiling is explicitly marked as seed 13 only.
- Captions carry interpretation; figures remain visually minimal.
- All numbers match the provided results.
- No ablation, error-analysis, motif, external baseline, or SOTA figure is included without data.
