"""Figure: what the pretest's timing does to the stored model. Change in control error against the ladder (stored
model minus ladder, negative is better), three forms of the pretest, 20 structures a cell: median and quartiles.
Data: ../data/e26_timing.json (experiments/e26_delay_fit/s1_output_kd.json)."""
import json, os
import numpy as np
from style import *
J = json.load(open(os.path.join(DATA, 'e26_timing.json')))
ORDER = [('6x6', '6 x 6\nlinear'), ('12x12', '12 x 12\nlinear'), ('24x12', '12 x 24\nlinear'), ('12x12-realistic', '12 x 12\nrealistic'), ('24x12-realistic', '12 x 24\nrealistic')]
ARMS = [('ka', 'Delay read from a correlation peak (first form)', MUTED, None), ('kf8', 'Delay told to the pretest (8 samples)', BLUE, '...'), ('kd', 'Delay fitted from the pretest\'s own data', ORANGE, '///')]
fig, ax = plt.subplots(figsize=(7.4, 3.9)); x = np.arange(len(ORDER)); w = 0.26
for k, (arm, name, col, hatch) in enumerate(ARMS):
    v = [[r[arm]['d_b3'] for r in J[c] if r.get(arm) and r[arm].get('d_b3') is not None] for c, _ in ORDER]
    med = [np.median(a) for a in v]; q1 = [np.percentile(a, 25) for a in v]; q3 = [np.percentile(a, 75) for a in v]
    ax.bar(x + (k - 1) * w, med, w - 0.03, color=col, hatch=hatch, edgecolor='white', linewidth=0.6, label=name)
    ax.errorbar(x + (k - 1) * w, med, yerr=[np.subtract(med, q1), np.subtract(q3, med)], fmt='none', ecolor=TEXT, elinewidth=0.9, capsize=2.5)
ax.axhline(0, color=TEXT, linewidth=0.9); ax.set_xticks(x); ax.set_xticklabels([l for _, l in ORDER])
ax.set_ylabel('Change in control error against\nthe ladder, dB (below zero is better)'); ax.set_xlabel('System (shakers x control gauges) and size of the level effects')
clean(ax); ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.32), ncol=1); save(fig, 'fig_timing')
