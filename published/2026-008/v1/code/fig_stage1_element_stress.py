"""Stage 1 figure: the stress in every beam element against its stress in service, two example problems.

Reads ../data/fig_stage1_element_stress.csv only. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'data', 'fig_stage1_element_stress.csv'))))

SERIES = [('frame-12x6/line', dict(marker='o', color='#0072B2', ls='-'), 'frame-12x6: 6 shakers, 12 control gauges'),
          ('frame-6x6/line', dict(marker='^', color='#D55E00', ls='--'), 'frame-6x6: 6 shakers, 6 control gauges')]

fig, ax = plt.subplots(figsize=(7.5, 5.2))
for pid, st, label in SERIES:
    x = np.sort([float(r['rms_stress_error_db']) for r in rows if r['problem'] == pid])
    share = (np.arange(x.size) + 0.5) / x.size * 100
    ax.plot(x, share, linestyle=st['ls'], lw=1.2, marker=st['marker'], color=st['color'], mfc='white', ms=4.5,
            label=f'{label} (mean {x.mean():+.1f} dB)')
ax.axvline(0, color='black', lw=0.8)
ax.axvspan(-3, 3, color='0.85', zorder=0, label='Within 3 dB of service')
ax.set_xlabel('Element RMS stress on the shakers over its RMS stress in service (dB)')
ax.set_ylabel('Share of elements at or below (%)')
ax.set_ylim(0, 100)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=8, loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=1)
fig.tight_layout()
out = os.path.join(HERE, '..', 'figures', 'fig_stage1_element_stress.png')
fig.savefig(out, dpi=150)
print('wrote', out)
