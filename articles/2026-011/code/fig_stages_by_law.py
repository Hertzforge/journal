"""Each law's stress error at its defaults on the linear structures and on the two sizes of the
level-dependent structures. Median over structures 0 to 9, with a line from the first to the third
quartile. From ../data/study_scores.csv.

Copyright 2026 Kevin Cross and Norman Hunter. MIT license.
"""
from style import BLUE, GREEN, GROUPS, LAWS, ORANGE, one, plt, rows, save

STAGES = [('none', 'Linear', BLUE, 'o', '-'), ('realistic', 'Level-dependent, realistic size', GREEN, 's', '--'),
          ('strong', 'Level-dependent, strong size', ORANGE, '^', ':')]
t = rows('study_scores.csv')
fig, axes = plt.subplots(1, 2, figsize=(10, 3.9), sharey=True)
for ax, (grp, title) in zip(axes, GROUPS):
    for k, (v, label, c, m, ls) in enumerate(STAGES):
        xs, med = [], []
        for i, law in enumerate(LAWS):
            r = one(t, systems=grp, structure_kind=v, law=law, structures='all')
            if r is None:
                continue
            x = i + (k - 1) * 0.22
            xs.append(x); med.append(float(r['stress_db']))
            ax.plot([x, x], [float(r['stress_q1']), float(r['stress_q3'])], color=c, ls=ls, lw=1.2)
        ax.plot(xs, med, color=c, marker=m, ms=6, mfc='white' if k else c, ls='none', label=label)
    ax.axvline(5.5, color='#c9d3df', lw=0.8)
    ax.set_xticks(range(len(LAWS)))
    ax.set_xticklabels(LAWS, rotation=35, ha='right', fontsize=7.5)
    ax.grid(axis='x', visible=False)
    ax.set_title(title, fontsize=9)
axes[0].set_ylabel('Error in stress, dB\n(lower is better)')
axes[0].legend(fontsize=7.5, loc='upper left')
fig.tight_layout()
save(fig, 'fig_stages_by_law.png')
