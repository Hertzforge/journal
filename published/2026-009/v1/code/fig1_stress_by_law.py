"""Figure 1: each law's stress score at its defaults, on the linear structure and at the two sizes of
stage 2, for the systems with more control gauges than shakers and the systems with as many shakers as
control gauges. Median over the 20 structures, with the quartiles. A result of the study, from
../data/study_scores.csv (written by study_results.py).

Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
from style import BLUE, GREEN, ORANGE, plt, rows, save

LAWS = ['pinv_closed', 'pinv_open', 'shape_svd', 'buzz_match', 'min_drive', 'band_average']
STAGES = [('none', 'Stage 1, linear', BLUE, 'o', '-'), ('realistic', 'Stage 2, realistic size', GREEN, 's', '--'),
          ('strong', 'Stage 2, strong size', ORANGE, '^', ':')]
t = [r for r in rows('study_scores.csv') if r['structures'] == 'all']
fig, axes = plt.subplots(1, 2, figsize=(10, 3.9), sharey=True)
for ax, grp, title in ((axes[0], 'more_controls', 'More control gauges than shakers\n(3 x 12, 6 x 12, 12 x 24)'),
                       (axes[1], 'equal', 'As many shakers as control gauges\n(6 x 6, 12 x 12)')):
    for k, (v, label, c, m, ls) in enumerate(STAGES):
        xs, med, lo, hi = [], [], [], []
        for i, law in enumerate(LAWS):
            r = [x for x in t if x['rigs'] == grp and x['structure'] == v and x['law'] == law][0]
            xs.append(i + (k - 1) * 0.22)
            med.append(float(r['stress_db'])); lo.append(float(r['stress_q1'])); hi.append(float(r['stress_q3']))
        ax.plot(xs, med, color=c, marker=m, ms=6, mfc='white' if k else c, ls='none', label=label)
        for x, a, b in zip(xs, lo, hi):
            ax.plot([x, x], [a, b], color=c, ls=ls, lw=1.2)
    ax.set_xticks(range(len(LAWS)))
    ax.set_xticklabels(LAWS, rotation=30, ha='right', fontsize=8)
    ax.set_title(title, fontsize=9)
axes[0].set_ylabel('Stress error, dB (RMS over the elements of\nthe error in RMS stress against service)')
axes[0].legend(fontsize=7.5, loc='upper left')
fig.tight_layout()
save(fig, 'fig1_stress_by_law.png')
