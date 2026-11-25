"""Figure: how hard the pretest drives the structure at full level. Drive of the pretest's full-level loop against
the minimum-drive test's first full-level loop on the ladder, dB (rms over shakers), per cell: median and quartiles.
Two pretests: on the per-line pseudo-inverse law, and on the test's own minimum-drive law.
Data: ../data/e25_cells.json (experiments/runner/e25_analyze.py)."""
import json, os
import numpy as np
from style import *
C = json.load(open(os.path.join(DATA, 'e25_cells.json')))
ORDER = [('6x6|linear', '6 x 6\nlinear'), ('6x6|realistic', '6 x 6\nrealistic'), ('6x6|strong', '6 x 6\nstrong'),
         ('12x12|linear', '12 x 12\nlinear'), ('12x12|realistic', '12 x 12\nrealistic'), ('12x12|strong', '12 x 12\nstrong')]
fig, ax = plt.subplots(figsize=(7.4, 3.6)); x = np.arange(len(ORDER)); w = 0.38
for off, key, col, hatch, name in ((-w / 2, 'drive_pinv', BLUE, None, 'Pretest on the per-line pseudo-inverse law'), (w / 2, 'drive_md', ORANGE, '///', 'Pretest on the minimum-drive law')):
    v = [C[c][key] for c, _ in ORDER]; med = [np.median(a) for a in v]; q1 = [np.percentile(a, 25) for a in v]; q3 = [np.percentile(a, 75) for a in v]
    ax.bar(x + off, med, w - 0.04, color=col, hatch=hatch, edgecolor='white', linewidth=0.6, label=name)
    ax.errorbar(x + off, med, yerr=[np.subtract(med, q1), np.subtract(q3, med)], fmt='none', ecolor=TEXT, elinewidth=0.9, capsize=2.5)
ax.axhline(0, color=TEXT, linewidth=0.9); ax.set_xticks(x); ax.set_xticklabels([l for _, l in ORDER])
ax.set_ylabel('Pretest drive at full level against\nthe test\'s first full-level loop, dB'); ax.set_xlabel('System (shakers x control gauges) and size of the level effects')
clean(ax); ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.22), ncol=2); save(fig, 'fig_pretest_drive')
