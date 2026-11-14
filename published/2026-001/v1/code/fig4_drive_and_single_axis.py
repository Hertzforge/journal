"""Figure 4: (a) the six shaker drive spectra of the example test, and (b) how the single-axis
vertical specification is formed from the four mount spectra.

Seed 0, unit perturbation 3 percent. Reads ../data/model_example_drive.csv and
../data/model_single_axis_z.csv only. Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'data')
drive = [r for r in csv.DictReader(open(os.path.join(D, 'model_example_drive.csv'))) if r['rig'] == '6x12']
sa = list(csv.DictReader(open(os.path.join(D, 'model_single_axis_z.csv'))))

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
STY = [('#0072B2', '-'), ('#D55E00', '--'), ('#009E73', ':'), ('#CC79A7', '-.'), ('#E69F00', (0, (5, 1))),
       ('#000000', (0, (1, 1)))]
ref = max(float(r['drive_psd_relative']) for r in drive)
for k in sorted({int(r['shaker']) for r in drive}):
    sel = [r for r in drive if int(r['shaker']) == k]
    f = np.array([float(r['f_hz']) for r in sel]); g = np.array([float(r['drive_psd_relative']) for r in sel])
    c, ls = STY[(k - 1) % len(STY)]
    a1.semilogx(f, 10 * np.log10(g / ref), color=c, ls=ls, lw=0.9,
                label=f'Shaker {k}: node {sel[0]["node"]}, {sel[0]["axis"]}')
a1.set_xlabel('Frequency (Hz)'); a1.set_ylabel('Force PSD (dB re largest)')
a1.set_title('(a) Drive force spectra, 6 shakers, 12 controls, line law', fontsize=10)
a1.set_ylim(-80, 5); a1.grid(True, which='both', alpha=0.25); a1.legend(fontsize=7, loc='lower left')

mk = ['o', 's', 'D', 'v']
mounts = sorted({r['mount_node'] for r in sa if r['curve'] == 'mount_band'}, key=int)
spec = [r for r in sa if r['curve'] == 'spec']
ref = max(float(r['psd']) for r in spec)
for i, n in enumerate(mounts):
    ln = [r for r in sa if r['curve'] == 'mount_line' and r['mount_node'] == n]
    a2.semilogx([float(r['f_hz']) for r in ln], [10 * np.log10(float(r['psd']) / ref) for r in ln],
                color='0.75', lw=0.5)
    bd = [r for r in sa if r['curve'] == 'mount_band' and r['mount_node'] == n]
    a2.semilogx([float(r['f_hz']) for r in bd], [10 * np.log10(float(r['psd']) / ref) for r in bd],
                mk[i], color='#0072B2', mfc='white', ms=5, label=f'Mount {n}, 1/3-octave band')
a2.semilogx([], [], color='0.75', lw=0.5, label='Mount spectra, line by line')
mm = [r for r in sa if r['curve'] == 'mount_mean']
a2.semilogx([float(r['f_hz']) for r in mm], [10 * np.log10(float(r['psd']) / ref) for r in mm],
            color='#009E73', lw=1.0, ls=':', label='Mean of the four mounts')
a2.semilogx([float(r['f_hz']) for r in spec], [10 * np.log10(float(r['psd']) / ref) for r in spec],
            color='#D55E00', lw=2.2, ls='-', label='Specification: straight-line envelope')
a2.set_xlabel('Frequency (Hz)'); a2.set_ylabel('Vertical acceleration PSD (dB re specification peak)')
a2.set_title('(b) Single-axis vertical specification from the four mounts', fontsize=10)
a2.set_ylim(-60, 5); a2.grid(True, which='both', alpha=0.25); a2.legend(fontsize=7, loc='lower center')
fig.tight_layout()
out = os.path.join(HERE, '..', 'figures', 'fig4_drive_and_single_axis.png')
fig.savefig(out, dpi=150)
print('wrote', out)
