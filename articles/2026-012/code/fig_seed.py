"""Figure: the minimum-drive test on the level ladder, started at full level on the model a pretest stored, and started
at full level on the model stored during a previous ladder test. 10 structures a cell, realistic size.
Bars: median; whiskers: quartiles. Data: ../data/e30_e33_cells.json (e30_e33_analyze.py)."""
import json, os
import numpy as np
from style import *
J = json.load(open(os.path.join(DATA, 'e30_e33_cells.json')))['e30']
CELLS = [('6x6-realistic', '6 x 6'), ('12x12-realistic', '12 x 12')]
keys = list(J['6x6-realistic']['b3'].keys())
ARMS = [(keys[0], BLUE, None, 'Level ladder (no stored model)'), (keys[1], ORANGE, '///', 'Full level, model from a pretest'),
        (keys[2], GREEN, '...', 'Full level, model from a previous test')]
fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.2)); x = np.arange(len(CELLS)); w = 0.26
for ax, (kind, lab) in zip(axes, (('b3', 'Control error, dB'), ('stress', 'Typical element stress error, dB'))):
    for i, (k, col, hatch, name) in enumerate(ARMS):
        if k not in J[CELLS[0][0]][kind]: continue
        v = [J[c][kind][k] for c, _ in CELLS]; med = [np.median(a) for a in v]
        q1 = [np.percentile(a, 25) for a in v]; q3 = [np.percentile(a, 75) for a in v]
        ax.bar(x + (i - 1) * w, med, w - 0.03, color=col, hatch=hatch, edgecolor='white', linewidth=0.6, label=name)
        ax.errorbar(x + (i - 1) * w, med, yerr=[np.subtract(med, q1), np.subtract(q3, med)], fmt='none', ecolor=TEXT, elinewidth=0.9, capsize=2.5)
    ax.set_xticks(x); ax.set_xticklabels([n for _, n in CELLS]); ax.set_ylabel(lab); ax.set_ylim(0, None); clean(ax)
axes[0].legend(loc='upper left', bbox_to_anchor=(0, 1.32), ncol=1, fontsize=8)
save(fig, 'fig_seed')
