"""Figure 10: spread of element peak stress among synthesized shots that match one target spectrum.

Reads ../data/fig10_shock_same_spectrum_spread.csv only. Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'data', 'fig10_shock_same_spectrum_spread.csv'))))
rigs = [(6, 6), (12, 12), (3, 12), (6, 12), (3, 24), (6, 24)]
fig, axes = plt.subplots(1, 2, figsize=(10, 3.9))
rng = np.random.default_rng(0)
for ax, col, title, ylab in (
        (axes[0], 'element_peak_stress_sd_median_db', 'Standard deviation among shots',
         'Per-element standard deviation of peak\nstress among 20 shots, median over elements (dB)'),
        (axes[1], 'element_peak_stress_range_median_db', 'Lowest to highest shot',
         'Per-element range of peak stress among\n20 shots, median over elements (dB)')):
    for i, rig in enumerate(rigs):
        v = np.array([float(r[col]) for r in rows if (int(r['shakers']), int(r['controls'])) == rig])
        ax.plot(i + rng.uniform(-0.15, 0.15, v.size), v, 'o', color='#0072B2', mfc='white', ms=4)
        ax.plot(i, v.mean(), 'D', color='#D55E00', ms=8)
    ax.set_xticks(range(len(rigs)))
    ax.set_xticklabels([f'{a} x {b}' for a, b in rigs], fontsize=8)
    ax.set_xlabel('Rig (shakers x controls)')
    ax.set_ylabel(ylab, fontsize=8.5)
    ax.set_title(title, fontsize=10)
    ax.set_ylim(bottom=0)
    ax.grid(True, axis='y', alpha=0.3)
axes[0].plot([], [], 'o', color='#0072B2', mfc='white', label='One case (seed and unit)')
axes[0].plot([], [], 'D', color='#D55E00', label='Mean over cases')
axes[0].legend(fontsize=8, loc='lower right')
fig.tight_layout()
out = os.path.join(HERE, '..', 'figures', 'fig10_shock_same_spectrum_spread.png')
fig.savefig(out, dpi=150)
print('wrote', out)
