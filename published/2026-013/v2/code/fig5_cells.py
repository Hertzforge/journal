"""Figure 5: how hard each cell of the matrix is: the share of runs whose last full-level pulse is
inside Method 516.8's SRS tolerance, pooled over the five laws, on the study's structures (bars)
and the held-back structures (diamonds), with the best single law's share (tick).
Copyright 2026 Kevin Cross. MIT license."""
import matplotlib.pyplot as plt

from style import BLUE, ORANGE, TEXT, SYSTEM, TIER, TIER_ORDER, rows, num, save, percent_axis

table = [r for r in rows('pooled_cells.csv') if r['kind'] == 'all' and r['cls'] != 'all']
cell = {(r['set'], r['cls'], r['tier']): r for r in table}
layout = [('12x3', 0, 0), ('24x12', 0, 1), ('12x12', 0, 2), ('12x6', 1, 0), ('6x6', 1, 1)]
fig = plt.figure(figsize=(10.5, 6.0))
grid = fig.add_gridspec(2, 6)
for cls, row, col in layout:
    ax = fig.add_subplot(grid[row, col * 2:col * 2 + 2] if row == 0 else
                         grid[row, col * 3:col * 3 + 3])
    tiers = [t for t in TIER_ORDER if ('study', cls, t) in cell]
    for i, tier in enumerate(tiers):
        s = cell[('study', cls, tier)]
        a = cell[('audit', cls, tier)]
        ax.bar(i, num(s['ends']), color=BLUE, alpha=0.75, width=0.6)
        ax.plot(i, num(a['ends']), marker='D', color=ORANGE, ms=5, ls='none')
        ax.plot([i - 0.3, i + 0.3], [num(s['ends_best_law'])] * 2, color=TEXT, lw=1.5)
    ax.set_xticks(range(len(tiers)))
    ax.set_xticklabels([TIER[t] for t in tiers], fontsize=7)
    ax.set_ylim(0, 1.05)
    ax.set_title(f'{SYSTEM[cls]} system', loc='left', fontsize=9)
    if col == 0:
        ax.set_ylabel('Runs ending in tolerance (%)')
    percent_axis(ax)
handles = [plt.Rectangle((0, 0), 1, 1, color=BLUE, alpha=0.75),
           plt.Line2D([], [], marker='D', color=ORANGE, ls='none'),
           plt.Line2D([], [], color=TEXT, lw=1.5)]
fig.legend(handles, ['study, pooled over five laws',
                     'held-back structures, pooled', 'best single law, study'],
           loc='lower center', ncol=3, fontsize=8, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.04, 1, 1))
save(fig, 'fig5_cells')
