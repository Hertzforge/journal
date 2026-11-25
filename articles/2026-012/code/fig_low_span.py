"""Figure: a test at 12 dB below full level run on five models: the low-level identification, the model after the
pretest's -12 dB loop, the model interpolated to -12 dB from the identification and the -6 dB model, the -6 dB model,
and the full-level model. 10 structures a cell. Bars: median control error; whiskers: quartiles.
Data: ../data/e34_cells.json (e34_analyze.py)."""
import json, os
import numpy as np
from style import *
J = json.load(open(os.path.join(DATA, 'e34_cells.json')))['cells']
CELLS = [('6x6-realistic', '6 x 6'), ('12x12-realistic', '12 x 12')]
keys = list(J['6x6-realistic']['b3'].keys()); print(keys)
NAME = {'id': 'Low-level identification', 'm12': "After the pretest's -12 dB loop", 'interp': 'Interpolated to -12 dB', 'm6': 'Measured at -6 dB', 'full': 'Measured at full level'}
LOOK = {'id': (MUTED, None), 'm12': (BLUE, None), 'interp': (ORANGE, '///'), 'm6': (GREEN, '...'), 'full': (PURPLE, 'xxx')}
ORDER = [k for k in ('id', 'm12', 'interp', 'm6', 'full') if k in keys]; assert len(ORDER) == 5, keys
fig, ax = plt.subplots(figsize=(6.8, 3.2)); x = np.arange(len(CELLS)); w = 0.16
for i, k in enumerate(ORDER):
    v = [J[c]['b3'][k] for c, _ in CELLS]; med = [np.median(a) for a in v]; q1 = [np.percentile(a, 25) for a in v]; q3 = [np.percentile(a, 75) for a in v]
    ax.bar(x + (i - 2) * w, med, w - 0.02, color=LOOK[k][0], hatch=LOOK[k][1], edgecolor='white', linewidth=0.6, label=NAME[k])
    ax.errorbar(x + (i - 2) * w, med, yerr=[np.subtract(med, q1), np.subtract(q3, med)], fmt='none', ecolor=TEXT, elinewidth=0.9, capsize=2.5)
ax.set_xticks(x); ax.set_xticklabels([n for _, n in CELLS]); ax.set_ylabel('Control error of the test at -12 dB, dB'); ax.set_ylim(0, None); clean(ax)
ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize=8, title='Model the test ran on', title_fontsize=8)
save(fig, 'fig_low_span')
