"""Figure 7: the floor, a second unit in the same service environment.

Reads ../data/fig7_floor.csv only. Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'data', 'fig7_floor.csv'))))

LABEL = {'control_line_rms': 'Controls,\nline RMS', 'worst_control_line_rms': 'Worst\ncontrol,\nline RMS',
         'control_band_third_octave_rms': 'Controls,\n1/3-octave\nbands', 'element_stress_rms': 'Element\nstress',
         'control_srs_rms': 'Controls,\nSRS', 'element_peak_stress_rms': 'Element\npeak stress'}
STRESS = {'element_stress_rms', 'element_peak_stress_rms'}
panels = [('random', '3', 'Random, units 3 % apart'), ('random', '6', 'Random, units 6 % apart'),
          ('shock', '3', 'Shock, units 3 % apart')]
fig, axes = plt.subplots(1, 3, figsize=(10, 4), sharey=True, gridspec_kw=dict(width_ratios=[4, 4, 2]))
rng = np.random.default_rng(0)
for ax, (study, pct, title) in zip(axes, panels):
    qs = []
    for r in rows:
        if r['study'] == study and r['unit_scatter_percent'] == pct and r['quantity'] not in qs:
            qs.append(r['quantity'])
    for i, q in enumerate(qs):
        v = np.array([float(r['value_db']) for r in rows
                      if r['study'] == study and r['unit_scatter_percent'] == pct and r['quantity'] == q])
        gauge = q not in STRESS
        ax.plot(i + rng.uniform(-0.15, 0.15, v.size), v, linestyle='none',
                marker='o' if gauge else 'D', color='#0072B2' if gauge else '#D55E00',
                mfc='white', ms=4, alpha=0.7)
        ax.plot([i - 0.3, i + 0.3], [v.mean()] * 2, color='black', lw=2.2)
        ax.annotate(f'{v.mean():.2f}', (i + 0.32, v.mean()), fontsize=8, va='center')
    ax.set_xticks(range(len(qs)))
    ax.set_xticklabels([LABEL[q] for q in qs], fontsize=8)
    ax.set_xlim(-0.6, len(qs) - 0.2)
    ax.set_title(title, fontsize=10)
    ax.grid(True, axis='y', alpha=0.3)
axes[0].set_ylabel('Difference between the two units (dB)')
axes[0].plot([], [], 'o', color='#0072B2', mfc='white', label='Gauge metric, one seed and control set')
axes[0].plot([], [], 'D', color='#D55E00', mfc='white', label='Stress truth, one seed (repeated per control set)')
axes[0].plot([], [], color='black', lw=2.2, label='Mean over seeds')
axes[0].legend(fontsize=8, loc='upper right')
fig.tight_layout()
out = os.path.join(HERE, '..', 'figures', 'fig7_floor.png')
fig.savefig(out, dpi=150)
print('wrote', out)
