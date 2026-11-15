"""Figure 3: when a three-gauge reference can be played.

Reads ../data/fig3_realizable.csv only. Writes ../figures/fig3_realizable.png.
Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
BLUE, ORANGE, GREEN, PURPLE, GRAY = '#0072B2', '#D55E00', '#009E73', '#CC79A7', '#6b6b6b'

with open(os.path.join(DATA, 'fig3_realizable.csv'), newline='') as f:
    r = list(csv.DictReader(f))

fig, ax = plt.subplots(figsize=(7.2, 4.4))
for g2, color, ls, mk in (('1.0', GRAY, '-', None), ('0.9', BLUE, '--', 's'),
                          ('0.7', ORANGE, '-.', 'o'), ('0.5', GREEN, ':', '^')):
    rr = [x for x in r if float(x['pair_coherence']) == float(g2)]
    ax.plot([float(x['loop_phase_miss_deg']) for x in rr],
            [float(x['smallest_eigenvalue']) for x in rr], color=color, ls=ls, lw=1.8,
            marker=mk, markevery=15, ms=5, label='coherence %s on every pair' % g2)
ax.axhline(0, color='black', lw=1)
ax.axhspan(-1.3, 0, color='#fbe3d3', lw=0)
ax.text(3, -1.2, 'below zero, the reference cannot be played: it asks for negative power\nin some '
        'combination of the three gauges', ha='left', fontsize=7.5)
ax.set_xlim(0, 180)
ax.set_ylim(-1.27, 0.55)
ax.set_xlabel('how far the three phases miss closing the loop, '
              r'$\theta_{12}+\theta_{23}-\theta_{13}$ (deg)', fontsize=8.5)
ax.set_ylabel('smallest eigenvalue of the coherence matrix', fontsize=8.5)
ax.legend(fontsize=7.5, loc='upper right', frameon=False)
ax.tick_params(labelsize=7.5)

out = os.path.join(HERE, '..', 'figures', 'fig3_realizable.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
