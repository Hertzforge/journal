"""Figure 9: line control against band control fitted in decibels.

(a) paired stress error difference by rig on twenty seeds; (b) worst control band over-test on the
first shot from a wrong model. Reads ../data/fig9a_line_vs_band_paired.csv and
../data/fig9b_first_shot.csv only. Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'data')
pa = list(csv.DictReader(open(os.path.join(D, 'fig9a_line_vs_band_paired.csv'))))
pb = list(csv.DictReader(open(os.path.join(D, 'fig9b_first_shot.csv'))))

fig = plt.figure(figsize=(11, 4.3))
gs = fig.add_gridspec(1, 3, width_ratios=[1.5, 1, 1])
ax = fig.add_subplot(gs[0])
rigs = sorted({(int(r['shakers']), int(r['controls'])) for r in pa if r['rig_class'] != 'equal'})
rng = np.random.default_rng(0)
for i, (ns, nc) in enumerate(rigs):
    d = np.array([float(r['band_minus_line_db']) for r in pa if (int(r['shakers']), int(r['controls'])) == (ns, nc)])
    ax.plot(i + rng.uniform(-0.18, 0.18, d.size), d, 'o', color='0.55', mfc='white', ms=4)
    ax.plot(i, d.mean(), 'D', color='#0072B2', ms=8)
    ax.annotate(f'{d.mean():+.2f}', (i + 0.22, d.mean()), fontsize=7.5, va='center')
ax.axhline(0, color='0.3', lw=0.8, ls='--')
ax.set_xticks(range(len(rigs)))
ax.set_xticklabels([f'{ns} x {nc}' for ns, nc in rigs], fontsize=8)
ax.set_xlabel('Rig (shakers x controls)')
ax.set_ylabel('Band law minus line law, element stress\nerror RMS (dB; negative = band law better)')
ax.set_title('(a) Converged, true model, twenty seeds', fontsize=9)
ax.plot([], [], 'o', color='0.55', mfc='white', label='One seed')
ax.plot([], [], 'D', color='#0072B2', label='Mean over seeds')
ax.legend(fontsize=7.5, loc='lower left')
ax.grid(True, axis='y', alpha=0.3)

models = [('true', 'True\nmodel,\nconverged'), ('K+1%', 'Freq.\n+1 %,\nfirst shot'),
          ('K+3%', 'Freq.\n+3 %,\nfirst shot'), ('zeta/2', 'Damping\nhalved,\nfirst shot')]
LAWS = {'LINE': dict(marker='o', ls='-', color='#D55E00', mfc='#D55E00', label='Line law'),
        'BAND3': dict(marker='s', ls=':', color='#009E73', mfc='white', label='Band law, fitted in power'),
        'BANDLOG3': dict(marker='^', ls='--', color='#0072B2', mfc='white', label='Band law, fitted in dB')}
for k, (counts, title) in enumerate((('unequal', '(b) Shaker and control counts unequal'),
                                    ('equal', '(c) As many shakers as controls'))):
    axk = fig.add_subplot(gs[k + 1], sharey=fig.axes[1] if k else None)
    for law, st in LAWS.items():
        y = [float(next(r for r in pb if r['law'] == law and r['model'] == m and r['counts'] == counts)
                   ['worst_control_band_over_mean_db']) for m, _ in models]
        axk.plot(range(len(models)), y, marker=st['marker'], ls=st['ls'], color=st['color'],
                 mfc=st['mfc'], mew=1.5, ms=7, label=st['label'])
    axk.set_xticks(range(len(models)))
    axk.set_xticklabels([lab for _, lab in models], fontsize=7)
    axk.set_xlabel('Model the drive was computed from', fontsize=8)
    axk.set_title(title, fontsize=9)
    axk.grid(True, axis='y', alpha=0.3)
    if k == 0:
        axk.set_ylabel('Worst control 1/3-octave band over-test,\nmean over cases (dB)')
        axk.legend(fontsize=7.5, loc='upper left')
fig.tight_layout()
out = os.path.join(HERE, '..', 'figures', 'fig9_line_vs_band.png')
fig.savefig(out, dpi=150)
print('wrote', out)
