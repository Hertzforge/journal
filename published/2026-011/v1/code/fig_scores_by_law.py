"""Each law at its defaults on the linear structures: the error at the control gauges, at the
held-out gauges and in stress, for the systems with more control gauges than shakers and the systems
with as many shakers as control gauges. Median over structures 0 to 9, with a line from the first to
the third quartile. From ../data/study_scores.csv (written by law_results.py).

Copyright 2026 Kevin Cross and Norman Hunter. MIT license.
"""
from style import GROUPS, law_bars, legend_laws, plt, rows, save

LINES = (('control', 'Control gauges, dB'), ('held_out', 'Held-out gauges, dB'), ('stress', 'Stress, dB'))
t = rows('study_scores.csv')
fig, axes = plt.subplots(len(LINES), 2, figsize=(10, 7.4), sharex=True, sharey='row')
for row, (key, label) in zip(axes, LINES):
    for ax, (grp, title) in zip(row, GROUPS):
        law_bars(ax, t, key, systems=grp, structure_kind='none', structures='all')
        if key == LINES[0][0]:
            ax.set_title(title, fontsize=9)
    row[0].set_ylabel('Error at the ' + label[0].lower() + label[1:] + '\n(lower is better)' if key != 'stress'
                      else 'Error in stress, dB\n(lower is better)')
legend_laws(axes[0][1], loc='upper right')
fig.tight_layout()
save(fig, 'fig_scores_by_law.png')
