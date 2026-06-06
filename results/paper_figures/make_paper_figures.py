from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

RESULTS = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)
SUMMARY = OUT / 'paper_main_results_summary.csv'
COMBINED = OUT / 'paper_main_runs_combined.csv'
RESOURCE = RESULTS / 'resource_analysis' / 'paper_table_resource_usage_real.csv'

mpl.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 8.2,
    'axes.labelsize': 8.8,
    'xtick.labelsize': 7.8,
    'ytick.labelsize': 7.8,
    'legend.fontsize': 7.7,
    'axes.linewidth': 0.7,
    'xtick.major.width': 0.7,
    'ytick.major.width': 0.7,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'svg.fonttype': 'none',
})

TASK_ORDER = ['promoter', 'core_promoter', 'nontata_promoter', 'splice']
TASK_LABEL = {
    'promoter': 'Promoter',
    'core_promoter': 'Core promoter',
    'nontata_promoter': 'Non-TATA promoter',
    'splice': 'Splice site',
}
RATIOS = [0.05, 0.1, 1.0, 10.0, 100.0]
RATIO_LABEL = ['0.05', '0.1', '1', '10', '100']
COLORS = {
    'promoter': '#167C80',
    'core_promoter': '#3A68A8',
    'nontata_promoter': '#8E5EA2',
    'splice': '#D9822B',
}
NEUTRAL = '#2E3440'
GRID = '#D8DEE9'


def savefig(fig, stem, dpi=450):
    for ext in ['pdf', 'svg', 'png']:
        fig.savefig(OUT / f'{stem}.{ext}', bbox_inches='tight', dpi=dpi)
    plt.close(fig)


def fig1_pipeline():
    fig, ax = plt.subplots(figsize=(7.7, 2.25))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    boxes = [
        (0.025, 0.36, 0.155, 0.34, 'Dataset splits', '4 tasks\ntrain/dev/test'),
        (0.225, 0.36, 0.155, 0.34, 'Train only', '0.05, 0.1, 1\n10, 100%'),
        (0.425, 0.36, 0.155, 0.34, 'Fine-tuning', 'DNABERT-2\nseeds 13/42/3407'),
        (0.625, 0.36, 0.155, 0.34, 'Test eval.', 'fixed test\nF1, AUROC, AUPRC'),
        (0.825, 0.36, 0.155, 0.34, 'Analysis', 'mean/std\nΔF1 + resources'),
    ]
    for x, y, w, h, head, body in boxes:
        patch = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.012,rounding_size=0.018',
                               linewidth=0.85, edgecolor='#4C566A', facecolor='#F8FAFC')
        ax.add_patch(patch)
        ax.text(x + w/2, y + h*0.68, head, ha='center', va='center', fontsize=8.0,
                fontweight='bold', color=NEUTRAL)
        ax.text(x + w/2, y + h*0.35, body, ha='center', va='center', fontsize=6.8,
                color='#4C566A', linespacing=1.18)
    for i in range(len(boxes)-1):
        x1 = boxes[i][0] + boxes[i][2]
        x2 = boxes[i+1][0]
        y = 0.53
        ax.add_patch(FancyArrowPatch((x1+0.012, y), (x2-0.012, y), arrowstyle='-|>', mutation_scale=8,
                                     linewidth=0.85, color='#4C566A'))

    ax.text(0.5, 0.20, 'dev/test fixed; train split changes only', ha='center', va='center',
            fontsize=7.4, color='#4C566A')
    ax.text(0.5, 0.105, '4 tasks x 5 ratios x 3 seeds = 60 fine-tuning runs; resource profile measured on seed 13',
            ha='center', va='center', fontsize=7.0, color='#5E6778')
    savefig(fig, 'paper_fig1_pipeline')


def fig2_f1_trends():
    df = pd.read_csv(SUMMARY)
    fig, ax = plt.subplots(figsize=(6.9, 3.05))
    x = np.arange(len(RATIOS))
    for task in TASK_ORDER:
        sub = df[df.task == task].sort_values('ratio_percent')
        y = sub['eval_f1_macro_mean'].to_numpy()
        yerr = sub['eval_f1_macro_std'].to_numpy()
        ax.errorbar(x, y, yerr=yerr, color=COLORS[task], marker='o', markersize=4.0,
                    linewidth=1.45, elinewidth=0.85, capsize=2.2, capthick=0.85,
                    label=TASK_LABEL[task])
    ax.set_xticks(x, RATIO_LABEL)
    ax.set_xlabel('Training data (%)')
    ax.set_ylabel('F1-macro (mean ± SD)')
    ax.set_ylim(0.18, 0.98)
    ax.grid(True, axis='y', color=GRID, linewidth=0.55, alpha=0.9)
    ax.grid(True, axis='x', color='#EDF2F7', linewidth=0.45, alpha=0.65)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.13), ncol=4, frameon=False,
              handlelength=1.6, columnspacing=1.05)
    savefig(fig, 'paper_fig2_f1_trends')


