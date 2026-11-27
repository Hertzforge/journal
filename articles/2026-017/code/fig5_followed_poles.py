"""Figure 5: followed_poles against the Python version's matrix, cell by cell. Each point is one cell (system and
structure kind) on one test: the median over its structures of followed_poles' reading less matrix's. Filled
where the claims rule made a claim, by the law it favours. Copyright 2026 Kevin Cross. MIT
license."""
import numpy as np
import matplotlib.pyplot as plt

from style import LAW_STYLE, TIERS, TIER_STYLE, MUTED, rows, num, save, percent_axis

data = rows('law_followed_poles_cells.csv')
TESTS = ['T1', 'T2', 'T5', 'L1']
PANELS = [('completion', 'Completion, followed_poles less matrix\n(points of the test)', True),
          ('iec_share', 'IEC check-point share,\nfollowed_poles less matrix (points)', True),
          ('worst_over_db', 'Worst over-test,\nfollowed_poles less matrix (dB)', False)]
fig, axes = plt.subplots(1, 3, figsize=(11, 3.8))
rng = np.random.default_rng(0)
for ax, (reading, label, share) in zip(axes, PANELS):
    for t, test in enumerate(TESTS):
        for r in [r for r in data if r['test'] == test and r['reading'] == reading]:
            k = TIERS.index(r['tier'])
            xx = t + (k - 1) * 0.22 + rng.uniform(-0.05, 0.05)
            y = num(r['median_followed_poles_less_matrix'])
            color = TIER_STYLE[r['tier']][0]
            if r['claim_favours'] == 'followed_poles':
                ax.plot(xx, y, marker=LAW_STYLE['followed_poles'][1], color=color, ms=6, ls='none')
            elif r['claim_favours'] == 'matrix':
                ax.plot(xx, y, marker=LAW_STYLE['matrix'][1], color=color, ms=6, ls='none',
                        markeredgecolor='black')
            else:
                ax.plot(xx, y, marker='o', mfc='none', color=color, ms=4.5, ls='none')
    ax.axhline(0, color='#10161d', lw=0.8)
    ax.set_xticks(range(len(TESTS)))
    ax.set_xticklabels(TESTS)
    ax.set_ylabel(label, fontsize=8)
    if share:
        percent_axis(ax)
for tier in TIERS:
    axes[0].plot([], [], marker='s', color=TIER_STYLE[tier][0], ls='none', label=tier)
axes[0].plot([], [], marker=LAW_STYLE['followed_poles'][1], color=MUTED, ls='none', label='claim favours followed_poles')
axes[0].plot([], [], marker='o', color=MUTED, markeredgecolor='black', ls='none',
             label='claim favours matrix')
axes[0].plot([], [], marker='o', mfc='none', color=MUTED, ls='none', label='no claim')
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, fontsize=7, loc='lower center', ncol=6)
fig.tight_layout(rect=(0, 0.08, 1, 1))
save(fig, 'fig5_followed_poles')
