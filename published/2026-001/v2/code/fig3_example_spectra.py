"""Figure 3: target against achieved acceleration spectra at one control and one held-out gauge.

Seed 0, unit perturbation 3 percent, line law, converged with the true lab frequency response;
two rigs: 6 shakers with 12 controls, and 12 shakers with the same 12 controls.
Reads ../data/model_example_spectra.csv only. Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'data', 'model_example_spectra.csv'))))


def third_octave(f, g):
    """Average a line spectrum into one-third-octave bands (centers 1000 * 2^(k/3) Hz)."""
    k = np.round(3 * np.log2(f / 1000.0)).astype(int)
    u = np.unique(k)
    return 1000 * 2.0 ** (u / 3), np.array([g[k == j].mean() for j in u])


fig, axes = plt.subplots(2, 2, figsize=(11, 6.6), sharex=True, sharey=True)
for i, rig in enumerate(('6x12', '12x12')):
    for j, gauge in enumerate(('control', 'held_out')):
        sel = [r for r in rows if r['rig'] == rig and r['gauge'] == gauge]
        f = np.array([float(r['f_hz']) for r in sel])
        t = np.array([float(r['target_psd']) for r in sel]); a = np.array([float(r['achieved_psd']) for r in sel])
        ref = t.max()
        ax = axes[i, j]
        ax.semilogx(f, 10 * np.log10(t / ref), color='black', lw=0.8, ls='-', label='Target, line by line')
        ax.semilogx(f, 10 * np.log10(a / ref), color='#0072B2', lw=0.8, ls='--', alpha=0.9,
                    label='Achieved, line by line')
        fb, tb = third_octave(f, t); _, ab = third_octave(f, a)
        ax.semilogx(fb, 10 * np.log10(tb / ref), 'o', color='black', mfc='white', ms=5,
                    label='Target, 1/3-octave band')
        ax.semilogx(fb, 10 * np.log10(ab / ref), '^', color='#D55E00', ms=5,
                    label='Achieved, 1/3-octave band')
        e = 10 * np.log10(ab / tb)
        ns, nc = rig.split('x')
        where = 'control gauge' if gauge == 'control' else 'held-out gauge'
        ax.set_title(f'{ns} shakers, {nc} controls: {where} {sel[0]["node"]}{sel[0]["axis"]}\n'
                     f'band error: RMS {np.sqrt(np.mean(e ** 2)):.1f} dB, worst {e[np.argmax(np.abs(e))]:+.1f} dB',
                     fontsize=9)
        ax.grid(True, which='both', alpha=0.25)
        ax.set_ylim(-75, 15)
for ax in axes[1]:
    ax.set_xlabel('Frequency (Hz)')
for ax in axes[:, 0]:
    ax.set_ylabel('Acceleration PSD (dB re target peak)')
axes[0, 0].legend(fontsize=8, loc='lower left')
fig.tight_layout()
out = os.path.join(HERE, '..', 'figures', 'fig3_example_spectra.png')
fig.savefig(out, dpi=150)
print('wrote', out)
