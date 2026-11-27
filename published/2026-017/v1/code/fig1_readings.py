"""Figure 1: each law on each test it takes, by tier, under the three readings of the claims rule:
the share of runs completed, the median IEC check-point share and the median worst over-test.
Copyright 2026 Kevin Cross. MIT license."""
import numpy as np
import matplotlib.pyplot as plt

from style import JOBS, TIERS, TIER_STYLE, job_label, rows, num, save, percent_axis

table = {(r['version'], r['law'], r['test'], r['tier']): r for r in rows('law_readings.csv')}
PANELS = [('share_completed', 'Runs completed (%)', True),
          ('iec_share_median', 'IEC check-point share,\nmedian (%)', True),
          ('worst_over_db_median', 'Worst over-test,\nmedian (dB)', False)]
fig, axes = plt.subplots(3, 1, figsize=(11, 7.6), sharex=True)
w = 0.27
x0 = np.arange(len(JOBS))
for ax, (key, label, share) in zip(axes, PANELS):
    for k, tier in enumerate(TIERS):
        color, hatch = TIER_STYLE[tier]
        vals = [num(table[j + (tier,)][key]) if j + (tier,) in table else np.nan for j in JOBS]
        ax.bar(x0 + (k - 1) * w, vals, w, color=color, alpha=0.85, hatch=hatch, edgecolor='white',
               label=tier)
    ax.set_ylabel(label)
    if share:
        ax.set_ylim(0, 1.05)
        percent_axis(ax)
    else:
        ax.axhline(3, color='#10161d', lw=0.8, ls='--')
        ax.axhline(6, color='#10161d', lw=0.8, ls=':')
    for edge in (11.5,):
        ax.axvline(edge, color='#c9d3df', lw=1.2)
axes[0].legend(ncol=3, fontsize=8, loc='upper center', bbox_to_anchor=(0.5, 1.32))
axes[2].text(len(JOBS) - 0.5, 3.4, '3 dB', fontsize=7, ha='right')
axes[2].text(len(JOBS) - 0.5, 6.4, '6 dB', fontsize=7, ha='right')
axes[0].text(5.5, 1.02, 'Hertzforge version', ha='center', fontsize=8)
axes[0].text(15.5, 1.02, 'Python version', ha='center', fontsize=8)
axes[2].set_xticks(x0)
axes[2].set_xticklabels([job_label(*j) for j in JOBS], fontsize=7)
fig.tight_layout()
save(fig, 'fig1_readings')
