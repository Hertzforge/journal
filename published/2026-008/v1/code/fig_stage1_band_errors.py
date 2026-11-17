"""Stage 1 figure: one-third-octave band errors at the control gauges and at the held-out gauges, two example problems.

Reads ../data/fig_stage1_band_errors.csv only. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'data', 'fig_stage1_band_errors.csv'))))

PANELS = [('frame-12x6/line', '(a) frame-12x6: 6 shakers, 12 control gauges'),
          ('frame-6x6/line', '(b) frame-6x6: 6 shakers, 6 control gauges')]
STYLE = {'control': dict(marker='o', color='#0072B2', label='Control gauge, one band'),
         'held_out': dict(marker='^', color='#D55E00', label='Held-out gauge, one band')}
SHIFT = {'control': 0.97, 'held_out': 1.03}          # the two groups sit side by side in each band

fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
for ax, (pid, title) in zip(axes, PANELS):
    for group in ('control', 'held_out'):
        sel = [r for r in rows if r['problem'] == pid and r['group'] == group]
        f = np.array([float(r['band_centre_hz']) for r in sel]) * SHIFT[group]
        e = np.array([float(r['error_db']) for r in sel])
        st = STYLE[group]
        ax.plot(f, e, linestyle='none', marker=st['marker'], color=st['color'], mfc='white', ms=4.5, alpha=0.8,
                label=st['label'])
    ax.axhline(0, color='black', lw=0.8)
    ax.axhline(6, color='black', lw=1.0, ls=':')
    ax.axhline(-6, color='black', lw=1.0, ls=':')
    ax.set_xscale('log')
    ax.set_xlim(17, 2300)
    ax.set_xticks([20, 50, 100, 200, 500, 1000, 2000])
    ax.set_xticklabels(['20', '50', '100', '200', '500', '1000', '2000'])
    ax.set_xlabel('One-third-octave band centre (Hz)')
    ax.set_title(title, fontsize=10)
    ax.grid(True, which='major', alpha=0.3)
axes[0].set_ylabel('Achieved over target (dB)')
axes[0].plot([], [], color='black', lw=1.0, ls=':', label='6 dB either side of the target')
axes[0].legend(fontsize=8, loc='lower left')
fig.tight_layout()
out = os.path.join(HERE, '..', 'figures', 'fig_stage1_band_errors.png')
fig.savefig(out, dpi=150)
print('wrote', out)