def fig3_practical_drop_heatmap():
    df = pd.read_csv(COMBINED)
    rows = []
    low_ratios = [0.05, 0.1, 1.0, 10.0]
    for task in TASK_ORDER:
        for ratio in low_ratios:
            drops = []
            for seed in sorted(df.seed.unique()):
                a = df[(df.task == task) & (np.isclose(df.ratio_percent, ratio)) & (df.seed == seed)]
                b = df[(df.task == task) & (np.isclose(df.ratio_percent, 100.0)) & (df.seed == seed)]
                if len(a) and len(b):
                    drops.append(float(b.eval_f1_macro.iloc[0]) - float(a.eval_f1_macro.iloc[0]))
            rows.append({'task': task, 'ratio': ratio, 'drop': np.mean(drops)})
    ddf = pd.DataFrame(rows)
    mat = np.zeros((len(TASK_ORDER), len(low_ratios)))
    for i, task in enumerate(TASK_ORDER):
        for j, r in enumerate(low_ratios):
            mat[i, j] = ddf[(ddf.task == task) & (np.isclose(ddf.ratio, r))]['drop'].iloc[0]

    fig, ax = plt.subplots(figsize=(5.85, 2.75))
    im = ax.imshow(mat, cmap='OrRd', vmin=0, vmax=max(0.65, np.nanmax(mat)), aspect='auto')
    ax.set_xticks(range(len(low_ratios)), ['0.05', '0.1', '1', '10'])
    ax.set_yticks(range(len(TASK_ORDER)), [TASK_LABEL[t] for t in TASK_ORDER])
    ax.set_xlabel('Training data (%)')
    ax.set_ylabel('Task')
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            color = 'white' if v > 0.28 else '#111827'
            ax.text(j, i, f'{v:.3f}', ha='center', va='center', color=color, fontsize=7.4, fontweight='bold')
            if v < 0.05:
                ax.add_patch(Rectangle((j-0.47, i-0.47), 0.94, 0.94, fill=False,
                                       edgecolor='#1B9E77', linewidth=1.55))
    ax.set_xticks(np.arange(-.5, len(low_ratios), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(TASK_ORDER), 1), minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=1.2)
    ax.tick_params(which='minor', bottom=False, left=False)
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.025)
    cbar.set_label('ΔF1 vs 100%')
    cbar.outline.set_linewidth(0.6)
    ax.text(3.49, -0.70, 'green border: ΔF1 < 0.05; lower is better', ha='right', va='center',
            fontsize=7.0, color='#256D4F')
    savefig(fig, 'paper_fig3_practical_drop_heatmap')


def fig4_resource_profile():
    df = pd.read_csv(RESOURCE)
    fig, axes = plt.subplots(1, 2, figsize=(7.05, 2.85), gridspec_kw={'width_ratios': [1.15, 1.0]})
    ax = axes[0]
    for task in TASK_ORDER:
        sub = df[df.task == task].sort_values('ratio_percent')
        ax.plot(sub.ratio_percent, sub.train_runtime_min, marker='o', linewidth=1.45, markersize=3.6,
                color=COLORS[task], label=TASK_LABEL[task])
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xticks(RATIOS, RATIO_LABEL)
    ax.set_xlabel('Training data (%)')
    ax.set_ylabel('Training runtime (min)')
    ax.grid(True, which='major', axis='both', color=GRID, linewidth=0.55, alpha=0.85)
    ax.text(-0.12, 1.04, 'A', transform=ax.transAxes, fontsize=9.8, fontweight='bold', va='bottom')

    ax2 = axes[1]
    for task in TASK_ORDER:
        sub = df[df.task == task].sort_values('ratio_percent')
        ax2.plot(sub.ratio_percent, sub.peak_gpu_memory_gb, marker='o', linewidth=1.45, markersize=3.6,
                 color=COLORS[task], label=TASK_LABEL[task])
    ax2.set_xscale('log')
    ax2.set_xticks(RATIOS, RATIO_LABEL)
    ax2.set_ylim(1.8, 4.35)
    ax2.set_xlabel('Training data (%)')
    ax2.set_ylabel('Peak GPU memory (GB)')
    ax2.grid(True, which='major', axis='both', color=GRID, linewidth=0.55, alpha=0.85)
    ax2.text(-0.12, 1.04, 'B', transform=ax2.transAxes, fontsize=9.8, fontweight='bold', va='bottom')
    ax2.text(0.98, 0.05, 'seed 13 resource profile', transform=ax2.transAxes,
             ha='right', va='bottom', fontsize=6.9, color='#5E6778')
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=4, frameon=False, bbox_to_anchor=(0.52, 1.04),
               handlelength=1.55, columnspacing=1.1)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    savefig(fig, 'paper_fig4_resource_profile')


if __name__ == '__main__':
    fig1_pipeline()
    fig2_f1_trends()
    fig3_practical_drop_heatmap()
    fig4_resource_profile()
    for old in OUT.glob('paper_fig2_f1_heatmap.*'):
        old.unlink()
    print(f'Wrote figures to {OUT}')
