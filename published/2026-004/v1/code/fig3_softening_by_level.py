"""Figure 3: how far each simulated structure softens, by test level.

Reads ../data/fig3_softening_by_level.csv only. Writes ../figures/fig3_softening_by_level.png.
Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, '..', 'data', 'fig3_softening_by_level.csv'), newline='') as f:
    rows = list(csv.DictReader(f))
STYLE = {
    'moderate': ('#0072B2', '--', 'o', 'development: moderate (first mode)'),
    'severe': ('#D55E00', '-', 's', 'development: severe (first mode)'),
    'non-saturating': ('#CC79A7', '-.', '^', 'development: non-saturating (first mode)'),
    'held-out moderate joints': ('#009E73', ':', 'D', 'held out: realistic joints (largest of nine modes)'),
    'held-out low preload': ('#000000', (0, (6, 2, 1, 2)), 'x', 'held out: low preload (largest of nine modes)'),
}
fig, ax = plt.subplots(figsize=(8.2, 4.8))
ax.axhspan(0.1, 4.0, color='#d9d9d9', zorder=0)
ax.axhspan(4.0, 10.0, facecolor='none', edgecolor='#9a9a9a', hatch='//', lw=0, zorder=0)
ax.text(-19.5, 2.0, 'solid gray: well-tightened bolted joints, measured (about 0.1 to 4 %)', fontsize=7.2,
        va='center', color='#3b3b3b')
ax.text(-41.5, 9.4, 'hatched: loose or friction joints under shaker drive, measured (up to about 10 %)',
        fontsize=7.2, va='center', color='#3b3b3b')
for name, (c, ls, m, lab) in STYLE.items():
    pts = sorted((float(r['level_db']), float(r['largest_drop_percent'])) for r in rows if r['structure'] == name)
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=c, ls=ls, marker=m, mfc='white', mew=1.4,
            ms=6, lw=1.6, label=lab)
for x, t in ((-40, 'probes'), (-34, ''), (-12, 'first ladder level'), (0, 'full level')):
    ax.axvline(x, color='#6b6b6b', lw=0.8, ls=(0, (1, 2)))
    if t:
        ax.text(x + 0.4, 15.4, t, fontsize=7.5, color='#3b3b3b', rotation=90, va='top')
ax.set_xlabel('Test level (dB re full-level target)', fontsize=8.5)
ax.set_ylabel('Frequency drop (%)', fontsize=8.5)
ax.set_xlim(-42, 1.5)
ax.set_ylim(0, 16)
ax.tick_params(labelsize=7.5)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=7.5, loc='upper left', bbox_to_anchor=(0.08, 0.99), frameon=True, framealpha=0.95)
out = os.path.join(HERE, '..', 'figures', 'fig3_softening_by_level.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
