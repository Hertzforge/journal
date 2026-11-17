"""Figure: how the member's mode and a softening mode of the article change with level, by the problem's own rule.

Reads ../data/fig_level_rule.csv (written by stage2_known.py from the 6 x 12 problems of seed 0, both tiers). The
horizontal axis is r, a mode's amplitude over its reference amplitude, the quantity the rule is written in.
Needs NumPy and matplotlib. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'data', 'fig_level_rule.csv'))))
STYLE = {('member', 'realistic'): dict(color='#D55E00', ls='-', marker='o'),
         ('member', 'strong'): dict(color='#D55E00', ls='--', marker='s'),
         ('softening', 'realistic'): dict(color='#0072B2', ls='-', marker='^'),
         ('softening', 'strong'): dict(color='#0072B2', ls='--', marker='D')}
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
for (curve, tier), st in STYLE.items():
    rr = [r for r in rows if r['curve'] == curve and r['tier'] == tier]
    if not rr:
        continue
    r = np.array([float(x['r']) for x in rr])
    who = (f'member mode ({float(rr[0]["f0_hz"]):.0f} Hz)' if curve == 'member'
           else f'article mode {rr[0]["mode"]} ({float(rr[0]["f0_hz"]):.0f} Hz)')
    lab = f'{who}, {tier}'
    axes[0].plot(r, [float(x['change_pct']) for x in rr], markevery=20, mfc='white', ms=5, lw=1.4, label=lab, **st)
    axes[1].plot(r, [float(x['damping_factor']) for x in rr], markevery=20, mfc='white', ms=5, lw=1.4, label=lab, **st)
for ax in axes:
    ax.axvline(1, color='black', lw=0.6, ls=':')
    ax.set_xlim(0, 2.5)
    ax.set_xlabel('r: the mode\'s amplitude over its reference amplitude')
    ax.grid(True, alpha=0.3)
axes[0].axhline(0, color='black', lw=0.8)
axes[0].set_ylabel('Frequency change (%)')
axes[0].set_title('(a) Frequency: the member rises, the article falls', fontsize=10)
axes[1].set_ylabel('Damping over its small-signal value')
axes[1].set_title('(b) Damping: both rise, then stop at the cap', fontsize=10)
axes[0].legend(fontsize=8, loc='upper left')
fig.tight_layout()
out = os.path.join(HERE, '..', 'figures', 'fig_level_rule.png')
fig.savefig(out, dpi=150)
print('wrote', out)
