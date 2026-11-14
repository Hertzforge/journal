"""Figure 5: control error against element stress error, by rig, random and shock.

Reads ../data/fig5_exact_fit.csv only. Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'data', 'fig5_exact_fit.csv'))))

# Okabe-Ito colors; every class also has its own marker and fill.
STYLE = {
    'equal': dict(marker='s', color='#D55E00', mfc='#D55E00', label='As many shakers as controls'),
    'more_shakers': dict(marker='^', color='#009E73', mfc='white', label='More shakers than controls (12 x 6)'),
    'fewer_shakers': dict(marker='o', color='#0072B2', mfc='white', label='Fewer shakers than controls'),
}
fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
for ax, study, xlab, title in (
        (axes[0], 'random', 'Control error, 1/3-octave bands, dB RMS', 'Random, line law (inverse)'),
        (axes[1], 'shock', 'Control error, shock spectra, dB RMS', 'Shock, waveform control (inverse)')):
    for cls, st in STYLE.items():
        pts = [r for r in rows if r['study'] == study and r['rig_class'] == cls]
        x = [max(float(r['control_error_db']), 0.01) for r in pts]
        y = [float(r['stress_bias_db']) for r in pts]
        ax.plot(x, y, linestyle='none', marker=st['marker'], color=st['color'], mfc=st['mfc'],
                ms=5, alpha=0.75, label=st['label'])
    ax.axhline(0, color='0.3', lw=0.8, ls='--')
    ax.set_xscale('log')
    ax.set_xlabel(xlab + ' (log scale)')
    ax.set_title(title, fontsize=10)
    ax.grid(True, which='both', alpha=0.25)
axes[0].set_ylabel('Element stress error, mean over elements (dB)\n(positive = over-test)')
axes[0].legend(fontsize=8, loc='upper right')
fig.tight_layout()
out = os.path.join(HERE, '..', 'figures', 'fig5_exact_fit.png')
fig.savefig(out, dpi=150)
print('wrote', out)
