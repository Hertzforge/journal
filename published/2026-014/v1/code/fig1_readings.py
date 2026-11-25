"""Figure 1: how often each law works, under each reading, on the study's structures (bars) and
the held-back structures (diamonds). Copyright 2026 Kevin Cross. MIT license."""
import numpy as np
import matplotlib.pyplot as plt

from style import LAWS, LAW_STYLE, LAW_HATCH, TEXT, rows, num, save, percent_axis

table = {(r['set'], r['law']): r for r in rows('law_readings.csv')}
READINGS = [('strict', 'strict\ncriteria'), ('ends', 'ends in\ntolerance'),
            ('ends_with_te_on_srs', 'ends in tolerance,\nwith TE on SRS'),
            ('ends_pm3', 'ends within\n-3/+3 dB'), ('level', 'Level\nreading'),
            ('exposure', 'never over\n+3 dB')]
fig, ax = plt.subplots(figsize=(10.5, 3.6))
w = 0.16
for k, law in enumerate(LAWS):
    color, marker = LAW_STYLE[law]
    x = np.arange(len(READINGS)) + (k - 2) * w
    ax.bar(x, [num(table[('study', law)][key]) for key, _ in READINGS], w, color=color, alpha=0.8,
           hatch=LAW_HATCH[law], edgecolor='white', label=law)
    ax.plot(x, [num(table[('audit', law)][key]) for key, _ in READINGS], marker='D', ms=3.5,
            color=TEXT, ls='none', label='held-back structures' if k == 0 else None)
ax.set_xticks(range(len(READINGS)))
ax.set_xticklabels([label for _, label in READINGS], fontsize=8)
ax.set_ylim(0, 1.05)
ax.set_ylabel('Runs (%, higher is better)')
percent_axis(ax)
ax.legend(ncol=6, fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.2))
fig.tight_layout()
save(fig, 'fig1_readings')
