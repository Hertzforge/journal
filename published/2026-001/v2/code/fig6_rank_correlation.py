"""Figure 6: rank correlation of each metric with element stress error, on controls and held-out gauges.

Reads ../data/fig6_rank_correlation.csv only. Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'data', 'fig6_rank_correlation.csv'))))

sets = []
for r in rows:
    if (r['case_set'], r['case_set_label'], r['n_cases']) not in sets:
        sets.append((r['case_set'], r['case_set_label'], r['n_cases']))
metrics = []
for r in rows:
    if (r['metric'], r['metric_label']) not in metrics:
        metrics.append((r['metric'], r['metric_label']))
look = {(r['case_set'], r['metric'], r['gauges']): float(r['spearman_rho']) for r in rows}

fig, axes = plt.subplots(1, len(sets), figsize=(11, 4.4), sharey=True)
ypos = list(range(len(metrics)))[::-1]
for ax, (skey, slabel, n) in zip(axes, sets):
    for y, (mkey, _) in zip(ypos, metrics):
        c, h = look[(skey, mkey, 'controls')], look[(skey, mkey, 'held_out')]
        ax.plot([c, h], [y, y], color='0.7', lw=1, zorder=1)
    ax.plot([look[(skey, m, 'controls')] for m, _ in metrics], ypos, 'o', color='#0072B2', ms=7,
            label='Control gauges', zorder=2)
    ax.plot([look[(skey, m, 'held_out')] for m, _ in metrics], ypos, '^', color='#E69F00', mfc='white',
            mew=1.6, ms=8, label='Held-out gauges', zorder=3)
    ax.axvline(0, color='0.3', lw=0.8, ls='--')
    ax.set_xlim(-0.3, 1.0)
    ax.set_title(f'{slabel}\n({n} cases)', fontsize=9)
    ax.set_xlabel('Spearman rank correlation with\nelement stress error (RMS over elements)')
    ax.grid(True, axis='x', alpha=0.3)
axes[0].set_yticks(ypos)
axes[0].set_yticklabels([lab for _, lab in metrics], fontsize=8)
axes[0].legend(fontsize=8, loc='lower right')
fig.tight_layout()
out = os.path.join(HERE, '..', 'figures', 'fig6_rank_correlation.png')
fig.savefig(out, dpi=150)
print('wrote', out)
