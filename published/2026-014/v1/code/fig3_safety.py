"""Figure 3: over-tests. The number of runs, of 1,140 a law on the study's structures, whose
largest exposure against the full-level target was more than 3 dB (a) and more than 6 dB (b),
split by the level of the pulse that made it; diamonds are the held-back structures' counts
scaled to 1,140 runs. Copyright 2026 Kevin Cross. MIT license."""
import numpy as np
import matplotlib.pyplot as plt

from style import LAWS, LAW_STYLE, TEXT, rows, num, save

table = {(r['set'], r['law']): r for r in rows('law_safety.csv')}
fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.4))
x = np.arange(len(LAWS))
for a, key, title in ((ax[0], 'over_3db', '(a) More than 3 dB over'), (ax[1], 'over_6db', '(b) More than 6 dB over')):
    near = np.array([num(table[('study', law)][f'{key}_at_or_near_full']) for law in LAWS])
    total = np.array([num(table[('study', law)][key]) for law in LAWS])
    colors = [LAW_STYLE[law][0] for law in LAWS]
    a.bar(x, near, 0.6, color=colors, label='on a pulse at -3 dB or above')
    a.bar(x, total - near, 0.6, bottom=near, color=colors, alpha=0.35, hatch='///', edgecolor='white',
          label='on a pulse below -3 dB')
    audit = [num(table[('audit', law)][key]) * 1140 / num(table[('audit', law)]['runs']) for law in LAWS]
    a.plot(x, audit, marker='D', ms=4, color=TEXT, ls='none', label='held-back structures, scaled')
    a.set_xticks(x)
    a.set_xticklabels(LAWS)
    a.set_ylabel('Runs of 1,140 (lower is safer)')
    a.set_title(title, loc='left', fontsize=9)
    a.set_ylim(0, 1200)
from style import MUTED  # noqa: E402
ax[0].legend([plt.Rectangle((0, 0), 1, 1, color=MUTED),
              plt.Rectangle((0, 0), 1, 1, facecolor=MUTED, alpha=0.35, hatch='///', edgecolor='white'),
              plt.Line2D([], [], marker='D', color=TEXT, ls='none')],
             ['on a pulse at -3 dB or above', 'on a pulse below -3 dB', 'held-back structures, scaled'],
             fontsize=7, loc='upper left')
fig.tight_layout()
save(fig, 'fig3_safety')
