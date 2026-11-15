"""Figure 2: the test sequence of one run.

Reads ../data/fig2_test_sequence.csv only. Writes ../figures/fig2_test_sequence.png.
Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
BLUE, ORANGE, GREEN, GRAY = '#0072B2', '#D55E00', '#009E73', '#6b6b6b'
with open(os.path.join(HERE, '..', 'data', 'fig2_test_sequence.csv'), newline='') as f:
    rows = list(csv.DictReader(f))
n = [int(r['pulse']) for r in rows]
lvl = [float(r['level_db']) for r in rows]
over = [float(r['over_db']) for r in rows]
kind = [('full' if float(r['level_db']) == 0.0 else r['kind']) for r in rows]
full = [i for i, k in enumerate(kind) if k == 'full']
judged = {full[0]: 'first full-level pulse', full[2]: 'third full-level pulse'}

fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 6.2), sharex=True,
                             gridspec_kw=dict(height_ratios=[1.6, 1], hspace=0.08))
a1.add_patch(Rectangle((-1.6, -21), 1.2, 2, facecolor='#d9d9d9', edgecolor=GRAY, hatch='...'))
a1.text(-1.0, -22, 'buzz: 102 s\nof random\nexcitation,\nits rms 20 dB\nunder the\nfull-level\ntest\'s rms', ha='center',
        va='top', fontsize=7)
style = {'probe': ('^', BLUE, 'white', 'probe pulse (below the ladder)'),
         'pulse': ('o', ORANGE, ORANGE, 'ladder pulse'),
         'full': ('s', GREEN, GREEN, 'full-level pulse')}
for k, (m, c, fc, lab) in style.items():
    idx = [i for i in range(len(n)) if kind[i] == k]
    a1.plot([n[i] for i in idx], [lvl[i] for i in idx], m, color=c, mfc=fc, mew=1.5, ms=8, ls='none',
            label=lab)
    a2.plot([n[i] for i in idx], [over[i] for i in idx], m, color=c, mfc=fc, mew=1.5, ms=7, ls='none')
a1.plot(n, lvl, color=GRAY, lw=0.8, ls=':', zorder=0)
for (i, t), dx in zip(judged.items(), (-5.5, -2.2)):
    a1.annotate(t, (n[i], lvl[i]), xytext=(n[i] + dx, lvl[i] - (6 if dx < -3 else 17)), fontsize=7.5,
                arrowprops=dict(arrowstyle='->', lw=0.8))
a1.axhline(-12, color=GRAY, lw=0.8, ls='--')
a1.text(15.6, -11.4, 'first ladder level', fontsize=7.5, ha='right', color=GRAY)
a1.set_ylabel('Level (dB re full-level target)', fontsize=8.5)
a1.set_ylim(-44, 4)
a1.legend(fontsize=7.5, loc='lower right', frameon=False)
a1.set_title('One run: the followed family with its ceiling on the severe development structure, no added noise',
             fontsize=9, loc='left')
a2.axhline(3, color='black', lw=1, ls='--')
a2.text(15.6, 3.15, '+3 dB: the tolerance', fontsize=7.5, ha='right')
a2.axhline(0, color=GRAY, lw=0.6)
a2.set_ylabel('Over its own level\'s target (dB)', fontsize=8.5)
a2.set_xlabel('Pulse number (B: the identification buzz)', fontsize=8.5)
a2.set_ylim(-0.5, 4)
a2.set_xticks([-1] + n)
a2.set_xticklabels(['B'] + [str(k) for k in n], fontsize=7.5)
a2.set_xlim(-2, 16)
for a in (a1, a2):
    a.tick_params(labelsize=7.5)
    a.grid(True, axis='y', alpha=0.3)
out = os.path.join(HERE, '..', 'figures', 'fig2_test_sequence.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
