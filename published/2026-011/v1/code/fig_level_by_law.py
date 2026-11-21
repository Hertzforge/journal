"""Each law's level at its defaults on the linear structures: the mean error over the control gauges
and bands, with its sign. Above zero the test ran high, below zero it ran low. Median over structures
0 to 9, with a line from the first to the third quartile. From ../data/study_scores.csv.

Copyright 2026 Kevin Cross and Norman Hunter. MIT license.
"""
from style import GROUPS, TEXT, law_bars, legend_laws, plt, rows, save

t = rows('study_scores.csv')
fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True)
for ax, (grp, title) in zip(axes, GROUPS):
    law_bars(ax, t, 'level', systems=grp, structure_kind='none', structures='all')
    ax.axhline(0, color=TEXT, lw=0.8)
    ax.set_title(title, fontsize=9)
axes[0].set_ylabel('Level error, dB\n(zero is on level; above zero is high)')
legend_laws(axes[1], loc='best')
fig.tight_layout()
save(fig, 'fig_level_by_law.png')
