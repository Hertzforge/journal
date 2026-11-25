"""Figure 4: how each run ended, as a share of the runs: inside the tolerance at full level; at
full level and outside it; stopped below full level after the probes; stopped at a probe. Study
(upper bar of each pair) and held-back structures (lower bar). Copyright 2026 Kevin Cross. MIT
license."""
import numpy as np
import matplotlib.pyplot as plt

from style import LAWS, BLUE, PURPLE, YELLOW, RED, rows, num, save, percent_axis

table = {(r['set'], r['law']): r for r in rows('law_misses.csv')}
parts = [('ends in tolerance', BLUE, ''), ('full level, outside tolerance', RED, 'xxx'),
         ('stopped below full level', YELLOW, '...'), ('stopped at a probe', PURPLE, '///')]
fig, ax = plt.subplots(figsize=(9.0, 3.6))
labels, y = [], []
for i, law in enumerate(LAWS):
    for j, which in enumerate(('study', 'audit')):
        r = table[(which, law)]
        n = num(r['runs'])
        probes = num(r['misses_never_past_probes'])
        vals = [num(r['ends_passes']), num(r['misses_at_full_level']),
                num(r['misses_no_full_level']) - probes, probes]
        pos = i * 2.6 + j
        left = 0.0
        for (name, color, hatch), v in zip(parts, vals):
            ax.barh(pos, v / n, left=left, color=color, alpha=0.9 if which == 'study' else 0.55,
                    hatch=hatch, edgecolor='white', linewidth=0,
                    height=0.85, label=name if (i, j) == (0, 0) else None)
            left += v / n
        y.append(pos)
        labels.append(f"{law}, {'study' if which == 'study' else 'held back'}")
ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=8)
ax.invert_yaxis()
ax.set_xlim(0, 1)
ax.set_xlabel('Runs (%)')
percent_axis(ax, 'x')
ax.legend(ncol=4, fontsize=8, loc='upper center', bbox_to_anchor=(0.45, -0.18))
fig.tight_layout()
save(fig, 'fig4_misses')
