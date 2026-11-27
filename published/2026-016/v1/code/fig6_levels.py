"""Figure 6: every level claim at the IEC check point: the median, over a cell's structures, of
a law's worst excursion beyond the band, by test. 0 dB or less is inside. Reads data/levels.csv.
Copyright 2026 Kevin Cross. MIT license."""
import random

import matplotlib.pyplot as plt

from style import BLUE, GREEN, MUTED, ORANGE, TEST, TEST_ORDER, TEXT, num, rows, save

levels = [r for r in rows('levels.csv') if r['line'] == 'iec_check_point']
rng = random.Random(0)
look = {'linear': (BLUE, 'o'), 'realistic': (ORANGE, 's'), 'strong': (GREEN, '^')}
fig, ax = plt.subplots(figsize=(8.5, 4.0))
top = 100
for i, test in enumerate(TEST_ORDER):
    for r in levels:
        if r['test'] != test:
            continue
        base = r['kind'].split('_')[0]
        color, marker = look[base]
        x = i + (-0.17 if r['version'] == 'hertzforge' else 0.17) + rng.uniform(-0.1, 0.1)
        y = num(r['median_db'])
        face = color if r['kind'] == base else 'none'
        if y != y:
            ax.scatter(x, top - 3, marker='x', color=MUTED, s=14, lw=0.8)
            continue
        ax.scatter(x, y, marker=marker, s=14, facecolors=face, edgecolors=color, lw=0.8)
ax.axhline(0, color=TEXT, lw=1)
ax.text(5.45, 1.5, 'inside', fontsize=7, color=TEXT, ha='right')
ax.set_xticks(range(len(TEST_ORDER)), [TEST[t] for t in TEST_ORDER])
ax.set_ylim(-8, top)
ax.set_ylabel('median worst excursion beyond\nthe check-point band, dB')
ax.text(-0.45, top - 3, 'x: median unscored', fontsize=7, color=MUTED, va='center')
handles = [plt.Line2D([], [], color=c, marker=m, ls='', label=k) for k, (c, m) in look.items()]
handles.append(plt.Line2D([], [], color=MUTED, marker='o', mfc='none', ls='', label='one effect only'))
ax.legend(handles=handles, fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=4)
ax.set_title('Hertzforge version left of each test, Python version right', fontsize=8, color=TEXT,
             loc='left')
fig.tight_layout()
save(fig, 'fig6_levels')
