"""Figure 2: the share of runs ending in tolerance, law by law and cell by cell, on the study's
structures. paired ends in tolerance in no cell and is left out. Copyright 2026 Kevin Cross.
MIT license."""
import matplotlib.pyplot as plt

from style import LAW_STYLE, LAW_HATCH, SYSTEM, TIER, TIER_ORDER, rows, num, save, percent_axis

LAWS = ['followed', 'followed-hold', 'inverse', 'shape']
cell = {(r['law'], r['cls'], r['tier']): r for r in rows('law_cells.csv') if r['set'] == 'study'}
layout = [('12x3', 0, 0), ('24x12', 0, 1), ('12x12', 0, 2), ('12x6', 1, 0), ('6x6', 1, 1)]
fig = plt.figure(figsize=(10.5, 6.0))
grid = fig.add_gridspec(2, 6)
w = 0.2
for cls, row, col in layout:
    ax = fig.add_subplot(grid[row, col * 2:col * 2 + 2] if row == 0 else grid[row, col * 3:col * 3 + 3])
    tiers = [t for t in TIER_ORDER if ('followed', cls, t) in cell]
    for k, law in enumerate(LAWS):
        color, _ = LAW_STYLE[law]
        ax.bar([i + (k - 1.5) * w for i in range(len(tiers))],
               [num(cell[(law, cls, t)]['ends']) for t in tiers], w, color=color, alpha=0.85,
               hatch=LAW_HATCH[law], edgecolor='white', label=law if (row, col) == (0, 0) else None)
    ax.set_xticks(range(len(tiers)))
    ax.set_xticklabels([TIER[t] for t in tiers], fontsize=7)
    ax.set_ylim(0, 1.05)
    ax.set_title(f'{SYSTEM[cls]} system', loc='left', fontsize=9)
    if col == 0:
        ax.set_ylabel('Runs ending in tolerance (%)')
    percent_axis(ax)
fig.legend(loc='lower center', ncol=4, fontsize=8, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.04, 1, 1))
save(fig, 'fig2_cells')
