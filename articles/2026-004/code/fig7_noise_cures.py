"""Figure 7: two attempted cures for the hold rule's failures under heavy measurement noise.

Reads ../data/fig7_noise_cures.csv only. Writes ../figures/fig7_noise_cures.png.
Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, '..', 'data', 'fig7_noise_cures.csv'), newline='') as f:
    rows = list(csv.DictReader(f))
METHODS = [('hold rule as it is (jump from -34 dB to -12 dB)', 'hold rule as it is', '#0072B2', '-', 'o'),
           ('each probe averaged 16 times', 'each probe averaged 16 times', '#D55E00', '--', 's'),
           ('climb in 6 dB steps, unchecked', 'climb in 6 dB steps, unchecked', '#009E73', ':', '^')]
NOISES = [0.0, 0.001, 0.003, 0.01]
PANELS = [('strict', 160, '(a) All seven criteria, of 160'),
          ('ends_at_full_level_in_tolerance', 160, '(b) Ends at full level inside 3 dB, of 160'),
          ('realistic_strict', 40, '(c) Realistic tier, all seven criteria, of 40')]
fig, axes = plt.subplots(1, 3, figsize=(12, 3.9), gridspec_kw=dict(wspace=0.28))
for ax, (col, total, title) in zip(axes, PANELS):
    for key, lab, c, ls, m in METHODS:
        pts = [(NOISES.index(float(r['noise'])), int(r[col])) for r in rows if r['method'] == key]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color=c, ls=ls, marker=m, mfc='white', mew=1.5,
                ms=7, lw=1.6, label=lab)
    ax.set_xticks(range(4))
    ax.set_xticklabels(['0', '1e-3', '3e-3', '1e-2'])
    ax.set_xlabel('Measurement noise (fraction of the full-level rms)', fontsize=8)
    ax.set_title(title, fontsize=9.5, loc='left')
    ax.set_ylim(total * 0.55, total * 1.03)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=7.5)
axes[0].set_ylabel('Runs that pass', fontsize=8.5)
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.5, -0.02), ncol=3, fontsize=8, frameon=False)
out = os.path.join(HERE, '..', 'figures', 'fig7_noise_cures.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
