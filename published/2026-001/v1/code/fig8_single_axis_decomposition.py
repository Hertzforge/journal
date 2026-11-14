"""Figure 8: where the single-axis over-test comes from (decomposed on one rigid base).

Reads ../data/fig8_single_axis_decomposition.csv only. Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'data', 'fig8_single_axis_decomposition.csv'))))
inputs = []
for r in rows:
    if (r['base_input'], r['base_input_label']) not in inputs:
        inputs.append((r['base_input'], r['base_input_label']))

fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6), sharey=True)
ypos = list(range(len(inputs)))[::-1]
for ax, study, title in ((axes[0], 'random', 'Random: element RMS stress'),
                         (axes[1], 'shock', 'Shock: element peak stress')):
    for y, (key, _) in zip(ypos, inputs):
        sel = [r for r in rows if r['study'] == study and r['base_input'] == key]
        b = np.array([float(r['stress_bias_db']) for r in sel])
        p5 = np.array([float(r['stress_p5_db']) for r in sel])
        ax.plot(b, [y + 0.12] * b.size, '|', color='#0072B2', alpha=0.5, ms=7)
        ax.plot([p5.mean(), b.mean()], [y, y], color='0.6', lw=1)
        ax.plot(b.mean(), y, 'o', color='#0072B2', ms=8)
        ax.plot(p5.mean(), y, 'v', color='#D55E00', mfc='white', mew=1.5, ms=8)
        ax.annotate(f'{b.mean():+.2f}', (b.mean(), y - 0.32), fontsize=7.5, ha='center')
    ax.axvline(0, color='0.3', lw=0.8, ls='--')
    ax.set_title(title, fontsize=10)
    ax.set_xlabel('Stress error, lab against service (dB)')
    ax.grid(True, axis='x', alpha=0.3)
axes[0].set_yticks(ypos)
axes[0].set_yticklabels([lab for _, lab in inputs], fontsize=8)
axes[0].plot([], [], 'o', color='#0072B2', label='Mean over elements (average over seeds)')
axes[0].plot([], [], 'v', color='#D55E00', mfc='white', label='5th percentile of elements')
axes[0].plot([], [], '|', color='#0072B2', label='Mean, one seed')
fig.legend(fontsize=8, loc='lower center', ncol=3, frameon=False)
fig.tight_layout(rect=(0, 0.07, 1, 1))
out = os.path.join(HERE, '..', 'figures', 'fig8_single_axis_decomposition.png')
fig.savefig(out, dpi=150)
print('wrote', out)
