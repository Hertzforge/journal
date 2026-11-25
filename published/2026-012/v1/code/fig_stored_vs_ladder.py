"""Figure: the minimum-drive test on the ladder and on the stored model (timing corrected), per cell.
One bar pair a cell; bar = median over the cell's structures, whisker = first to third quartile.
Top: control error. Bottom: typical element stress error. Data: ../data/e27_cells.json (from e27_analyze.py)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
BLUE, ORANGE, TEXT, MUTED, GRID = '#2a78d6', '#eb6834', '#10161d', '#566372', '#e2e8ef'

plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'], 'font.size': 9,
                     'axes.edgecolor': '#c9d3df', 'axes.labelcolor': TEXT, 'xtick.color': TEXT, 'ytick.color': TEXT,
                     'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8, 'axes.axisbelow': True,
                     'legend.frameon': False, 'savefig.dpi': 200, 'hatch.linewidth': 0.6})
C = json.load(open(os.path.join(HERE, '..', 'data', 'e27_cells.json')))
ORDER = [('6x6', '6 x 6\nlinear'), ('6x6-realistic', '6 x 6\nrealistic'), ('12x12', '12 x 12\nlinear'), ('12x12-realistic', '12 x 12\nrealistic'),
         ('12x12-strong', '12 x 12\nstrong'), ('24x12', '12 x 24\nlinear'), ('24x12-realistic', '12 x 24\nrealistic'), ('12x6-realistic', '6 x 12\nrealistic')]
fig, axes = plt.subplots(2, 1, figsize=(7.4, 5.6), sharex=True)
x = np.arange(len(ORDER)); w = 0.38
for ax, (kl, kn, lab) in zip(axes, (('b3_l', 'b3_n', 'Control error, dB'), ('st_l', 'st_n', 'Typical element stress error, dB'))):
    for off, key, col, hatch, name in ((-w / 2, kl, BLUE, None, 'Level ladder (no pretest)'), (w / 2, kn, ORANGE, '///', 'Started at full level on the stored model')):
        med = [np.median(C[c][key]) for c, _ in ORDER]; q1 = [np.percentile(C[c][key], 25) for c, _ in ORDER]; q3 = [np.percentile(C[c][key], 75) for c, _ in ORDER]
        ax.bar(x + off, med, w - 0.04, color=col, hatch=hatch, edgecolor='white', linewidth=0.6, label=name)
        ax.errorbar(x + off, med, yerr=[np.subtract(med, q1), np.subtract(q3, med)], fmt='none', ecolor=TEXT, elinewidth=0.9, capsize=2.5)
    ax.set_ylabel(lab); ax.set_ylim(0, None); ax.grid(axis='x', visible=False)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
top = axes[0].get_ylim()[1]; axes[0].set_ylim(0, top * 1.22)
for i, (c, _) in enumerate(ORDER):
    axes[0].text(i, top * 1.2, f"{C[c]['better']} of {C[c]['n']}\nbetter", ha='center', va='top', fontsize=7.5, color=MUTED)
axes[1].set_xticks(x); axes[1].set_xticklabels([l for _, l in ORDER]); axes[0].legend(loc='upper left', bbox_to_anchor=(0, 1.22), ncol=2)
axes[1].set_xlabel('System (shakers x control gauges) and size of the level effects')
fig.tight_layout(); out = os.path.join(HERE, '..', 'figures', 'fig_stored_vs_ladder')
fig.savefig(out + '.png'); fig.savefig(out + '.pdf'); print(out)
