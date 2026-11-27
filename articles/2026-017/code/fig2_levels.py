"""Figure 2: the level claims. For each law and test, the cells (system and structure kind) whose
median run is inside each tolerance line, of the cells the law ran. Copyright 2026 Kevin Cross.
MIT license."""
import numpy as np
import matplotlib.pyplot as plt

from style import JOBS, job_label, rows, save, TEXT

LINES = [('iec_check_point', 'IEC check\npoint'), ('iec_reference_point', 'IEC reference\npoint'),
         ('mil_composite', 'MIL\ncomposite'), ('mil_average_individual', 'MIL average,\nindividual'),
         ('mil_maxi_individual', 'MIL maxi,\nindividual')]
counts = {(r['version'], r['law'], r['test'], r['line']): r for r in rows('law_level_counts.csv')}
grid = np.full((len(JOBS), len(LINES)), np.nan)
text = [['' for _ in LINES] for _ in JOBS]
for i, j in enumerate(JOBS):
    for k, (line, _) in enumerate(LINES):
        r = counts.get(j + (line,))
        if r:
            grid[i, k] = int(r['cells_inside']) / int(r['cells'])
            text[i][k] = f"{r['cells_inside']} of {r['cells']}"
fig, ax = plt.subplots(figsize=(6.4, 8.2))
im = ax.imshow(grid, cmap='Blues', vmin=0, vmax=1, aspect='auto')
for i in range(len(JOBS)):
    for k in range(len(LINES)):
        ax.text(k, i, text[i][k], ha='center', va='center', fontsize=7,
                color='white' if grid[i, k] > 0.6 else TEXT)
ax.set_xticks(range(len(LINES)))
ax.set_xticklabels([label for _, label in LINES], fontsize=7)
ax.xaxis.tick_top()
ax.set_yticks(range(len(JOBS)))
ax.set_yticklabels([job_label(*j, short=False).replace('\n', ', ') for j in JOBS], fontsize=7)
ax.axhline(11.5, color=TEXT, lw=0.8)
ax.grid(False)
bar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
bar.set_label('Cells whose median run is inside the line (%)')
bar.set_ticks([0, 0.25, 0.5, 0.75, 1])
bar.set_ticklabels(['0', '25', '50', '75', '100'])
fig.tight_layout()
save(fig, 'fig2_levels')
