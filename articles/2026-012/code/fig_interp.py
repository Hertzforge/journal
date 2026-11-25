"""Figure: a test at 3 dB below full level run on four models: the model measured at that level, the model interpolated
to it from the -6 dB and full-level models, the -6 dB model, and the full-level model. 10 structures a cell.
Bars: median control error; whiskers: quartiles. Data: ../data/e30_e33_cells.json (e30_e33_analyze.py)."""
import json, os
import numpy as np
from style import *
J = json.load(open(os.path.join(DATA, 'e30_e33_cells.json')))['e33']['tests']
CELLS = [('6x6-realistic', '6 x 6'), ('12x12-realistic', '12 x 12')]
ARMS = [('m3', BLUE, None, 'Measured at -3 dB'), ('interp', ORANGE, '///', 'Interpolated to -3 dB'), ('m6', GREEN, '...', 'Measured at -6 dB'), ('full', PURPLE, 'xxx', 'Measured at full level')]
fig, ax = plt.subplots(figsize=(6.6, 3.2)); x = np.arange(len(CELLS)); w = 0.2
for i, (k, col, hatch, name) in enumerate(ARMS):
    v = [J[c]['b3'][k] for c, _ in CELLS]; med = [np.median(a) for a in v]; q1 = [np.percentile(a, 25) for a in v]; q3 = [np.percentile(a, 75) for a in v]
    ax.bar(x + (i - 1.5) * w, med, w - 0.03, color=col, hatch=hatch, edgecolor='white', linewidth=0.6, label=name)
    ax.errorbar(x + (i - 1.5) * w, med, yerr=[np.subtract(med, q1), np.subtract(q3, med)], fmt='none', ecolor=TEXT, elinewidth=0.9, capsize=2.5)
ax.set_xticks(x); ax.set_xticklabels([n for _, n in CELLS]); ax.set_ylabel('Control error of the test at -3 dB, dB'); ax.set_ylim(0, None); clean(ax)
ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize=8, title='Model the test ran on', title_fontsize=8)
save(fig, 'fig_interp')
