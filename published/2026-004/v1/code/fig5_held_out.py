"""Figure 5: runs on the held-out 4 x 4 structures that pass, by law, tier and reading.

Reads ../data/fig5_held_out_runs.csv only. Writes ../figures/fig5_held_out.png.
Copyright 2026 Kevin Cross. MIT license.
"""
import csv
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, '..', 'data', 'fig5_held_out_runs.csv'), newline='') as f:
    rows = list(csv.DictReader(f))
LAWS = ['frozen', 'followed', 'hold rule', 'coupled corrector', 'physics model',
        'network as the law\'s model', 'network sets the ceiling']
LABEL = {'frozen': 'frozen law (baseline)', 'followed': 'followed family, 12 % ceiling (baseline)',
         'hold rule': 'hold rule (baseline)', 'coupled corrector': 'coupled corrector',
         'physics model': 'physics model with rehearsal',
         'network as the law\'s model': 'network as the law\'s model',
         'network sets the ceiling': 'network sets the ceiling'}
READ = [('strict', 'pass', 'o', '#0072B2', 'all seven criteria'),
        ('ends_at_full_level_in_tolerance', 'yes', 's', '#D55E00', 'ends at full level inside 3 dB'),
        ('never_over_full_level_target_by_3db', 'yes', '^', '#009E73', 'never 3 dB over the full-level target')]
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True, gridspec_kw=dict(wspace=0.06))
for ax, (tier, title) in zip(axes, (('realistic', '(a) Realistic tier: 3 structures x 2 noise levels'),
                                    ('stress', '(b) Stress tier: 5 structures x 2 noise levels'))):
    for k, (col, ok, m, c, lab) in enumerate(READ):
        xs, ys = [], []
        for i, law in enumerate(LAWS):
            sel = [r for r in rows if r['law'] == law and r['tier'] == tier]
            xs.append(sum(r[col] == ok for r in sel))
            ys.append(len(LAWS) - 1 - i + (k - 1) * 0.22)
            total = len(sel)
        ax.plot(xs, ys, m, color=c, mfc='white' if k else c, mew=1.6, ms=7.5, ls='none', label=lab)
    ax.set_xlim(-0.4, total + 0.4)
    ax.set_xticks(range(0, total + 1))
    ax.set_xlabel('Runs that pass, of %d' % total, fontsize=8.5)
    ax.set_title(title, fontsize=9.5, loc='left')
    ax.grid(True, axis='x', alpha=0.3)
    for y in range(len(LAWS)):
        ax.axhline(y + 0.5, color='#d0d0d0', lw=0.6)
    ax.tick_params(labelsize=7.5)
axes[0].set_yticks(range(len(LAWS)))
axes[0].set_yticklabels([LABEL[l] for l in reversed(LAWS)], fontsize=8)
axes[0].set_ylim(-0.6, len(LAWS) - 0.4)
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc='upper center', bbox_to_anchor=(0.55, -0.0), ncol=3, fontsize=8, frameon=False)
out = os.path.join(HERE, '..', 'figures', 'fig5_held_out.png')
fig.savefig(out, dpi=150, bbox_inches='tight')
print('wrote', out)
