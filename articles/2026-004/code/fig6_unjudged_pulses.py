"""Figure 6: every full-level pulse on the 32 % spring at measurement noise 1e-3, seeds 11 to 15.

Reads ../data/fig6_full_level_pulses.csv only. Writes ../figures/fig6_unjudged_pulses.png.
Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, '..', 'data', 'fig6_full_level_pulses.csv'), newline='') as f:
    rows = list(csv.DictReader(f))
LAWS = [('coupled corrector', '(a) The coupled corrector'),
        ('hold rule', '(b) The hold rule'),
        ('followed family, 12 % ceiling', '(c) The followed family with its 12 % ceiling')]
SEEDS = {11: ('#0072B2', '-', 'o'), 12: ('#D55E00', '--', 's'), 13: ('#009E73', ':', '^'),
         14: ('#CC79A7', '-.', 'D'), 15: ('#000000', (0, (6, 2, 1, 2)), 'v')}
fig, axes = plt.subplots(1, 3, figsize=(12, 4.0), sharey=True, gridspec_kw=dict(wspace=0.08))
for ax, (law, title) in zip(axes, LAWS):
    for seed, (c, ls, m) in SEEDS.items():
        pts = [(int(r['full_level_pulse']), float(r['over_db']), r['judged_by_first_third_last'] == 'yes')
               for r in rows if r['law'] == law and int(r['seed']) == seed]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=c, ls=ls, lw=1.2,
                label='seed %d' % seed)
        ax.plot([p[0] for p in pts if p[2]], [p[1] for p in pts if p[2]], m, color=c, ms=7, ls='none')
        ax.plot([p[0] for p in pts if not p[2]], [p[1] for p in pts if not p[2]], m, color=c, mfc='white',
                mew=1.4, ms=7, ls='none')
    ax.axhline(3, color='black', lw=1, ls='--')
    ax.axhline(0, color='#6b6b6b', lw=0.6)
    ax.set_title(title, fontsize=9.5, loc='left')
    ax.set_xlabel('Full-level pulse', fontsize=8.5)
    ax.set_xticks(range(1, 9))
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=7.5)
axes[0].set_ylabel('Over the full-level target (dB)', fontsize=8.5)
axes[0].text(8.2, 3.25, '+3 dB', fontsize=7.5, ha='right')
axes[0].plot([], [], 'o', color='#6b6b6b', ms=7, label='judged when only the first, third\nand last full-level pulses count')
axes[0].plot([], [], 'o', color='#6b6b6b', mfc='white', mew=1.4, ms=7, label='not judged that way')
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, -0.02), ncol=7, fontsize=7.5, frameon=False)
out = os.path.join(HERE, '..', 'figures', 'fig6_unjudged_pulses.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
