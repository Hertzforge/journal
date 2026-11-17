"""Section 8 figure: how far softening only, hardening only and both move three lines of the scorecard against the
same law on the linear structure, pooled over the six laws, on the study's ten structures and the audit's ten held-back structures.

Open markers joined by lines: the study's structures; filled markers beside them: the held-back structures.
Reads ../data/effects_by_line.csv only. Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, '..', 'data', 'effects_by_line.csv'))))
LINES = [('control', 'Control\ngauges'), ('heldout', 'Held-out\ngauges'), ('stress', 'Stress')]
SERIES = [('soft', dict(marker='o', color='#0072B2', ls='-'), 'Softening joints only'),
          ('hard', dict(marker='^', color='#D55E00', ls='--'), 'Hardening member only'),
          ('both', dict(marker='s', color='#555555', ls=':'), 'Both')]
PANELS = [('realistic', '6x12', '(a) Realistic size, 6 shakers, 12 control gauges'),
          ('realistic', '6x6', '(b) Realistic size, 6 shakers, 6 control gauges'),
          ('strong', '6x12', '(c) Strong size, 6 shakers, 12 control gauges'),
          ('strong', '6x6', '(d) Strong size, 6 shakers, 6 control gauges')]

fig, axes = plt.subplots(2, 2, figsize=(10, 7.2), sharey=True)
for ax, (tier, rig, title) in zip(axes.flat, PANELS):
    for j, (eff, sty, label) in enumerate(SERIES):
        for which, dx, filled in (('study', 0.0, False), ('held-back', 0.09, True)):
            x, y, lo, hi = [], [], [], []
            for i, (line, _) in enumerate(LINES):
                sel = [r for r in rows if r['tier'] == tier and r['setup'] == rig and r['effect'] == eff
                       and r['line'] == line and r.get('structures', 'study') == which]
                if not sel:
                    continue
                r = sel[0]
                m = float(r['abs_median_db'])
                x.append(i + (j - 1) * 0.26 + dx)
                y.append(m)
                lo.append(m - float(r['abs_q1_db']))
                hi.append(float(r['abs_q3_db']) - m)
            if not x:
                continue
            ax.errorbar(x, y, yerr=[lo, hi], color=sty['color'], marker=sty['marker'],
                        ls=sty['ls'] if not filled else 'none', lw=1.2 if not filled else 0.8, ms=6,
                        mfc=sty['color'] if filled else 'white', capsize=3,
                        label=f'{label}, ' + ('held-back structures' if filled else "study's structures"))
    ax.set_xticks(range(len(LINES)))
    ax.set_xticklabels([l for _, l in LINES])
    ax.set_title(title, fontsize=9)
    ax.grid(True, axis='y', alpha=0.3)
for ax in axes[:, 0]:
    ax.set_ylabel('Change against the linear structure,\nsize regardless of sign (dB)')
h, l = axes[0, 0].get_legend_handles_labels()
fig.legend(h, l, loc='lower center', ncol=3, fontsize=8, frameon=False)
fig.tight_layout(rect=(0, 0.08, 1, 1))
out = os.path.join(HERE, '..', 'figures', 'fig_effects.png')
fig.savefig(out, dpi=150)
print('wrote', out)
