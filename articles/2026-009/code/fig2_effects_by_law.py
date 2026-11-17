"""Figure 2: the change in each law's stress score from the linear structure, at the strong size, with
both effects, with the softening joints only and with the hardening member only, on the system with six
shakers and twelve control gauges and the system with six of each. Median over the ten structures run
both ways, with the quartiles. A result of the study, from ../data/study_single_effects.csv (written by
study_results.py).

Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
from style import BLUE, ORANGE, PURPLE, TEXT, plt, rows, save

LAWS = ['pinv_closed', 'pinv_open', 'shape_svd', 'buzz_match', 'min_drive', 'band_average']
EFFECTS = [('both', 'Both effects', BLUE, 'o', '-'), ('softening only', 'Softening joints only', ORANGE, 's', '--'),
           ('hardening only', 'Hardening member only', PURPLE, 'D', ':')]
t = [r for r in rows('study_single_effects.csv') if r['structures'] == 'all' and r['size'] == 'strong']
fig, axes = plt.subplots(1, 2, figsize=(10, 3.9), sharey=True)
for ax, rig, title in ((axes[0], '6x12', '6 shakers, 12 control gauges'), (axes[1], '6x6', '6 shakers, 6 control gauges')):
    ax.axhline(0, color=TEXT, lw=0.8)
    ax.axhspan(-0.2, 0.2, color='#e2e8ef', lw=0)
    for k, (eff, label, c, m, ls) in enumerate(EFFECTS):
        for i, law in enumerate(LAWS):
            r = [x for x in t if x['rig'] == rig and x['effects'] == eff and x['law'] == law][0]
            x = i + (k - 1) * 0.22
            med, lo, hi = float(r['stress_median']), float(r['stress_q1']), float(r['stress_q3'])
            ax.plot([x, x], [lo, hi], color=c, ls=ls, lw=1.3)
            ax.plot([x], [med], color=c, marker=m, ms=6, mfc='white' if k else c, ls='none', label=label if i == 0 else None)
    ax.set_xticks(range(len(LAWS)))
    ax.set_xticklabels(LAWS, rotation=30, ha='right', fontsize=8)
    ax.set_title(title, fontsize=9)
axes[0].set_ylabel('Change in stress error from the\nlinear structure, dB (strong size)')
axes[0].legend(fontsize=7.5, loc='upper left')
fig.tight_layout()
save(fig, 'fig2_effects_by_law.png')
