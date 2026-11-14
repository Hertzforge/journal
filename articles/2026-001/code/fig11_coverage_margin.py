"""Figure 11: the coverage margin set by rule P against the margin that truly covers 95 percent of elements.

Reads ../data/fig11_coverage_margin.csv only. Copyright 2026 Kevin Cross and Brandon Zwink. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rows = [r for r in csv.DictReader(open(os.path.join(HERE, '..', 'data', 'fig11_coverage_margin.csv')))
        if r['rig_class'] != 'equal']
LAWS = {'LINE': dict(marker='o', color='#D55E00', mfc='white', label='Line law'),
        'BANDLOG3': dict(marker='^', color='#0072B2', mfc='white', label='Band law, fitted in dB')}
fig, ax = plt.subplots(figsize=(5.6, 5.2))
for law, st in LAWS.items():
    t = np.array([float(r['truth_cover95_margin_db']) for r in rows if r['law'] == law])
    p = np.array([float(r['rule_p_margin_db']) for r in rows if r['law'] == law])
    ax.plot(t, p, linestyle='none', marker=st['marker'], color=st['color'], mfc=st['mfc'], ms=5, alpha=0.8,
            label=f"{st['label']}: mean {p.mean():.1f} against {t.mean():.1f} dB")
allv = [float(r[k]) for r in rows for k in ('truth_cover95_margin_db', 'rule_p_margin_db')]
lo, hi = np.floor(min(allv)) - 1, np.ceil(max(allv)) + 1
x = np.array([lo, hi])
ax.plot(x, x, color='black', lw=1, ls='-', label='Rule equals truth')
ax.plot(x, x + 2, color='0.4', lw=0.8, ls=':', label='2 dB either side')
ax.plot(x, x - 2, color='0.4', lw=0.8, ls=':')
ax.set_xlim(lo, hi)
ax.set_ylim(lo, hi)
ax.set_aspect('equal')
ax.set_xlabel('Level raise that leaves 5 % of elements under-tested (dB)\n(needs the stress truth)')
ax.set_ylabel('Level raise set by rule P (dB)\n(10th percentile of held-out band errors at -3 dB)')
ax.set_title('One test per point; shaker and control counts unequal', fontsize=9)
ax.legend(fontsize=7.5, loc='upper left')
ax.grid(True, alpha=0.3)
fig.tight_layout()
out = os.path.join(HERE, '..', 'figures', 'fig11_coverage_margin.png')
fig.savefig(out, dpi=150)
print('wrote', out)
