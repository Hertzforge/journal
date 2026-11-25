"""Figure 6: the held-back structures against the study's, cell by cell, pooled over the five
laws: (a) the share ending in tolerance, (b) the share never over +3 dB. Each marker is one cell
of the matrix. Copyright 2026 Kevin Cross. MIT license."""
import matplotlib.pyplot as plt

from style import BLUE, ORANGE, MUTED, rows, num, save, percent_axis

table = [r for r in rows('pooled_cells.csv') if r['kind'] == 'all' and r['cls'] != 'all']
cell = {(r['set'], r['cls'], r['tier']): r for r in table}
keys = sorted({(r['cls'], r['tier']) for r in table})
fig, ax = plt.subplots(1, 2, figsize=(7.0, 3.4))
for a, column, title in ((ax[0], 'ends', '(a) Ending in tolerance'),
                         (ax[1], 'exposure', '(b) Never over +3 dB')):
    for cls, tier in keys:
        s, h = num(cell[('study', cls, tier)][column]), num(cell[('audit', cls, tier)][column])
        linear = tier == 'none'
        a.plot(s, h, marker='o' if linear else 's', ms=5, ls='none',
               color=BLUE if linear else ORANGE, alpha=0.8)
    a.plot([0, 1], [0, 1], color=MUTED, lw=0.8, ls='--')
    a.set_xlim(0, 1)
    a.set_ylim(0, 1)
    a.set_aspect('equal')
    a.set_xlabel('Study structures, pooled (%)')
    a.set_ylabel('Held-back structures, pooled (%)')
    percent_axis(a, 'x')
    percent_axis(a, 'y')
    a.set_title(title, loc='left', fontsize=9)
ax[0].legend([plt.Line2D([], [], marker='o', color=BLUE, ls='none'),
              plt.Line2D([], [], marker='s', color=ORANGE, ls='none')],
             ['linear cell', 'cell that changes with level'], fontsize=7, loc='upper left')
fig.tight_layout()
save(fig, 'fig6_audit')
